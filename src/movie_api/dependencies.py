"""
Dependency Injection providers.

Contains functions that FastAPI's `Depends` system will use to
create and inject instances of our service and cache classes into the
API route handlers.
"""
from movie_api.services.cache_json import JSONFileCache
from movie_api.services.cache_redis import RedisCache
from movie_api.config import settings
from movie_api.interfaces import (
    CacheInterface,
    FavoritesInterface,
    MovieServiceInterface,
)
from movie_api.services.favorites_service_json import JSONFileFavorites
from movie_api.services.in_memory_favorites import InMemoryFavorites
from movie_api.services.tmdb import TMDBService

CACHE_IMPLEMENTATIONS = {
    "redis": RedisCache,
    "json_file": JSONFileCache,
}

FAVORITES_IMPLEMENTATIONS = {
    "json_file": JSONFileFavorites,
    "in_memory": InMemoryFavorites,
}

def create_cache_instance() -> CacheInterface:
    """Factory function to create the appropriate cache instance."""
    impl_key = settings.cache_implementation
    ImplementationClass = CACHE_IMPLEMENTATIONS.get(impl_key)

    if not ImplementationClass:
        raise ValueError(f"Unknown cache_implementation: '{impl_key}'")

    if ImplementationClass == RedisCache:
        return RedisCache(redis_url=settings.redis_url)
    
    elif ImplementationClass == JSONFileCache:
        return JSONFileCache(filepath=settings.cache_filepath)
    
    else:
        return ImplementationClass()

def create_favorites_instance() -> FavoritesInterface:
    """Factory function to create the appropriate favorites service instance."""
    impl_key = settings.favorites_implementation
    ImplementationClass = FAVORITES_IMPLEMENTATIONS.get(impl_key)

    if not ImplementationClass:
        raise ValueError(f"Unknown favorites_implementation: '{impl_key}'")

    if ImplementationClass == JSONFileFavorites:
        return JSONFileFavorites(filepath=settings.favorites_filepath)

    else:
        # No-arg constructors (e.g. InMemoryFavorites)
        return ImplementationClass()

_cache_instance = create_cache_instance()
_favorites_instance = create_favorites_instance()


def get_cache() -> CacheInterface:
    """Dependency provider for the cache."""
    return _cache_instance


def get_movie_service() -> MovieServiceInterface:
    """Dependency provider for the movie service."""
    return TMDBService()


def get_favorites_service() -> FavoritesInterface:
    """Dependency provider for the favorites service."""
    return _favorites_instance
