"""
Caching service for storing and retrieving frequently accessed data.
Implements caching strategies to improve application performance.
"""

import redis
import json
import logging
from typing import Any, Optional
from datetime import datetime, timedelta

from app.core.config import settings
from app.core.exceptions import ExternalServiceError

logger = logging.getLogger(__name__)

class CacheService:
    """
    Service for managing application-wide caching using Redis.
    Provides methods for storing and retrieving cached data with TTL support.
    """
    
    def __init__(self):
        """Initialize Redis connection and configure cache settings."""
        self.redis = redis.from_url(settings.REDIS_URL)
        self.default_ttl = settings.CACHE_TTL
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the cache.
        
        Args:
            key: Cache key to look up
            
        Returns:
            Cached value if found, None otherwise
        """
        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
            return None
            
        except Exception as e:
            logger.error(f"Cache retrieval error: {str(e)}")
            return None
    
    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None
    ) -> None:
        """
        Store a value in the cache.
        
        Args:
            key: Cache key
            value: Value to store
            expire: Optional TTL in seconds
        """
        try:
            expire = expire or self.default_ttl
            self.redis.setex(
                key,
                expire,
                json.dumps(value)
            )
            
        except Exception as e:
            logger.error(f"Cache storage error: {str(e)}")
    
    async def delete(self, key: str) -> None:
        """
        Remove a value from the cache.
        
        Args:
            key: Cache key to remove
        """
        try:
            self.redis.delete(key)
            
        except Exception as e:
            logger.error(f"Cache deletion error: {str(e)}")
    
    async def clear(self, pattern: str = "*") -> None:
        """
        Clear all cached values matching a pattern.
        
        Args:
            pattern: Redis key pattern to match
        """
        try:
            keys = self.redis.keys(pattern)
            if keys:
                self.redis.delete(*keys)
                
        except Exception as e:
            logger.error(f"Cache clear error: {str(e)}")
    
    async def is_healthy(self) -> bool:
        """
        Check if the cache service is healthy.
        
        Returns:
            True if the cache is working, False otherwise
        """
        try:
            self.redis.ping()
            return True
            
        except Exception as e:
            logger.error(f"Cache health check failed: {str(e)}")
            return False