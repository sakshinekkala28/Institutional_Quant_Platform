"""
====================================================================
Institutional Quant Platform

Performance Risk

Author : Institutional Quant Platform

Purpose
-------
Institutional performance risk model.

Provides

• Sharpe Ratio
• Sortino Ratio
• Treynor Ratio
• Information Ratio
• Calmar Ratio
• Omega Ratio
• Gain/Loss Ratio
• Maximum Drawdown
• Average Drawdown
• Drawdown Duration
• Recovery Period
• Upside Capture
• Downside Capture

Inherited From

• BaseRiskModel

====================================================================
"""

from __future__ import annotations

from core.math.drawdown import (
    average_drawdown,
    drawdown_duration,
    maximum_drawdown,
    recovery_period,
)

from core.math.performance import (
    calmar_ratio,
    downside_capture_ratio,
    gain_loss_ratio,
    information_ratio,
    omega_ratio,
    sharpe_ratio,
    sortino_ratio,
    treynor_ratio,
    upside_capture_ratio,
)

from core.models.risk_report import RiskReport

from core.risk.base_risk_model import BaseRiskModel


class PerformanceRisk(

    BaseRiskModel

):
    """
    Institutional performance risk model.
    """

    # =====================================================
    # SHARPE
    # =====================================================

    @property
    def sharpe_ratio(

        self

    ) -> float:

        return sharpe_ratio(

            self.portfolio_returns,

            self.risk_free_rate

        )

    # =====================================================
    # SORTINO
    # =====================================================

    @property
    def sortino_ratio(

        self

    ) -> float:

        return sortino_ratio(

            self.portfolio_returns,

            self.risk_free_rate

        )

    # =====================================================
    # TREYNOR
    # =====================================================

    @property
    def treynor_ratio(

        self

    ) -> float:

        return treynor_ratio(

            self.portfolio_returns,

            self.benchmark_returns,

            self.risk_free_rate

        )

    # =====================================================
    # INFORMATION
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
    # CALMAR
    # =====================================================

    @property
    def calmar_ratio(

        self

    ) -> float:

        return calmar_ratio(

            self.portfolio_returns

        )

    # =====================================================
    # OMEGA
    # =====================================================

    @property
    def omega_ratio(

        self

    ) -> float:

        return omega_ratio(

            self.portfolio_returns

        )

    # =====================================================
    # GAIN / LOSS
    # =====================================================

    @property
    def gain_loss_ratio(

        self

    ) -> float:

        return gain_loss_ratio(

            self.portfolio_returns

        )

    # =====================================================
    # MAXIMUM DRAWDOWN
    # =====================================================

    @property
    def maximum_drawdown(

        self

    ) -> float:

        return maximum_drawdown(

            self.portfolio_returns

        )

    # =====================================================
    # AVERAGE DRAWDOWN
    # =====================================================

    @property
    def average_drawdown(

        self

    ) -> float:

        return average_drawdown(

            self.portfolio_returns

        )

    # =====================================================
    # DRAWDOWN DURATION
    # =====================================================

    @property
    def drawdown_duration(

        self

    ) -> int:

        return drawdown_duration(

            self.portfolio_returns

        )

    # =====================================================
    # RECOVERY PERIOD
    # =====================================================

    @property
    def recovery_period(

        self

    ) -> int:

        return recovery_period(

            self.portfolio_returns

        )

    # =====================================================
    # UPSIDE CAPTURE
    # =====================================================

    @property
    def upside_capture_ratio(

        self

    ) -> float:

        return upside_capture_ratio(

            self.portfolio_returns,

            self.benchmark_returns

        )

    # =====================================================
    # DOWNSIDE CAPTURE
    # =====================================================

    @property
    def downside_capture_ratio(

        self

    ) -> float:

        return downside_capture_ratio(

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

        report.sharpe_ratio = self.sharpe_ratio

        report.sortino_ratio = self.sortino_ratio

        report.treynor_ratio = self.treynor_ratio

        report.information_ratio = (

            self.information_ratio

        )

        report.calmar_ratio = (

            self.calmar_ratio

        )

        report.omega_ratio = (

            self.omega_ratio

        )

        report.gain_loss_ratio = (

            self.gain_loss_ratio

        )

        report.maximum_drawdown = (

            self.maximum_drawdown

        )

        report.average_drawdown = (

            self.average_drawdown

        )

        report.drawdown_duration = (

            self.drawdown_duration

        )

        report.recovery_period = (

            self.recovery_period

        )

        report.upside_capture_ratio = (

            self.upside_capture_ratio

        )

        report.downside_capture_ratio = (

            self.downside_capture_ratio

        )

        report.metadata.update(

            {

                "risk_model":

                    self.__class__.__name__

            }

        )

        return report