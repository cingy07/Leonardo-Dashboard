"""
Custom exception classes and exception handling utilities.
Defines application-specific exceptions and their handling logic.
"""
from fastapi import HTTPException
from typing import Optional, Dict, Any

class AppException(Exception):
    """Base exception for application-specific errors"""
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class ConfigurationError(AppException):
    """Raised when there's an error in application configuration"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=500, details=details)

class ExternalServiceError(AppException):
    """Raised when an external service call fails"""
    def __init__(self, service: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            f"{service} service error: {message}",
            status_code=503,
            details=details
        )

class ValidationError(AppException):
    """Raised when input validation fails"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, details=details)