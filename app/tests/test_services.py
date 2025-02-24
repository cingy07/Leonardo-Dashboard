"""
Tests for service layer functionality.
Verifies that services handle business logic correctly and manage external dependencies.
"""

import pytest
from unittest.mock import patch, Mock
import json
from datetime import datetime

from app.services.congressional import CongressionalService
from app.services.cache import CacheService
from app.services.metrics import MetricsService
from app.core.exceptions import ExternalServiceError

@pytest.mark.asyncio
async def test_congressional_service_get_representative():
    """Test representative information retrieval."""
    service = CongressionalService()
    
    # Mock external API call
    with patch('httpx.AsyncClient.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "divisions": {
                "ocd-division/country:us/state:dc/cd:01": {
                    "name": "District of Columbia's 1st district"
                }
            },
            "officials": [TEST_REPRESENTATIVE]
        }
        mock_get.return_value = mock_response
        
        result = await service.get_representative_info(TEST_ZIP_CODE)
        
        assert result["name"] == TEST_REPRESENTATIVE["name"]
        assert result["district"] == "01"
        assert result["state"] == "DC"

@pytest.mark.asyncio
async def test_cache_service_operations(mock_redis):
    """Test cache operations."""
    service = CacheService()
    test_key = "test_key"
    test_value = {"data": "test"}
    
    # Test setting cache
    await service.set(test_key, test_value)
    mock_redis.setex.assert_called_once()
    
    # Test getting cache
    mock_redis.get.return_value = json.dumps(test_value)
    result = await service.get(test_key)
    assert result == test_value
    
    # Test cache deletion
    await service.delete(test_key)
    mock_redis.delete.assert_called_once_with(test_key)

@pytest.mark.asyncio
async def test_metrics_service_recording():
    """Test metrics recording and retrieval."""
    service = MetricsService()
    
    # Record test metrics
    await service.record_api_call("test_endpoint", 200, 100.0)
    
    # Get current metrics
    metrics = await service.get_current_metrics()
    
    assert metrics["requests_total"] >= 1
    assert "average_response_time" in metrics
    assert "error_rate" in metrics
