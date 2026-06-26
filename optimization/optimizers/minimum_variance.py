"""
====================================================================
Institutional Quant Platform

Minimum Variance Optimizer

Author : Institutional Quant Platform

Purpose
-------
Institutional minimum variance optimizer.

Objective

    Minimize

        wᵀΣw

Subject To

    Σw = 1
    w ≥ 0 (Long Only)

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


class MinimumVarianceOptimizer(

    BaseOptimizer

):
    """
    Institutional minimum variance optimizer.
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
    # OBJECTIVE
    # =====================================================

    def objective(

        self,

        weights: np.ndarray,

    ) -> float:

        covariance = self.covariance_matrix.matrix

        return float(

            weights.T

            @ covariance

            @ weights

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

        holdings = len(

            portfolio

        )

        initial = np.full(

            holdings,

            1.0 / holdings,

            dtype=np.float64,

        )

        bounds = [

            (

                self.min_weight,

                self.max_weight,

            )

            for _ in range(

                holdings

            )

        ]

        constraints = [

            {

                "type": "eq",

                "fun":

                    lambda w: np.sum(

                        w

                    ) - 1.0,

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

        self,

    ) -> str:

        return "Minimum Variance"

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"LongOnly={self.long_only}"

            f")"

        )

    __str__ = __repr__