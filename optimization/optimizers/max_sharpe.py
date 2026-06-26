"""
====================================================================
Institutional Quant Platform

Maximum Sharpe Optimizer

Author : Institutional Quant Platform

Purpose
-------
Institutional maximum Sharpe ratio optimizer.

Objective

    Maximize

        (Rp - Rf) / σ

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


class MaximumSharpeOptimizer(

    BaseOptimizer

):
    """
    Institutional Maximum Sharpe Optimizer.
    """

    def __init__(

        self,

        covariance_matrix: CovarianceMatrix,

        expected_returns: ExpectedReturns,

        risk_free_rate: float = 0.0,

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

        self.risk_free_rate = risk_free_rate

    # =====================================================
    # OBJECTIVE
    # =====================================================

    def objective(

        self,

        weights: np.ndarray,

    ) -> float:

        covariance = self.covariance_matrix.matrix

        mu = self.expected_returns.values

        portfolio_return = float(

            weights @ mu

        )

        portfolio_variance = float(

            weights.T

            @ covariance

            @ weights

        )

        portfolio_volatility = np.sqrt(

            portfolio_variance

        )

        if portfolio_volatility <= 0.0:

            return 1e9

        sharpe = (

            portfolio_return

            - self.risk_free_rate

        ) / portfolio_volatility

        return -sharpe

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

                "fun": lambda w:

                    np.sum(

                        w

                    ) - 1.0

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

        return "Maximum Sharpe"

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"RiskFree={self.risk_free_rate:.2%}"

            f")"

        )

    __str__ = __repr__