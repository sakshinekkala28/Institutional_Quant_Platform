"""
====================================================================
Institutional Quant Platform

Tail Risk

Author : Institutional Quant Platform

Purpose
-------
Institutional tail risk model.

Provides

• Historical VaR
• Parametric VaR
• Conditional VaR
• Expected Shortfall
• Tail Ratio
• Worst Return
• Tail Volatility

Inherited From

• BaseRiskModel

====================================================================
"""

from __future__ import annotations

from core.math.tail import (
    conditional_var,
    expected_shortfall,
    historical_var,
    parametric_var,
    tail_ratio,
    tail_volatility,
    worst_return,
)

from core.models.risk_report import RiskReport

from core.risk.base_risk_model import BaseRiskModel


class TailRisk(

    BaseRiskModel

):
    """
    Institutional tail risk model.
    """

    # =====================================================
    # HISTORICAL VAR
    # =====================================================

    @property
    def historical_var(

        self

    ) -> float:

        return historical_var(

            self.portfolio_returns

        )

    # =====================================================
    # PARAMETRIC VAR
    # =====================================================

    @property
    def parametric_var(

        self

    ) -> float:

        return parametric_var(

            self.portfolio_returns

        )

    # =====================================================
    # CONDITIONAL VAR
    # =====================================================

    @property
    def conditional_var(

        self

    ) -> float:

        return conditional_var(

            self.portfolio_returns

        )

    # =====================================================
    # EXPECTED SHORTFALL
    # =====================================================

    @property
    def expected_shortfall(

        self

    ) -> float:

        return expected_shortfall(

            self.portfolio_returns

        )

    # =====================================================
    # TAIL RATIO
    # =====================================================

    @property
    def tail_ratio(

        self

    ) -> float:

        return tail_ratio(

            self.portfolio_returns

        )

    # =====================================================
    # WORST RETURN
    # =====================================================

    @property
    def worst_return(

        self

    ) -> float:

        return worst_return(

            self.portfolio_returns

        )

    # =====================================================
    # TAIL VOLATILITY
    # =====================================================

    @property
    def tail_volatility(

        self

    ) -> float:

        return tail_volatility(

            self.portfolio_returns

        )

    # =====================================================
    # CALCULATE
    # =====================================================

    def calculate(

        self

    ) -> RiskReport:

        report = self.create_report()

        report.historical_var = (

            self.historical_var

        )

        report.parametric_var = (

            self.parametric_var

        )

        report.conditional_var = (

            self.conditional_var

        )

        report.expected_shortfall = (

            self.expected_shortfall

        )

        report.tail_ratio = (

            self.tail_ratio

        )

        report.worst_return = (

            self.worst_return

        )

        report.tail_volatility = (

            self.tail_volatility

        )

        report.metadata.update(

            {

                "risk_model":

                    self.__class__.__name__

            }

        )

        return report

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self

    ) -> dict[str, float]:

        return {

            "historical_var":

                self.historical_var,

            "parametric_var":

                self.parametric_var,

            "conditional_var":

                self.conditional_var,

            "expected_shortfall":

                self.expected_shortfall,

            "tail_ratio":

                self.tail_ratio,

            "worst_return":

                self.worst_return,

            "tail_volatility":

                self.tail_volatility

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"HistoricalVaR={self.historical_var:.4f}, "

            f"CVaR={self.conditional_var:.4f}"

            f")"

        )

    __str__ = __repr__