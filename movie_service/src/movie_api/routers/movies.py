"""
API endpoints for movie-related requests.

This router is decoupled from the underlying service implementations
through the use of FastAPI's dependency injection system.
"""

from enum import Enum
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from movie_service.src.movie_api.dependencies import (
    get_distributed_cache,
    get_in_memory_cache,
    get_movie_service,
)
from movie_service.src.movie_api.interfaces import (
    CacheInterface,
    MovieServiceInterface,
)
from movie_service.src.movie_api.monitoring import metrics
from movie_service.src.movie_api.monitoring.cache_stats import cache_stats
from movie_service.src.movie_api.schemas import (
    BatchMovieError,
    BatchMovieRequest,
    BatchMovieResponse,
    MovieDetail,
    TrendingMoviesResponse,
)

router = APIRouter(prefix="/api", tags=["Movies"])

L1CacheDep = Annotated[CacheInterface, Depends(get_in_memory_cache)]
L2CacheDep = Annotated[CacheInterface, Depends(get_distributed_cache)]
MovieServiceDep = Annotated[MovieServiceInterface, Depends(get_movie_service)]


class TimeWindow(str, Enum):
    DAY = "day"
    WEEK = "week"


@router.get("/trending/{time_window}", response_model=TrendingMoviesResponse)
async def get_trending_movies(
    time_window: TimeWindow,
    l1_cache: L1CacheDep,
    l2_cache: L2CacheDep,
    movie_service: MovieServiceDep,
):
    """
    Fetches trending movies using a 3-level cache:
    L1 (In-Memory) -> L2 (Redis/JSON) -> L3 (TMDB API)

    Endpoint is cached; response validated against TrendingMoviesResponse schema.
    """
    cache_key = f"trending_movies_{time_window.value}"

    # Check L1 Cache
    if cached_data := await l1_cache.get(cache_key):
        metrics.CACHE_HITS_TOTAL.labels(cache_level="l1").inc()
        cache_stats.record_l1_hit()
        return cached_data
    metrics.CACHE_MISSES_TOTAL.labels(cache_level="l1").inc()
    cache_stats.record_l1_miss()

    # Check L2 Cache
    if cached_data := await l2_cache.get(cache_key):
        metrics.CACHE_HITS_TOTAL.labels(cache_level="l2").inc()
        cache_stats.record_l2_hit()
        await l1_cache.set(cache_key, cached_data)  # Populate L1
        return cached_data
    metrics.CACHE_MISSES_TOTAL.labels(cache_level="l2").inc()
    cache_stats.record_l2_miss()

    # Fetch from L3 (TMDB Service)
    metrics.TMDB_API_CALLS_TOTAL.labels(endpoint="get_trending_movies").inc()
    cache_stats.record_api_call()
    fresh_data = await movie_service.get_trending_movies(time_window=time_window.value)

    # Populate L1 and L2 caches (sequential is fine)
    await l2_cache.set(cache_key, fresh_data)
    await l1_cache.set(cache_key, fresh_data)

    return fresh_data


async def _get_movie_details_with_cache(
    movie_id: int,
    l1_cache: CacheInterface,
    l2_cache: CacheInterface,
    movie_service: MovieServiceInterface,
) -> MovieDetail:
    """
    Helper function to fetch a single movie with 3-level caching.

    This eliminates code duplication between individual and batch endpoints.
    """
    cache_key = f"movie_details_{movie_id}"

    # Check L1 Cache
    if cached_data := await l1_cache.get(cache_key):
        metrics.CACHE_HITS_TOTAL.labels(cache_level="l1").inc()
        cache_stats.record_l1_hit()
        return MovieDetail.model_validate(cached_data)
    metrics.CACHE_MISSES_TOTAL.labels(cache_level="l1").inc()
    cache_stats.record_l1_miss()

    # Check L2 Cache
    if cached_data := await l2_cache.get(cache_key):
        metrics.CACHE_HITS_TOTAL.labels(cache_level="l2").inc()
        cache_stats.record_l2_hit()
        await l1_cache.set(cache_key, cached_data)  # Populate L1
        return MovieDetail.model_validate(cached_data)
    metrics.CACHE_MISSES_TOTAL.labels(cache_level="l2").inc()
    cache_stats.record_l2_miss()

    # Fetch from L3 (TMDB Service)
    metrics.TMDB_API_CALLS_TOTAL.labels(endpoint="get_movie_details").inc()
    cache_stats.record_api_call()
    fresh_data_dict = await movie_service.get_movie_details(movie_id)

    # Populate L1 and L2 caches (sequential is fine)
    await l2_cache.set(cache_key, fresh_data_dict)
    await l1_cache.set(cache_key, fresh_data_dict)

    return MovieDetail.model_validate(fresh_data_dict)


@router.get("/movie/{movie_id}", response_model=MovieDetail)
async def get_movie_details(
    movie_id: int,
    l1_cache: L1CacheDep,
    l2_cache: L2CacheDep,
    movie_service: MovieServiceDep,
):
    """
    Fetches movie details using a 3-level cache:
    L1 (In-Memory) -> L2 (Redis/JSON) -> L3 (TMDB API)

    Endpoint is cached; response validated against MovieDetail schema.
    """
    return await _get_movie_details_with_cache(
        movie_id, l1_cache, l2_cache, movie_service
    )


@router.post("/movies/batch", response_model=BatchMovieResponse)
async def get_movies_batch(
    request: BatchMovieRequest,
    l1_cache: L1CacheDep,
    l2_cache: L2CacheDep,
    movie_service: MovieServiceDep,
):
    """
    Fetches multiple movie details in a single request concurrently.

    Uses the same 3-level caching strategy as individual movie fetches.
    Processes requests concurrently for better performance.

    - **movie_ids**: List of movie IDs to fetch (max 50). Duplicates are ignored.
    - Returns lists of successfully fetched movies and any errors encountered.
    """
    if not request.movie_ids:
        raise HTTPException(status_code=400, detail="movie_ids cannot be empty.")

    # Remove duplicates while preserving order
    unique_ids = list(dict.fromkeys(request.movie_ids))

    if len(unique_ids) > 50:
        raise HTTPException(
            status_code=400, detail="Cannot request more than 50 unique movie IDs."
        )

    async def fetch_and_handle_errors(movie_id: int) -> MovieDetail | BatchMovieError:
        """Wrapper to catch exceptions and return a structured error."""
        try:
            return await _get_movie_details_with_cache(
                movie_id, l1_cache, l2_cache, movie_service
            )
        except HTTPException as e:
            return BatchMovieError(movie_id=movie_id, error=e.detail)
        except Exception as e:
            return BatchMovieError(movie_id=movie_id, error=str(e))

    # Fetch all movies concurrently
    import asyncio

    results = await asyncio.gather(
        *[fetch_and_handle_errors(mid) for mid in unique_ids]
    )

    # Separate successful results from errors
    movies = [res for res in results if isinstance(res, MovieDetail)]
    errors = [res for res in results if isinstance(res, BatchMovieError)]

    return BatchMovieResponse(
        movies=movies,
        total_requested=len(unique_ids),
        total_found=len(movies),
        errors=errors if errors else None,
    )


@router.get("/search", response_model=TrendingMoviesResponse)
async def search_movies(query: str, movies: MovieServiceDep):
    """
    Searches for movies by query string via the TMDB API.

    This endpoint is NOT cached as search results are dynamic.
    Response validated against TrendingMoviesResponse schema.
    """
    metrics.TMDB_API_CALLS_TOTAL.labels(endpoint="search_movies").inc()
    cache_stats.record_api_call()
    return await movies.search_movies(query)
