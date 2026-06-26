"""
====================================================================
Institutional Quant Platform

Base Optimizer

Author : Institutional Quant Platform

Purpose
-------
Abstract base class for all portfolio optimizers.

Provides

• Validation
• Optimization Contract
• Portfolio Construction
• Weight Validation

Inherited By

• EqualWeightOptimizer
• MinimumVarianceOptimizer
• MeanVarianceOptimizer
• MaximumSharpeOptimizer
• RiskParityOptimizer
• HRPOptimizer
• BlackLittermanOptimizer

====================================================================
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

import numpy as np

from core.models.portfolio import Portfolio
from core.models.portfolio_position import PortfolioPosition


class BaseOptimizer(ABC):
    """
    Institutional optimizer base class.
    """

    def __init__(

        self,

        long_only: bool = True,

        fully_invested: bool = True,

        max_weight: float = 1.0,

        min_weight: float = 0.0,

    ) -> None:

        self.long_only = long_only

        self.fully_invested = fully_invested

        self.max_weight = max_weight

        self.min_weight = min_weight

    # =====================================================
    # VALIDATION
    # =====================================================

    def validate(

        self,

        portfolio: Portfolio,

    ) -> None:

        if portfolio.is_empty:

            raise ValueError(

                "Portfolio cannot be empty."

            )

    # =====================================================
    # NORMALIZE
    # =====================================================

    def normalize(

        self,

        weights: np.ndarray,

    ) -> np.ndarray:

        weights = np.asarray(

            weights,

            dtype=np.float64,

        )

        total = weights.sum()

        if total <= 0:

            raise ValueError(

                "Weight sum must be positive."

            )

        return weights / total

    # =====================================================
    # CLIP
    # =====================================================

    def clip(

        self,

        weights: np.ndarray,

    ) -> np.ndarray:

        return np.clip(

            weights,

            self.min_weight,

            self.max_weight,

        )

    # =====================================================
    # BUILD PORTFOLIO
    # =====================================================

    def build_portfolio(

        self,

        portfolio: Portfolio,

        weights: np.ndarray,

    ) -> Portfolio:

        weights = self.normalize(

            self.clip(

                weights

            )

        )

        positions = []

        for position, weight in zip(

            portfolio,

            weights,

            strict=True,

        ):

            positions.append(

                PortfolioPosition(

                    symbol=position.symbol,

                    weight=float(weight),

                    sector=position.sector,

                    industry=position.industry,

                    alpha=position.alpha,

                    alpha_adjusted=position.alpha_adjusted,

                    market_cap=position.market_cap,

                    adv_20d=position.adv_20d,

                )

            )

        return Portfolio(

            positions=positions,

            nav=portfolio.nav,

        )

    # =====================================================
    # OPTIMIZATION CONTRACT
    # =====================================================

    @abstractmethod
    def optimize(

        self,

        portfolio: Portfolio,

    ) -> Portfolio:
        """
        Execute optimizer.
        """

        raise NotImplementedError

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"LongOnly={self.long_only}, "

            f"FullyInvested={self.fully_invested}"

            f")"

        )

    __str__ = __repr__