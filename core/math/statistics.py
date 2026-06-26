"""
====================================================================
Institutional Quant Platform

Statistical Utilities

Author : Institutional Quant Platform

Purpose
-------
Generic statistical utility functions.

This module contains reusable statistical
operations that are independent of financial
concepts.

Used By

• Risk Engine
• Portfolio Analytics
• Optimizer
• Performance Engine
• Factor Models
• Attribution

====================================================================
"""

from __future__ import annotations

import numpy as np

from core.constants import RiskConstants


# ==========================================================
# MEAN
# ==========================================================

def mean(

    values: np.ndarray

) -> float:
    """
    Arithmetic mean.
    """

    values = np.asarray(

        values,

        dtype=np.float64

    )

    if values.size == 0:

        return 0.0

    return float(

        np.mean(

            values

        )

    )


# ==========================================================
# MEDIAN
# ==========================================================

def median(

    values: np.ndarray

) -> float:
    """
    Median.
    """

    values = np.asarray(

        values,

        dtype=np.float64

    )

    if values.size == 0:

        return 0.0

    return float(

        np.median(

            values

        )

    )


# ==========================================================
# VARIANCE
# ==========================================================

def variance(

    values: np.ndarray,

    ddof: int = 1

) -> float:
    """
    Sample variance.
    """

    values = np.asarray(

        values,

        dtype=np.float64

    )

    if values.size < 2:

        return 0.0

    return float(

        np.var(

            values,

            ddof=ddof

        )

    )


# ==========================================================
# STANDARD DEVIATION
# ==========================================================

def standard_deviation(

    values: np.ndarray,

    ddof: int = 1

) -> float:
    """
    Sample standard deviation.
    """

    values = np.asarray(

        values,

        dtype=np.float64

    )

    if values.size < 2:

        return 0.0

    return float(

        np.std(

            values,

            ddof=ddof

        )

    )


# ==========================================================
# COVARIANCE
# ==========================================================

def covariance(

    x: np.ndarray,

    y: np.ndarray

) -> float:
    """
    Sample covariance.
    """

    x = np.asarray(

        x,

        dtype=np.float64

    )

    y = np.asarray(

        y,

        dtype=np.float64

    )

    if x.size != y.size:

        raise ValueError(

            "Arrays must have equal length."

        )

    if x.size < 2:

        return 0.0

    return float(

        np.cov(

            x,

            y,

            ddof=1

        )[0, 1]

    )


# ==========================================================
# CORRELATION
# ==========================================================

def correlation(

    x: np.ndarray,

    y: np.ndarray

) -> float:
    """
    Pearson correlation coefficient.
    """

    x = np.asarray(

        x,

        dtype=np.float64

    )

    y = np.asarray(

        y,

        dtype=np.float64

    )

    if x.size != y.size:

        raise ValueError(

            "Arrays must have equal length."

        )

    if x.size < 2:

        return 0.0

    std_x = standard_deviation(

        x

    )

    std_y = standard_deviation(

        y

    )

    if (

        std_x

        <= RiskConstants.EPSILON

        or

        std_y

        <= RiskConstants.EPSILON

    ):

        return 0.0

    return float(

        np.corrcoef(

            x,

            y

        )[0, 1]

    )


# ==========================================================
# ROOT MEAN SQUARE
# ==========================================================

def root_mean_square(

    values: np.ndarray

) -> float:
    """
    Root mean square.
    """

    values = np.asarray(

        values,

        dtype=np.float64

    )

    if values.size == 0:

        return 0.0

    return float(

        np.sqrt(

            np.mean(

                values ** 2

            )

        )

    )


# ==========================================================
# NORMALIZATION
# ==========================================================

def normalize(

    values: np.ndarray

) -> np.ndarray:
    """
    Normalize values to [0,1].
    """

    values = np.asarray(

        values,

        dtype=np.float64

    )

    if values.size == 0:

        return values

    minimum = float(

        np.min(

            values

        )

    )

    maximum = float(

        np.max(

            values

        )

    )

    spread = (

        maximum

        -

        minimum

    )

    if spread <= RiskConstants.EPSILON:

        return np.zeros_like(

            values,

            dtype=np.float64

        )

    return (

        values

        -

        minimum

    ) / spread


# ==========================================================
# STANDARDIZATION
# ==========================================================

def standardize(

    values: np.ndarray

) -> np.ndarray:
    """
    Z-score standardization.
    """

    values = np.asarray(

        values,

        dtype=np.float64

    )

    sigma = standard_deviation(

        values,

        ddof=0

    )

    if sigma <= RiskConstants.EPSILON:

        return np.zeros_like(

            values,

            dtype=np.float64

        )

    return (

        values

        -

        mean(

            values

        )

    ) / sigma