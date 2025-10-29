"""
Implementation of the FavoritesServiceInterface using a local JSON file.
"""

import json
import logging
import os
from collections import defaultdict

from user_service.src.user_api.interfaces import FavoritesServiceInterface


class JSONFileFavoritesService(FavoritesServiceInterface):
    """Stores favorite movie IDs in a local JSON file, keyed by user ID."""

    def __init__(self, filepath: str):
        self._filepath = filepath
        # Ensure the directory for the file exists.
        data_dir = os.path.dirname(self._filepath)
        os.makedirs(data_dir, exist_ok=True)
        # The internal cache is a dict mapping user_id (str) to a set of movie_ids (int)
        self._favorites: dict[str, set[int]] = self._load()

    def _load(self) -> dict[str, set[int]]:
        """Loads favorites from the JSON file."""
        if not os.path.exists(self._filepath):
            return defaultdict(set)

        try:
            with open(self._filepath) as f:
                # Load data, converting lists of movie_ids to sets
                raw_data = json.load(f)
                return defaultdict(
                    set,
                    {
                        user_id: set(movie_ids)
                        for user_id, movie_ids in raw_data.items()
                    },
                )
        except (json.JSONDecodeError, TypeError):
            logging.warning(
                f"Favorites file at {self._filepath} is corrupted. Starting fresh."
            )
            return defaultdict(set)

    def _save(self):
        """Saves the current favorites to the JSON file."""
        with open(self._filepath, "w") as f:
            # Convert sets to lists for JSON serialization
            serializable_data = {
                user_id: list(movie_ids)
                for user_id, movie_ids in self._favorites.items()
            }
            json.dump(serializable_data, f, indent=2)

    def add(self, user_id: int, movie_id: int) -> None:
        """Adds a movie to a user's favorites and saves to file."""
        self._favorites[str(user_id)].add(movie_id)
        self._save()

    def remove(self, user_id: int, movie_id: int) -> None:
        """Removes a movie from a user's favorites and saves to file."""
        self._favorites[str(user_id)].discard(movie_id)
        self._save()

    def get_all_for_user(self, user_id: int) -> list[int]:
        """Returns all favorite movie IDs for a specific user."""
        return list(self._favorites.get(str(user_id), set()))

    def is_favorite(self, user_id: int, movie_id: int) -> bool:
        """Checks if a movie is in a user's favorites."""
        return movie_id in self._favorites.get(str(user_id), set())
