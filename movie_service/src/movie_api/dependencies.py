"""
Dependency Injection providers.

Contains functions that FastAPI's `Depends` system will use to
create and inject instances of our service and cache classes into the
API route handlers.
"""

from functools import cache, lru_cache

from movie_service.src.movie_api.config import settings
from movie_service.src.movie_api.interfaces import (
    CacheInterface,
    MovieServiceInterface,
)
from movie_service.src.movie_api.services.cache_in_memory import InMemoryCache
from movie_service.src.movie_api.services.cache_json import JSONFileCache
from movie_service.src.movie_api.services.cache_redis import RedisCache
from movie_service.src.movie_api.services.tmdb import TMDBService

CACHE_IMPLEMENTATIONS = {
    "redis": lambda: RedisCache(redis_url=settings.redis_url),
    "json_file": lambda: JSONFileCache(filepath=settings.cache_filepath),
}


@lru_cache
def get_in_memory_cache() -> CacheInterface:
    """Dependency provider for the L1 in-memory cache."""
    return InMemoryCache()


@cache
def get_distributed_cache() -> CacheInterface:
    """Dependency provider for the cache."""
    factory = CACHE_IMPLEMENTATIONS.get(settings.cache_implementation)
    if not factory:
        raise ValueError(
            f"Unknown cache_implementation: '{settings.cache_implementation}'"
        )
    return factory()


@cache
def get_movie_service() -> MovieServiceInterface:
    """Dependency provider for the movie service."""
    return TMDBService()
