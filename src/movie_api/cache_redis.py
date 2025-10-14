import json
from typing import Any
import logging
import redis.asyncio as redis
from redis.asyncio.client import Redis

from movie_api.config import settings
from movie_api.interfaces import CacheInterface


class RedisCache(CacheInterface):
    def __init__(self, redis_url: str):
        self._client: Redis = redis.from_url(redis_url)
        
    async def get(self, key: str):
        cached_data = await self._client.get(key)
        if cached_data:
            logging.info(f"Cache hit for key: {key}")
            return json.loads(cached_data.decode("utf-8"))
        
        logging.info(f"Cache miss for key: {key}")
        
    async def set(self, key: str, data: Any):
        json_data = json.dumps(data)
        await self._client.set(key, json_data, ex=settings.cache_duration)
        logging.info(f"Cache set for key: {key}")
        