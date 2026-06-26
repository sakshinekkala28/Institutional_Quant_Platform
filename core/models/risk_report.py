"""
====================================================================
Institutional Quant Platform

Risk Report

Author : Institutional Quant Platform

Purpose
-------
Institutional portfolio risk report.

Aggregates all portfolio risk analytics into a
single strongly typed domain model.

Used By

• Risk Engine
• Portfolio Service
• Reporting Service
• Monitoring Service
• Governance Service
• API Layer

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field


@dataclass(slots=True)
class RiskReport:
    """
    Institutional portfolio risk report.
    """

    portfolio_variance: float = 0.0

    portfolio_volatility: float = 0.0

    portfolio_beta: float = 0.0

    tracking_error: float = 0.0

    active_risk: float = 0.0

    active_return: float = 0.0

    information_ratio: float = 0.0

    sharpe_ratio: float = 0.0

    sortino_ratio: float = 0.0

    calmar_ratio: float = 0.0

    maximum_drawdown: float = 0.0

    value_at_risk: float = 0.0

    expected_shortfall: float = 0.0

    diversification_ratio: float = 0.0

    effective_holdings: float = 0.0

    concentration_ratio: float = 0.0

    factor_exposures: dict[str, float] = field(

        default_factory=dict

    )

    metadata: dict[str, str] = field(

        default_factory=dict

    )

    __hash__ = None

    # =====================================================
    # BASIC
    # =====================================================

    @property
    def is_empty(

        self

    ) -> bool:

        """
        True when no risk values are populated.
        """

        return all(

            value == 0.0

            for value in (

                self.portfolio_variance,

                self.portfolio_volatility,

                self.portfolio_beta,

                self.tracking_error,

                self.active_risk,

                self.active_return,

                self.information_ratio,

                self.sharpe_ratio,

                self.sortino_ratio,

                self.calmar_ratio,

                self.maximum_drawdown,

                self.value_at_risk,

                self.expected_shortfall

            )

        )

    @property
    def factor_count(

        self

    ) -> int:

        return len(

            self.factor_exposures

        )

    # =====================================================
    # LOOKUPS
    # =====================================================

    def factor(

        self,

        name: str

    ) -> float:

        """
        Factor exposure lookup.
        """

        return self.factor_exposures.get(

            name,

            0.0

        )

    # =====================================================
    # MODIFICATION
    # =====================================================

    def add_factor(

        self,

        name: str,

        exposure: float

    ) -> None:

        """
        Add or replace factor exposure.
        """

        self.factor_exposures[

            name

        ] = exposure

    # =====================================================
    # VALIDATION
    # =====================================================

    def validate(

        self

    ) -> None:

        """
        Validate report.
        """

        numeric_fields = (

            self.portfolio_variance,

            self.portfolio_volatility,

            self.portfolio_beta,

            self.tracking_error,

            self.active_risk,

            self.active_return,

            self.information_ratio,

            self.sharpe_ratio,

            self.sortino_ratio,

            self.calmar_ratio,

            self.maximum_drawdown,

            self.value_at_risk,

            self.expected_shortfall,

            self.diversification_ratio,

            self.effective_holdings,

            self.concentration_ratio

        )

        for value in numeric_fields:

            if not isinstance(

                value,

                (int, float)

            ):

                raise TypeError(

                    "Risk metrics must be numeric."

                )

    # =====================================================
    # EXPORT
    # =====================================================

    def to_dict(

        self

    ) -> dict:

        """
        Convert report to dictionary.
        """

        return {

            "portfolio_variance":

                self.portfolio_variance,

            "portfolio_volatility":

                self.portfolio_volatility,

            "portfolio_beta":

                self.portfolio_beta,

            "tracking_error":

                self.tracking_error,

            "active_risk":

                self.active_risk,

            "active_return":

                self.active_return,

            "information_ratio":

                self.information_ratio,

            "sharpe_ratio":

                self.sharpe_ratio,

            "sortino_ratio":

                self.sortino_ratio,

            "calmar_ratio":

                self.calmar_ratio,

            "maximum_drawdown":

                self.maximum_drawdown,

            "value_at_risk":

                self.value_at_risk,

            "expected_shortfall":

                self.expected_shortfall,

            "diversification_ratio":

                self.diversification_ratio,

            "effective_holdings":

                self.effective_holdings,

            "concentration_ratio":

                self.concentration_ratio,

            "factor_exposures":

                dict(

                    self.factor_exposures

                ),

            "metadata":

                dict(

                    self.metadata

                )

        }

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self

    ) -> dict:

        """
        Compact report summary.
        """

        return {

            "volatility":

                self.portfolio_volatility,

            "beta":

                self.portfolio_beta,

            "tracking_error":

                self.tracking_error,

            "sharpe":

                self.sharpe_ratio,

            "var":

                self.value_at_risk,

            "expected_shortfall":

                self.expected_shortfall,

            "factor_count":

                self.factor_count

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self

    ) -> str:

        return (

            f"RiskReport("

            f"volatility={self.portfolio_volatility:.4f}, "

            f"beta={self.portfolio_beta:.4f}, "

            f"tracking_error={self.tracking_error:.4f}"

            f")"

        )

    __str__ = __repr__