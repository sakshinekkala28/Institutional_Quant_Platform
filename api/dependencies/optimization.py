"""
====================================================================
Institutional Quant Platform

Optimization Dependencies

Author : Institutional Quant Platform

Purpose
-------
FastAPI dependency providers for optimization services.

Provides

• Portfolio Optimizer
• Mean Variance Optimizer
• Risk Parity Optimizer
• Black-Litterman Engine
• Efficient Frontier Engine
• Covariance Engine
• Expected Return Engine
• Constraint Manager

Used By

• Optimization Router
• Portfolio Router
• Risk Router
• Backtest Router

====================================================================
"""

from __future__ import annotations

from functools import lru_cache

from optimization.portfolio_optimizer import (
    PortfolioOptimizer,
)

from optimization.mean_variance_optimizer import (
    MeanVarianceOptimizer,
)

from optimization.risk_parity_optimizer import (
    RiskParityOptimizer,
)

from optimization.black_litterman import (
    BlackLittermanEngine,
)

from optimization.efficient_frontier import (
    EfficientFrontierEngine,
)

from optimization.covariance_engine import (
    CovarianceEngine,
)

from optimization.expected_return_engine import (
    ExpectedReturnEngine,
)

from optimization.constraint_manager import (
    ConstraintManager,
)


# ==========================================================
# PORTFOLIO OPTIMIZER
# ==========================================================


@lru_cache
def get_optimizer(

) -> PortfolioOptimizer:
    """
    Portfolio optimizer.
    """

    return PortfolioOptimizer()


# ==========================================================
# MEAN VARIANCE
# ==========================================================


@lru_cache
def get_mean_variance_optimizer(

) -> MeanVarianceOptimizer:
    """
    Mean-Variance optimizer.
    """

    return MeanVarianceOptimizer()


# ==========================================================
# RISK PARITY
# ==========================================================


@lru_cache
def get_risk_parity_optimizer(

) -> RiskParityOptimizer:
    """
    Risk parity optimizer.
    """

    return RiskParityOptimizer()


# ==========================================================
# BLACK-LITTERMAN
# ==========================================================


@lru_cache
def get_black_litterman_engine(

) -> BlackLittermanEngine:
    """
    Black-Litterman model.
    """

    return BlackLittermanEngine()


# ==========================================================
# EFFICIENT FRONTIER
# ==========================================================


@lru_cache
def get_efficient_frontier_engine(

) -> EfficientFrontierEngine:
    """
    Efficient frontier engine.
    """

    return EfficientFrontierEngine()


# ==========================================================
# COVARIANCE
# ==========================================================


@lru_cache
def get_covariance_engine(

) -> CovarianceEngine:
    """
    Covariance engine.
    """

    return CovarianceEngine()


# ==========================================================
# EXPECTED RETURNS
# ==========================================================


@lru_cache
def get_expected_return_engine(

) -> ExpectedReturnEngine:
    """
    Expected return engine.
    """

    return ExpectedReturnEngine()


# ==========================================================
# CONSTRAINT MANAGER
# ==========================================================


@lru_cache
def get_constraint_manager(

) -> ConstraintManager:
    """
    Constraint manager.
    """

    return ConstraintManager()


# ==========================================================
# HEALTH
# ==========================================================


def optimization_health(

) -> dict:

    return {

        "engine": "PortfolioOptimizer",

        "status": "healthy",

        "singleton": True,

    }


# ==========================================================
# SUMMARY
# ==========================================================


def optimization_summary(

) -> dict:

    return {

        "services": [

            "PortfolioOptimizer",

            "MeanVarianceOptimizer",

            "RiskParityOptimizer",

            "BlackLittermanEngine",

            "EfficientFrontierEngine",

            "CovarianceEngine",

            "ExpectedReturnEngine",

            "ConstraintManager",

        ],

        "count": 8,

    }


# ==========================================================
# EXPORTS
# ==========================================================


__all__ = [

    "get_optimizer",

    "get_mean_variance_optimizer",

    "get_risk_parity_optimizer",

    "get_black_litterman_engine",

    "get_efficient_frontier_engine",

    "get_covariance_engine",

    "get_expected_return_engine",

    "get_constraint_manager",

    "optimization_health",

    "optimization_summary",

]