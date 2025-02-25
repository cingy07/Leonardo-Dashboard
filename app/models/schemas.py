"""
Pydantic models for request/response validation and serialization.

This module defines the shape and validation rules for all data structures
used in the application. Each model includes detailed field descriptions,
validation rules, and examples to ensure data consistency.
"""

from pydantic import BaseModel, Field, field_validator, constr  # Changed validator to field_validator
from typing import List, Optional, Dict
from datetime import datetime
import re

class ZipRequest(BaseModel):
    """
    Request model for ZIP code lookups.
    
    Attributes:
        zip_codes: List of ZIP codes to look up representatives for.
                  Each ZIP code must be exactly 5 digits.
    
    Example:
        {
            "zip_codes": ["20001", "20002"]
        }
    """
    zip_codes: List[constr(pattern="^[0-9]{5}$")] = Field(  # Changed regex to pattern
        ...,
        description="List of 5-digit ZIP codes",
        min_items=1,
        max_items=10,
        example=["20001", "20002"]
    )

    @field_validator("zip_codes")  # Changed validator to field_validator
    @classmethod  # Added classmethod decorator
    def remove_duplicates(cls, v):
        """Remove duplicate ZIP codes while preserving order"""
        return list(dict.fromkeys(v))

class CommitteeInfo(BaseModel):
    """
    Information about a congressional committee.
    
    Attributes:
        name: Full name of the committee
        type: Type of committee (standing, select, joint)
        leadership: Committee leadership positions and members
    """
    name: str = Field(..., description="Full name of the committee")
    type: str = Field(..., description="Type of committee")
    leadership: Dict[str, str] = Field(
        default_factory=dict,
        description="Committee leadership positions"
    )

class RepresentativeResponse(BaseModel):
    """
    Response model containing representative information.
    
    Attributes:
        zip_code: The ZIP code queried
        name: Representative's full name
        party: Political party affiliation
        district: Congressional district (format: STATE-NUMBER)
        committees: List of committee assignments
        error: Error message if lookup failed
    
    Example:
        {
            "zip_code": "20001",
            "name": "John Smith",
            "party": "Democratic",
            "district": "DC-01",
            "committees": ["Appropriations", "Armed Services"],
            "error": null
        }
    """
    zip_code: str = Field(..., description="ZIP code queried")
    name: Optional[str] = Field(None, description="Representative's full name")
    party: Optional[str] = Field(None, description="Political party affiliation")
    district: Optional[str] = Field(
        None,
        description="Congressional district",
        pattern="^[A-Z]{2}-[0-9]{1,2}$"  # Changed regex to pattern
    )
    committees: List[str] = Field(
        default_factory=list,
        description="Committee assignments"
    )
    error: Optional[str] = Field(None, description="Error message if lookup failed")

    @field_validator("district")  # Changed validator to field_validator
    @classmethod  # Added classmethod decorator
    def validate_district_format(cls, v):
        """Ensure district follows STATE-NUMBER format"""
        if v is not None and not re.match(r"^[A-Z]{2}-[0-9]{1,2}$", v):
            raise ValueError("District must be in format STATE-NUMBER (e.g., DC-01)")
        return v

class HealthCheckResponse(BaseModel):
    """
    Response model for API health check endpoint.
    
    Attributes:
        status: Overall health status
        timestamp: Time of health check
        checks: Individual component health status
        version: API version
    """
    status: str = Field(..., description="Overall health status")
    timestamp: datetime = Field(..., description="Health check timestamp")
    checks: Dict[str, bool] = Field(
        ...,
        description="Individual component health status"
    )
    version: str = Field(..., description="API version")

class ErrorResponse(BaseModel):
    """
    Standardized error response model.
    
    Attributes:
        error: Error message
        detail: Additional error details
        timestamp: Time error occurred
        request_id: Unique identifier for the request
    """
    error: str = Field(..., description="Error message")
    detail: Optional[Dict[str, str]] = Field(
        None,
        description="Additional error details"
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Time error occurred"
    )
    request_id: str = Field(..., description="Unique request identifier")

class MetricsResponse(BaseModel):
    """
    Response model for API usage metrics.
    
    Attributes:
        requests_total: Total number of requests
        average_response_time: Average response time in milliseconds
        error_rate: Percentage of requests resulting in errors
        cache_hit_rate: Percentage of requests served from cache
        timestamp: Time metrics were collected
    """
    requests_total: int = Field(..., description="Total number of requests")
    average_response_time: float = Field(
        ...,
        description="Average response time (ms)"
    )
    error_rate: float = Field(
        ...,
        description="Error rate percentage",
        ge=0,
        le=100
    )
    cache_hit_rate: float = Field(
        ...,
        description="Cache hit rate percentage",
        ge=0,
        le=100
    )
    timestamp: datetime = Field(
        default_factory=datetime.utcnow,
        description="Metrics collection timestamp"
    )

    @field_validator("error_rate", "cache_hit_rate")  # Changed validator to field_validator
    @classmethod  # Added classmethod decorator
    def validate_percentage(cls, v):
        """Ensure percentage values are between 0 and 100"""
        if not 0 <= v <= 100:
            raise ValueError("Percentage must be between 0 and 100")
        return round(v, 2)  # Round to 2 decimal places