"""
In-memory cache implementation using functools.lru_cache.

Provides a simple, fast cache that lives in process memory.
"""

from functools import lru_cache
from typing import Any

from movie_service.src.movie_api.interfaces import CacheInterface

# Internal storage for cache data
_cache_store: dict[str, Any] = {}


@lru_cache(maxsize=256)
def _get_from_cache(key: str) -> Any | None:
    """
    Internal LRU cache lookup.

    This function's call results are memoized, so repeated calls
    with the same key are fast.
    """
    return _cache_store.get(key)


def _set_in_cache(key: str, data: Any) -> None:
    """Sets an item in the internal cache store."""
    _cache_store[key] = data
    # Clear the memoization so next get() will see new value
    _get_from_cache.cache_clear()


class InMemoryCache(CacheInterface):
    """
    Implementation of CacheInterface using Python's LRU cache.

    This cache is fast but:
    - Does not persist across service restarts
    - Is not shared across multiple service instances
    - Limited by process memory
    """

    async def get(self, key: str) -> Any | None:
        """Retrieves an item from the L1 cache."""
        return _get_from_cache(key)

    async def set(self, key: str, data: Any) -> None:
        """Sets an item in the L1 cache."""
        _set_in_cache(key, data)
