"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Risk Pipeline

Responsibilities
----------------
1. Build Returns Matrix
2. Build Factor Returns
3. Build Factor Covariance
4. Build Specific Risk
5. Build Factor Exposure Matrix
6. Build Factor Risk Model
7. Portfolio Risk Analysis
8. Risk Budget
9. Stress Testing
10. Risk Dashboard

=========================================================
"""

from __future__ import annotations

from collections.abc import Callable
from typing import ClassVar

from analytics.risk.build_factor_covariance import main as covariance_builder_engine
from analytics.risk.build_factor_exposure_matrix import main as exposure_matrix_engine
from analytics.risk.build_factor_returns import main as factor_returns_engine
from analytics.risk.build_factor_risk_model import main as factor_risk_builder
from analytics.risk.build_specific_risk import main as specific_risk_engine
from analytics.risk.exposure_engine import main as exposure_engine
from analytics.risk.factor_risk_model import main as factor_risk_engine
from analytics.risk.portfolio_risk_engine import main as portfolio_risk_engine

# ==========================================================
# RISK ENGINES
# ==========================================================
from analytics.risk.returns_matrix_builder import main as returns_matrix_engine
from analytics.risk.risk_budget_engine import main as risk_budget_engine
from analytics.risk.risk_dashboard_engine import main as risk_dashboard_engine
from analytics.risk.stress_test_engine import main as stress_test_engine
from orchestration.models.pipeline_result import PipelineResult
from orchestration.pipelines.base_pipeline import BasePipeline

# ==========================================================
# RISK PIPELINE
# ==========================================================


class RiskPipeline(BasePipeline):
    """
    Institutional Multi-Factor Risk Pipeline.
    """

    NAME = "RiskPipeline"

    #
    # Risk model construction has
    # strict sequential dependencies.
    #
    EXECUTOR = "sequential"

    ENGINES: ClassVar[list[tuple[str, Callable]]] = [
        (
            "Returns Matrix",
            returns_matrix_engine,
        ),
        (
            "Factor Returns",
            factor_returns_engine,
        ),
        (
            "Factor Covariance",
            covariance_builder_engine,
        ),
        (
            "Specific Risk",
            specific_risk_engine,
        ),
        (
            "Factor Exposure Matrix",
            exposure_matrix_engine,
        ),
        (
            "Factor Risk Model Builder",
            factor_risk_builder,
        ),
        (
            "Factor Risk Model",
            factor_risk_engine,
        ),
        (
            "Portfolio Risk",
            portfolio_risk_engine,
        ),
        (
            "Exposure Analysis",
            exposure_engine,
        ),
        (
            "Risk Budget",
            risk_budget_engine,
        ),
        (
            "Stress Testing",
            stress_test_engine,
        ),
        (
            "Risk Dashboard",
            risk_dashboard_engine,
        ),
    ]

    # =====================================================
    # OPTIONAL HOOKS
    # =====================================================

    def before_run(self) -> None:

        print("\nStarting Risk Pipeline...")

    # -----------------------------------------------------

    def after_run(
        self,
        result: PipelineResult,
    ) -> None:

        print(f"\nCompleted {self.NAME}")

        print(f"Status   : {result.status.value}")

        print(f"Duration : {result.duration:.2f}s")

    # =====================================================
    # ENTRY POINT
    # =====================================================

    @classmethod
    def main(
        cls,
    ) -> PipelineResult:

        return cls().run()


# ==========================================================
# MODULE ENTRY
# ==========================================================


def main() -> PipelineResult:

    return RiskPipeline.main()


# ==========================================================
# CLI
# ==========================================================

if __name__ == "__main__":
    result = main()

    print(result)
