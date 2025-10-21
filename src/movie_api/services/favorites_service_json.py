"""
Implementation of the JSONFileFavorites.

Provides store for favorite movies.
"""

import json
import os

from movie_api.interfaces import FavoritesInterface


class JSONFileFavorites(FavoritesInterface):
    """Stores favorite movie IDs in a local JSON file."""

    def __init__(self, filepath: str):
        self._filepath = filepath
        self._favorites = self._load()

    def _load(self) -> list[int]:
        if os.path.exists(self._filepath):
            with open(self._filepath) as f:
                data = json.load(f)
                if isinstance(data, dict) and "favorites" in data:
                    favorites_list = data["favorites"]
                    if isinstance(favorites_list, list) and all(
                        isinstance(i, int) for i in favorites_list
                    ):
                        return favorites_list
        return []

    def _save(self):
        with open(self._filepath, "w") as f:
            json.dump({"favorites": self._favorites}, f, indent=2)

    def add(self, movie_id: int) -> None:
        """Add a movie to favorite store if not already."""
        if movie_id not in self._favorites:
            self._favorites.append(movie_id)
            self._save()

    def remove(self, movie_id: int) -> None:
        """Verify if a movie is favorited and remove it."""
        if movie_id in self._favorites:
            self._favorites.remove(movie_id)
            self._save()

    def get_all(self) -> list[int]:
        """Return all current favorited movies."""
        return self._favorites.copy()

    def is_favorite(self, movie_id: int) -> bool:
        """Return if a movie is currently favorited."""
        return movie_id in self._favorites
