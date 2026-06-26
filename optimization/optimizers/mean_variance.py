"""
====================================================================
Institutional Quant Platform

Mean Variance Optimizer

Author : Institutional Quant Platform

Purpose
-------
Institutional Markowitz Mean-Variance Optimizer.

Objective

    Maximize

        μᵀw − λ wᵀΣw

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
from core.models.expected_returns import ExpectedReturns
from core.models.portfolio import Portfolio

from optimization.base_optimizer import BaseOptimizer


class MeanVarianceOptimizer(

    BaseOptimizer

):

    """
    Institutional Mean-Variance Optimizer.
    """

    def __init__(

        self,

        covariance_matrix: CovarianceMatrix,

        expected_returns: ExpectedReturns,

        risk_aversion: float = 1.0,

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

        self.expected_returns = expected_returns

        self.risk_aversion = risk_aversion

    # =====================================================
    # OBJECTIVE
    # =====================================================

    def objective(

        self,

        weights: np.ndarray,

    ) -> float:

        covariance = self.covariance_matrix.matrix

        expected = self.expected_returns.values

        portfolio_return = float(

            weights @ expected

        )

        portfolio_variance = float(

            weights.T

            @ covariance

            @ weights

        )

        utility = (

            portfolio_return

            -

            self.risk_aversion

            * portfolio_variance

        )

        return -utility

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

                result.message

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

        return "Mean Variance"

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Lambda={self.risk_aversion:.2f}"

            f")"

        )

    __str__ = __repr__