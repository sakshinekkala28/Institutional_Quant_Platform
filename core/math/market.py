"""
====================================================================
Institutional Quant Platform

Market Mathematics

Author : Institutional Quant Platform

Purpose
-------
Reusable market-relative mathematics.

Provides

• Beta
• Alpha
• Active Return
• Tracking Error
• Information Ratio

Used By

• MarketRisk
• PerformanceRisk
• Attribution

====================================================================
"""

from __future__ import annotations

import numpy as np

from core.constants import RiskConstants

from core.math.statistics import (

    covariance,

    mean,

    standard_deviation,

    variance

)

from core.math.returns import (

    active_returns,

    excess_returns

)

from core.math.annualization import (

    annualize_information_ratio

)


# ==========================================================
# BETA
# ==========================================================

def beta(

    portfolio_returns: np.ndarray,

    benchmark_returns: np.ndarray

) -> float:

    benchmark_variance = variance(

        benchmark_returns

    )

    if benchmark_variance <= RiskConstants.MIN_VARIANCE:

        return 0.0

    return (

        covariance(

            portfolio_returns,

            benchmark_returns

        )

        /

        benchmark_variance

    )


# ==========================================================
# ACTIVE RETURN
# ==========================================================

def active_return(

    portfolio_returns: np.ndarray,

    benchmark_returns: np.ndarray

) -> float:

    return mean(

        active_returns(

            portfolio_returns,

            benchmark_returns

        )

    )


# ==========================================================
# TRACKING ERROR
# ==========================================================

def tracking_error(

    portfolio_returns: np.ndarray,

    benchmark_returns: np.ndarray

) -> float:

    return standard_deviation(

        active_returns(

            portfolio_returns,

            benchmark_returns

        )

    )


# ==========================================================
# INFORMATION RATIO
# ==========================================================

def information_ratio(

    portfolio_returns: np.ndarray,

    benchmark_returns: np.ndarray

) -> float:

    te = tracking_error(

        portfolio_returns,

        benchmark_returns

    )

    if te <= RiskConstants.MIN_VOLATILITY:

        return 0.0

    periodic = (

        active_return(

            portfolio_returns,

            benchmark_returns

        )

        / te

    )

    return annualize_information_ratio(

        periodic

    )


# ==========================================================
# ALPHA
# ==========================================================

def alpha(

    portfolio_returns: np.ndarray,

    benchmark_returns: np.ndarray,

    risk_free_rate: float

) -> float:

    b = beta(

        portfolio_returns,

        benchmark_returns

    )

    benchmark = mean(

        benchmark_returns

    )

    portfolio = mean(

        portfolio_returns

    )

    return (

        portfolio

        -

        (

            risk_free_rate

            +

            b

            *

            (

                benchmark

                -

                risk_free_rate

            )

        )

    )