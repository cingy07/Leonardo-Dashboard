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
        self.redis_client = None
        self.default_ttl = settings.CACHE_TTL
        self.metrics_service = None
    
    def initialize(self):
        """Initialize the cache service and establish connections."""
        self.redis_client = redis.from_url(settings.REDIS_URL)
        
        # Import here to avoid circular imports
        from app.services import metrics_service
        self.metrics_service = metrics_service
        
        logger.info("Cache service initialized")
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Retrieve a value from the cache.
        
        Args:
            key: Cache key to look up
            
        Returns:
            Cached value if found, None otherwise
        """
        try:
            if self.redis_client is None:
                self.initialize()
                
            value = self.redis_client.get(key)
            
            # Record cache event for metrics
            if self.metrics_service:
                await self.metrics_service.record_cache_event(hit=bool(value))
                
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
            if self.redis_client is None:
                self.initialize()
                
            expire = expire or self.default_ttl
            self.redis_client.setex(
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
            if self.redis_client is None:
                self.initialize()
                
            self.redis_client.delete(key)
            
        except Exception as e:
            logger.error(f"Cache deletion error: {str(e)}")
    
    async def clear(self, pattern: str = "*") -> None:
        """
        Clear all cached values matching a pattern.
        
        Args:
            pattern: Redis key pattern to match
        """
        try:
            if self.redis_client is None:
                self.initialize()
                
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
                
        except Exception as e:
            logger.error(f"Cache clear error: {str(e)}")
    
    async def is_healthy(self) -> bool:
        """
        Check if the cache service is healthy.
        
        Returns:
            True if the cache is working, False otherwise
        """
        try:
            if self.redis_client is None:
                self.initialize()
                
            self.redis_client.ping()
            return True
            
        except Exception as e:
            logger.error(f"Cache health check failed: {str(e)}")
            return False
    
    async def get_metrics(self, metric_name: str) -> Any:
        """
        Get a specific metric value from the metrics service.
        
        Args:
            metric_name: Name of the metric to retrieve
            
        Returns:
            The metric value or None if not available
        """
        if self.metrics_service is None:
            from app.services import metrics_service
            self.metrics_service = metrics_service
            
        return await self.metrics_service.get_metrics(metric_name)