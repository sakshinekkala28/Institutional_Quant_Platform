"""
====================================================================
Institutional Quant Platform

Risk Service

Author : Institutional Quant Platform

Purpose
-------
Institutional risk orchestration service.

Coordinates

• Portfolio Risk
• Market Risk
• Performance Risk
• Tail Risk
• Factor Risk

Produces

• Unified Risk Report
• Risk Dashboard
• Optimizer Input
• Governance Input

====================================================================
"""

from __future__ import annotations

from core.models.asset_returns import AssetReturns
from core.models.benchmark import Benchmark
from core.models.covariance_matrix import CovarianceMatrix
from core.models.factor_exposure import FactorExposure
from core.models.portfolio import Portfolio

from core.risk.factor_risk import FactorRisk
from core.risk.market_risk import MarketRisk
from core.risk.performance_risk import PerformanceRisk
from core.risk.portfolio_risk import PortfolioRisk
from core.risk.risk_metrics import RiskMetrics
from core.risk.tail_risk import TailRisk


class RiskService:
    """
    Institutional Risk Service.
    """

    def __init__(

        self,

        portfolio: Portfolio,

        asset_returns: AssetReturns,

        covariance_matrix: CovarianceMatrix,

        benchmark: Benchmark | None = None,

        factor_exposure: FactorExposure | None = None,

    ) -> None:

        self.portfolio = portfolio

        self.asset_returns = asset_returns

        self.covariance_matrix = covariance_matrix

        self.benchmark = benchmark

        self.factor_exposure = factor_exposure

    # =====================================================
    # BUILD MODELS
    # =====================================================

    def build(

        self

    ) -> RiskMetrics:

        portfolio_risk = PortfolioRisk(

            portfolio=self.portfolio,

            asset_returns=self.asset_returns,

            covariance_matrix=self.covariance_matrix,

            benchmark=self.benchmark,

            factor_exposure=self.factor_exposure,

        )

        market_risk = MarketRisk(

            portfolio=self.portfolio,

            asset_returns=self.asset_returns,

            covariance_matrix=self.covariance_matrix,

            benchmark=self.benchmark,

            factor_exposure=self.factor_exposure,

        )

        performance_risk = PerformanceRisk(

            portfolio=self.portfolio,

            asset_returns=self.asset_returns,

            covariance_matrix=self.covariance_matrix,

            benchmark=self.benchmark,

            factor_exposure=self.factor_exposure,

        )

        tail_risk = TailRisk(

            portfolio=self.portfolio,

            asset_returns=self.asset_returns,

            covariance_matrix=self.covariance_matrix,

            benchmark=self.benchmark,

            factor_exposure=self.factor_exposure,

        )

        factor_risk = FactorRisk(

            portfolio=self.portfolio,

            asset_returns=self.asset_returns,

            covariance_matrix=self.covariance_matrix,

            benchmark=self.benchmark,

            factor_exposure=self.factor_exposure,

        )

        return RiskMetrics(

            portfolio_risk=portfolio_risk,

            market_risk=market_risk,

            performance_risk=performance_risk,

            tail_risk=tail_risk,

            factor_risk=factor_risk,

        )

    # =====================================================
    # CALCULATE
    # =====================================================

    def calculate(

        self,

    ) -> dict:

        return self.build().calculate()

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self,

    ) -> dict:

        return self.build().summary()

    # =====================================================
    # DASHBOARD
    # =====================================================

    def dashboard(

        self,

    ) -> dict:

        metrics = self.build()

        return {

            "portfolio":

                metrics.portfolio.summary(),

            "market":

                metrics.market.summary(),

            "performance":

                metrics.performance.summary(),

            "tail":

                metrics.tail.summary(),

            "factor":

                metrics.factor.summary(),

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Portfolio={self.portfolio.holdings}, "

            f"Models=5"

            f")"

        )

    __str__ = __repr__