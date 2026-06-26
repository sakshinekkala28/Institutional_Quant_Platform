"""
====================================================================
Institutional Quant Platform

Portfolio Risk

Author : Institutional Quant Platform

Purpose
-------
Portfolio mathematical risk model.

Provides

• Portfolio Variance
• Portfolio Volatility
• Marginal Risk
• Component Risk
• Risk Contributions
• Diversification Ratio
• Effective Holdings

Inherited From

• BaseRiskModel

====================================================================
"""

from __future__ import annotations

from core.math.covariance import (
    component_risk,
    diversification_ratio,
    effective_holdings,
    marginal_risk,
    portfolio_variance,
    portfolio_volatility,
    risk_contribution,
)

from core.models.risk_report import RiskReport

from core.risk.base_risk_model import BaseRiskModel


class PortfolioRisk(

    BaseRiskModel

):
    """
    Institutional portfolio risk model.
    """

    # =====================================================
    # INTERNAL
    # =====================================================

    @property
    def covariance(

        self

    ):

        """
        Covariance matrix.
        """

        return self.covariance_matrix.matrix

    # =====================================================
    # PORTFOLIO VARIANCE
    # =====================================================

    @property
    def portfolio_variance(

        self

    ) -> float:

        return portfolio_variance(

            self.weights,

            self.covariance

        )

    # =====================================================
    # PORTFOLIO VOLATILITY
    # =====================================================

    @property
    def portfolio_volatility(

        self

    ) -> float:

        return portfolio_volatility(

            self.weights,

            self.covariance

        )

    # =====================================================
    # MARGINAL RISK
    # =====================================================

    @property
    def marginal_risk(

        self

    ) -> dict[str, float]:

        values = marginal_risk(

            self.weights,

            self.covariance

        )

        return {

            symbol: float(value)

            for symbol, value

            in zip(

                self.symbols,

                values,

                strict=True

            )

        }

    # =====================================================
    # COMPONENT RISK
    # =====================================================

    @property
    def component_risk(

        self

    ) -> dict[str, float]:

        values = component_risk(

            self.weights,

            self.covariance

        )

        return {

            symbol: float(value)

            for symbol, value

            in zip(

                self.symbols,

                values,

                strict=True

            )

        }

    # =====================================================
    # RISK CONTRIBUTION
    # =====================================================

    @property
    def risk_contribution(

        self

    ) -> dict[str, float]:

        values = risk_contribution(

            self.weights,

            self.covariance

        )

        return {

            symbol: float(value)

            for symbol, value

            in zip(

                self.symbols,

                values,

                strict=True

            )

        }

    # =====================================================
    # DIVERSIFICATION RATIO
    # =====================================================

    @property
    def diversification_ratio(

        self

    ) -> float:

        return diversification_ratio(

            self.weights,

            self.covariance

        )

    # =====================================================
    # EFFECTIVE HOLDINGS
    # =====================================================

    @property
    def effective_holdings(

        self

    ) -> float:

        return effective_holdings(

            self.weights

        )

    # =====================================================
    # CALCULATE
    # =====================================================

    def calculate(

        self

    ) -> RiskReport:

        report = self.create_report()

        report.portfolio_variance = (

            self.portfolio_variance

        )

        report.portfolio_volatility = (

            self.portfolio_volatility

        )

        report.diversification_ratio = (

            self.diversification_ratio

        )

        report.effective_holdings = (

            self.effective_holdings

        )

        report.metadata.update(

            {

                "risk_model":

                    self.__class__.__name__

            }

        )

        return report

