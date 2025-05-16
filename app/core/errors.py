from fastapi import Request, status
from fastapi.responses import JSONResponse
from aiomysql import Error as MySQLError
from typing import Any, Dict
import logging

# Configure logger
logger = logging.getLogger(__name__)

class AppError(Exception):
    """Base application error"""
    def __init__(
        self,
        status_code: int,
        message: str,
        details: Dict[str, Any] | None = None
    ):
        self.status_code = status_code
        self.message = message
        self.details = details or {}
        super().__init__(message)

class DatabaseError(AppError):
    """Database related errors"""
    def __init__(self, message: str, details: Dict[str, Any] | None = None):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, message=message, details=details)

class NotFoundError(AppError):
    """Resource not found errors"""
    def __init__(self, message: str, details: Dict[str, Any] | None = None):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, message=message, details=details)

class ValidationError(AppError):
    """Validation errors"""
    def __init__(self, message: str, details: Dict[str, Any] | None = None):
        super().__init__(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, message=message, details=details)

async def error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global error handler"""
    if isinstance(exc, AppError):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "error": {
                    "message": exc.message,
                    "details": exc.details
                }
            }
        )
    
    if isinstance(exc, MySQLError):
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "message": "Database error occurred",
                    "details": {"original_error": str(exc)}
                }
            }
        )
    
    # Log unexpected errors
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "message": "An unexpected error occurred",
                "details": {"type": exc.__class__.__name__}
            }
        }
    ) 