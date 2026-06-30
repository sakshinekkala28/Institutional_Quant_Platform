"""
====================================================================
Institutional Quant Platform

Pagination API Schemas

Author : Institutional Quant Platform

Purpose
-------
Reusable pagination schemas.

Provides

• Page Request
• Offset Pagination
• Cursor Pagination
• Sorting
• Filtering
• Page Metadata

====================================================================
"""

from __future__ import annotations

from typing import Any
from typing import Generic
from typing import TypeVar

from pydantic import Field

from api.schemas.base import APIModel


T = TypeVar(

    "T"

)


# ==========================================================
# PAGE REQUEST
# ==========================================================


class PageRequest(
    APIModel,
):
    """
    Offset pagination request.
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


# ==========================================================
# SORT REQUEST
# ==========================================================


class SortRequest(
    APIModel,
):
    """
    Sorting request.
    """

    sort_by: str | None = None

    ascending: bool = True


# ==========================================================
# FILTER REQUEST
# ==========================================================


class FilterRequest(
    APIModel,
):
    """
    Generic filter.
    """

    filters: dict[
        str,
        Any,
    ] = Field(

        default_factory=dict,

    )


# ==========================================================
# PAGE METADATA
# ==========================================================


class PageMetadata(
    APIModel,
):
    """
    Pagination metadata.
    """

    page: int

    page_size: int

    total_records: int

    total_pages: int

    has_previous: bool

    has_next: bool


# ==========================================================
# PAGE RESPONSE
# ==========================================================


class PageResponse(
    APIModel,
    Generic[T],
):
    """
    Generic page response.
    """

    data: list[T]

    metadata: PageMetadata


# ==========================================================
# CURSOR REQUEST
# ==========================================================


class CursorRequest(
    APIModel,
):
    """
    Cursor pagination request.
    """

    cursor: str | None = None

    limit: int = Field(

        default=100,

        ge=1,

        le=1000,

    )


# ==========================================================
# CURSOR METADATA
# ==========================================================


class CursorMetadata(
    APIModel,
):
    """
    Cursor metadata.
    """

    next_cursor: str | None = None

    previous_cursor: str | None = None

    has_next: bool

    has_previous: bool


# ==========================================================
# CURSOR RESPONSE
# ==========================================================


class CursorResponse(
    APIModel,
    Generic[T],
):
    """
    Cursor response.
    """

    data: list[T]

    metadata: CursorMetadata


# ==========================================================
# SEARCH REQUEST
# ==========================================================


class SearchRequest(
    PageRequest,
    SortRequest,
    FilterRequest,
):
    """
    Generic search request.
    """

    query: str | None = None


# ==========================================================
# EXPORTS
# ==========================================================


__all__ = [

    "PageRequest",

    "SortRequest",

    "FilterRequest",

    "PageMetadata",

    "PageResponse",

    "CursorRequest",

    "CursorMetadata",

    "CursorResponse",

    "SearchRequest",

]