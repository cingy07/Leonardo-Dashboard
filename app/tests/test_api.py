# tests/test_api.py
"""
Tests for API endpoints and request handling.
Ensures that API endpoints work correctly and handle various scenarios appropriately.
"""

import pytest
from fastapi import status
from httpx import AsyncClient
import json
from unittest.mock import patch

from app.core.config import settings
from app.models.schemas import ZipRequest, RepresentativeResponse

async def test_lookup_endpoint_success(client, mock_redis):
    """Test successful ZIP code lookup."""
    # Prepare test data
    test_data = {"zip_codes": [TEST_ZIP_CODE]}
    
    # Mock successful API response
    with patch('app.services.congressional.CongressionalService.get_representative_info') as mock_get_rep:
        mock_get_rep.return_value = TEST_REPRESENTATIVE
        
        response = client.post(
            "/congressional/lookup",
            json=test_data,
            headers={"X-API-Key": TEST_API_KEY}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 1
        assert data[0]["zip_code"] == TEST_ZIP_CODE
        assert data[0]["name"] == TEST_REPRESENTATIVE["name"]

async def test_lookup_endpoint_invalid_zip(client):
    """Test handling of invalid ZIP codes."""
    test_data = {"zip_codes": ["invalid"]}
    
    response = client.post(
        "/congressional/lookup",
        json=test_data,
        headers={"X-API-Key": TEST_API_KEY}
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

async def test_lookup_endpoint_missing_api_key(client):
    """Test handling of missing API key."""
    test_data = {"zip_codes": [TEST_ZIP_CODE]}
    
    response = client.post(
        "/congressional/lookup",
        json=test_data
    )
    
    assert response.status_code == status.HTTP_403_FORBIDDEN