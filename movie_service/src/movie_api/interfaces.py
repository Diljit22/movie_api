"""
Defines the abstract interfaces for services used in the Movie API.

These abstract base classes will define the "contracts" that concrete
service implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import Any, Literal


class CacheInterface(ABC):
    """Abstract interface for a key-value cache."""

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """Retrieves an item from the cache."""
        pass

    @abstractmethod
    async def set(self, key: str, data: Any) -> None:
        """Stores an item in the cache."""
        pass


class MovieServiceInterface(ABC):
    """Abstract interface for a service that provides movie data."""

    @abstractmethod
    async def get_trending_movies(self, time_window: Literal["day", "week"]) -> dict:
        """Fetches the list of trending movies."""
        pass

    @abstractmethod
    async def get_movie_details(self, movie_id: int) -> dict:
        """Fetches details for a specific movie by its ID."""
        pass

    @abstractmethod
    async def search_movies(self, query: str) -> dict:
        """Searches for movies by a query string."""
        pass
