"""
====================================================================
Institutional Quant Platform

Factor Risk

Author : Institutional Quant Platform

Purpose
-------
Institutional multi-factor risk model.

Provides

• Portfolio Factor Exposure
• Factor Contribution
• Factor Variance
• Specific Risk
• Systematic Risk
• Active Factor Exposure

Inherited From

• BaseRiskModel

====================================================================
"""

from __future__ import annotations

from core.models.risk_report import RiskReport

from core.risk.base_risk_model import BaseRiskModel

from core.math.factor import (
    active_factor_exposure,
    factor_contribution,
    factor_variance,
    portfolio_factor_exposure,
    specific_risk,
    systematic_risk,
)


class FactorRisk(

    BaseRiskModel

):
    """
    Institutional factor risk model.
    """

    # =====================================================
    # FACTOR EXPOSURE
    # =====================================================

    @property
    def factor_exposure(

        self

    ) -> dict[str, float]:

        return portfolio_factor_exposure(

            self.weights,

            self.factor_exposure.factor_matrix

        )

    # =====================================================
    # FACTOR CONTRIBUTION
    # =====================================================

    @property
    def factor_contribution(

        self

    ) -> dict[str, float]:

        return factor_contribution(

            self.weights,

            self.factor_exposure.factor_matrix,

            self.factor_exposure.factor_covariance

        )

    # =====================================================
    # FACTOR VARIANCE
    # =====================================================

    @property
    def factor_variance(

        self

    ) -> float:

        return factor_variance(

            self.weights,

            self.factor_exposure.factor_matrix,

            self.factor_exposure.factor_covariance

        )

    # =====================================================
    # SYSTEMATIC RISK
    # =====================================================

    @property
    def systematic_risk(

        self

    ) -> float:

        return systematic_risk(

            self.weights,

            self.factor_exposure.factor_matrix,

            self.factor_exposure.factor_covariance

        )

    # =====================================================
    # SPECIFIC RISK
    # =====================================================

    @property
    def specific_risk(

        self

    ) -> float:

        return specific_risk(

            self.weights,

            self.factor_exposure.specific_variance

        )

    # =====================================================
    # ACTIVE FACTOR EXPOSURE
    # =====================================================

    @property
    def active_factor_exposure(

        self

    ) -> dict[str, float]:

        if self.benchmark is None:

            return {}

        return active_factor_exposure(

            self.factor_exposure.factor_matrix,

            self.benchmark.factor_exposure.factor_matrix,

            self.weights,

            self.benchmark.weights

        )

    # =====================================================
    # CALCULATE
    # =====================================================

    def calculate(

        self

    ) -> RiskReport:

        report = self.create_report()

        report.factor_variance = (

            self.factor_variance

        )

        report.systematic_risk = (

            self.systematic_risk

        )

        report.specific_risk = (

            self.specific_risk

        )

        report.factor_exposure = (

            self.factor_exposure

        )

        report.factor_contribution = (

            self.factor_contribution

        )

        report.active_factor_exposure = (

            self.active_factor_exposure

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

    ) -> dict:

        return {

            "factor_variance":

                self.factor_variance,

            "systematic_risk":

                self.systematic_risk,

            "specific_risk":

                self.specific_risk

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Systematic={self.systematic_risk:.4f}, "

            f"Specific={self.specific_risk:.4f}"

            f")"

        )

    __str__ = __repr__