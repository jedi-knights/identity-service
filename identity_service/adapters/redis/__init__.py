"""Redis cache adapter."""
from typing import Optional

from redis.asyncio import Redis

from identity_service.ports.cache import CachePort


class RedisCache(CachePort):
    """Redis-based cache implementation."""

    def __init__(self, redis_client: Redis) -> None:
        self.redis = redis_client

    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        value = await self.redis.get(key)
        return value.decode("utf-8") if value else None

    async def set(self, key: str, value: str, expiry_seconds: Optional[int] = None) -> bool:
        """Set value in cache with optional expiry."""
        if expiry_seconds:
            await self.redis.setex(key, expiry_seconds, value)
        else:
            await self.redis.set(key, value)
        return True

    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        result = await self.redis.delete(key)
        return result > 0

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        result = await self.redis.exists(key)
        return result > 0
