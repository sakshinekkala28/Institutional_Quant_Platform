"""
====================================================================
Institutional Quant Platform

Risk Metrics

Author : Institutional Quant Platform

Purpose
-------
Institutional risk aggregation layer.

Aggregates all risk models into a single
risk snapshot.

Provides

• Portfolio Risk
• Market Risk
• Performance Risk
• Tail Risk
• Factor Risk

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from core.models.risk_report import RiskReport

from core.risk.factor_risk import FactorRisk
from core.risk.market_risk import MarketRisk
from core.risk.performance_risk import PerformanceRisk
from core.risk.portfolio_risk import PortfolioRisk
from core.risk.tail_risk import TailRisk


@dataclass(slots=True)
class RiskMetrics:
    """
    Institutional risk aggregation.
    """

    portfolio_risk: PortfolioRisk

    market_risk: MarketRisk

    performance_risk: PerformanceRisk

    tail_risk: TailRisk

    factor_risk: FactorRisk

    # =====================================================
    # REPORTS
    # =====================================================

    @property
    def portfolio(

        self

    ) -> RiskReport:

        return self.portfolio_risk.calculate()

    @property
    def market(

        self

    ) -> RiskReport:

        return self.market_risk.calculate()

    @property
    def performance(

        self

    ) -> RiskReport:

        return self.performance_risk.calculate()

    @property
    def tail(

        self

    ) -> RiskReport:

        return self.tail_risk.calculate()

    @property
    def factor(

        self

    ) -> RiskReport:

        return self.factor_risk.calculate()

    # =====================================================
    # COMPLETE REPORT
    # =====================================================

    def calculate(

        self

    ) -> dict[str, RiskReport]:

        return {

            "portfolio":

                self.portfolio,

            "market":

                self.market,

            "performance":

                self.performance,

            "tail":

                self.tail,

            "factor":

                self.factor,

        }

    # =====================================================
    # FLAT SUMMARY
    # =====================================================

    def summary(

        self

    ) -> dict:

        return {

            "portfolio":

                self.portfolio.summary(),

            "market":

                self.market.summary(),

            "performance":

                self.performance.summary(),

            "tail":

                self.tail.summary(),

            "factor":

                self.factor.summary(),

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Portfolio=True, "

            f"Market=True, "

            f"Performance=True, "

            f"Tail=True, "

            f"Factor=True"

            f")"

        )

    __str__ = __repr__