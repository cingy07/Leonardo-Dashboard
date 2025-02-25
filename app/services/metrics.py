"""
Metrics service for collecting and reporting application performance data.
Provides methods for recording and querying API usage patterns and performance metrics.
"""

import logging
import time
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from statistics import mean, median
import redis

from app.core.config import settings

logger = logging.getLogger(__name__)

class MetricsService:
    """
    Service for collecting and reporting application metrics.
    Handles recording API calls, response times, error rates, and other performance data.
    """
    
    def __init__(self):
        """Initialize the metrics service."""
        self.redis_client = None
        
    def initialize(self):
        """Initialize connections and setup metrics service."""
        self.redis_client = redis.from_url(settings.REDIS_URL)
        logger.info("Metrics service initialized")
        
    async def record_request_time(self, time_ms: float, endpoint: Optional[str] = None) -> None:
        """
        Record the time taken to process a request.
        
        Args:
            time_ms: Time in milliseconds
            endpoint: Optional endpoint identifier
        """
        try:
            if self.redis_client is None:
                self.initialize()
                
            # Get the current day for daily stats
            today = datetime.utcnow().strftime("%Y-%m-%d")
            
            # Update total requests
            self.redis_client.incr("metrics:requests_total")
            self.redis_client.incr(f"metrics:requests:{today}")
            
            # Record response time
            self.redis_client.lpush("metrics:response_times", time_ms)
            self.redis_client.ltrim("metrics:response_times", 0, 999)  # Keep last 1000 times
            
            # If endpoint is specified, record endpoint-specific metrics
            if endpoint:
                self.redis_client.incr(f"metrics:endpoint:{endpoint}:count")
                self.redis_client.lpush(f"metrics:endpoint:{endpoint}:times", time_ms)
                self.redis_client.ltrim(f"metrics:endpoint:{endpoint}:times", 0, 99)  # Keep last 100
                
        except Exception as e:
            logger.error(f"Error recording request time: {str(e)}")
    
    async def record_api_call(self, api_name: str, status_code: int, time_ms: Optional[float] = None) -> None:
        """
        Record metrics for an external API call.
        
        Args:
            api_name: Name of the API being called
            status_code: HTTP status code of the response
            time_ms: Optional response time in milliseconds
        """
        try:
            if self.redis_client is None:
                self.initialize()
                
            # Record call
            self.redis_client.incr(f"metrics:api:{api_name}:calls")
            
            # Record success/failure
            if 200 <= status_code < 300:
                self.redis_client.incr(f"metrics:api:{api_name}:success")
            else:
                self.redis_client.incr(f"metrics:api:{api_name}:error")
                self.redis_client.incr(f"metrics:api:{api_name}:error:{status_code}")
                
            # Record response time if provided
            if time_ms is not None:
                self.redis_client.lpush(f"metrics:api:{api_name}:times", time_ms)
                self.redis_client.ltrim(f"metrics:api:{api_name}:times", 0, 99)
                
        except Exception as e:
            logger.error(f"Error recording API call: {str(e)}")
    
    async def record_cache_event(self, hit: bool) -> None:
        """
        Record a cache hit or miss.
        
        Args:
            hit: True for a cache hit, False for a miss
        """
        try:
            if self.redis_client is None:
                self.initialize()
                
            # Increment total cache access counter
            self.redis_client.incr("metrics:cache:total")
            
            # Increment hit or miss counter
            if hit:
                self.redis_client.incr("metrics:cache:hits")
            else:
                self.redis_client.incr("metrics:cache:misses")
                
        except Exception as e:
            logger.error(f"Error recording cache event: {str(e)}")
    
    async def get_cache_hit_rate(self) -> float:
        """
        Calculate the cache hit rate percentage.
        
        Returns:
            Percentage of cache hits
        """
        try:
            if self.redis_client is None:
                self.initialize()
                
            total = int(self.redis_client.get("metrics:cache:total") or 0)
            hits = int(self.redis_client.get("metrics:cache:hits") or 0)
            
            if total == 0:
                return 0.0
                
            return (hits / total) * 100
            
        except Exception as e:
            logger.error(f"Error calculating cache hit rate: {str(e)}")
            return 0.0
    
    async def get_error_rate(self) -> float:
        """
        Calculate the API error rate percentage.
        
        Returns:
            Percentage of requests resulting in errors
        """
        try:
            if self.redis_client is None:
                self.initialize()
                
            # Get stats for the past day
            today = datetime.utcnow().strftime("%Y-%m-%d")
            requests = int(self.redis_client.get(f"metrics:requests:{today}") or 0)
            errors = int(self.redis_client.get(f"metrics:errors:{today}") or 0)
            
            if requests == 0:
                return 0.0
                
            return (errors / requests) * 100
            
        except Exception as e:
            logger.error(f"Error calculating error rate: {str(e)}")
            return 0.0
    
    async def get_average_response_time(self) -> float:
        """
        Calculate the average response time.
        
        Returns:
            Average response time in milliseconds
        """
        try:
            if self.redis_client is None:
                self.initialize()
                
            # Get the last 100 response times
            times = self.redis_client.lrange("metrics:response_times", 0, 99)
            
            if not times:
                return 0.0
                
            times = [float(t) for t in times]
            return sum(times) / len(times)
            
        except Exception as e:
            logger.error(f"Error calculating average response time: {str(e)}")
            return 0.0
    
    async def get_metrics(self, metric_name: str) -> Any:
        """
        Get a specific metric by name.
        
        Args:
            metric_name: Name of the metric to retrieve
            
        Returns:
            Metric value
        """
        try:
            if self.redis_client is None:
                self.initialize()
                
            if metric_name == "requests_total":
                return int(self.redis_client.get("metrics:requests_total") or 0)
                
            elif metric_name == "avg_response_time":
                return await self.get_average_response_time()
                
            elif metric_name == "error_rate":
                return await self.get_error_rate()
                
            elif metric_name == "cache_hit_rate":
                return await self.get_cache_hit_rate()
                
            else:
                # Try to get the metric directly from Redis
                value = self.redis_client.get(f"metrics:{metric_name}")
                if value is not None:
                    try:
                        return int(value)
                    except ValueError:
                        try:
                            return float(value)
                        except ValueError:
                            return value.decode("utf-8")
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving metric {metric_name}: {str(e)}")
            return None
    
    async def get_current_metrics(self) -> Dict[str, Any]:
        """
        Get a comprehensive metrics report.
        
        Returns:
            Dictionary of all current metrics
        """
        try:
            return {
                "requests_total": await self.get_metrics("requests_total"),
                "average_response_time": await self.get_average_response_time(),
                "error_rate": await self.get_error_rate(),
                "cache_hit_rate": await self.get_cache_hit_rate(),
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error retrieving current metrics: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }