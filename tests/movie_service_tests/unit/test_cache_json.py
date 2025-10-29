"""
Unit tests for the JSONFileCache implementation.
"""

import asyncio
import json

import pytest

from movie_service.src.movie_api.config import settings
from movie_service.src.movie_api.services.cache_json import JSONFileCache


@pytest.mark.asyncio
async def test_cache_set_and_get(tmp_path):
    """Tests that a value can be set and then retrieved correctly."""
    cache_file = tmp_path / "test_cache.json"
    cache = JSONFileCache(filepath=str(cache_file))

    test_data = {"movie_id": 123, "title": "Test Movie"}
    await cache.set("my_key", test_data)

    retrieved_data = await cache.get("my_key")
    assert retrieved_data is not None
    assert retrieved_data["title"] == "Test Movie"


@pytest.mark.asyncio
async def test_cache_miss_for_non_existent_key(tmp_path):
    """Tests that getting a key that does not exist returns None."""
    cache_file = tmp_path / "test_cache.json"
    cache = JSONFileCache(filepath=str(cache_file))

    assert await cache.get("non_existent_key") is None


@pytest.mark.asyncio
async def test_cache_returns_none_for_stale_data(tmp_path, monkeypatch):
    """Tests that a value is not returned if its timestamp is older than the cache duration."""
    cache_file = tmp_path / "test_cache.json"
    cache = JSONFileCache(filepath=str(cache_file))

    # Temporarily change cache duration to -1 hour (instant staleness)
    monkeypatch.setattr(settings, "cache_duration_hours", -1)

    test_data = {"title": "A Stale Movie"}
    await cache.set("stale_key", test_data)

    # Data should be stale and return None
    assert await cache.get("stale_key") is None


@pytest.mark.asyncio
async def test_cache_persists_to_file(tmp_path):
    """Tests that cache data is persisted to the JSON file."""
    cache_file = tmp_path / "test_cache.json"
    cache = JSONFileCache(filepath=str(cache_file))

    test_data = {"title": "Persisted Movie"}
    await cache.set("persist_key", test_data)

    # Verify file was created
    assert cache_file.exists()

    # Read file directly and verify content
    with open(cache_file) as f:
        file_content = json.load(f)

    assert "persist_key" in file_content
    assert file_content["persist_key"]["data"]["title"] == "Persisted Movie"


@pytest.mark.asyncio
async def test_cache_loads_from_existing_file(tmp_path):
    """Tests that cache loads data from an existing file."""
    cache_file = tmp_path / "test_cache.json"

    # Create first cache instance and write data
    cache1 = JSONFileCache(filepath=str(cache_file))
    await cache1.set("key1", {"value": "first"})

    # Create second cache instance (should load from file)
    cache2 = JSONFileCache(filepath=str(cache_file))
    result = await cache2.get("key1")

    assert result is not None
    assert result["value"] == "first"


@pytest.mark.asyncio
async def test_cache_handles_corrupted_file(tmp_path):
    """Tests that cache handles a corrupted JSON file gracefully."""
    cache_file = tmp_path / "corrupted_cache.json"

    # Create a corrupted JSON file
    with open(cache_file, "w") as f:
        f.write("{invalid json content")

    # Cache should start fresh without crashing
    cache = JSONFileCache(filepath=str(cache_file))
    await cache.set("key", {"value": "data"})

    result = await cache.get("key")
    assert result is not None
    assert result["value"] == "data"


@pytest.mark.asyncio
async def test_cache_creates_directory_if_not_exists(tmp_path):
    """Tests that cache creates the directory structure if it doesn't exist."""
    cache_file = tmp_path / "nested" / "dir" / "cache.json"

    # Directory doesn't exist yet
    assert not cache_file.parent.exists()

    # Creating cache should create the directory
    cache = JSONFileCache(filepath=str(cache_file))
    await cache.set("key", {"value": "test"})

    # Verify directory was created
    assert cache_file.parent.exists()
    assert cache_file.exists()


@pytest.mark.asyncio
async def test_cache_handles_concurrent_writes(tmp_path):
    """Tests that cache handles concurrent writes correctly."""
    cache_file = tmp_path / "concurrent_cache.json"
    cache = JSONFileCache(filepath=str(cache_file))

    async def write_cache(i):
        await cache.set(f"key_{i}", {"value": i})

    # Concurrent writes
    await asyncio.gather(*[write_cache(i) for i in range(10)])

    # Verify all writes succeeded
    for i in range(10):
        result = await cache.get(f"key_{i}")
        assert result is not None
        assert result["value"] == i


@pytest.mark.asyncio
async def test_cache_overwrites_existing_key(tmp_path):
    """Tests that setting an existing key overwrites the old value."""
    cache_file = tmp_path / "test_cache.json"
    cache = JSONFileCache(filepath=str(cache_file))

    await cache.set("key", {"value": 1})
    await cache.set("key", {"value": 2})

    result = await cache.get("key")
    assert result["value"] == 2


@pytest.mark.asyncio
async def test_cache_stores_complex_data(tmp_path):
    """Tests that cache can store complex nested data structures."""
    cache_file = tmp_path / "test_cache.json"
    cache = JSONFileCache(filepath=str(cache_file))

    complex_data = {
        "movie": {
            "id": 550,
            "title": "Fight Club",
            "cast": ["Edward Norton", "Brad Pitt"],
            "ratings": {"imdb": 8.8, "rotten_tomatoes": 79},
            "genres": ["Drama", "Thriller"],
        }
    }

    await cache.set("complex", complex_data)
    result = await cache.get("complex")

    assert result is not None
    assert result["movie"]["id"] == 550
    assert len(result["movie"]["cast"]) == 2
    assert result["movie"]["ratings"]["imdb"] == 8.8
