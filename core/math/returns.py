"""
====================================================================
Institutional Quant Platform

Return Mathematics

Author : Institutional Quant Platform

Purpose
-------
Institutional return mathematics.

Provides reusable return calculations for

• Risk Engine
• Performance Engine
• Portfolio Analytics
• Optimizer
• Attribution

====================================================================
"""

from __future__ import annotations

import numpy as np

from core.constants import RiskConstants


# ==========================================================
# SIMPLE RETURNS
# ==========================================================

def simple_returns(

    prices: np.ndarray

) -> np.ndarray:
    """
    Compute simple returns from prices.
    """

    prices = np.asarray(

        prices,

        dtype=np.float64

    )

    if prices.size < 2:

        return np.empty(

            0,

            dtype=np.float64

        )

    return (

        prices[1:]

        /

        prices[:-1]

    ) - 1.0


# ==========================================================
# LOG RETURNS
# ==========================================================

def log_returns(

    prices: np.ndarray

) -> np.ndarray:
    """
    Compute logarithmic returns.
    """

    prices = np.asarray(

        prices,

        dtype=np.float64

    )

    if prices.size < 2:

        return np.empty(

            0,

            dtype=np.float64

        )

    return np.log(

        prices[1:]

        /

        prices[:-1]

    )


# ==========================================================
# CUMULATIVE RETURN
# ==========================================================

def cumulative_return(

    returns: np.ndarray

) -> float:
    """
    Total cumulative return.
    """

    returns = np.asarray(

        returns,

        dtype=np.float64

    )

    if returns.size == 0:

        return 0.0

    return float(

        np.prod(

            1.0 + returns

        )

        - 1.0

    )


# ==========================================================
# CUMULATIVE RETURN SERIES
# ==========================================================

def cumulative_returns(

    returns: np.ndarray

) -> np.ndarray:
    """
    Cumulative return series.
    """

    returns = np.asarray(

        returns,

        dtype=np.float64

    )

    if returns.size == 0:

        return np.empty(

            0,

            dtype=np.float64

        )

    return np.cumprod(

        1.0 + returns

    ) - 1.0


# ==========================================================
# COMPOUND GROWTH
# ==========================================================

def compound_growth(

    returns: np.ndarray

) -> np.ndarray:
    """
    Wealth index.
    """

    returns = np.asarray(

        returns,

        dtype=np.float64

    )

    if returns.size == 0:

        return np.empty(

            0,

            dtype=np.float64

        )

    return np.cumprod(

        1.0 + returns

    )


# ==========================================================
# MEAN RETURN
# ==========================================================

def mean_return(

    returns: np.ndarray

) -> float:
    """
    Arithmetic mean return.
    """

    returns = np.asarray(

        returns,

        dtype=np.float64

    )

    if returns.size == 0:

        return 0.0

    return float(

        np.mean(

            returns

        )

    )


# ==========================================================
# GEOMETRIC RETURN
# ==========================================================

def geometric_return(

    returns: np.ndarray

) -> float:
    """
    Geometric average return.
    """

    returns = np.asarray(

        returns,

        dtype=np.float64

    )

    if returns.size == 0:

        return 0.0

    wealth = np.prod(

        1.0 + returns

    )

    return float(

        wealth ** (

            1.0

            /

            returns.size

        )

        - 1.0

    )


# ==========================================================
# EXCESS RETURNS
# ==========================================================

def excess_returns(

    returns: np.ndarray,

    risk_free_rate: float = (
        RiskConstants.DEFAULT_RISK_FREE_RATE
    )

) -> np.ndarray:
    """
    Excess returns.
    """

    returns = np.asarray(

        returns,

        dtype=np.float64

    )

    return (

        returns

        - risk_free_rate

    )


# ==========================================================
# ACTIVE RETURNS
# ==========================================================

def active_returns(

    portfolio_returns: np.ndarray,

    benchmark_returns: np.ndarray

) -> np.ndarray:
    """
    Active return series.
    """

    portfolio_returns = np.asarray(

        portfolio_returns,

        dtype=np.float64

    )

    benchmark_returns = np.asarray(

        benchmark_returns,

        dtype=np.float64

    )

    if portfolio_returns.shape != benchmark_returns.shape:

        raise ValueError(

            "Return series must have identical shape."

        )

    return (

        portfolio_returns

        - benchmark_returns

    )


# ==========================================================
# WEIGHTED PORTFOLIO RETURNS
# ==========================================================

def portfolio_returns(

    weights: np.ndarray,

    asset_returns: np.ndarray

) -> np.ndarray:
    """
    Weighted portfolio return series.

    Parameters
    ----------
    weights
        Shape (N,)

    asset_returns
        Shape (N,T)
    """

    weights = np.asarray(

        weights,

        dtype=np.float64

    )

    asset_returns = np.asarray(

        asset_returns,

        dtype=np.float64

    )

    if asset_returns.ndim != 2:

        raise ValueError(

            "Asset returns must be a 2-D matrix."

        )

    if weights.size != asset_returns.shape[0]:

        raise ValueError(

            "Weights and asset dimensions differ."

        )

    return weights @ asset_returns


# ==========================================================
# VALIDATE RETURN SERIES
# ==========================================================

def validate_returns(

    returns: np.ndarray

) -> np.ndarray:
    """
    Validate and sanitize return series.
    """

    returns = np.asarray(

        returns,

        dtype=np.float64

    )

    if np.isnan(

        returns

    ).any():

        raise ValueError(

            "Return series contains NaN."

        )

    if np.isinf(

        returns

    ).any():

        raise ValueError(

            "Return series contains Inf."

        )

    return returns