"""
Global Exception Handlers for FastAPI
This module defines global exception handlers for various application errors.
It ensures structured responses and logs critical errors for debugging.
Best Practices:
- Keep error handling structured and centralized.
- Log exceptions with request details for better debugging.
- Use standardized JSON responses for API consistency.
Author: Zafar Hussain Luni
Version: 1.1.0
"""

import logging
import traceback

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.core.exceptions import (
    CategoryNotFoundError,
    DatabaseError,
    DuplicateCategoryError,
    DuplicateResourceError,
    InvalidInputError,
    PermissionDeniedError,
    ResourceNotFoundError,
)
from app.utils.config import get_settings

settings = get_settings()

# Configure logging for error tracking
logger = logging.getLogger(__name__)

# Exception mapping dictionary
EXCEPTION_MAP = {
    RequestValidationError: (422, "Validation Error"),
    ResourceNotFoundError: (404, "Resource Not Found"),
    CategoryNotFoundError: (404, "Resource Not Found"),
    DuplicateCategoryError: (400, "Duplicate Resource"),
    DuplicateResourceError: (400, "Duplicate Resource"),
    PermissionDeniedError: (403, "Permission Denied"),
    InvalidInputError: (422, "Invalid Input"),
    DatabaseError: (500, "Database Error"),
}


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handles all defined and unexpected exceptions, returning appropriate responses.
    Includes traceback in debug mode for easier debugging during development.

    Args:
        request (Request): The incoming request object.
        exc (Exception): The raised exception.

    Returns:
        JSONResponse: A structured error response.
    """
    # If its a Validation Error, return a human-readable message
    if isinstance(exc, ValidationError):
        return return_human_readable_validation_error(exc)

    # Map the exception to a status code and message
    exception_info = EXCEPTION_MAP.get(type(exc), (500, "Internal Server Error"))
    status_code, error_message = exception_info

    # Include traceback in debug mode
    include_traceback = settings.debug_mode
    traceback_details = traceback.format_exc() if include_traceback else None

    # Logging the error
    log_level = logging.WARNING if status_code < 500 else logging.ERROR
    logger.log(
        log_level,
        "%s Error: %s %s - %s\nTraceback:\n%s",
        error_message,
        request.method,
        request.url.path,
        str(exc),
        traceback_details or "No traceback available.",
    )

    # Construct the error response
    error_response = {
        "error": {
            "code": status_code,
            "message": error_message,
            "details": str(exc) if status_code != 500 else "An unexpected error occurred.",
        }
    }

    # Add traceback only if debug mode is enabled
    if include_traceback:
        error_response["error"]["traceback"] = traceback_details

    return JSONResponse(status_code=status_code, content=error_response)


def return_human_readable_validation_error(exc: ValidationError) -> JSONResponse:
    # Extract simplified error details
    error_details = [
        {
            "field": error["loc"][-1],  # Field name
            "message": error["msg"],  # Human-readable error message
        }
        for error in exc.errors()
    ]
    status_code = 422
    error_message = "Validation Error"
    response_content = {
        "error": {
            "code": status_code,
            "message": error_message,
            "details": error_details,  # Simplified error details
        }
    }
    return JSONResponse(status_code=status_code, content=response_content)
