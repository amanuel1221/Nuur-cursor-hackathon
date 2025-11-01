"""
Redis connection and utilities
"""
import redis
from typing import Optional, Any
import json
from app.core.config import settings


class RedisClient:
    """Redis client wrapper"""
    
    def __init__(self):
        self.client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            encoding="utf-8",
        )
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from Redis"""
        value = self.client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in Redis"""
        if ttl is None:
            ttl = settings.REDIS_CACHE_TTL
        
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        
        return self.client.setex(key, ttl, value)
    
    def delete(self, key: str) -> bool:
        """Delete key from Redis"""
        return self.client.delete(key) > 0
    
    def exists(self, key: str) -> bool:
        """Check if key exists"""
        return self.client.exists(key) > 0
    
    def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter"""
        return self.client.incrby(key, amount)
    
    def expire(self, key: str, ttl: int) -> bool:
        """Set expiration on key"""
        return self.client.expire(key, ttl)


# Global Redis client instance
redis_client = RedisClient()

