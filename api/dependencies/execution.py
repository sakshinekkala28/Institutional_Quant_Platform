"""
====================================================================
Institutional Quant Platform

Execution Dependencies

Author : Institutional Quant Platform

Purpose
-------
FastAPI dependency providers for execution services.

Provides

• Execution Engine
• Trade Engine
• Order Router
• Slippage Engine
• Market Impact
• Transaction Cost Engine
• Execution Analytics
• Monitoring Engine

Used By

• Execution Router
• Portfolio Router
• Backtest Router

====================================================================
"""

from __future__ import annotations

from functools import lru_cache

from execution.execution_engine import (
    ExecutionEngine,
)

from execution.trade_engine import (
    TradeEngine,
)

from execution.order_router import (
    OrderRouter,
)

from execution.slippage_engine import (
    SlippageEngine,
)

from execution.market_impact import (
    MarketImpact,
)

from execution.transaction_cost_engine import (
    TransactionCostEngine,
)

from execution.execution_simulator import (
    ExecutionAnalytics,
)

from execution.monitoring_engine import (
    MonitoringEngine,
)


# ==========================================================
# EXECUTION ENGINE
# ==========================================================


@lru_cache
def get_execution_engine() -> ExecutionEngine:
    """
    Primary execution engine.
    """
    return ExecutionEngine()


# ==========================================================
# TRADE ENGINE
# ==========================================================


@lru_cache
def get_trade_engine() -> TradeEngine:
    """
    Trade generation engine.
    """
    return TradeEngine()


# ==========================================================
# ORDER ROUTER
# ==========================================================


@lru_cache
def get_order_router() -> OrderRouter:
    """
    Order routing engine.
    """
    return OrderRouter()


# ==========================================================
# SLIPPAGE ENGINE
# ==========================================================


@lru_cache
def get_slippage_engine() -> SlippageEngine:
    """
    Slippage model.
    """
    return SlippageEngine()


# ==========================================================
# MARKET IMPACT
# ==========================================================


@lru_cache
def get_market_impact() -> MarketImpact:
    """
    Market impact model.
    """
    return MarketImpact()


# ==========================================================
# TRANSACTION COST ENGINE
# ==========================================================


@lru_cache
def get_transaction_cost_engine() -> TransactionCostEngine:
    """
    Transaction cost engine.
    """
    return TransactionCostEngine()


# ==========================================================
# EXECUTION ANALYTICS
# ==========================================================


@lru_cache
def get_execution_analytics() -> ExecutionAnalytics:
    """
    Execution analytics.
    """
    return ExecutionAnalytics()


# ==========================================================
# MONITORING ENGINE
# ==========================================================


@lru_cache
def get_monitoring_engine() -> MonitoringEngine:
    """
    Execution monitoring.
    """
    return MonitoringEngine()


# ==========================================================
# HEALTH
# ==========================================================


def execution_health() -> dict:
    """
    Dependency health.
    """

    return {

        "engine": "ExecutionEngine",

        "status": "healthy",

        "singleton": True,

    }


# ==========================================================
# SUMMARY
# ==========================================================


def execution_summary() -> dict:
    """
    Registered services.
    """

    return {

        "services": [

            "ExecutionEngine",

            "TradeEngine",

            "OrderRouter",

            "SlippageEngine",

            "MarketImpact",

            "TransactionCostEngine",

            "ExecutionAnalytics",

            "MonitoringEngine",

        ],

        "count": 8,

    }


# ==========================================================
# EXPORTS
# ==========================================================


__all__ = [

    "get_execution_engine",

    "get_trade_engine",

    "get_order_router",

    "get_slippage_engine",

    "get_market_impact",

    "get_transaction_cost_engine",

    "get_execution_analytics",

    "get_monitoring_engine",

    "execution_health",

    "execution_summary",

]