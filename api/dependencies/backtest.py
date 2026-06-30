"""
====================================================================
Institutional Quant Platform

Backtest Dependencies

Author : Institutional Quant Platform

Purpose
-------
FastAPI dependency providers for backtesting services.

Provides

• Backtest Engine
• Performance Engine
• Benchmark Engine
• Backtest Report
• Portfolio Tracker
• Position Manager
• Cash Manager
• Event Engine

Used By

• Backtest Router
• Portfolio Router
• Optimization Router
• Monitoring Router

====================================================================
"""

from __future__ import annotations

from functools import lru_cache

from backtesting.backtest_engine import (
    BacktestEngine,
)

from backtesting.performance_engine import (
    PerformanceEngine,
)

from backtesting.benchmark_engine import (
    BenchmarkEngine,
)

from backtesting.backtest_report import (
    BacktestReport,
)

from backtesting.portfolio_tracker import (
    PortfolioTracker,
)

from backtesting.position_manager import (
    PositionManager,
)

from backtesting.cash_manager import (
    CashManager,
)

from backtesting.event_engine import (
    EventEngine,
)


# ==========================================================
# BACKTEST ENGINE
# ==========================================================


@lru_cache
def get_backtest_engine() -> BacktestEngine:
    """
    Primary backtest engine.
    """
    return BacktestEngine()


# ==========================================================
# PERFORMANCE ENGINE
# ==========================================================


@lru_cache
def get_performance_engine() -> PerformanceEngine:
    """
    Performance engine.
    """
    return PerformanceEngine()


# ==========================================================
# BENCHMARK ENGINE
# ==========================================================


@lru_cache
def get_benchmark_engine() -> BenchmarkEngine:
    """
    Benchmark engine.
    """
    return BenchmarkEngine()


# ==========================================================
# BACKTEST REPORT
# ==========================================================


@lru_cache
def get_backtest_report() -> BacktestReport:
    """
    Backtest reporting service.
    """
    return BacktestReport()


# ==========================================================
# PORTFOLIO TRACKER
# ==========================================================


@lru_cache
def get_portfolio_tracker() -> PortfolioTracker:
    """
    Portfolio tracker.
    """
    return PortfolioTracker()


# ==========================================================
# POSITION MANAGER
# ==========================================================


@lru_cache
def get_position_manager() -> PositionManager:
    """
    Position manager.
    """
    return PositionManager()


# ==========================================================
# CASH MANAGER
# ==========================================================


@lru_cache
def get_cash_manager() -> CashManager:
    """
    Cash manager.
    """
    return CashManager()


# ==========================================================
# EVENT ENGINE
# ==========================================================


@lru_cache
def get_event_engine() -> EventEngine:
    """
    Event processing engine.
    """
    return EventEngine()


# ==========================================================
# HEALTH
# ==========================================================


def backtest_health() -> dict:
    """
    Dependency health.
    """

    return {

        "engine": "BacktestEngine",

        "status": "healthy",

        "singleton": True,

    }


# ==========================================================
# SUMMARY
# ==========================================================


def backtest_summary() -> dict:
    """
    Registered services.
    """

    return {

        "services": [

            "BacktestEngine",

            "PerformanceEngine",

            "BenchmarkEngine",

            "BacktestReport",

            "PortfolioTracker",

            "PositionManager",

            "CashManager",

            "EventEngine",

        ],

        "count": 8,

    }


# ==========================================================
# EXPORTS
# ==========================================================


__all__ = [

    "get_backtest_engine",

    "get_performance_engine",

    "get_benchmark_engine",

    "get_backtest_report",

    "get_portfolio_tracker",

    "get_position_manager",

    "get_cash_manager",

    "get_event_engine",

    "backtest_health",

    "backtest_summary",

]