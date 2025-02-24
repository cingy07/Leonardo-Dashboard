"""
Test suite for the Leonardo Dashboard application.
Contains fixtures and configurations used across all test modules.
"""

import pytest
from fastapi.testclient import TestClient
import redis
from typing import Generator
from unittest.mock import Mock

from app.main import app
from app.core.config import settings
from app.services import congressional_service, cache_service, metrics_service

# Test constants
TEST_ZIP_CODE = "20001"
TEST_API_KEY = "test_key"
TEST_REPRESENTATIVE = {
    "name": "Test Representative",
    "party": "Independent",
    "district": "DC-01"
}

@pytest.fixture
def test_app() -> Generator:
    """
    Fixture that provides a test instance of the FastAPI application.
    """
    # Configure test settings
    settings.API_KEY = TEST_API_KEY
    settings.TESTING = True
    
    yield app

@pytest.fixture
def client(test_app) -> Generator:
    """
    Fixture that provides a test client for making HTTP requests.
    """
    with TestClient(test_app) as test_client:
        yield test_client

@pytest.fixture
def mock_redis() -> Generator:
    """
    Fixture that provides a mock Redis instance for testing cache operations.
    """
    mock_redis = Mock(spec=redis.Redis)
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.delete.return_value = True
    
    # Store original Redis client
    original_redis = cache_service.redis
    
    # Replace with mock
    cache_service.redis = mock_redis
    
    yield mock_redis
    
    # Restore original Redis client
    cache_service.redis = original_redis