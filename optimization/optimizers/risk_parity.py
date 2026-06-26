"""
====================================================================
Institutional Quant Platform

Risk Parity Optimizer

Author : Institutional Quant Platform

Purpose
-------
Institutional Risk Parity Optimizer.

Objective

    Equalize risk contributions
    across all portfolio positions.

Subject To

    Σw = 1
    w ≥ 0

Inherited From

• BaseOptimizer

====================================================================
"""

from __future__ import annotations

import numpy as np

from scipy.optimize import minimize

from core.models.covariance_matrix import CovarianceMatrix
from core.models.portfolio import Portfolio

from optimization.base_optimizer import BaseOptimizer


class RiskParityOptimizer(

    BaseOptimizer

):
    """
    Institutional Risk Parity Optimizer.
    """

    def __init__(

        self,

        covariance_matrix: CovarianceMatrix,

        long_only: bool = True,

        fully_invested: bool = True,

        min_weight: float = 0.0,

        max_weight: float = 1.0,

    ) -> None:

        super().__init__(

            long_only=long_only,

            fully_invested=fully_invested,

            min_weight=min_weight,

            max_weight=max_weight,

        )

        self.covariance_matrix = covariance_matrix

    # =====================================================
    # PORTFOLIO VOLATILITY
    # =====================================================

    def portfolio_volatility(

        self,

        weights: np.ndarray,

    ) -> float:

        covariance = self.covariance_matrix.matrix

        variance = (

            weights.T

            @ covariance

            @ weights

        )

        return float(

            np.sqrt(

                variance

            )

        )

    # =====================================================
    # RISK CONTRIBUTION
    # =====================================================

    def risk_contribution(

        self,

        weights: np.ndarray,

    ) -> np.ndarray:

        covariance = self.covariance_matrix.matrix

        sigma = self.portfolio_volatility(

            weights

        )

        if sigma <= 0.0:

            return np.zeros_like(

                weights

            )

        marginal = (

            covariance

            @ weights

        ) / sigma

        return (

            weights

            * marginal

        )

    # =====================================================
    # OBJECTIVE
    # =====================================================

    def objective(

        self,

        weights: np.ndarray,

    ) -> float:

        contribution = (

            self.risk_contribution(

                weights

            )

        )

        target = np.mean(

            contribution

        )

        return float(

            np.sum(

                (

                    contribution

                    - target

                ) ** 2

            )

        )

    # =====================================================
    # OPTIMIZE
    # =====================================================

    def optimize(

        self,

        portfolio: Portfolio,

    ) -> Portfolio:

        self.validate(

            portfolio

        )

        n = len(

            portfolio

        )

        initial = np.full(

            n,

            1.0 / n,

            dtype=np.float64,

        )

        bounds = [

            (

                self.min_weight,

                self.max_weight,

            )

            for _ in range(

                n

            )

        ]

        constraints = [

            {

                "type": "eq",

                "fun":

                    lambda w:

                    np.sum(

                        w

                    )

                    - 1.0

            }

        ]

        result = minimize(

            fun=self.objective,

            x0=initial,

            method="SLSQP",

            bounds=bounds,

            constraints=constraints,

        )

        if not result.success:

            raise RuntimeError(

                f"Optimization failed: "

                f"{result.message}"

            )

        return self.build_portfolio(

            portfolio,

            result.x,

        )

    # =====================================================
    # NAME
    # =====================================================

    @property
    def name(

        self

    ) -> str:

        return "Risk Parity"

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"LongOnly={self.long_only}"

            f")"

        )

    __str__ = __repr__