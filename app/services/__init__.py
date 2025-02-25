"""
Services package for the Leonardo Dashboard application.
This package contains service classes that implement core business logic,
handle external API interactions, and manage data operations.
"""

# Import service classes
from app.services.congressional import CongressionalService
from app.services.cache import CacheService
from app.services.metrics import MetricsService

# Create singleton instances of services
cache_service = CacheService()
metrics_service = MetricsService()
congressional_service = CongressionalService()

# Initialize services that require references to other services
def initialize_services():
    """Initialize all services in the correct order."""
    cache_service.initialize()
    metrics_service.initialize()
    congressional_service.initialize()

# Try to initialize services
try:
    initialize_services()
except Exception as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Error initializing services: {str(e)}")

__all__ = [
    "congressional_service",
    "cache_service",
    "metrics_service"
]