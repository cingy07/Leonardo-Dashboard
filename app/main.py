"""
Leonardo Dashboard - Main Application Module
This module initializes the FastAPI application with all required middleware,
routes, and event handlers.
"""

import logging
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import redis
import time
from contextlib import asynccontextmanager

from app.core.config import settings
from app.api import api_router
from app.core.middleware import LoggingMiddleware, ErrorHandlingMiddleware
from app.services import cache_service, congressional_service, metrics_service

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for the FastAPI application.
    Handles startup and shutdown events.
    """
    # Startup: Initialize services and connections
    logger.info("Application starting up")
    
    # Initialize Redis connection
    app.state.redis = redis.from_url(settings.REDIS_URL)
    
    # Initialize services
    await congressional_service.load_committee_data()
    
    logger.info("Application startup complete")
    
    yield
    
    # Shutdown: Clean up resources
    logger.info("Application shutting down")
    app.state.redis.close()
    logger.info("Application shutdown complete")

# Create FastAPI application
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.ALLOWED_HOSTS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add custom middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(ErrorHandlingMiddleware)

# Add request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    
    # Record metrics if not a docs or health check request
    path = request.url.path
    if not path.startswith(("/docs", "/redoc", "/openapi.json", "/health")):
        await metrics_service.record_request_time(process_time * 1000)
    
    return response

# Include API routes
app.include_router(api_router)

@app.get("/")
async def root():
    """Root endpoint that provides basic API information"""
    return {
        "app": settings.API_TITLE,
        "version": settings.API_VERSION,
        "description": settings.API_DESCRIPTION,
        "docs": "/docs"
    }

# If this file is run directly, start the application with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)