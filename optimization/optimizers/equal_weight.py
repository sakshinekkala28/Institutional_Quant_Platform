"""
====================================================================
Institutional Quant Platform

Equal Weight Optimizer

Author : Institutional Quant Platform

Purpose
-------
Institutional equal-weight optimizer.

Produces

• Equal-weight portfolio

Inherited From

• BaseOptimizer

====================================================================
"""

from __future__ import annotations

import numpy as np

from core.models.portfolio import Portfolio

from optimization.base_optimizer import BaseOptimizer


class EqualWeightOptimizer(

    BaseOptimizer

):
    """
    Equal-weight portfolio optimizer.
    """

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

        if holdings == 0:

            raise ValueError(

                "Portfolio is empty."

            )

        weights = np.full(

            holdings,

            1.0 / holdings,

            dtype=np.float64,

        )

        return self.build_portfolio(

            portfolio,

            weights,

        )

    # =====================================================
    # NAME
    # =====================================================

    @property
    def name(

        self,

    ) -> str:

        return "Equal Weight"

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Equal Weight"

            f")"

        )

    __str__ = __repr__