"""
Unit tests for the InMemoryCache implementation.
"""

import pytest

from movie_service.src.movie_api.services.cache_in_memory import InMemoryCache


@pytest.mark.asyncio
async def test_cache_set_and_get():
    """Tests that a value can be set and then retrieved correctly."""
    cache = InMemoryCache()

    test_data = {"movie_id": 123, "title": "Test Movie"}
    await cache.set("my_key", test_data)

    retrieved_data = await cache.get("my_key")
    assert retrieved_data is not None
    assert retrieved_data["title"] == "Test Movie"
    assert retrieved_data["movie_id"] == 123


@pytest.mark.asyncio
async def test_cache_miss_for_non_existent_key():
    """Tests that getting a key that does not exist returns None."""
    cache = InMemoryCache()

    assert await cache.get("non_existent_key") is None


@pytest.mark.asyncio
async def test_cache_overwrites_existing_key():
    """Tests that setting an existing key overwrites the old value."""
    cache = InMemoryCache()

    await cache.set("key", {"value": 1})
    await cache.set("key", {"value": 2})

    result = await cache.get("key")
    assert result["value"] == 2


@pytest.mark.asyncio
async def test_cache_stores_different_data_types():
    """Tests that cache can store different data types."""
    cache = InMemoryCache()

    # Store dict
    await cache.set("dict", {"type": "dictionary"})
    assert await cache.get("dict") == {"type": "dictionary"}

    # Store list
    await cache.set("list", [1, 2, 3])
    assert await cache.get("list") == [1, 2, 3]

    # Store string
    await cache.set("string", "test")
    assert await cache.get("string") == "test"

    # Store int
    await cache.set("int", 42)
    assert await cache.get("int") == 42


@pytest.mark.asyncio
async def test_cache_handles_multiple_keys():
    """Tests that cache can handle multiple keys independently."""
    cache = InMemoryCache()

    await cache.set("key1", {"value": 1})
    await cache.set("key2", {"value": 2})
    await cache.set("key3", {"value": 3})

    assert (await cache.get("key1"))["value"] == 1
    assert (await cache.get("key2"))["value"] == 2
    assert (await cache.get("key3"))["value"] == 3


@pytest.mark.asyncio
async def test_cache_concurrent_operations():
    """Tests that cache handles concurrent operations."""
    import asyncio

    cache = InMemoryCache()

    async def write_cache(i):
        await cache.set(f"key_{i}", {"value": i})

    # Concurrent writes
    await asyncio.gather(*[write_cache(i) for i in range(20)])

    # Verify all writes succeeded
    for i in range(20):
        result = await cache.get(f"key_{i}")
        assert result["value"] == i
