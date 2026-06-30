"""
====================================================================
Institutional Quant Platform

Error API Schemas

Author : Institutional Quant Platform

Purpose
-------
Standardized API error models.

Provides

• Error Response
• Validation Error
• Authentication Error
• Authorization Error
• Not Found Error
• Conflict Error
• Rate Limit Error
• Internal Server Error

====================================================================
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import Field

from api.schemas.base import APIModel


# ==========================================================
# ERROR DETAIL
# ==========================================================


class ErrorDetail(
    APIModel,
):
    """
    Individual error detail.
    """

    field: str | None = None

    message: str

    rejected_value: Any | None = None


# ==========================================================
# BASE ERROR
# ==========================================================


class APIError(
    APIModel,
):
    """
    Standard API error.
    """

    success: bool = False

    error: str

    error_code: str

    status_code: int

    timestamp: datetime = Field(

        default_factory=datetime.utcnow,

    )

    request_id: str | None = None

    details: list[
        ErrorDetail
    ] = Field(

        default_factory=list,

    )


# ==========================================================
# VALIDATION ERROR
# ==========================================================


class ValidationError(
    APIError,
):
    """
    Validation error.
    """

    error: str = "Validation Error"

    error_code: str = "VALIDATION_ERROR"

    status_code: int = 422


# ==========================================================
# AUTHENTICATION ERROR
# ==========================================================


class AuthenticationError(
    APIError,
):
    """
    Authentication failed.
    """

    error: str = "Authentication Failed"

    error_code: str = "AUTHENTICATION_ERROR"

    status_code: int = 401


# ==========================================================
# AUTHORIZATION ERROR
# ==========================================================


class AuthorizationError(
    APIError,
):
    """
    Permission denied.
    """

    error: str = "Permission Denied"

    error_code: str = "AUTHORIZATION_ERROR"

    status_code: int = 403


# ==========================================================
# NOT FOUND
# ==========================================================


class ResourceNotFoundError(
    APIError,
):
    """
    Resource not found.
    """

    error: str = "Resource Not Found"

    error_code: str = "NOT_FOUND"

    status_code: int = 404

    resource: str | None = None


# ==========================================================
# CONFLICT
# ==========================================================


class ConflictError(
    APIError,
):
    """
    Resource conflict.
    """

    error: str = "Conflict"

    error_code: str = "CONFLICT"

    status_code: int = 409


# ==========================================================
# BAD REQUEST
# ==========================================================


class BadRequestError(
    APIError,
):
    """
    Bad request.
    """

    error: str = "Bad Request"

    error_code: str = "BAD_REQUEST"

    status_code: int = 400


# ==========================================================
# RATE LIMIT
# ==========================================================


class RateLimitError(
    APIError,
):
    """
    Rate limit exceeded.
    """

    error: str = "Rate Limit Exceeded"

    error_code: str = "RATE_LIMIT"

    status_code: int = 429

    retry_after_seconds: int | None = None


# ==========================================================
# INTERNAL SERVER ERROR
# ==========================================================


class InternalServerError(
    APIError,
):
    """
    Internal server error.
    """

    error: str = "Internal Server Error"

    error_code: str = "INTERNAL_SERVER_ERROR"

    status_code: int = 500


# ==========================================================
# SERVICE UNAVAILABLE
# ==========================================================


class ServiceUnavailableError(
    APIError,
):
    """
    Service unavailable.
    """

    error: str = "Service Unavailable"

    error_code: str = "SERVICE_UNAVAILABLE"

    status_code: int = 503


# ==========================================================
# TIMEOUT ERROR
# ==========================================================


class TimeoutError(
    APIError,
):
    """
    Request timeout.
    """

    error: str = "Request Timeout"

    error_code: str = "REQUEST_TIMEOUT"

    status_code: int = 408


# ==========================================================
# EXPORTS
# ==========================================================


__all__ = [

    "ErrorDetail",

    "APIError",

    "ValidationError",

    "AuthenticationError",

    "AuthorizationError",

    "ResourceNotFoundError",

    "ConflictError",

    "BadRequestError",

    "RateLimitError",

    "InternalServerError",

    "ServiceUnavailableError",

    "TimeoutError",

]