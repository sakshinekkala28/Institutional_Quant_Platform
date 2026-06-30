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
• Order Manager
• Execution Manager
• VWAP Engine
• TWAP Engine
• Slippage Engine
• Market Impact Engine
• Transaction Cost Engine
• Execution Analytics

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

from execution.order_manager import (
    OrderManager,
)

from execution.execution_manager import (
    ExecutionManager,
)

from execution.vwap_engine import (
    VWAPEngine,
)

from execution.twap_engine import (
    TWAPEngine,
)

from execution.slippage_engine import (
    SlippageEngine,
)

from execution.market_impact_engine import (
    MarketImpactEngine,
)

from execution.transaction_cost_engine import (
    TransactionCostEngine,
)

from execution.execution_analytics import (
    ExecutionAnalytics,
)


# ==========================================================
# EXECUTION ENGINE
# ==========================================================


@lru_cache
def get_execution_engine(

) -> ExecutionEngine:
    """
    Execution engine.
    """

    return ExecutionEngine()


# ==========================================================
# ORDER MANAGER
# ==========================================================


@lru_cache
def get_order_manager(

) -> OrderManager:
    """
    Order manager.
    """

    return OrderManager()


# ==========================================================
# EXECUTION MANAGER
# ==========================================================


@lru_cache
def get_execution_manager(

) -> ExecutionManager:
    """
    Execution manager.
    """

    return ExecutionManager()


# ==========================================================
# VWAP
# ==========================================================


@lru_cache
def get_vwap_engine(

) -> VWAPEngine:
    """
    VWAP engine.
    """

    return VWAPEngine()


# ==========================================================
# TWAP
# ==========================================================


@lru_cache
def get_twap_engine(

) -> TWAPEngine:
    """
    TWAP engine.
    """

    return TWAPEngine()


# ==========================================================
# SLIPPAGE
# ==========================================================


@lru_cache
def get_slippage_engine(

) -> SlippageEngine:
    """
    Slippage engine.
    """

    return SlippageEngine()


# ==========================================================
# MARKET IMPACT
# ==========================================================


@lru_cache
def get_market_impact_engine(

) -> MarketImpactEngine:
    """
    Market impact model.
    """

    return MarketImpactEngine()


# ==========================================================
# TRANSACTION COST
# ==========================================================


@lru_cache
def get_transaction_cost_engine(

) -> TransactionCostEngine:
    """
    Transaction cost engine.
    """

    return TransactionCostEngine()


# ==========================================================
# EXECUTION ANALYTICS
# ==========================================================


@lru_cache
def get_execution_analytics(

) -> ExecutionAnalytics:
    """
    Execution analytics.
    """

    return ExecutionAnalytics()


# ==========================================================
# HEALTH
# ==========================================================


def execution_health(

) -> dict:

    return {

        "engine": "ExecutionEngine",

        "status": "healthy",

        "singleton": True,

    }


# ==========================================================
# SUMMARY
# ==========================================================


def execution_summary(

) -> dict:

    return {

        "services": [

            "ExecutionEngine",

            "OrderManager",

            "ExecutionManager",

            "VWAPEngine",

            "TWAPEngine",

            "SlippageEngine",

            "MarketImpactEngine",

            "TransactionCostEngine",

            "ExecutionAnalytics",

        ],

        "count": 9,

    }


# ==========================================================
# EXPORTS
# ==========================================================


__all__ = [

    "get_execution_engine",

    "get_order_manager",

    "get_execution_manager",

    "get_vwap_engine",

    "get_twap_engine",

    "get_slippage_engine",

    "get_market_impact_engine",

    "get_transaction_cost_engine",

    "get_execution_analytics",

    "execution_health",

    "execution_summary",

]