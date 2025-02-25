"""
API Route Definitions

This module contains all the route handlers for the congressional dashboard API.
Each route is documented with OpenAPI specifications and includes proper error
handling and input validation.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime

from app.models.schemas import (
    ZipRequest,
    RepresentativeResponse,
    ErrorResponse,
    HealthCheckResponse
)
from app.services import congressional_service, cache_service
from app.core.dependencies import get_api_key, rate_limit
from app.utils.logging import log_request

# Create separate routers for different functional areas
congressional_router = APIRouter()
health_router = APIRouter()
metrics_router = APIRouter()

@congressional_router.post(
    "/lookup",
    response_model=List[RepresentativeResponse],
    responses={
        200: {"description": "Successfully retrieved representative information"},
        400: {"model": ErrorResponse, "description": "Invalid input"},
        429: {"model": ErrorResponse, "description": "Too many requests"},
        500: {"model": ErrorResponse, "description": "Internal server error"}
    }
)
async def lookup_representatives(
    request: ZipRequest,
    api_key: str = Depends(get_api_key),
    _: None = Depends(rate_limit)
) -> List[RepresentativeResponse]:
    """
    Look up congressional representatives by ZIP code.
    
    This endpoint accepts a list of ZIP codes and returns information about the
    corresponding representatives, including their committee assignments.
    """
    try:
        # Log the incoming request
        log_request("lookup_representatives", request.model_dump())  # Changed from dict() to model_dump()
        
        # Check cache first
        cache_key = f"zip_lookup:{','.join(request.zip_codes)}"
        cached_result = await cache_service.get(cache_key)
        if cached_result:
            return cached_result
        
        # Process each ZIP code
        results = []
        for zip_code in request.zip_codes:
            rep_info = await congressional_service.get_representative_info(zip_code)
            if rep_info:
                committees = await congressional_service.get_committees(
                    rep_info["name"]
                )
                results.append(
                    RepresentativeResponse(
                        zip_code=zip_code,
                        name=rep_info["name"],
                        party=rep_info["party"],
                        district=f"{rep_info['state']}-{rep_info['district']}",
                        committees=committees
                    )
                )
            else:
                results.append(
                    RepresentativeResponse(
                        zip_code=zip_code,
                        error="No representative found"
                    )
                )
        
        # Cache the results
        await cache_service.set(cache_key, results, expire=3600)
        return results
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

@health_router.get(
    "",
    response_model=HealthCheckResponse,
    responses={
        200: {"description": "System is healthy"},
        500: {"description": "System is unhealthy"}
    }
)
async def health_check() -> HealthCheckResponse:
    """
    Check the health status of the API and its dependencies.
    
    This endpoint verifies the connection to external services and
    data sources, returning detailed health information.
    """
    status = "healthy"
    checks = {
        "api": True,
        "cache": await cache_service.is_healthy(),
        "congressional_service": await congressional_service.is_healthy()
    }
    
    if not all(checks.values()):
        status = "unhealthy"
    
    return HealthCheckResponse(
        status=status,
        timestamp=datetime.utcnow(),
        checks=checks
    )

@metrics_router.get(
    "",
    response_model=dict,
    dependencies=[Depends(get_api_key)]
)
async def get_metrics() -> dict:
    """
    Retrieve API usage metrics and statistics.
    
    This endpoint provides information about API usage patterns,
    response times, and error rates.
    """
    return {
        "requests_total": await cache_service.get_metrics("requests_total"),
        "average_response_time": await cache_service.get_metrics("avg_response_time"),
        "error_rate": await cache_service.get_metrics("error_rate"),
        "cache_hit_rate": await cache_service.get_metrics("cache_hit_rate")
    }