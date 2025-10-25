"""
In-memory implementation of the FavoritesServiceInterface.

Data is stored in a dictionary and is lost on application restart.
"""
from collections import defaultdict

from user_service.src.user_api.interfaces import FavoritesServiceInterface


class InMemoryFavoritesService(FavoritesServiceInterface):
    """Stores favorite movie IDs in memory, keyed by user ID."""

    def __init__(self):
        # A dictionary where each key is a user_id and each value is a set of movie_ids
        self._favorites: dict[int, set[int]] = defaultdict(set)

    def add(self, user_id: int, movie_id: int) -> None:
        self._favorites[user_id].add(movie_id)

    def remove(self, user_id: int, movie_id: int) -> None:
        if user_id in self._favorites:
            self._favorites[user_id].discard(movie_id)

    def get_all_for_user(self, user_id: int) -> list[int]:
        return list(self._favorites.get(user_id, set()))

    def is_favorite(self, user_id: int, movie_id: int) -> bool:
        return movie_id in self._favorites.get(user_id, set())