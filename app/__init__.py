"""
Leonardo Dashboard Application
A web-based dashboard for Government Relations department providing quick access to congressional information.

This is the main package initializer that sets up the application environment,
configures essential services, and exposes the primary application components.
"""

import logging
from pathlib import Path
from typing import Dict, Any

# Version information
__version__ = "1.0.0"
__author__ = "Leonardo US Corporation"
__description__ = "Congressional Information Dashboard"

# Configure base logging before other imports to ensure proper log capture
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import core application components
try:
    from app.core.config import settings
    from app.core.logging import setup_logging
    from app.services import congressional_service, cache_service
    
    # Initialize application logging with custom configuration
    setup_logging()
    logger.info(f"Starting {__description__} v{__version__}")
    
    # Verify required data directories exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Application metadata that can be accessed by other parts of the app
    APP_METADATA: Dict[str, Any] = {
        "version": __version__,
        "author": __author__,
        "description": __description__,
        "data_directory": str(data_dir),
        "settings": settings.model_dump()  # Changed from dict() to model_dump()
    }
    
    # Initialize core services
    congressional_service.initialize()
    cache_service.initialize()
    
    # Export the main application components that should be available when importing the package
    __all__ = [
        "settings",
        "congressional_service",
        "cache_service",
        "APP_METADATA"
    ]

except Exception as e:
    logger.critical(f"Failed to initialize application: {str(e)}")
    raise

logger.info("Application initialization completed successfully")