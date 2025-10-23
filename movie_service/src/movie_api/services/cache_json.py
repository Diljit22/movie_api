"""
File-based JSON cache implementation.

Provides implementation of the CacheInterface using a local JSON file for
persistent storage.
"""

import json
import logging
import os
from datetime import UTC, datetime
from typing import Any, cast

from movie_service.src.movie_api.config import settings
from movie_service.src.movie_api.interfaces import CacheInterface


class JSONFileCache(CacheInterface):
    """A cache that persists data to a local JSON file."""

    def __init__(self, filepath: str):
        self._filepath = filepath
        # Ensure the directory for the cache file exists.
        data_dir = os.path.dirname(self._filepath)
        os.makedirs(data_dir, exist_ok=True)
        self._cache = self._load_cache_from_file()

    def _load_cache_from_file(self) -> dict[str, Any]:
        """Loads cache data from the JSON file."""
        if os.path.exists(self._filepath):
            with open(self._filepath) as f:
                try:
                    return cast(dict[str, Any], json.load(f))
                except json.JSONDecodeError:
                    logging.warning(
                        f"Cache file at {self._filepath} is corrupted. Starting fresh."
                    )
                    return {}
        return {}

    def _save_cache_to_file(self):
        """Saves the current cache to the JSON file."""
        with open(self._filepath, "w") as f:
            json.dump(self._cache, f, indent=2)

    async def get(self, key: str) -> Any | None:
        """Gets an item from the cache if the key exists and the item is not stale."""
        if key in self._cache:
            cached_item = self._cache[key]
            timestamp = datetime.fromisoformat(cached_item["timestamp"])
            if datetime.now(UTC) - timestamp < settings.cache_duration:
                logging.info(f"Cache hit for key: '{key}'")
                return cached_item["data"]
            else:
                logging.info(f"Cache stale for key: '{key}'")
        logging.info(f"Cache miss for key: '{key}'")
        return None

    async def set(self, key: str, data: Any) -> None:
        """Sets an item in the cache and saves it to the file."""
        self._cache[key] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "data": data,
        }
        self._save_cache_to_file()
        logging.info(f"Cache set for key: '{key}'")
