"""
API endpoints for movie-related requests.

This router is decoupled from the underlying service implementations
through the use of FastAPI's dependency injection system.
"""

import asyncio
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
    L1 (In-Memory) -> L2 (Redis) -> L3 (TMDB API)

    Endpoint is cached; response validated against TrendingMoviesResponse schema.
    """
    cache_key = f"trending_movies_{time_window.value}"

    # Check L1
    cached_data = await l1_cache.get(cache_key)
    if cached_data:
        return cached_data

    # Check L2
    cached_data = await l2_cache.get(cache_key)
    if cached_data:
        await l1_cache.set(cache_key, cached_data)  # Populate L1
        return cached_data

    # Fetch from L3
    fresh_data = await movie_service.get_trending_movies(time_window=time_window.value)

    # Populate L1 + L2
    await l2_cache.set(cache_key, fresh_data)
    await l1_cache.set(cache_key, fresh_data)

    return fresh_data


@router.get("/movie/{movie_id}", response_model=MovieDetail)
async def get_movie_details(
    movie_id: int,
    l1_cache: L1CacheDep,
    l2_cache: L2CacheDep,
    movie_service: MovieServiceDep,
):
    """
    Fetches movie details using a 3-level cache:
    L1 (In-Memory) -> L2 (Redis) -> L3 (TMDB API)

    Endpoint is cached; response validated against MovieDetail schema.
    """
    cache_key = f"movie_details_{movie_id}"

    # Check L1
    cached_data = await l1_cache.get(cache_key)
    if cached_data:
        return cached_data

    # Check L2
    cached_data = await l2_cache.get(cache_key)
    if cached_data:
        await l1_cache.set(cache_key, cached_data)  # Populate L1
        return cached_data

    # Fetch from L3
    fresh_data = await movie_service.get_movie_details(movie_id)

    # Populate L1 + L2
    await l2_cache.set(cache_key, fresh_data)
    await l1_cache.set(cache_key, fresh_data)

    return fresh_data


@router.post("/movies/batch", response_model=BatchMovieResponse)
async def get_movies_batch(
    request: BatchMovieRequest,
    l1_cache: L1CacheDep,
    l2_cache: L2CacheDep,
    movie_service: MovieServiceDep,
):
    """
    Fetches multiple movie details in a single request.

    Uses the same 3-level caching strategy as individual movie fetches,
    but processes multiple movies concurrently for better performance.

    - **movie_ids**: List of movie IDs to fetch (max 50)
    - Returns: List of movie details with success status for each
    """
    if len(request.movie_ids) > 50:
        raise HTTPException(
            status_code=400, detail="Maximum 50 movies can be requested at once"
        )

    if not request.movie_ids:
        raise HTTPException(
            status_code=400, detail="At least one movie_id must be provided"
        )

    # Remove duplicates while preserving order
    unique_ids = list(dict.fromkeys(request.movie_ids))

    async def fetch_single_movie(
        movie_id: int,
    ) -> tuple[bool, MovieDetail | None, int | None, str | None]:
        """
        Fetch a single movie with the same caching logic.
        Returns: (success, movie_data, movie_id_on_error, error_message)
        """
        try:
            cache_key = f"movie_details_{movie_id}"

            # Check L1
            cached_data = await l1_cache.get(cache_key)
            if cached_data:
                return (True, cached_data, None, None)

            # Check L2
            cached_data = await l2_cache.get(cache_key)
            if cached_data:
                await l1_cache.set(cache_key, cached_data)
                return (True, cached_data, None, None)

            # Fetch from L3
            fresh_data = await movie_service.get_movie_details(movie_id)

            # Populate caches
            await l2_cache.set(cache_key, fresh_data)
            await l1_cache.set(cache_key, fresh_data)

            return (True, fresh_data, None, None)

        except HTTPException as e:
            return (False, None, movie_id, e.detail)
        except Exception as e:
            return (False, None, movie_id, str(e))

    # Fetch all movies concurrently
    results = await asyncio.gather(*[fetch_single_movie(mid) for mid in unique_ids])

    # Separate successful and failed results
    movies: list[MovieDetail] = []
    errors: list[BatchMovieError] = []

    for success, movie_data, failed_id, error_msg in results:
        if success and movie_data:
            movies.append(movie_data)
        elif failed_id is not None and error_msg is not None:
            errors.append(BatchMovieError(movie_id=failed_id, error=error_msg))

    return BatchMovieResponse(
        movies=movies,
        total_requested=len(unique_ids),
        total_found=len(movies),
        errors=errors if errors else None,
    )


@router.get("/search", response_model=TrendingMoviesResponse)
async def search_movies(query: str, movies: MovieServiceDep):
    """
    Fetches movie details via query.

    Endpoint is NOT cached; response validated against TrendingMoviesResponse schema.
    """
    return await movies.search_movies(query)
