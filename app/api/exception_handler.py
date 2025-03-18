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
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from app.utils.config import settings
from app.core.exceptions import (
    CategoryNotFoundException,
    DuplicateCategoryException,
    DatabaseException,
    InvalidInputException,
    PermissionDeniedException,
    ResourceNotFoundException,
    DuplicateResourceException,
)

# Configure logging for error tracking
logger = logging.getLogger(__name__)

# Exception mapping dictionary
EXCEPTION_MAP = {
    RequestValidationError: (422, "Validation Error"),
    ResourceNotFoundException: (404, "Resource Not Found"),
    CategoryNotFoundException: (404, "Resource Not Found"),
    DuplicateCategoryException: (400, "Duplicate Resource"),
    DuplicateResourceException: (400, "Duplicate Resource"),
    PermissionDeniedException: (403, "Permission Denied"),
    InvalidInputException: (422, "Invalid Input"),
    DatabaseException: (500, "Database Error"),
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
    include_traceback = settings.DEBUG_MODE
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
