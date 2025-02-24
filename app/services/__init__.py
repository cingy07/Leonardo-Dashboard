"""
Services package for the Leonardo Dashboard application.
This package contains service classes that implement core business logic,
handle external API interactions, and manage data operations.
"""

from app.services.congressional import CongressionalService
from app.services.cache import CacheService
from app.services.metrics import MetricsService

# Create singleton instances of services
congressional_service = CongressionalService()
cache_service = CacheService()
metrics_service = MetricsService()

__all__ = [
    "congressional_service",
    "cache_service",
    "metrics_service"
]