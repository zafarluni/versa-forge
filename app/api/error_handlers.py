"""
Global Exception Handlers for FastAPI

This module defines global exception handlers for various application errors.
It ensures structured responses and logs critical errors for debugging.

Best Practices:
- Keep error handling structured and centralized.
- Log exceptions with request details for better debugging.
- Use standardized JSON responses for API consistency.

Author: Zafar Hussain Luni
Version: 1.0.0
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


async def resource_not_found_exception_handler(request: Request, exc: CategoryNotFoundException) -> JSONResponse:
    """
    Handles Resource Not Found exceptions and returns 404 HTTP responses.

    Args:
        request (Request): The incoming request object.
        exc (CategoryNotFoundException): The raised exception.

    Returns:
        JSONResponse: The formatted response with a 404 status code.
    """
    logger.warning("Resource Not Found: %s %s - %s", request.method, request.url.path, str(exc))
    return JSONResponse(
        status_code=404,
        content={
            "error": {
                "code": 404,
                "message": "Resource Not Found",
                "details": str(exc),
            }
        },
    )


async def duplicate_resource_exception_handler(request: Request, exc: DuplicateCategoryException) -> JSONResponse:
    """
    Handles Duplicate Resource exceptions and returns 400 HTTP responses.

    Args:
        request (Request): The incoming request object.
        exc (DuplicateCategoryException): The raised exception.

    Returns:
        JSONResponse: The formatted response with a 400 status code.
    """
    logger.warning("Duplicate Resource: %s %s - %s", request.method, request.url.path, str(exc))
    return JSONResponse(
        status_code=400,
        content={
            "error": {
                "code": 400,
                "message": "Duplicate Resource",
                "details": str(exc),
            }
        },
    )


async def permission_denied_exception_handler(request: Request, exc: PermissionDeniedException) -> JSONResponse:
    """
    Handles Permission Denied exceptions and returns 403 HTTP responses.

    Args:
        request (Request): The incoming request object.
        exc (PermissionDeniedException): The raised exception.

    Returns:
        JSONResponse: The formatted response with a 403 status code.
    """
    logger.warning("Permission Denied: %s %s - %s", request.method, request.url.path, str(exc))
    return JSONResponse(
        status_code=403,
        content={
            "error": {
                "code": 403,
                "message": "Permission Denied",
                "details": str(exc),
            }
        },
    )

async def invalid_input_exception_handler(request: Request, exc: InvalidInputException) -> JSONResponse:
    """
    Handles invalid input errors and returns a 422 HTTP response.

    Args:
        request (Request): The incoming request object.
        exc (InvalidInputException): The raised exception.

    Returns:
        JSONResponse: The formatted response with a 422 status code.
    """
    logger.warning("Invalid Input: %s %s - %s", request.method, request.url.path, str(exc))
    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": 422,
                "message": "Invalid Input",
                "details": str(exc),
            }
        },
    )

async def database_exception_handler(request: Request, exc: DatabaseException) -> JSONResponse:
    """
    Handles database errors and returns a 500 HTTP response.

    Args:
        request (Request): The incoming request object.
        exc (DatabaseException): The raised exception.

    Returns:
        JSONResponse: The formatted response with a 500 status code.
    """
    logger.error("Database Error: %s %s - %s", request.method, request.url.path, str(exc))
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": 500,
                "message": "Database Error",
                "details": str(exc),
            }
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handles all uncaught exceptions and prevents exposing internal errors.

    Args:
        request (Request): The incoming request object.
        exc (Exception): The raised exception.

    Returns:
        JSONResponse: The formatted response with a 500 status code.
    """
    logger.error("Unhandled Exception: %s %s - %s", request.method, request.url.path, str(exc), exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": 500,
                "message": "Internal Server Error",
                "details": "An unexpected error occurred.",
            }
        },
    )
