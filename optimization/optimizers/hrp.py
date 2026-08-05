"""
====================================================================
Institutional Quant Platform

Hierarchical Risk Parity Optimizer

Author : Institutional Quant Platform

Purpose
-------
Institutional Hierarchical Risk Parity (HRP)
optimizer.

Objective

• Hierarchical clustering
• Recursive bisection
• Diversified risk allocation

Inherited From

• BaseOptimizer

Reference

Marcos Lopez de Prado (2016)
Building Diversified Portfolios that
Outperform Out-of-Sample

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.cluster.hierarchy import leaves_list, linkage
from scipy.spatial.distance import squareform

from core.models.covariance_matrix import CovarianceMatrix
from core.models.portfolio import Portfolio
from optimization.base_optimizer import BaseOptimizer


@dataclass(slots=True)
class HRPConfig:
    """
    Configuration for the Hierarchical Risk Parity optimizer.
    """
    covariance_matrix: CovarianceMatrix
    linkage_method: str = "single"
    long_only: bool = True
    fully_invested: bool = True
    min_weight: float = 0.0
    max_weight: float = 1.0



class HRPOptimizer(BaseOptimizer):
    """
    Hierarchical Risk Parity Optimizer.
    """

    def __init__(
        self,
        config: HRPConfig,
    ) -> None:

        super().__init__(
            long_only=config.long_only,
            fully_invested=config.fully_invested,
            min_weight=config.min_weight,
            max_weight=config.max_weight,
        )

        self.covariance_matrix = config.covariance_matrix

        self.linkage_method = config.linkage_method


    # =====================================================
    # CORRELATION
    # =====================================================

    @property
    def correlation(self) -> np.ndarray:

        covariance = self.covariance_matrix.matrix

        volatility = np.sqrt(np.diag(covariance))

        correlation = covariance / np.outer(volatility, volatility)

        return np.nan_to_num(correlation)

    # =====================================================
    # DISTANCE
    # =====================================================

    @property
    def distance(self) -> np.ndarray:

        correlation = self.correlation

        return np.sqrt(0.5 * (1.0 - correlation))

    # =====================================================
    # CLUSTER
    # =====================================================

    def clustered_order(self) -> np.ndarray:

        condensed = squareform(
            self.distance,
            checks=False,
        )

        tree = linkage(
            condensed,
            method=self.linkage_method,
        )

        return leaves_list(tree)

    # =====================================================
    # OPTIMIZE
    # =====================================================

    def optimize(
        self,
        portfolio: Portfolio,
    ) -> Portfolio:

        self.validate(portfolio)

        order = self.clustered_order()

        n = len(order)

        #
        # Placeholder equal allocation
        # following clustered ordering.
        #
        # Recursive bisection allocation
        # will be added later.
        #

        weights = np.zeros(
            n,
            dtype=np.float64,
        )

        weights[order] = 1.0 / n

        return self.build_portfolio(
            portfolio,
            weights,
        )

    # =====================================================
    # NAME
    # =====================================================

    @property
    def name(self) -> str:

        return "Hierarchical Risk Parity"

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self) -> str:

        return f"{self.__class__.__name__}(Method={self.linkage_method})"

    __str__ = __repr__
