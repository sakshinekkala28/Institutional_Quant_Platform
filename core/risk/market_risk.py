"""
====================================================================
Institutional Quant Platform

Market Risk

Author : Institutional Quant Platform

Purpose
-------
Institutional market-relative risk model.

Provides

• Portfolio Beta
• Portfolio Alpha
• Active Return
• Tracking Error
• Information Ratio

Inherited From

• BaseRiskModel

====================================================================
"""

from __future__ import annotations

from core.math.market import (
    active_return,
    alpha,
    beta,
    information_ratio,
    tracking_error,
)

from core.models.risk_report import RiskReport

from core.risk.base_risk_model import BaseRiskModel


class MarketRisk(

    BaseRiskModel

):
    """
    Institutional market risk model.
    """

    # =====================================================
    # BETA
    # =====================================================

    @property
    def beta(

        self

    ) -> float:

        return beta(

            self.portfolio_returns,

            self.benchmark_returns

        )

    # =====================================================
    # ALPHA
    # =====================================================

    @property
    def alpha(

        self

    ) -> float:

        return alpha(

            self.portfolio_returns,

            self.benchmark_returns,

            self.risk_free_rate

        )

    # =====================================================
    # ACTIVE RETURN
    # =====================================================

    @property
    def active_return(

        self

    ) -> float:

        return active_return(

            self.portfolio_returns,

            self.benchmark_returns

        )

    # =====================================================
    # TRACKING ERROR
    # =====================================================

    @property
    def tracking_error(

        self

    ) -> float:

        return tracking_error(

            self.portfolio_returns,

            self.benchmark_returns

        )

    # =====================================================
    # INFORMATION RATIO
    # =====================================================

    @property
    def information_ratio(

        self

    ) -> float:

        return information_ratio(

            self.portfolio_returns,

            self.benchmark_returns

        )

    # =====================================================
    # CALCULATE
    # =====================================================

    def calculate(

        self

    ) -> RiskReport:

        report = self.create_report()

        report.portfolio_beta = (

            self.beta

        )

        report.portfolio_alpha = (

            self.alpha

        )

        report.active_return = (

            self.active_return

        )

        report.tracking_error = (

            self.tracking_error

        )

        report.information_ratio = (

            self.information_ratio

        )

        report.metadata.update(

            {

                "risk_model":

                    self.__class__.__name__

            }

        )

        return report