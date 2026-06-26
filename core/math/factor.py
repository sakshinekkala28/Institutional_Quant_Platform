"""
====================================================================
Institutional Quant Platform

Factor Mathematics

Author : Institutional Quant Platform

Purpose
-------
Institutional factor model mathematics.

Provides

• Portfolio Factor Exposure
• Active Factor Exposure
• Factor Variance
• Systematic Risk
• Specific Risk
• Total Risk
• Factor Contribution

Used By

• FactorRisk
• Optimizer
• Attribution
• Risk Budgeting

====================================================================
"""

from __future__ import annotations

import numpy as np

from core.constants import RiskConstants


# ==========================================================
# VALIDATION
# ==========================================================

def validate_factor_matrix(

    factor_matrix: np.ndarray

) -> np.ndarray:

    factor_matrix = np.asarray(

        factor_matrix,

        dtype=np.float64

    )

    if factor_matrix.ndim != 2:

        raise ValueError(

            "Factor matrix must be two-dimensional."

        )

    return factor_matrix


# ==========================================================
# PORTFOLIO FACTOR EXPOSURE
# ==========================================================

def portfolio_factor_exposure(

    weights: np.ndarray,

    factor_matrix: np.ndarray,

    factor_names: list[str] | None = None

) -> dict[str, float]:

    weights = np.asarray(

        weights,

        dtype=np.float64

    )

    factor_matrix = validate_factor_matrix(

        factor_matrix

    )

    if weights.size != factor_matrix.shape[0]:

        raise ValueError(

            "Weights and factor matrix dimensions differ."

        )

    exposures = (

        weights

        @ factor_matrix

    )

    if factor_names is None:

        factor_names = [

            f"Factor_{i+1}"

            for i

            in range(

                factor_matrix.shape[1]

            )

        ]

    return {

        name: float(value)

        for name, value

        in zip(

            factor_names,

            exposures,

            strict=True

        )

    }


# ==========================================================
# ACTIVE FACTOR EXPOSURE
# ==========================================================

def active_factor_exposure(

    portfolio_factor_matrix: np.ndarray,

    benchmark_factor_matrix: np.ndarray,

    portfolio_weights: np.ndarray,

    benchmark_weights: np.ndarray,

    factor_names: list[str] | None = None

) -> dict[str, float]:

    portfolio = portfolio_factor_exposure(

        portfolio_weights,

        portfolio_factor_matrix,

        factor_names

    )

    benchmark = portfolio_factor_exposure(

        benchmark_weights,

        benchmark_factor_matrix,

        factor_names

    )

    return {

        factor:

        portfolio[factor]

        -

        benchmark[factor]

        for factor

        in portfolio

    }


# ==========================================================
# FACTOR VARIANCE
# ==========================================================

def factor_variance(

    weights: np.ndarray,

    factor_matrix: np.ndarray,

    factor_covariance: np.ndarray

) -> float:

    weights = np.asarray(

        weights,

        dtype=np.float64

    )

    factor_matrix = validate_factor_matrix(

        factor_matrix

    )

    factor_covariance = np.asarray(

        factor_covariance,

        dtype=np.float64

    )

    exposure = (

        weights

        @ factor_matrix

    )

    return float(

        exposure

        @ factor_covariance

        @ exposure.T

    )


# ==========================================================
# SYSTEMATIC RISK
# ==========================================================

def systematic_risk(

    weights: np.ndarray,

    factor_matrix: np.ndarray,

    factor_covariance: np.ndarray

) -> float:

    variance = factor_variance(

        weights,

        factor_matrix,

        factor_covariance

    )

    if variance <= RiskConstants.MIN_VARIANCE:

        return 0.0

    return float(

        np.sqrt(

            variance

        )

    )


# ==========================================================
# SPECIFIC RISK
# ==========================================================

def specific_risk(

    weights: np.ndarray,

    specific_variance: np.ndarray

) -> float:

    weights = np.asarray(

        weights,

        dtype=np.float64

    )

    specific_variance = np.asarray(

        specific_variance,

        dtype=np.float64

    )

    variance = float(

        np.sum(

            (weights ** 2)

            *

            specific_variance

        )

    )

    if variance <= RiskConstants.MIN_VARIANCE:

        return 0.0

    return float(

        np.sqrt(

            variance

        )

    )


# ==========================================================
# TOTAL RISK
# ==========================================================

def total_risk(

    weights: np.ndarray,

    factor_matrix: np.ndarray,

    factor_covariance: np.ndarray,

    specific_variance: np.ndarray

) -> float:

    systematic = systematic_risk(

        weights,

        factor_matrix,

        factor_covariance

    )

    specific = specific_risk(

        weights,

        specific_variance

    )

    return float(

        np.sqrt(

            systematic ** 2

            +

            specific ** 2

        )

    )


# ==========================================================
# FACTOR CONTRIBUTION
# ==========================================================

def factor_contribution(

    weights: np.ndarray,

    factor_matrix: np.ndarray,

    factor_covariance: np.ndarray,

    factor_names: list[str] | None = None

) -> dict[str, float]:

    weights = np.asarray(

        weights,

        dtype=np.float64

    )

    factor_matrix = validate_factor_matrix(

        factor_matrix

    )

    factor_covariance = np.asarray(

        factor_covariance,

        dtype=np.float64

    )

    exposure = (

        weights

        @ factor_matrix

    )

    contribution = (

        exposure

        *

        (

            factor_covariance

            @ exposure

        )

    )

    if factor_names is None:

        factor_names = [

            f"Factor_{i+1}"

            for i

            in range(

                contribution.size

            )

        ]

    return {

        name: float(value)

        for name, value

        in zip(

            factor_names,

            contribution,

            strict=True

        )

    }