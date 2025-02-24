"""
Logging configuration and setup.
Configures logging handlers, formatters, and log routing for the application.
"""
import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional
from app.core.config import settings

def setup_logging(log_file: Optional[str] = None) -> None:
    """
    Configure application-wide logging with both console and file handlers.
    
    Args:
        log_file: Optional path to log file. If None, uses settings.LOG_FILE
    """
    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)
    
    # Create formatters
    detailed_formatter = logging.Formatter(settings.LOG_FORMAT)
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(detailed_formatter)
    root_logger.addHandler(console_handler)
    
    # File Handler (if log file is specified)
    log_file = log_file or settings.LOG_FILE
    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=10485760,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(detailed_formatter)
        root_logger.addHandler(file_handler)
    
    # Set logging levels for third-party libraries
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    # Log startup message
    root_logger.info(
        f"Logging configured: level={settings.LOG_LEVEL}, "
        f"file={'enabled' if log_file else 'disabled'}"
    )

