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
• Portfolio Constructor
• Portfolio Validator
• Portfolio Health Check
• Risk Parity Allocator
• Constraint Engine
• Black-Litterman Overlay

Used By

• Portfolio Router
• Optimization Router
• Risk Router
• Execution Router

====================================================================
"""

from __future__ import annotations

from functools import lru_cache

from portfolio.portfolio_engine import (
    PortfolioEngine,
    PortfolioConstructor,
    PortfolioDataValidator,
    PortfolioHealthCheck,
    RiskParityAllocator,
    ConstraintEngine,
    BlackLittermanOverlay,
)


# ==========================================================
# PORTFOLIO ENGINE
# ==========================================================


@lru_cache
def get_portfolio_engine() -> PortfolioEngine:
    """
    Primary portfolio engine.
    """
    return PortfolioEngine()


# ==========================================================
# PORTFOLIO CONSTRUCTOR
# ==========================================================


@lru_cache
def get_portfolio_constructor() -> PortfolioConstructor:
    """
    Portfolio construction engine.
    """
    return PortfolioConstructor()


# ==========================================================
# PORTFOLIO VALIDATOR
# ==========================================================


@lru_cache
def get_portfolio_validator() -> PortfolioDataValidator:
    """
    Portfolio validation service.
    """
    return PortfolioDataValidator()


# ==========================================================
# HEALTH CHECK
# ==========================================================


@lru_cache
def get_portfolio_health_check() -> PortfolioHealthCheck:
    """
    Portfolio health checker.
    """
    return PortfolioHealthCheck()


# ==========================================================
# RISK PARITY
# ==========================================================


@lru_cache
def get_risk_parity_allocator() -> RiskParityAllocator:
    """
    Risk parity allocation engine.
    """
    return RiskParityAllocator()


# ==========================================================
# CONSTRAINT ENGINE
# ==========================================================


@lru_cache
def get_constraint_engine() -> ConstraintEngine:
    """
    Portfolio constraint engine.
    """
    return ConstraintEngine()


# ==========================================================
# BLACK-LITTERMAN
# ==========================================================


@lru_cache
def get_black_litterman_overlay() -> BlackLittermanOverlay:
    """
    Black-Litterman overlay.
    """
    return BlackLittermanOverlay()


# ==========================================================
# HEALTH
# ==========================================================


def portfolio_health() -> dict:
    """
    Dependency health.
    """

    return {

        "engine": "PortfolioEngine",

        "status": "healthy",

        "singleton": True,

    }


# ==========================================================
# SUMMARY
# ==========================================================


def portfolio_summary() -> dict:
    """
    Registered services.
    """

    return {

        "services": [

            "PortfolioEngine",

            "PortfolioConstructor",

            "PortfolioDataValidator",

            "PortfolioHealthCheck",

            "RiskParityAllocator",

            "ConstraintEngine",

            "BlackLittermanOverlay",

        ],

        "count": 7,

    }


# ==========================================================
# EXPORTS
# ==========================================================


__all__ = [

    "get_portfolio_engine",

    "get_portfolio_constructor",

    "get_portfolio_validator",

    "get_portfolio_health_check",

    "get_risk_parity_allocator",

    "get_constraint_engine",

    "get_black_litterman_overlay",

    "portfolio_health",

    "portfolio_summary",

]