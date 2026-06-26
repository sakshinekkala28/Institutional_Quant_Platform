"""
====================================================================
Institutional Quant Platform

Downside Mathematics

Author : Institutional Quant Platform

Purpose
-------
Institutional downside risk mathematics.

Provides reusable downside risk calculations for

• Downside Returns

====================================================================

Provides reusable downside risk calculations for

• Downside Returns
• Downside Deviation
• Semi-Variance
• Semi-Deviation
• Lower Partial Moments
• Downside Capture
• Gain/Loss Separation

Used By

• PerformanceRisk
• TailRisk
• Risk Analytics

====================================================================
"""

from __future__ import annotations

import numpy as np

from core.constants import RiskConstants


# ==========================================================
# DOWNSIDE RETURNS
# ==========================================================

def downside_returns(

    returns: np.ndarray,

    threshold: float = (
        RiskConstants.DEFAULT_TARGET_RETURN
    )

) -> np.ndarray:
    """
    Returns below threshold.
    """

    returns = np.asarray(

        returns,

        dtype=np.float64

    )

    return returns[

        returns < threshold

    ]


# ==========================================================
# UPSIDE RETURNS
# ==========================================================

def upside_returns(

    returns: np.ndarray,

    threshold: float = (
        RiskConstants.DEFAULT_TARGET_RETURN
    )

) -> np.ndarray:
    """
    Returns above threshold.
    """

    returns = np.asarray(

        returns,

        dtype=np.float64

    )

    return returns[

        returns >= threshold

    ]


# ==========================================================
# DOWNSIDE DEVIATION
# ==========================================================

def downside_deviation(

    returns: np.ndarray,

    threshold: float = (
        RiskConstants.DEFAULT_TARGET_RETURN
    )

) -> float:
    """
    Downside deviation.
    """

    downside = downside_returns(

        returns,

        threshold

    )

    if downside.size == 0:

        return 0.0

    deviation = (

        downside

        - threshold

    ) ** 2

    return float(

        np.sqrt(

            np.mean(

                deviation

            )

        )

    )


# ==========================================================
# SEMI VARIANCE
# ==========================================================

def semivariance(

    returns: np.ndarray,

    threshold: float = (
        RiskConstants.DEFAULT_TARGET_RETURN
    )

) -> float:
    """
    Semi-variance.
    """

    downside = downside_returns(

        returns,

        threshold

    )

    if downside.size == 0:

        return 0.0

    return float(

        np.mean(

            (

                downside

                - threshold

            ) ** 2

        )

    )


# ==========================================================
# SEMI DEVIATION
# ==========================================================

def semideviation(

    returns: np.ndarray,

    threshold: float = (
        RiskConstants.DEFAULT_TARGET_RETURN
    )

) -> float:
    """
    Semi-deviation.
    """

    return float(

        np.sqrt(

            semivariance(

                returns,

                threshold

            )

        )

    )


# ==========================================================
# LOWER PARTIAL MOMENT
# ==========================================================

def lower_partial_moment(

    returns: np.ndarray,

    threshold: float = (
        RiskConstants.DEFAULT_TARGET_RETURN
    ),

    order: int = 2

) -> float:
    """
    Lower Partial Moment.
    """

    returns = np.asarray(

        returns,

        dtype=np.float64

    )

    downside = np.maximum(

        threshold - returns,

        0.0

    )

    return float(

        np.mean(

            downside ** order

        )

    )


# ==========================================================
# UPSIDE PARTIAL MOMENT
# ==========================================================

def upper_partial_moment(

    returns: np.ndarray,

    threshold: float = (
        RiskConstants.DEFAULT_TARGET_RETURN
    ),

    order: int = 2

) -> float:
    """
    Upper Partial Moment.
    """

    returns = np.asarray(

        returns,

        dtype=np.float64

    )

    upside = np.maximum(

        returns - threshold,

        0.0

    )

    return float(

        np.mean(

            upside ** order

        )

    )


# ==========================================================
# GAIN / LOSS RATIO
# ==========================================================

def gain_loss_ratio(

    returns: np.ndarray,

    threshold: float = (
        RiskConstants.DEFAULT_TARGET_RETURN
    )

) -> float:
    """
    Gain/Loss Ratio.
    """

    gains = upside_returns(

        returns,

        threshold

    )

    losses = downside_returns(

        returns,

        threshold

    )

    if losses.size == 0:

        return float(

            "inf"

        )

    average_gain = (

        float(

            np.mean(

                gains

            )

        )

        if gains.size

        else 0.0

    )

    average_loss = abs(

        float(

            np.mean(

                losses

            )

        )

    )

    if average_loss <= RiskConstants.EPSILON:

        return float(

            "inf"

        )

    return (

        average_gain

        /

        average_loss

    )


# ==========================================================
# DOWNSIDE FREQUENCY
# ==========================================================

def downside_frequency(

    returns: np.ndarray,

    threshold: float = (
        RiskConstants.DEFAULT_TARGET_RETURN
    )

) -> float:
    """
    Percentage of observations
    below threshold.
    """

    returns = np.asarray(

        returns,

        dtype=np.float64

    )

    if returns.size == 0:

        return 0.0

    return float(

        np.mean(

            returns < threshold

        )

    )