import logging
import json
from typing import Optional, Any
import redis.asyncio as redis

from ..config.settings import settings

logger = logging.getLogger(__name__)


class RedisService:
    """
    Azure Cache for Redis service for:
    - Session memory
    - User context caching
    - Rate limiting
    - Temporary data storage
    """
    
    def __init__(self):
        self.client: Optional[redis.Redis] = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Redis client"""
        try:
            self.client = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                password=settings.REDIS_PASSWORD,
                ssl=settings.REDIS_SSL,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True
            )
            logger.info("Redis client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            self.client = None
    
    async def ping(self) -> bool:
        """Check Redis connection"""
        if not self.client:
            return False
        try:
            await self.client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set a key-value pair with optional TTL (seconds)"""
        if not self.client:
            logger.warning("Redis not available")
            return False
        
        try:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            
            if ttl:
                await self.client.setex(key, ttl, value)
            else:
                await self.client.set(key, value)
            
            logger.debug(f"Redis SET: {key}")
            return True
        except Exception as e:
            logger.error(f"Redis SET failed for {key}: {e}")
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value by key"""
        if not self.client:
            return None
        
        try:
            value = await self.client.get(key)
            if value is None:
                return None
            
            # Try to parse as JSON
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                return value
                
        except Exception as e:
            logger.error(f"Redis GET failed for {key}: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """Delete a key"""
        if not self.client:
            return False
        
        try:
            await self.client.delete(key)
            logger.debug(f"Redis DEL: {key}")
            return True
        except Exception as e:
            logger.error(f"Redis DELETE failed for {key}: {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> Optional[int]:
        """Increment a counter"""
        if not self.client:
            return None
        
        try:
            result = await self.client.incrby(key, amount)
            return result
        except Exception as e:
            logger.error(f"Redis INCR failed for {key}: {e}")
            return None
    
    async def check_rate_limit(self, user_id: str, limit: int, window: int) -> bool:
        """
        Check rate limit using sliding window
        
        Args:
            user_id: User identifier
            limit: Maximum requests allowed
            window: Time window in seconds
        
        Returns:
            True if allowed, False if rate limited
        """
        if not self.client:
            return True  # Allow if Redis unavailable
        
        key = f"rate_limit:{user_id}"
        
        try:
            # Get current count
            count = await self.client.get(key)
            
            if count is None:
                # First request in window
                await self.client.setex(key, window, 1)
                return True
            
            count = int(count)
            
            if count >= limit:
                logger.warning(f"Rate limit exceeded for user {user_id}: {count}/{limit}")
                return False
            
            # Increment counter
            await self.client.incr(key)
            return True
            
        except Exception as e:
            logger.error(f"Rate limit check failed: {e}")
            return True  # Fail open
    
    async def cache_user_context(self, user_id: str, context: dict, ttl: int = 3600) -> bool:
        """Cache user context for faster retrieval"""
        key = f"user_context:{user_id}"
        return await self.set(key, context, ttl)
    
    async def get_user_context(self, user_id: str) -> Optional[dict]:
        """Get cached user context"""
        key = f"user_context:{user_id}"
        return await self.get(key)
    
    async def cache_kb_article(self, article_id: str, content: dict, ttl: int = 86400) -> bool:
        """Cache frequently accessed knowledge base articles"""
        key = f"kb_article:{article_id}"
        return await self.set(key, content, ttl)
    
    async def get_kb_article(self, article_id: str) -> Optional[dict]:
        """Get cached KB article"""
        key = f"kb_article:{article_id}"
        return await self.get(key)
    
    async def close(self):
        """Close Redis connection"""
        if self.client:
            await self.client.close()
            logger.info("Redis connection closed")


# Singleton instance
_redis_service = None

def get_redis_service() -> RedisService:
    """Get singleton Redis service instance"""
    global _redis_service
    if _redis_service is None:
        _redis_service = RedisService()
    return _redis_service
