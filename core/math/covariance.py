"""
====================================================================
Institutional Quant Platform

Covariance Mathematics

Author : Institutional Quant Platform

Purpose
-------
Institutional covariance mathematics.

Provides reusable linear algebra routines for

• Portfolio Variance
• Portfolio Volatility
• Marginal Risk
• Component Risk
• Risk Contribution
• Diversification Ratio

Used By

• PortfolioRisk
• Optimizer
• HRP
• Black-Litterman
• Risk Budgeting

====================================================================
"""

from __future__ import annotations

import numpy as np

from core.constants import RiskConstants


# ==========================================================
# VALIDATION
# ==========================================================

def validate_covariance_matrix(

    covariance: np.ndarray

) -> np.ndarray:
    """
    Validate covariance matrix.
    """

    covariance = np.asarray(

        covariance,

        dtype=np.float64

    )

    if covariance.ndim != 2:

        raise ValueError(

            "Covariance matrix must be 2-dimensional."

        )

    rows, cols = covariance.shape

    if rows != cols:

        raise ValueError(

            "Covariance matrix must be square."

        )

    if np.isnan(covariance).any():

        raise ValueError(

            "Covariance matrix contains NaN."

        )

    if np.isinf(covariance).any():

        raise ValueError(

            "Covariance matrix contains Inf."

        )

    if not np.allclose(

        covariance,

        covariance.T

    ):

        raise ValueError(

            "Covariance matrix must be symmetric."

        )

    return covariance


# ==========================================================
# PORTFOLIO VARIANCE
# ==========================================================

def portfolio_variance(

    weights: np.ndarray,

    covariance: np.ndarray

) -> float:
    """
    σ² = wᵀΣw
    """

    weights = np.asarray(

        weights,

        dtype=np.float64

    )

    covariance = validate_covariance_matrix(

        covariance

    )

    if weights.size != covariance.shape[0]:

        raise ValueError(

            "Weights and covariance dimensions differ."

        )

    return float(

        weights.T

        @ covariance

        @ weights

    )


# ==========================================================
# PORTFOLIO VOLATILITY
# ==========================================================

def portfolio_volatility(

    weights: np.ndarray,

    covariance: np.ndarray

) -> float:
    """
    σ = √(wᵀΣw)
    """

    variance = portfolio_variance(

        weights,

        covariance

    )

    if variance <= RiskConstants.MIN_VARIANCE:

        return 0.0

    return float(

        np.sqrt(

            variance

        )

    )


# ==========================================================
# MARGINAL RISK
# ==========================================================

def marginal_risk(

    weights: np.ndarray,

    covariance: np.ndarray

) -> np.ndarray:
    """
    Marginal contribution to risk.

    Σw / σ
    """

    weights = np.asarray(

        weights,

        dtype=np.float64

    )

    covariance = validate_covariance_matrix(

        covariance

    )

    sigma = portfolio_volatility(

        weights,

        covariance

    )

    if sigma <= RiskConstants.MIN_VOLATILITY:

        return np.zeros_like(

            weights

        )

    return (

        covariance

        @ weights

    ) / sigma


# ==========================================================
# COMPONENT RISK
# ==========================================================

def component_risk(

    weights: np.ndarray,

    covariance: np.ndarray

) -> np.ndarray:
    """
    Component contribution to risk.
    """

    return (

        weights

        * marginal_risk(

            weights,

            covariance

        )

    )


# ==========================================================
# RISK CONTRIBUTION
# ==========================================================

def risk_contribution(

    weights: np.ndarray,

    covariance: np.ndarray

) -> np.ndarray:
    """
    Percentage contribution to risk.
    """

    sigma = portfolio_volatility(

        weights,

        covariance

    )

    if sigma <= RiskConstants.MIN_VOLATILITY:

        return np.zeros_like(

            weights

        )

    return (

        component_risk(

            weights,

            covariance

        )

        / sigma

    )


# ==========================================================
# DIVERSIFICATION RATIO
# ==========================================================

def diversification_ratio(

    weights: np.ndarray,

    covariance: np.ndarray

) -> float:
    """
    Diversification ratio.
    """

    covariance = validate_covariance_matrix(

        covariance

    )

    weights = np.asarray(

        weights,

        dtype=np.float64

    )

    sigma = portfolio_volatility(

        weights,

        covariance

    )

    if sigma <= RiskConstants.MIN_VOLATILITY:

        return 0.0

    asset_volatility = np.sqrt(

        np.diag(

            covariance

        )

    )

    numerator = float(

        np.dot(

            weights,

            asset_volatility

        )

    )

    return numerator / sigma


# ==========================================================
# EFFECTIVE HOLDINGS
# ==========================================================

def effective_holdings(

    weights: np.ndarray

) -> float:
    """
    Effective number of holdings.
    """

    weights = np.asarray(

        weights,

        dtype=np.float64

    )

    denominator = float(

        np.sum(

            weights ** 2

        )

    )

    if denominator <= RiskConstants.EPSILON:

        return 0.0

    return 1.0 / denominator


# ==========================================================
# PORTFOLIO COVARIANCE
# ==========================================================

def portfolio_covariance_vector(

    weights: np.ndarray,

    covariance: np.ndarray

) -> np.ndarray:
    """
    Σw
    """

    weights = np.asarray(

        weights,

        dtype=np.float64

    )

    covariance = validate_covariance_matrix(

        covariance

    )

    return covariance @ weights