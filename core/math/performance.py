"""
====================================================================
Institutional Quant Platform

Performance Mathematics

Author : Institutional Quant Platform

Purpose
-------
Institutional performance mathematics.

Provides reusable performance metrics.

Used By

• PerformanceRisk
• MarketRisk
• Reporting
• Analytics

====================================================================
"""

from __future__ import annotations

import numpy as np

from core.constants import RiskConstants

from core.math.annualization import (
    annualize_return,
    annualize_volatility
)

from core.math.statistics import (
    mean,
    standard_deviation,
    covariance,
    variance
)

from core.math.downside import (
    downside_deviation,
    gain_loss_ratio
)

from core.math.drawdown import (
    maximum_drawdown
)

from core.math.returns import (
    excess_returns,
    active_returns
)


# ==========================================================
# SHARPE RATIO
# ==========================================================

def sharpe_ratio(

    returns: np.ndarray,

    risk_free_rate: float = (
        RiskConstants.DEFAULT_RISK_FREE_RATE
    )

) -> float:
    """
    Annualized Sharpe Ratio.
    """

    excess = excess_returns(

        returns,

        risk_free_rate

    )

    sigma = standard_deviation(

        excess

    )

    if sigma <= RiskConstants.MIN_VOLATILITY:

        return 0.0

    periodic = (

        mean(

            excess

        )

        / sigma

    )

    return annualize_volatility(

        periodic

    )


# ==========================================================
# SORTINO RATIO
# ==========================================================

def sortino_ratio(

    returns: np.ndarray,

    risk_free_rate: float = (
        RiskConstants.DEFAULT_RISK_FREE_RATE
    )

) -> float:
    """
    Annualized Sortino Ratio.
    """

    downside = downside_deviation(

        returns,

        risk_free_rate

    )

    if downside <= RiskConstants.MIN_VOLATILITY:

        return 0.0

    periodic = (

        mean(

            excess_returns(

                returns,

                risk_free_rate

            )

        )

        / downside

    )

    return annualize_volatility(

        periodic

    )


# ==========================================================
# TREYNOR RATIO
# ==========================================================

def treynor_ratio(

    portfolio_returns: np.ndarray,

    benchmark_returns: np.ndarray,

    risk_free_rate: float = (
        RiskConstants.DEFAULT_RISK_FREE_RATE
    )

) -> float:
    """
    Treynor Ratio.
    """

    beta_variance = variance(

        benchmark_returns

    )

    if beta_variance <= RiskConstants.MIN_VARIANCE:

        return 0.0

    beta = (

        covariance(

            portfolio_returns,

            benchmark_returns

        )

        / beta_variance

    )

    if abs(beta) <= RiskConstants.EPSILON:

        return 0.0

    return (

        mean(

            excess_returns(

                portfolio_returns,

                risk_free_rate

            )

        )

        / beta

    )


# ==========================================================
# INFORMATION RATIO
# ==========================================================

def information_ratio(

    portfolio_returns: np.ndarray,

    benchmark_returns: np.ndarray

) -> float:
    """
    Information Ratio.
    """

    active = active_returns(

        portfolio_returns,

        benchmark_returns

    )

    tracking_error = standard_deviation(

        active

    )

    if tracking_error <= RiskConstants.MIN_VOLATILITY:

        return 0.0

    periodic = (

        mean(

            active

        )

        / tracking_error

    )

    return annualize_volatility(

        periodic

    )


# ==========================================================
# CALMAR RATIO
# ==========================================================

def calmar_ratio(

    returns: np.ndarray

) -> float:
    """
    Annualized Calmar Ratio.
    """

    drawdown = maximum_drawdown(

        returns

    )

    if drawdown <= RiskConstants.MIN_DRAWDOWN:

        return 0.0

    annual_return = annualize_return(

        mean(

            returns

        )

    )

    return annual_return / drawdown


# ==========================================================
# OMEGA RATIO
# ==========================================================

def omega_ratio(

    returns: np.ndarray,

    threshold: float = (
        RiskConstants.DEFAULT_TARGET_RETURN
    )

) -> float:
    """
    Omega Ratio.
    """

    returns = np.asarray(

        returns,

        dtype=np.float64

    )

    gains = np.clip(

        returns - threshold,

        a_min=0.0,

        a_max=None

    )

    losses = np.clip(

        threshold - returns,

        a_min=0.0,

        a_max=None

    )

    denominator = float(

        np.sum(

            losses

        )

    )

    if denominator <= RiskConstants.EPSILON:

        return float("inf")

    numerator = float(

        np.sum(

            gains

        )

    )

    return numerator / denominator


# ==========================================================
# UPSIDE CAPTURE
# ==========================================================

def upside_capture_ratio(

    portfolio_returns: np.ndarray,

    benchmark_returns: np.ndarray

) -> float:
    """
    Upside Capture Ratio.
    """

    mask = benchmark_returns > 0.0

    if not np.any(mask):

        return 0.0

    benchmark_up = mean(

        benchmark_returns[mask]

    )

    if abs(

        benchmark_up

    ) <= RiskConstants.EPSILON:

        return 0.0

    portfolio_up = mean(

        portfolio_returns[mask]

    )

    return portfolio_up / benchmark_up


# ==========================================================
# DOWNSIDE CAPTURE
# ==========================================================

def downside_capture_ratio(

    portfolio_returns: np.ndarray,

    benchmark_returns: np.ndarray

) -> float:
    """
    Downside Capture Ratio.
    """

    mask = benchmark_returns < 0.0

    if not np.any(mask):

        return 0.0

    benchmark_down = abs(

        mean(

            benchmark_returns[mask]

        )

    )

    if benchmark_down <= RiskConstants.EPSILON:

        return 0.0

    portfolio_down = abs(

        mean(

            portfolio_returns[mask]

        )

    )

    return portfolio_down / benchmark_down


# ==========================================================
# GAIN / LOSS RATIO
# ==========================================================

__all__ = [

    "sharpe_ratio",

    "sortino_ratio",

    "treynor_ratio",

    "information_ratio",

    "calmar_ratio",

    "omega_ratio",

    "gain_loss_ratio",

    "upside_capture_ratio",

    "downside_capture_ratio"

]