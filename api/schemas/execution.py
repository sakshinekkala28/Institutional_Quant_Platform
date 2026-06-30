"""
====================================================================
Institutional Quant Platform

Execution API Schemas

Author : Institutional Quant Platform

Purpose
-------
Execution request/response schemas.

Provides

• Orders
• Trades
• Execution Reports
• VWAP
• TWAP
• Slippage
• Market Impact
• Participation
• Fill Rate

====================================================================
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from api.schemas.base import APIModel
from api.schemas.base import BaseResponse
from api.schemas.base import SuccessResponse


# ==========================================================
# ORDER
# ==========================================================


class Order(
    APIModel,
):
    """
    Trading order.
    """

    order_id: str

    symbol: str

    side: Literal["BUY", "SELL"]

    quantity: float

    order_type: Literal[
        "MARKET",
        "LIMIT",
        "STOP",
    ]

    limit_price: float | None = None

    status: str

    created_at: datetime


# ==========================================================
# TRADE
# ==========================================================


class Trade(
    APIModel,
):
    """
    Executed trade.
    """

    trade_id: str

    order_id: str

    symbol: str

    side: Literal["BUY", "SELL"]

    quantity: float

    execution_price: float

    execution_time: datetime


# ==========================================================
# EXECUTION METRICS
# ==========================================================


class ExecutionMetrics(
    APIModel,
):
    """
    Execution metrics.
    """

    fill_rate: float

    participation_rate: float

    slippage_bps: float

    market_impact_bps: float

    execution_cost: float

    implementation_shortfall: float


# ==========================================================
# VWAP
# ==========================================================


class VWAPAnalytics(
    APIModel,
):
    """
    VWAP analytics.
    """

    vwap_price: float

    execution_price: float

    difference: float


# ==========================================================
# TWAP
# ==========================================================


class TWAPAnalytics(
    APIModel,
):
    """
    TWAP analytics.
    """

    twap_price: float

    execution_price: float

    difference: float


# ==========================================================
# EXECUTION REPORT
# ==========================================================


class ExecutionReport(
    APIModel,
):
    """
    Execution report.
    """

    report_id: str

    generated_at: datetime

    total_orders: int

    executed_orders: int

    cancelled_orders: int

    rejected_orders: int

    metrics: ExecutionMetrics


# ==========================================================
# EXECUTION REQUEST
# ==========================================================


class ExecutionRequest(
    APIModel,
):
    """
    Execution request.
    """

    strategy: str = "VWAP"

    simulate: bool = True

    participation_limit: float = 0.10

    allow_partial_fill: bool = True


# ==========================================================
# EXECUTION RESPONSE
# ==========================================================


class ExecutionResponse(
    BaseResponse,
):
    """
    Execution response.
    """

    execution_id: str

    status: str


# ==========================================================
# RESPONSES
# ==========================================================


class OrderResponse(
    SuccessResponse,
):
    """
    Order response.
    """

    data: Order


class OrdersResponse(
    SuccessResponse,
):
    """
    Orders response.
    """

    data: list[
        Order
    ]


class TradeResponse(
    SuccessResponse,
):
    """
    Trade response.
    """

    data: Trade


class TradesResponse(
    SuccessResponse,
):
    """
    Trades response.
    """

    data: list[
        Trade
    ]


class ExecutionReportResponse(
    SuccessResponse,
):
    """
    Report response.
    """

    data: ExecutionReport


class VWAPResponse(
    SuccessResponse,
):
    """
    VWAP response.
    """

    data: VWAPAnalytics


class TWAPResponse(
    SuccessResponse,
):
    """
    TWAP response.
    """

    data: TWAPAnalytics


# ==========================================================
# EXPORTS
# ==========================================================


__all__ = [

    "Order",

    "Trade",

    "ExecutionMetrics",

    "VWAPAnalytics",

    "TWAPAnalytics",

    "ExecutionReport",

    "ExecutionRequest",

    "ExecutionResponse",

    "OrderResponse",

    "OrdersResponse",

    "TradeResponse",

    "TradesResponse",

    "ExecutionReportResponse",

    "VWAPResponse",

    "TWAPResponse",

]