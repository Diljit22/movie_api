import json
from unittest.mock import AsyncMock, patch

import pytest
from fakeredis.aioredis import FakeRedis

from movie_service.src.movie_api.config import settings
from movie_service.src.movie_api.services.cache_redis import RedisCache


@pytest.fixture
def mock_redis_pool():
    """Fixture to mock the redis.ConnectionPool.from_url call."""
    with patch("redis.asyncio.ConnectionPool.from_url") as mock_pool:
        # We don't need the pool itself, just to prevent the real connection
        yield mock_pool


@pytest.mark.asyncio
async def test_redis_cache_set_and_get(mock_redis_pool):
    """Tests that a value can be set and retrieved from the Redis cache."""
    cache = RedisCache(redis_url="redis://fake")
    # Manually inject FakeRedis client for testing
    cache._client = FakeRedis()

    test_data = {"movie_id": 550, "title": "Fight Club"}
    await cache.set("movie:550", test_data)

    retrieved = await cache.get("movie:550")
    assert retrieved is not None
    assert retrieved["title"] == "Fight Club"


@pytest.mark.asyncio
async def test_redis_cache_miss(mock_redis_pool):
    """Tests that getting a non-existent key returns None."""
    cache = RedisCache(redis_url="redis://fake")
    cache._client = FakeRedis()
    assert await cache.get("miss:key") is None


@pytest.mark.asyncio
async def test_redis_cache_set_with_ttl(mock_redis_pool):
    """Tests that the cache SET command is called with the correct TTL (ex)."""
    cache = RedisCache(redis_url="redis://fake")
    # Use a mock client to inspect calls
    with patch("redis.asyncio.Redis") as mock_redis_class:
        mock_client = AsyncMock()
        mock_redis_class.return_value = mock_client
        cache._client = mock_client

        test_data = {"id": 1}
        await cache.set("key", test_data)

        expected_ttl = int(settings.cache_duration.total_seconds())
        mock_client.set.assert_awaited_once_with(
            "key", json.dumps(test_data), ex=expected_ttl
        )


@pytest.mark.asyncio
async def test_redis_cache_close_connection(mock_redis_pool):
    """Tests that the close method properly disconnects the client and pool."""
    cache = RedisCache(redis_url="redis://fake")
    with patch("redis.asyncio.Redis") as mock_redis_class:
        mock_client = AsyncMock()
        mock_pool_instance = AsyncMock()  # The pool also has async methods

        mock_redis_class.return_value = mock_client
        mock_redis_pool.return_value = mock_pool_instance
        cache._client = mock_client
        cache._pool = mock_pool_instance

        await cache.close()

        mock_client.close.assert_awaited_once()
        mock_pool_instance.disconnect.assert_awaited_once()
