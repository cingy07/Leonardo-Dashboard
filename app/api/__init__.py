"""
API Package Initializer

This module serves as the entry point for the API package, organizing all routes
and providing a clean interface for the main application to access API functionality.
It combines different route modules and handles API-wide configuration.
"""

from fastapi import APIRouter
from app.api.routes import (
    congressional_router,
    health_router,
    metrics_router
)

# Create the main API router that will combine all sub-routers
api_router = APIRouter()

# Include all route modules with appropriate prefixes
api_router.include_router(
    congressional_router,
    prefix="/congressional",
    tags=["Congressional Data"]
)

api_router.include_router(
    health_router,
    prefix="/health",
    tags=["Health Checks"]
)

api_router.include_router(
    metrics_router,
    prefix="/metrics",
    tags=["Metrics"]
)

# Export the combined router for the main application to use
__all__ = ["api_router"]