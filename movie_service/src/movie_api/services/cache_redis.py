"""
Redis cache implementation.

Provides distributed caching using Redis for persistence across
service instances and restarts.
"""

import json
import logging
from typing import Any

import redis.asyncio as redis
from redis.asyncio.client import Redis

from movie_service.src.movie_api.config import settings
from movie_service.src.movie_api.interfaces import CacheInterface


class RedisCache(CacheInterface):
    """Redis-based cache implementation with connection pooling."""

    def __init__(self, redis_url: str):
        # Create connection pool for better performance
        self._pool = redis.ConnectionPool.from_url(
            redis_url,
            max_connections=10,
            decode_responses=False,
        )
        self._client: Redis = redis.Redis(connection_pool=self._pool)

    async def get(self, key: str) -> Any | None:
        """Retrieves an item from Redis cache."""
        cached_data = await self._client.get(key)
        if cached_data:
            logging.info(f"Cache hit for key: {key}")
            return json.loads(cached_data.decode("utf-8"))

        logging.info(f"Cache miss for key: {key}")
        return None

    async def set(self, key: str, data: Any) -> None:
        """Stores an item in Redis cache with TTL."""
        json_data = json.dumps(data)
        await self._client.set(
            key, json_data, ex=int(settings.cache_duration.total_seconds())
        )
        logging.info(f"Cache set for key: {key}")

    async def close(self) -> None:
        """Closes the Redis connection pool."""
        await self._client.close()
        await self._pool.disconnect()
