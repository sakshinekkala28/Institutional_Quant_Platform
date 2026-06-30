"""
====================================================================
Institutional Quant Platform

Backtest API Schemas

Author : Institutional Quant Platform

Purpose
-------
Backtesting request/response schemas.

Provides

• Backtest Request
• Backtest Configuration
• Performance Statistics
• Equity Curve
• Drawdown
• Trades
• Benchmark Comparison
• Backtest Report

====================================================================
"""

from __future__ import annotations

from datetime import date
from datetime import datetime

from pydantic import Field

from api.schemas.base import APIModel
from api.schemas.base import BaseResponse
from api.schemas.base import SuccessResponse


# ==========================================================
# BACKTEST CONFIGURATION
# ==========================================================


class BacktestConfiguration(
    APIModel,
):
    """
    Backtest configuration.
    """

    start_date: date

    end_date: date

    initial_capital: float = 10_000_000

    benchmark: str = "NIFTY 500"

    rebalance_frequency: str = "Monthly"

    transaction_cost_bps: float = 20.0

    slippage_bps: float = 5.0


# ==========================================================
# BACKTEST REQUEST
# ==========================================================


class BacktestRequest(
    APIModel,
):
    """
    Backtest request.
    """

    configuration: BacktestConfiguration

    strategy_name: str

    save_results: bool = True


# ==========================================================
# PERFORMANCE METRICS
# ==========================================================


class PerformanceMetrics(
    APIModel,
):
    """
    Portfolio performance.
    """

    cumulative_return: float

    annual_return: float

    annual_volatility: float

    sharpe_ratio: float

    sortino_ratio: float

    calmar_ratio: float

    information_ratio: float

    max_drawdown: float

    win_rate: float

    profit_factor: float


# ==========================================================
# EQUITY POINT
# ==========================================================


class EquityPoint(
    APIModel,
):
    """
    Equity curve point.
    """

    date: date

    portfolio_value: float


# ==========================================================
# DRAWDOWN POINT
# ==========================================================


class DrawdownPoint(
    APIModel,
):
    """
    Drawdown point.
    """

    date: date

    drawdown: float


# ==========================================================
# TRADE
# ==========================================================


class BacktestTrade(
    APIModel,
):
    """
    Backtest trade.
    """

    symbol: str

    side: str

    quantity: float

    entry_price: float

    exit_price: float

    pnl: float

    trade_date: datetime


# ==========================================================
# BENCHMARK
# ==========================================================


class BenchmarkComparison(
    APIModel,
):
    """
    Benchmark comparison.
    """

    benchmark_return: float

    strategy_return: float

    excess_return: float

    tracking_error: float


# ==========================================================
# BACKTEST RESULT
# ==========================================================


class BacktestResult(
    APIModel,
):
    """
    Backtest result.
    """

    backtest_id: str

    completed_at: datetime

    metrics: PerformanceMetrics

    benchmark: BenchmarkComparison


# ==========================================================
# BACKTEST REPORT
# ==========================================================


class BacktestReport(
    APIModel,
):
    """
    Complete report.
    """

    result: BacktestResult

    equity_curve: list[
        EquityPoint
    ]

    drawdown_curve: list[
        DrawdownPoint
    ]

    trades: list[
        BacktestTrade
    ]


# ==========================================================
# RESPONSES
# ==========================================================


class BacktestResponse(
    BaseResponse,
):
    """
    Backtest response.
    """

    backtest_id: str

    status: str


class BacktestResultResponse(
    SuccessResponse,
):
    """
    Backtest result response.
    """

    data: BacktestResult


class BacktestReportResponse(
    SuccessResponse,
):
    """
    Backtest report response.
    """

    data: BacktestReport


class EquityCurveResponse(
    SuccessResponse,
):
    """
    Equity curve response.
    """

    data: list[
        EquityPoint
    ]


class DrawdownResponse(
    SuccessResponse,
):
    """
    Drawdown response.
    """

    data: list[
        DrawdownPoint
    ]


class TradeHistoryResponse(
    SuccessResponse,
):
    """
    Trade history response.
    """

    data: list[
        BacktestTrade
    ]


# ==========================================================
# EXPORTS
# ==========================================================


__all__ = [

    "BacktestConfiguration",

    "BacktestRequest",

    "PerformanceMetrics",

    "EquityPoint",

    "DrawdownPoint",

    "BacktestTrade",

    "BenchmarkComparison",

    "BacktestResult",

    "BacktestReport",

    "BacktestResponse",

    "BacktestResultResponse",

    "BacktestReportResponse",

    "EquityCurveResponse",

    "DrawdownResponse",

    "TradeHistoryResponse",

]