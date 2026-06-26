"""
====================================================================
Institutional Quant Platform

Optimization Report

Author : Institutional Quant Platform

Purpose
-------
Institutional optimization report.

Produced By

• Equal Weight Optimizer
• Mean Variance Optimizer
• Risk Parity Optimizer
• HRP Optimizer
• Black-Litterman Optimizer
• Maximum Sharpe Optimizer

Consumed By

• Optimization Service
• Reporting Service
• Dashboard
• Governance

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from core.models.portfolio import Portfolio


@dataclass(slots=True)
class OptimizationReport:
    """
    Institutional optimization report.
    """

    original_portfolio: Portfolio | None = None

    optimized_portfolio: Portfolio | None = None

    optimizer_name: str = ""

    objective_value: float = 0.0

    expected_return: float = 0.0

    expected_risk: float = 0.0

    expected_volatility: float = 0.0

    expected_sharpe: float = 0.0

    turnover: float = 0.0

    tracking_error: float = 0.0

    diversification_ratio: float = 0.0

    optimization_time: float = 0.0

    converged: bool = True

    iterations: int = 0

    metadata: dict = field(

        default_factory=dict

    )

    # =====================================================
    # STATUS
    # =====================================================

    @property
    def success(

        self

    ) -> bool:

        return (

            self.converged

            and

            self.optimized_portfolio

            is not None

        )

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self

    ) -> dict:

        return {

            "optimizer":

                self.optimizer_name,

            "expected_return":

                self.expected_return,

            "expected_risk":

                self.expected_risk,

            "expected_volatility":

                self.expected_volatility,

            "expected_sharpe":

                self.expected_sharpe,

            "turnover":

                self.turnover,

            "tracking_error":

                self.tracking_error,

            "diversification_ratio":

                self.diversification_ratio,

            "objective_value":

                self.objective_value,

            "iterations":

                self.iterations,

            "converged":

                self.converged,

            "success":

                self.success

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Optimizer={self.optimizer_name}, "

            f"Sharpe={self.expected_sharpe:.4f}, "

            f"Converged={self.converged}"

            f")"

        )

    __str__ = __repr__