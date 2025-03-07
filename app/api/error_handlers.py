"""
Global Exception Handlers for FastAPI

This module defines global exception handlers for various application errors.
It ensures structured responses and logs critical errors for debugging.

Best Practices:
- Keep error handling structured and centralized.
- Log exceptions with request details for better debugging.
- Use standardized JSON responses for API consistency.

Author: Zafar Hussain Luni
Version: 1.0.1
"""

import logging
from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    CategoryNotFoundException, DuplicateCategoryException,
    DatabaseException, InvalidInputException, PermissionDeniedException
)

# Configure logging for error tracking
logger = logging.getLogger(__name__)


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handles all defined and unexpected exceptions, returning appropriate responses.

    Args:
        request (Request): The incoming request object.
        exc (Exception): The raised exception.

    Returns:
        JSONResponse: A structured error response.
    """

    if isinstance(exc, CategoryNotFoundException):
        status_code = 404
        error_message = "Resource Not Found"

    elif isinstance(exc, DuplicateCategoryException):
        status_code = 400
        error_message = "Duplicate Resource"

    elif isinstance(exc, PermissionDeniedException):
        status_code = 403
        error_message = "Permission Denied"

    elif isinstance(exc, InvalidInputException):
        status_code = 422
        error_message = "Invalid Input"

    elif isinstance(exc, DatabaseException):
        status_code = 500
        error_message = "Database Error"

    else:
        status_code = 500
        error_message = "Internal Server Error"

    # Logging the error
    log_level = logging.WARNING if status_code < 500 else logging.ERROR
    logger.log(log_level, "%s Error: %s %s - %s", error_message, request.method, request.url.path, str(exc))

    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": status_code,
                "message": error_message,
                "details": str(exc) if status_code != 500 else "An unexpected error occurred.",
            }
        },
    )
