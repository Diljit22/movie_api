"""
API endpoints for movie-related requests.

This router is decoupled from the underlying service implementations
through the use of FastAPI's dependency injection system.
"""

from enum import Enum
from typing import Annotated

from fastapi import APIRouter, Depends

from movie_api.dependencies import get_cache, get_movie_service
from movie_api.interfaces import CacheInterface, MovieServiceInterface
from movie_api.schemas import MovieDetail, TrendingMoviesResponse

router = APIRouter(prefix="/api", tags=["Movies"])

CacheDep = Annotated[CacheInterface, Depends(get_cache)]
MovieServiceDep = Annotated[MovieServiceInterface, Depends(get_movie_service)]


class TimeWindow(str, Enum):
    DAY = "day"
    WEEK = "week"


@router.get("/trending/{time_window}", response_model=TrendingMoviesResponse)
async def get_trending_movies(
    time_window: TimeWindow,
    cache: CacheDep,
    movie_service: MovieServiceDep,
):
    """
    Fetches the list of movies trending today.

    Endpoint is cached; response validated against TrendingMoviesResponse schema.
    """
    cache_key = f"trending_movies_{time_window.value}"

    cached_data = await cache.get(cache_key)
    if cached_data:
        return cached_data

    fresh_data = await movie_service.get_trending_movies(time_window=time_window.value)
    cache.set(cache_key, fresh_data)

    return fresh_data


@router.get("/movie/{movie_id}", response_model=MovieDetail)
async def get_movie_details(
    movie_id: int,
    cache: CacheDep,
    movie_service: MovieServiceDep,
):
    """
    Fetches movie details via movie ID.

    Endpoint is cached; response validated against MovieDetail schema.
    """
    cache_key = f"movie_details_{movie_id}"

    cached_data = await cache.get(cache_key)
    if cached_data:
        return cached_data

    fresh_data = await movie_service.get_movie_details(movie_id)
    cache.set(cache_key, fresh_data)

    return fresh_data


@router.get("/search", response_model=TrendingMoviesResponse)
async def search_movies(query: str, movies: MovieServiceDep):
    """
    Fetches movie details via query.

    Endpoint is NOT cached; response validated against MovieDetail schema.
    """
    return await movies.search_movies(query)