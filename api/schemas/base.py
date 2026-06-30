"""
====================================================================
Institutional Quant Platform

Base API Schemas

Author : Institutional Quant Platform

Purpose
-------
Common API request/response schemas.

Provides

• Base Response
• Success Response
• Error Response
• Metadata
• Pagination
• Timestamp Models

Used By

• Portfolio API
• Signals API
• Execution API
• Risk API
• Monitoring API

====================================================================
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel
from pydantic import ConfigDict
from pydantic import Field


# ==========================================================
# BASE MODEL
# ==========================================================


class APIModel(
    BaseModel,
):
    """
    Base schema.
    """

    model_config = ConfigDict(

        populate_by_name=True,

        extra="ignore",

        frozen=False,

    )


# ==========================================================
# METADATA
# ==========================================================


class Metadata(
    APIModel,
):
    """
    Response metadata.
    """

    timestamp: datetime = Field(

        default_factory=datetime.utcnow,

    )

    version: str = Field(

        default="1.0.0",

    )

    request_id: str | None = None

    processing_time_ms: float | None = None


# ==========================================================
# BASE RESPONSE
# ==========================================================


class BaseResponse(
    APIModel,
):
    """
    Generic API response.
    """

    success: bool = True

    message: str = "Success"

    metadata: Metadata = Field(

        default_factory=Metadata,

    )


# ==========================================================
# SUCCESS RESPONSE
# ==========================================================


class SuccessResponse(
    BaseResponse,
):
    """
    Successful response.
    """

    data: Any | None = None


# ==========================================================
# ERROR RESPONSE
# ==========================================================


class ErrorResponse(
    APIModel,
):
    """
    API error.
    """

    success: bool = False

    error: str

    detail: str | None = None

    error_code: int | None = None

    metadata: Metadata = Field(

        default_factory=Metadata,

    )


# ==========================================================
# PAGINATION
# ==========================================================


class Pagination(
    APIModel,
):
    """
    Pagination information.
    """

    page: int = Field(

        default=1,

        ge=1,

    )

    page_size: int = Field(

        default=100,

        ge=1,

        le=1000,

    )

    total_records: int = 0

    total_pages: int = 0


# ==========================================================
# PAGINATED RESPONSE
# ==========================================================


class PaginatedResponse(
    BaseResponse,
):
    """
    Paginated response.
    """

    data: list[Any] = Field(

        default_factory=list,

    )

    pagination: Pagination = Field(

        default_factory=Pagination,

    )


# ==========================================================
# HEALTH RESPONSE
# ==========================================================


class HealthResponse(
    BaseResponse,
):
    """
    Health endpoint response.
    """

    status: str = "Healthy"

    service: str

    uptime_seconds: float | None = None


# ==========================================================
# STATUS RESPONSE
# ==========================================================


class StatusResponse(
    BaseResponse,
):
    """
    Generic status response.
    """

    status: str

    progress: float | None = None


# ==========================================================
# DELETE RESPONSE
# ==========================================================


class DeleteResponse(
    BaseResponse,
):
    """
    Delete operation response.
    """

    deleted: bool = True

    resource_id: str | None = None


# ==========================================================
# VALIDATION ERROR
# ==========================================================


class ValidationErrorItem(
    APIModel,
):
    """
    Validation error item.
    """

    field: str

    message: str


class ValidationErrorResponse(
    ErrorResponse,
):
    """
    Validation error response.
    """

    validation_errors: list[
        ValidationErrorItem
    ] = Field(

        default_factory=list,

    )


# ==========================================================
# REPRESENTATION
# ==========================================================


__all__ = [

    "APIModel",

    "Metadata",

    "BaseResponse",

    "SuccessResponse",

    "ErrorResponse",

    "Pagination",

    "PaginatedResponse",

    "HealthResponse",

    "StatusResponse",

    "DeleteResponse",

    "ValidationErrorItem",

    "ValidationErrorResponse",

]