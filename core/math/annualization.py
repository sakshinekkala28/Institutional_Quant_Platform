"""
====================================================================
Institutional Quant Platform

Annualization Utilities

Author : Institutional Quant Platform

Purpose
-------
Institutional annualization mathematics.

Provides reusable annualization utilities for

• Returns
• Volatility
• Variance
• Tracking Error
• Information Ratio
• Sharpe Ratio

Used By

• Risk Engine
• Performance Engine
• Optimizer
• Analytics

====================================================================
"""

from __future__ import annotations

import numpy as np

from core.constants import RiskConstants


# ==========================================================
# RETURN
# ==========================================================

def annualize_return(

    periodic_return: float,

    periods_per_year: int = (
        RiskConstants.TRADING_DAYS_PER_YEAR
    )

) -> float:
    """
    Annualize arithmetic return.
    """

    return (

        periodic_return

        * periods_per_year

    )


# ==========================================================
# COMPOUNDED RETURN
# ==========================================================

def annualize_compounded_return(

    cumulative_return: float,

    observations: int,

    periods_per_year: int = (
        RiskConstants.TRADING_DAYS_PER_YEAR
    )

) -> float:
    """
    Annualize compounded return.
    """

    if observations <= 0:

        return 0.0

    years = (

        observations

        / periods_per_year

    )

    if years <= 0:

        return 0.0

    return (

        (1.0 + cumulative_return)

        **

        (1.0 / years)

    ) - 1.0


# ==========================================================
# VOLATILITY
# ==========================================================

def annualize_volatility(

    volatility: float,

    periods_per_year: int = (
        RiskConstants.TRADING_DAYS_PER_YEAR
    )

) -> float:
    """
    Annualize volatility.
    """

    return (

        volatility

        *

        np.sqrt(

            periods_per_year

        )

    )


# ==========================================================
# VARIANCE
# ==========================================================

def annualize_variance(

    variance: float,

    periods_per_year: int = (
        RiskConstants.TRADING_DAYS_PER_YEAR
    )

) -> float:
    """
    Annualize variance.
    """

    return (

        variance

        * periods_per_year

    )


# ==========================================================
# TRACKING ERROR
# ==========================================================

def annualize_tracking_error(

    tracking_error: float,

    periods_per_year: int = (
        RiskConstants.TRADING_DAYS_PER_YEAR
    )

) -> float:
    """
    Annualize tracking error.
    """

    return annualize_volatility(

        tracking_error,

        periods_per_year

    )


# ==========================================================
# SHARPE RATIO
# ==========================================================

def annualize_sharpe_ratio(

    sharpe_ratio: float,

    periods_per_year: int = (
        RiskConstants.TRADING_DAYS_PER_YEAR
    )

) -> float:
    """
    Annualize Sharpe ratio.
    """

    return (

        sharpe_ratio

        *

        np.sqrt(

            periods_per_year

        )

    )


# ==========================================================
# INFORMATION RATIO
# ==========================================================

def annualize_information_ratio(

    information_ratio: float,

    periods_per_year: int = (
        RiskConstants.TRADING_DAYS_PER_YEAR
    )

) -> float:
    """
    Annualize Information Ratio.
    """

    return (

        information_ratio

        *

        np.sqrt(

            periods_per_year

        )

    )


# ==========================================================
# GENERIC SCALER
# ==========================================================

def scale_by_periods(

    value: float,

    periods_per_year: int

) -> float:
    """
    Generic linear scaling.
    """

    return (

        value

        * periods_per_year

    )