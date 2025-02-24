# core/__init__.py
"""
Core package initializer.
This module initializes essential application components and configurations.
"""
from app.core.config import settings
from app.core.logging import setup_logging

__all__ = ["settings", "setup_logging"]