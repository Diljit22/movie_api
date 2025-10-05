"""
Defines the abstract interfaces for services used in the Movie API.

These abstract base classes will define the "contracts" that concrete
service implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import Any


class CacheInterface(ABC):
    """Abstract interface for a key-value cache."""

    @abstractmethod
    def get(self, key: str) -> Any | None:
        """Retrieves an item from the cache."""
        pass

    @abstractmethod
    def set(self, key: str, data: Any) -> None:
        """Stores an item in the cache."""
        pass


class MovieServiceInterface(ABC):
    """Abstract interface for a service that provides movie data."""

    @abstractmethod
    async def get_trending_movies(self) -> dict:
        """Fetches the list of trending movies."""
        pass

    @abstractmethod
    async def get_movie_details(self, movie_id: int) -> dict:
        """Fetches details for a specific movie by its ID."""
        pass


class FavoritesInterface(ABC):
    """Abstract interface for managing favorite movies."""

    @abstractmethod
    def add(self, movie_id: int) -> None:
        """Add a movie to favorites."""
        pass

    @abstractmethod
    def remove(self, movie_id: int) -> None:
        """Remove a movie from favorites."""
        pass

    @abstractmethod
    def get_all(self) -> list[int]:
        """Get all favorite movie IDs."""
        pass

    @abstractmethod
    def is_favorite(self, movie_id: int) -> bool:
        """Check if a movie is in favorites."""
        pass
