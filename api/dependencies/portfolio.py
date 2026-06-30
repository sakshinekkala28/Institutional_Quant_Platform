"""
====================================================================
Institutional Quant Platform

Portfolio Dependencies

Author : Institutional Quant Platform

Purpose
-------
FastAPI dependency providers for portfolio services.

Provides

• Portfolio Engine
• Portfolio Manager
• Holdings Service
• Allocation Service
• Performance Service
• Portfolio Analytics

Used By

• Portfolio Router
• Optimization Router
• Risk Router
• Execution Router

====================================================================
"""

from __future__ import annotations

from functools import lru_cache

from analytics.portfolio.portfolio_engine import (
    PortfolioEngine,
)

from analytics.portfolio.performance_engine import (
    PerformanceEngine,
)

from analytics.portfolio.allocation_engine import (
    AllocationEngine,
)

from analytics.portfolio.holdings_engine import (
    HoldingsEngine,
)

from analytics.portfolio.analytics_engine import (
    PortfolioAnalyticsEngine,
)


# ==========================================================
# PORTFOLIO ENGINE
# ==========================================================


@lru_cache
def get_portfolio_engine(

) -> PortfolioEngine:
    """
    Portfolio engine singleton.
    """

    return PortfolioEngine()


# ==========================================================
# HOLDINGS ENGINE
# ==========================================================


@lru_cache
def get_holdings_engine(

) -> HoldingsEngine:
    """
    Holdings engine.
    """

    return HoldingsEngine()


# ==========================================================
# ALLOCATION ENGINE
# ==========================================================


@lru_cache
def get_allocation_engine(

) -> AllocationEngine:
    """
    Allocation engine.
    """

    return AllocationEngine()


# ==========================================================
# PERFORMANCE ENGINE
# ==========================================================


@lru_cache
def get_performance_engine(

) -> PerformanceEngine:
    """
    Performance engine.
    """

    return PerformanceEngine()


# ==========================================================
# ANALYTICS ENGINE
# ==========================================================


@lru_cache
def get_portfolio_analytics(

) -> PortfolioAnalyticsEngine:
    """
    Portfolio analytics.
    """

    return PortfolioAnalyticsEngine()


# ==========================================================
# HEALTH
# ==========================================================


def portfolio_health(

) -> dict:
    """
    Portfolio dependency health.
    """

    return {

        "engine": "PortfolioEngine",

        "status": "healthy",

        "singleton": True,

    }


# ==========================================================
# SUMMARY
# ==========================================================


def portfolio_summary(

) -> dict:
    """
    Portfolio services summary.
    """

    return {

        "services": [

            "PortfolioEngine",

            "HoldingsEngine",

            "AllocationEngine",

            "PerformanceEngine",

            "PortfolioAnalyticsEngine",

        ],

        "count": 5,

    }


# ==========================================================
# EXPORTS
# ==========================================================


__all__ = [

    "get_portfolio_engine",

    "get_holdings_engine",

    "get_allocation_engine",

    "get_performance_engine",

    "get_portfolio_analytics",

    "portfolio_health",

    "portfolio_summary",

]