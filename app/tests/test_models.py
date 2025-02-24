# tests/test_models.py
"""
Tests for data models and validation.
Ensures that data models properly validate and process input data.
"""

import pytest
from pydantic import ValidationError

from app.models.schemas import (
    ZipRequest,
    RepresentativeResponse,
    CommitteeInfo
)

def test_zip_request_validation():
    """Test ZIP code request validation."""
    # Test valid ZIP
    valid_data = {"zip_codes": ["20001"]}
    request = ZipRequest(**valid_data)
    assert request.zip_codes == ["20001"]
    
    # Test invalid ZIP
    invalid_data = {"zip_codes": ["123"]}
    with pytest.raises(ValidationError):
        ZipRequest(**invalid_data)
    
    # Test duplicate removal
    duplicate_data = {"zip_codes": ["20001", "20001"]}
    request = ZipRequest(**duplicate_data)
    assert len(request.zip_codes) == 1

def test_representative_response_validation():
    """Test representative response validation."""
    valid_data = {
        "zip_code": "20001",
        "name": "Test Representative",
        "party": "Independent",
        "district": "DC-01",
        "committees": ["Committee 1", "Committee 2"]
    }
    
    response = RepresentativeResponse(**valid_data)
    assert response.name == valid_data["name"]
    assert response.district == valid_data["district"]
    
    # Test invalid district format
    invalid_data = valid_data.copy()
    invalid_data["district"] = "Invalid"
    with pytest.raises(ValidationError):
        RepresentativeResponse(**invalid_data)
