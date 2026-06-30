"""
====================================================================
Institutional Quant Platform

Portfolio API Schemas

Author : Institutional Quant Platform

Purpose
-------
Portfolio request/response schemas.

Provides

• Portfolio Summary
• Holdings
• Positions
• Weights
• Sector Exposure
• Factor Exposure
• Rebalance Request
• Portfolio Performance

====================================================================
"""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from api.schemas.base import APIModel
from api.schemas.base import BaseResponse
from api.schemas.base import SuccessResponse


# ==========================================================
# POSITION
# ==========================================================


class Position(
    APIModel,
):
    """
    Portfolio position.
    """

    symbol: str

    quantity: float

    average_price: float

    last_price: float

    market_value: float

    weight: float

    unrealized_pnl: float

    sector: str | None = None


# ==========================================================
# HOLDING
# ==========================================================


class Holding(
    Position,
):
    """
    Portfolio holding.
    """

    asset_class: str = "Equity"

    currency: str = "INR"


# ==========================================================
# PORTFOLIO SUMMARY
# ==========================================================


class PortfolioSummary(
    APIModel,
):
    """
    Portfolio summary.
    """

    portfolio_value: float

    cash: float

    invested_value: float

    total_return: float

    daily_return: float

    positions: int

    turnover: float

    updated_at: datetime = Field(

        default_factory=datetime.utcnow,

    )


# ==========================================================
# SECTOR EXPOSURE
# ==========================================================


class SectorExposure(
    APIModel,
):
    """
    Sector allocation.
    """

    sector: str

    weight: float

    market_value: float


# ==========================================================
# FACTOR EXPOSURE
# ==========================================================


class FactorExposure(
    APIModel,
):
    """
    Factor exposure.
    """

    factor: str

    exposure: float


# ==========================================================
# PERFORMANCE
# ==========================================================


class PortfolioPerformance(
    APIModel,
):
    """
    Portfolio performance.
    """

    annual_return: float

    annual_volatility: float

    sharpe_ratio: float

    sortino_ratio: float

    calmar_ratio: float

    max_drawdown: float


# ==========================================================
# REBALANCE REQUEST
# ==========================================================


class RebalanceRequest(
    APIModel,
):
    """
    Portfolio rebalance request.
    """

    rebalance_date: datetime

    optimizer: str = "MeanVariance"

    max_weight: float = 0.10

    min_weight: float = 0.00

    transaction_cost_bps: float = 20.0


# ==========================================================
# REBALANCE RESPONSE
# ==========================================================


class RebalanceResponse(
    BaseResponse,
):
    """
    Rebalance response.
    """

    rebalance_id: str

    status: str

    expected_turnover: float


# ==========================================================
# PORTFOLIO RESPONSE
# ==========================================================


class PortfolioResponse(
    SuccessResponse,
):
    """
    Portfolio response.
    """

    data: PortfolioSummary


# ==========================================================
# HOLDINGS RESPONSE
# ==========================================================


class HoldingsResponse(
    SuccessResponse,
):
    """
    Holdings response.
    """

    data: list[Holding]


# ==========================================================
# POSITIONS RESPONSE
# ==========================================================


class PositionsResponse(
    SuccessResponse,
):
    """
    Position response.
    """

    data: list[Position]


# ==========================================================
# SECTOR RESPONSE
# ==========================================================


class SectorExposureResponse(
    SuccessResponse,
):
    """
    Sector exposure response.
    """

    data: list[SectorExposure]


# ==========================================================
# FACTOR RESPONSE
# ==========================================================


class FactorExposureResponse(
    SuccessResponse,
):
    """
    Factor exposure response.
    """

    data: list[FactorExposure]


# ==========================================================
# PERFORMANCE RESPONSE
# ==========================================================


class PerformanceResponse(
    SuccessResponse,
):
    """
    Portfolio performance response.
    """

    data: PortfolioPerformance


# ==========================================================
# EXPORTS
# ==========================================================


__all__ = [

    "Position",

    "Holding",

    "PortfolioSummary",

    "SectorExposure",

    "FactorExposure",

    "PortfolioPerformance",

    "RebalanceRequest",

    "RebalanceResponse",

    "PortfolioResponse",

    "HoldingsResponse",

    "PositionsResponse",

    "SectorExposureResponse",

    "FactorExposureResponse",

    "PerformanceResponse",

]