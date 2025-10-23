from functools import lru_cache
from typing import Any

from movie_api.interfaces import CacheInterface

@lru_cache(maxsize=256)
def _get_from_cache(key: str) -> Any | None:
    """Internal LRU cache. This function's results are stored in memory."""
    return None

def get_from_l1_cache(key: str) -> Any | None:
    """Retrieves an item from the L1 cache."""
    return _get_from_cache(key)

def set_in_l1_cache(key: str, data: Any) -> None:
    """Sets an item in the L1 cache."""
    @lru_cache(maxsize=256)
    def _prime_cache(_key: str) -> Any:
        return data
    
    _prime_cache(key)

class InMemoryCacheService(CacheInterface):
    """Implementation of CacheInterface using our LRU functions."""
    
    def get(self, key: str) -> Any | None:
        return get_from_l1_cache(key)

    def set(self, key: str, data: Any) -> None:
        set_in_l1_cache(key, data)