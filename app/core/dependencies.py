"""
FastAPI dependencies and middleware.
Contains reusable dependencies for authentication, rate limiting, and request processing.
"""
from fastapi import Header, HTTPException, Request
from fastapi.security.api_key import APIKeyHeader
from typing import Optional
from datetime import datetime, timedelta
import time
from app.core.config import settings
from app.core.exceptions import AppException

api_key_header = APIKeyHeader(name=settings.API_KEY_NAME)

async def get_api_key(api_key: str = Header(..., alias=settings.API_KEY_NAME)) -> str:
    """Validate API key from request header"""
    if api_key != settings.API_KEY:
        raise HTTPException(
            status_code=403,
            detail="Invalid API key"
        )
    return api_key

async def rate_limit(request: Request) -> None:
    """Implement rate limiting based on API key"""
    api_key = request.headers.get(settings.API_KEY_NAME)
    
    # Calculate time window
    now = datetime.utcnow()
    window_start = now - timedelta(minutes=1)
    
    # Check rate limit in Redis
    key = f"rate_limit:{api_key}:{window_start.timestamp():.0f}"
    current = await request.app.state.redis.incr(key)
    
    # Set expiration if this is the first request in the window
    if current == 1:
        await request.app.state.redis.expire(key, 60)
    
    if current > settings.RATE_LIMIT_PER_MINUTE:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded"
        )