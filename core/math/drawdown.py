"""
====================================================================
Institutional Quant Platform

Drawdown Mathematics

Author : Institutional Quant Platform

Purpose
-------
Institutional drawdown mathematics.

Provides reusable drawdown calculations for

• Drawdown Series
• Maximum Drawdown
• Average Drawdown
• Drawdown Duration
• Recovery Period
• Underwater Curve

Used By

• PerformanceRisk
• TailRisk
• Performance Analytics
• Reporting

====================================================================
"""

from __future__ import annotations

import numpy as np

from core.constants import RiskConstants


# ==========================================================
# WEALTH INDEX
# ==========================================================

def wealth_index(

    returns: np.ndarray,

    initial_value: float = 1.0

) -> np.ndarray:
    """
    Compute cumulative wealth index.
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

    return (

        initial_value

        *

        np.cumprod(

            1.0 + returns

        )

    )


# ==========================================================
# RUNNING MAXIMUM
# ==========================================================

def running_maximum(

    wealth: np.ndarray

) -> np.ndarray:
    """
    Running peak wealth.
    """

    wealth = np.asarray(

        wealth,

        dtype=np.float64

    )

    if wealth.size == 0:

        return wealth

    return np.maximum.accumulate(

        wealth

    )


# ==========================================================
# DRAWDOWN SERIES
# ==========================================================

def drawdown_series(

    returns: np.ndarray

) -> np.ndarray:
    """
    Compute drawdown series.
    """

    wealth = wealth_index(

        returns

    )

    if wealth.size == 0:

        return wealth

    peak = running_maximum(

        wealth

    )

    return (

        wealth

        / peak

    ) - 1.0


# ==========================================================
# MAXIMUM DRAWDOWN
# ==========================================================

def maximum_drawdown(

    returns: np.ndarray

) -> float:
    """
    Maximum drawdown.
    """

    drawdowns = drawdown_series(

        returns

    )

    if drawdowns.size == 0:

        return 0.0

    return float(

        abs(

            np.min(

                drawdowns

            )

        )

    )


# ==========================================================
# AVERAGE DRAWDOWN
# ==========================================================

def average_drawdown(

    returns: np.ndarray

) -> float:
    """
    Average drawdown.
    """

    drawdowns = drawdown_series(

        returns

    )

    if drawdowns.size == 0:

        return 0.0

    negative = drawdowns[

        drawdowns < 0.0

    ]

    if negative.size == 0:

        return 0.0

    return float(

        abs(

            np.mean(

                negative

            )

        )

    )


# ==========================================================
# DRAWDOWN DURATION
# ==========================================================

def drawdown_duration(

    returns: np.ndarray

) -> int:
    """
    Longest consecutive drawdown.
    """

    drawdowns = drawdown_series(

        returns

    )

    longest = 0

    current = 0

    for value in drawdowns:

        if value < 0.0:

            current += 1

            longest = max(

                longest,

                current

            )

        else:

            current = 0

    return longest


# ==========================================================
# RECOVERY PERIOD
# ==========================================================

def recovery_period(

    returns: np.ndarray

) -> int:
    """
    Number of periods required
    to recover from maximum drawdown.
    """

    wealth = wealth_index(

        returns

    )

    if wealth.size == 0:

        return 0

    peak = running_maximum(

        wealth

    )

    peak_index = int(

        np.argmax(

            peak

        )

    )

    peak_value = peak[

        peak_index

    ]

    for index in range(

        peak_index,

        wealth.size

    ):

        if wealth[index] >= peak_value:

            return index - peak_index

    return wealth.size - peak_index


# ==========================================================
# UNDERWATER CURVE
# ==========================================================

def underwater_curve(

    returns: np.ndarray

) -> np.ndarray:
    """
    Alias for drawdown series.
    """

    return drawdown_series(

        returns

    )


# ==========================================================
# IS IN DRAWDOWN
# ==========================================================

def is_in_drawdown(

    returns: np.ndarray

) -> bool:
    """
    Whether current portfolio
    is below its historical peak.
    """

    drawdowns = drawdown_series(

        returns

    )

    if drawdowns.size == 0:

        return False

    return (

        drawdowns[-1]

        <

        -RiskConstants.EPSILON

    )