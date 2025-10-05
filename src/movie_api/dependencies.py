"""
Dependency Injection providers.

Contains functions that FastAPI's `Depends` system will use to
create and inject instances of our service and cache classes into the
API route handlers.
"""

import os

from movie_api.cache import JSONFileCache
from movie_api.config import settings
from movie_api.interfaces import (
    CacheInterface,
    FavoritesInterface,
    MovieServiceInterface,
)
from movie_api.services.favorites_service import JSONFileFavorites
from movie_api.services.tmdb import TMDBService

data_dir = os.path.dirname(settings.cache_filepath)
os.makedirs(data_dir, exist_ok=True)
_cache_instance = JSONFileCache(filepath=settings.cache_filepath)

_favorites_instance = JSONFileFavorites(filepath=settings.favorites_filepath)


def get_cache() -> CacheInterface:
    """Dependency provider for the cache."""
    return _cache_instance


def get_movie_service() -> MovieServiceInterface:
    """Dependency provider for the movie service."""
    return TMDBService()


def get_favorites_service() -> FavoritesInterface:
    """Dependency provider for the favorites service."""
    return _favorites_instance
