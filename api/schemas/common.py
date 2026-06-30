"""
====================================================================
Institutional Quant Platform

Common API Schemas

Author : Institutional Quant Platform

Purpose
-------
Reusable API schemas shared across all modules.

Provides

• Symbol
• Exchange
• Date Range
• Time Range
• Currency
• Money
• Price
• Quantity
• Statistics
• Metadata
• File Export
• Pagination Filters

====================================================================
"""

from __future__ import annotations

from datetime import date
from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import Field

from api.schemas.base import APIModel


# ==========================================================
# SYMBOL
# ==========================================================


class Symbol(
    APIModel,
):
    """
    Security symbol.
    """

    symbol: str

    exchange: str = "NSE"


# ==========================================================
# DATE RANGE
# ==========================================================


class DateRange(
    APIModel,
):
    """
    Date range.
    """

    start_date: date

    end_date: date


# ==========================================================
# DATETIME RANGE
# ==========================================================


class DateTimeRange(
    APIModel,
):
    """
    Datetime range.
    """

    start_datetime: datetime

    end_datetime: datetime


# ==========================================================
# MONEY
# ==========================================================


class Money(
    APIModel,
):
    """
    Monetary amount.
    """

    amount: Decimal

    currency: str = "INR"


# ==========================================================
# PRICE
# ==========================================================


class Price(
    APIModel,
):
    """
    Price.
    """

    value: float

    currency: str = "INR"


# ==========================================================
# QUANTITY
# ==========================================================


class Quantity(
    APIModel,
):
    """
    Quantity.
    """

    value: float

    unit: str = "Shares"


# ==========================================================
# STATISTICS
# ==========================================================


class Statistics(
    APIModel,
):
    """
    Generic statistics.
    """

    minimum: float

    maximum: float

    mean: float

    median: float

    standard_deviation: float

    observations: int


# ==========================================================
# KEY VALUE
# ==========================================================


class KeyValue(
    APIModel,
):
    """
    Generic key-value.
    """

    key: str

    value: str


# ==========================================================
# FILE EXPORT
# ==========================================================


class ExportInformation(
    APIModel,
):
    """
    Export metadata.
    """

    filename: str

    file_type: Literal[
        "csv",
        "xlsx",
        "json",
        "pdf",
        "html",
        "parquet",
    ]

    generated_at: datetime = Field(

        default_factory=datetime.utcnow,

    )

    file_size_bytes: int | None = None


# ==========================================================
# PAGE FILTER
# ==========================================================


class PageFilter(
    APIModel,
):
    """
    Pagination filter.
    """

    page: int = 1

    page_size: int = 100


# ==========================================================
# SORT FILTER
# ==========================================================


class SortFilter(
    APIModel,
):
    """
    Sorting.
    """

    sort_by: str

    ascending: bool = True


# ==========================================================
# SEARCH FILTER
# ==========================================================


class SearchFilter(
    APIModel,
):
    """
    Search filter.
    """

    query: str | None = None


# ==========================================================
# AUDIT INFORMATION
# ==========================================================


class AuditInformation(
    APIModel,
):
    """
    Audit information.
    """

    created_at: datetime

    updated_at: datetime

    created_by: str

    updated_by: str


# ==========================================================
# IDENTIFIER
# ==========================================================


class Identifier(
    APIModel,
):
    """
    Universal identifier.
    """

    id: str


# ==========================================================
# STATUS
# ==========================================================


class Status(
    APIModel,
):
    """
    Generic status.
    """

    status: str

    message: str | None = None


# ==========================================================
# EXPORTS
# ==========================================================


__all__ = [

    "Symbol",

    "DateRange",

    "DateTimeRange",

    "Money",

    "Price",

    "Quantity",

    "Statistics",

    "KeyValue",

    "ExportInformation",

    "PageFilter",

    "SortFilter",

    "SearchFilter",

    "AuditInformation",

    "Identifier",

    "Status",

]