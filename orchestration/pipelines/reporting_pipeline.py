"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Reporting Pipeline

Responsibilities
----------------
1. Portfolio Performance Attribution
2. Security Attribution
3. Brinson Attribution
4. Portfolio History
5. Risk Dashboard
6. Live Rebalance Dashboard

=========================================================
"""

from __future__ import annotations

from analytics.live.live_rebalance_engine import main as live_dashboard_engine
from analytics.performance.brinson_attribution_engine import main as brinson_engine

# ==========================================================
# REPORTING ENGINES
# ==========================================================
from analytics.performance.performance_attribution_engine import (
    main as performance_engine,
)
from analytics.performance.security_attribution_engine import (
    main as security_attribution_engine,
)
from analytics.portfolio.portfolio_history_engine import (
    main as portfolio_history_engine,
)
from analytics.risk.risk_dashboard_engine import main as risk_dashboard_engine
from orchestration.models.pipeline_result import PipelineResult
from orchestration.pipelines.base_pipeline import BasePipeline

# ==========================================================
# REPORTING PIPELINE
# ==========================================================


class ReportingPipeline(BasePipeline):
    """
    Institutional Reporting Pipeline.
    """

    NAME = "ReportingPipeline"

    EXECUTOR = "sequential"

    ENGINES = [
        (
            "Performance Attribution",
            performance_engine,
        ),
        (
            "Security Attribution",
            security_attribution_engine,
        ),
        (
            "Brinson Attribution",
            brinson_engine,
        ),
        (
            "Portfolio History",
            portfolio_history_engine,
        ),
        (
            "Risk Dashboard",
            risk_dashboard_engine,
        ),
        (
            "Live Rebalance Dashboard",
            live_dashboard_engine,
        ),
    ]

    # =====================================================
    # OPTIONAL HOOKS
    # =====================================================

    def before_run(self) -> None:

        print("\nStarting Reporting Pipeline...")

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

    return ReportingPipeline.main()


# ==========================================================
# CLI
# ==========================================================

if __name__ == "__main__":
    result = main()

    print(result)
