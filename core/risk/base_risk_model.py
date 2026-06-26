"""
====================================================================
Institutional Quant Platform

Base Risk Model

Author : Institutional Quant Platform

Purpose
-------
Abstract base class for all institutional
risk models.

Provides

• Common validation
• Common metadata
• Portfolio validation
• Report creation
• Logging hooks
• Execution contract

Inherited By

• PortfolioRisk
• MarketRisk
• PerformanceRisk
• TailRisk
• FactorRisk

====================================================================
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from core.models.asset_returns import AssetReturns
from core.models.benchmark import Benchmark
from core.models.covariance_matrix import CovarianceMatrix
from core.models.factor_exposure import FactorExposure
from core.models.portfolio import Portfolio
from core.models.risk_report import RiskReport

import numpy as np

from core.math.returns import (
    portfolio_returns
)

class BaseRiskModel(ABC):
    """
    Abstract institutional risk model.
    """

    def __init__(

        self,

        portfolio: Portfolio,

        asset_returns: AssetReturns,

        covariance_matrix: CovarianceMatrix,

        benchmark: Benchmark | None = None,

        factor_exposure: FactorExposure | None = None

    ) -> None:

        self._portfolio = portfolio

        self._asset_returns = asset_returns

        self._covariance_matrix = covariance_matrix

        self._benchmark = benchmark

        self._factor_exposure = factor_exposure

        self.validate()

    # =====================================================
    # PROPERTIES
    # =====================================================

    @property
    def portfolio(

        self

    ) -> Portfolio:

        return self._portfolio

    @property
    def asset_returns(

        self

    ) -> AssetReturns:

        return self._asset_returns

    @property
    def covariance_matrix(

        self

    ) -> CovarianceMatrix:

        return self._covariance_matrix

    @property
    def benchmark(

        self

    ) -> Benchmark | None:

        return self._benchmark

    @property
    def factor_exposure(

        self

    ) -> FactorExposure | None:

        return self._factor_exposure

    # =====================================================
    # VALIDATION
    # =====================================================

    def validate(

        self

    ) -> None:

        """
        Validate all dependencies.
        """

        if self.portfolio.is_empty:

            raise ValueError(

                "Portfolio cannot be empty."

            )

        self.asset_returns.validate()

        self.covariance_matrix.validate()

        if self.benchmark is not None:

            self.benchmark.validate()

        if self.factor_exposure is not None:

            self.factor_exposure.validate()

    # =====================================================
    # UTILITIES
    # =====================================================

    @property
    def weights(

        self

    ) -> np.ndarray:

        """
        Portfolio weights.
        """

        return np.asarray(

            [

                position.weight

                for position

                in self.portfolio

            ],

            dtype=np.float64

        )

    @property
    def symbols(

        self

    ) -> list[str]:

        return self.portfolio.symbols()

    @property
    def holdings(

        self

    ) -> int:

        return self.portfolio.holdings
    
    # =====================================================
    # RETURN MATRIX
    # =====================================================

    @property
    def return_matrix(

        self

    ) -> np.ndarray:
        """
        Asset return matrix.

        Shape:
            (Assets × Observations)
        """

        return self.asset_returns.matrix
    
    # =====================================================
    # PORTFOLIO RETURNS
    # =====================================================

    @property
    def portfolio_returns(

        self

    ) -> np.ndarray:
        """
        Weighted portfolio return series.
        """

        return portfolio_returns(

            self.weights,

            self.return_matrix

        )
    
    # =====================================================
    # BENCHMARK RETURNS
    # =====================================================

    @property
    def benchmark_returns(

        self

    ):

        if self.benchmark is None:

            return None

        return self.benchmark.return_series
    
    # =====================================================
    # RISK FREE RATE
    # =====================================================

    @property
    def risk_free_rate(

        self

    ) -> float:

        if self.benchmark is None:

            return 0.0

        return self.benchmark.risk_free_rate
    
    # =====================================================
    # REPORT
    # =====================================================

    def create_report(

        self

    ) -> RiskReport:

        """
        Create an empty institutional risk report.
        """

        return RiskReport()

    # =====================================================
    # EXECUTION
    # =====================================================

    @abstractmethod
    def calculate(

        self

    ) -> RiskReport:

        """
        Calculate risk model.
        """

        raise NotImplementedError