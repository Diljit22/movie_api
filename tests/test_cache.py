"""
Unit tests for the JSONFileCache implementation.
"""

import asyncio

import pytest

from movie_api.cache import JSONFileCache
from movie_api.config import settings


def test_cache_set_and_get(tmp_path):
    """Tests that a value can be set and then retrieved correctly."""
    cache_file = tmp_path / "test_cache.json"
    cache = JSONFileCache(filepath=str(cache_file))

    test_data = {"movie_id": 123, "title": "Test Movie"}
    cache.set("my_key", test_data)

    retrieved_data = cache.get("my_key")
    assert retrieved_data is not None
    assert retrieved_data["title"] == "Test Movie"


def test_cache_miss_for_non_existent_key(tmp_path):
    """Tests that getting a key that does not exist returns None."""
    cache_file = tmp_path / "test_cache.json"
    cache = JSONFileCache(filepath=str(cache_file))

    assert cache.get("non_existent_key") is None


def test_cache_returns_none_for_stale_data(tmp_path, monkeypatch):
    """Tests that a value is not returned if its timestamp is older than the cache duration."""
    cache_file = tmp_path / "test_cache.json"
    cache = JSONFileCache(filepath=str(cache_file))

    # Temporarily change cache duration
    monkeypatch.setattr(settings, "cache_duration_hours", -1)

    test_data = {"title": "A Stale Movie"}
    cache.set("stale_key", test_data)

    assert cache.get("stale_key") is None


@pytest.mark.asyncio
async def test_cache_thread_safety(tmp_path):
    """Test cache handles concurrent writes."""
    cache_file = tmp_path / "concurrent_cache.json"
    cache = JSONFileCache(filepath=str(cache_file))

    async def write_cache(i):
        cache.set(f"key_{i}", {"value": i})

    # Concurrent writes
    await asyncio.gather(*[write_cache(i) for i in range(10)])

    for i in range(10):
        assert cache.get(f"key_{i}") == {"value": i}
