"""
====================================================================
Institutional Quant Platform

Tail Mathematics

Author : Institutional Quant Platform

Purpose
-------
Institutional tail-risk mathematics.

Provides

• Historical VaR
• Parametric VaR
• Expected Shortfall
• CVaR
• Tail Ratio
• Worst Return
• Tail Volatility

====================================================================
"""

from __future__ import annotations

import numpy as np

from scipy.stats import norm

from core.math.statistics import (
    mean,
    standard_deviation,
)

from core.constants import RiskConstants


# ==========================================================
# HISTORICAL VAR
# ==========================================================

def historical_var(

    returns: np.ndarray,

    confidence: float = 0.95

) -> float:

    returns = np.asarray(

        returns,

        dtype=np.float64

    )

    if returns.size == 0:

        return 0.0

    percentile = (

        1.0

        - confidence

    ) * 100.0

    return abs(

        float(

            np.percentile(

                returns,

                percentile

            )

        )

    )


# ==========================================================
# PARAMETRIC VAR
# ==========================================================

def parametric_var(

    returns: np.ndarray,

    confidence: float = 0.95

) -> float:

    mu = mean(

        returns

    )

    sigma = standard_deviation(

        returns

    )

    z = norm.ppf(

        1.0

        - confidence

    )

    return abs(

        mu

        +

        z

        * sigma

    )


# ==========================================================
# EXPECTED SHORTFALL
# ==========================================================

def expected_shortfall(

    returns: np.ndarray,

    confidence: float = 0.95

) -> float:

    var = historical_var(

        returns,

        confidence

    )

    tail = returns[

        returns <= -var

    ]

    if tail.size == 0:

        return var

    return abs(

        float(

            np.mean(

                tail

            )

        )

    )


# ==========================================================
# CONDITIONAL VAR
# ==========================================================

def conditional_var(

    returns: np.ndarray,

    confidence: float = 0.95

) -> float:

    return expected_shortfall(

        returns,

        confidence

    )


# ==========================================================
# WORST RETURN
# ==========================================================

def worst_return(

    returns: np.ndarray

) -> float:

    if returns.size == 0:

        return 0.0

    return abs(

        float(

            np.min(

                returns

            )

        )

    )


# ==========================================================
# TAIL VOLATILITY
# ==========================================================

def tail_volatility(

    returns: np.ndarray,

    confidence: float = 0.95

) -> float:

    var = historical_var(

        returns,

        confidence

    )

    tail = returns[

        returns <= -var

    ]

    if tail.size < 2:

        return 0.0

    return standard_deviation(

        tail

    )


# ==========================================================
# TAIL RATIO
# ==========================================================

def tail_ratio(

    returns: np.ndarray

) -> float:

    upper = abs(

        np.percentile(

            returns,

            95

        )

    )

    lower = abs(

        np.percentile(

            returns,

            5

        )

    )

    if lower <= RiskConstants.EPSILON:

        return 0.0

    return upper / lower