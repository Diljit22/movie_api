"""Unit tests for the InMemoryCache implementation."""

import asyncio

import pytest

from movie_service.src.movie_api.services.cache_in_memory import InMemoryCache


@pytest.fixture
def cache() -> InMemoryCache:
    """Provides a fresh InMemoryCache instance for each test."""
    return InMemoryCache()


@pytest.mark.asyncio
async def test_cache_set_and_get(cache: InMemoryCache):
    """Tests that a value can be set and then retrieved correctly."""
    test_data = {"movie_id": 123, "title": "Test Movie"}
    await cache.set("my_key", test_data)

    retrieved_data = await cache.get("my_key")
    assert retrieved_data is not None
    assert retrieved_data["title"] == "Test Movie"
    assert retrieved_data["movie_id"] == 123


@pytest.mark.asyncio
async def test_cache_miss_for_non_existent_key(cache: InMemoryCache):
    """Tests that getting a key that does not exist returns None."""
    assert await cache.get("non_existent_key") is None


@pytest.mark.asyncio
async def test_cache_overwrites_existing_key(cache: InMemoryCache):
    """Tests that setting an existing key overwrites the old value."""
    await cache.set("key", {"value": 1})
    await cache.set("key", {"value": 2})

    result = await cache.get("key")
    assert result is not None
    assert result["value"] == 2


@pytest.mark.asyncio
async def test_cache_stores_different_data_types(cache: InMemoryCache):
    """Tests that cache can store different data types."""
    # Store dict and verify
    await cache.set("dict_key", {"type": "dictionary"})
    retrieved_dict = await cache.get("dict_key")
    assert retrieved_dict == {"type": "dictionary"}

    # Store list and verify
    await cache.set("list_key", [1, 2, 3])
    assert await cache.get("list_key") == [1, 2, 3]

    # Store string and verify
    await cache.set("string_key", "test")
    assert await cache.get("string_key") == "test"

    # Store int and verify
    await cache.set("int_key", 42)
    assert await cache.get("int_key") == 42


@pytest.mark.asyncio
async def test_cache_handles_multiple_keys(cache: InMemoryCache):
    """Tests that cache can handle multiple keys independently."""
    await cache.set("key1", {"value": 1})
    await cache.set("key2", {"value": 2})
    await cache.set("key3", {"value": 3})

    # Retrieve and assert each key
    result1 = await cache.get("key1")
    assert result1 is not None
    assert result1["value"] == 1

    result2 = await cache.get("key2")
    assert result2 is not None
    assert result2["value"] == 2

    result3 = await cache.get("key3")
    assert result3 is not None
    assert result3["value"] == 3


@pytest.mark.asyncio
async def test_cache_concurrent_operations(cache: InMemoryCache):
    """Tests that cache handles concurrent operations correctly."""

    async def write_to_cache(key: str, value: int):
        await cache.set(key, {"value": value})

    # Create 20 concurrent write tasks
    tasks = [write_to_cache(f"key_{i}", i) for i in range(20)]
    await asyncio.gather(*tasks)

    # Verify all writes succeeded
    for i in range(20):
        result = await cache.get(f"key_{i}")
        assert result is not None
        assert result["value"] == i
