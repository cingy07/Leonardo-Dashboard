"""
Logging utilities for tracking API requests and application events.
Provides standardized logging functions used throughout the application.
"""

import logging
import json
from typing import Any, Dict, Optional
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

def log_request(endpoint: str, data: Dict[str, Any], user_id: Optional[str] = None) -> str:
    """
    Log an API request with standardized formatting.
    
    Args:
        endpoint: The API endpoint being called
        data: Request data (will be sanitized)
        user_id: Optional identifier for the requesting user
        
    Returns:
        Request ID for tracking
    """
    request_id = str(uuid.uuid4())
    
    # Sanitize sensitive data
    sanitized_data = sanitize_log_data(data)
    
    log_data = {
        "request_id": request_id,
        "timestamp": datetime.utcnow().isoformat(),
        "endpoint": endpoint,
        "user_id": user_id,
        "data": sanitized_data
    }
    
    logger.info(f"API Request: {json.dumps(log_data)}")
    return request_id

def log_response(request_id: str, status_code: int, data: Dict[str, Any]) -> None:
    """
    Log an API response with standardized formatting.
    
    Args:
        request_id: Request ID from log_request
        status_code: HTTP status code
        data: Response data (will be sanitized)
    """
    # Sanitize sensitive data
    sanitized_data = sanitize_log_data(data)
    
    log_data = {
        "request_id": request_id,
        "timestamp": datetime.utcnow().isoformat(),
        "status_code": status_code,
        "data": sanitized_data
    }
    
    logger.info(f"API Response: {json.dumps(log_data)}")

def log_error(request_id: str, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """
    Log an error with standardized formatting.
    
    Args:
        request_id: Request ID from log_request
        error: The exception that occurred
        context: Optional contextual information
    """
    log_data = {
        "request_id": request_id,
        "timestamp": datetime.utcnow().isoformat(),
        "error_type": error.__class__.__name__,
        "error_message": str(error),
        "context": context or {}
    }
    
    logger.error(f"API Error: {json.dumps(log_data)}")

def sanitize_log_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Sanitize sensitive data before logging.
    
    Args:
        data: Data to sanitize
        
    Returns:
        Sanitized data with sensitive fields redacted
    """
    if not isinstance(data, dict):
        return data
    
    sanitized = data.copy()
    sensitive_fields = [
        "api_key", 
        "password", 
        "token", 
        "secret", 
        "authorization",
        "access_token",
        "refresh_token"
    ]
    
    for field in sensitive_fields:
        if field in sanitized:
            sanitized[field] = "[REDACTED]"
    
    # Recursively sanitize nested dictionaries
    for key, value in sanitized.items():
        if isinstance(value, dict):
            sanitized[key] = sanitize_log_data(value)
    
    return sanitized