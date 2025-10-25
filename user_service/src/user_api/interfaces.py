"""
Defines the abstract interfaces for services in the User API.
"""

from abc import ABC, abstractmethod
from typing import Any

from user_service.src.user_api.schemas import User, UserCreate

class FavoritesServiceInterface(ABC):
    """Abstract interface for managing a user's favorite movies."""

    @abstractmethod
    def add(self, user_id: int, movie_id: int) -> None:
        """Add a movie to a user's favorites."""
        pass

    @abstractmethod
    def remove(self, user_id: int, movie_id: int) -> None:
        """Remove a movie from a user's favorites."""
        pass

    @abstractmethod
    def get_all_for_user(self, user_id: int) -> list[int]:
        """Get all favorite movie IDs for a specific user."""
        pass

    @abstractmethod
    def is_favorite(self, user_id: int, movie_id: int) -> bool:
        """Check if a movie is in a user's favorites."""
        pass


class UserServiceInterface(ABC):
    """Abstract interface for managing users."""

    @abstractmethod
    def get_user_by_id(self, user_id: int) -> User | None:
        """Retrieves a user by their ID."""
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> User | None:
        """Retrieves a user by their email address."""
        pass

    @abstractmethod
    def create_user(self, user_data: UserCreate) -> User:
        """Creates a new user and returns their data."""
        pass