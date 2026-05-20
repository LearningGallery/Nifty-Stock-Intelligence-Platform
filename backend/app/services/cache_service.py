"""
Cache Service using Redis
"""
import json
from typing import Any, Optional
import redis.asyncio as redis

from app.config import settings
from app.core.logging import logger


class CacheService:
    """
    Redis-based caching service
    """
    
    def __init__(self):
        self.redis_client = None
        self.ttl = settings.CACHE_TTL_SECONDS
    
    async def _get_client(self) -> redis.Redis:
        """
        Get or create Redis client
        """
        if not self.redis_client:
            self.redis_client = redis.Redis(
                host=settings.REDIS_ENDPOINT,
                port=settings.REDIS_PORT,
                db=settings.REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
        return self.redis_client
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache
        """
        try:
            client = await self._get_client()
            value = await client.get(key)
            
            if value:
                logger.debug(f"Cache hit: {key}")
                return json.loads(value)
            
            logger.debug(f"Cache miss: {key}")
            return None
            
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache with TTL
        """
        try:
            client = await self._get_client()
            serialized = json.dumps(value, default=str)
            
            await client.setex(
                key,
                ttl or self.ttl,
                serialized
            )
            
            logger.debug(f"Cache set: {key} (TTL: {ttl or self.ttl}s)")
            return True
            
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """
        Delete key from cache
        """
        try:
            client = await self._get_client()
            await client.delete(key)
            logger.debug(f"Cache deleted: {key}")
            return True
            
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache
        """
        try:
            client = await self._get_client()
            return await client.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """
        Increment counter (for rate limiting)
        """
        try:
            client = await self._get_client()
            return await client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Cache increment error: {e}")
            return 0
    
    async def expire(self, key: str, seconds: int) -> bool:
        """
        Set expiration on key
        """
        try:
            client = await self._get_client()
            return await client.expire(key, seconds)
        except Exception as e:
            logger.error(f"Cache expire error: {e}")
            return False
    
    async def close(self):
        """
        Close Redis connection
        """
        if self.redis_client:
            await self.redis_client.close()
