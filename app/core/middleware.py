"""
Application middleware components.
Implements request/response processing, logging, and error handling middleware.
"""
from fastapi import Request, Response
from fastapi.middleware.base import BaseHTTPMiddleware
from typing import Callable
import time
import logging
from app.core.exceptions import AppException

logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        start_time = time.time()
        
        # Log request
        logger.info(
            f"Request: {request.method} {request.url.path} "
            f"Client: {request.client.host}"
        )
        
        try:
            response = await call_next(request)
            
            # Log response
            process_time = (time.time() - start_time) * 1000
            logger.info(
                f"Response: {response.status_code} "
                f"Process Time: {process_time:.2f}ms"
            )
            
            return response
        except Exception as e:
            logger.error(f"Request failed: {str(e)}")
            raise

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        try:
            return await call_next(request)
        except AppException as e:
            logger.error(f"Application error: {str(e)}", exc_info=True)
            return Response(
                content={"error": str(e), "details": e.details},
                status_code=e.status_code
            )
        except Exception as e:
            logger.error(f"Unhandled error: {str(e)}", exc_info=True)
            return Response(
                content={"error": "Internal server error"},
                status_code=500
            )