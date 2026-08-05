"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Live Pipeline

Responsibilities
----------------
1. Build Expected Returns
2. Live Portfolio Rebalancing

=========================================================
"""

from __future__ import annotations

from collections.abc import Callable
from typing import ClassVar

# ==========================================================
# LIVE ENGINES
# ==========================================================
from analytics.live.build_factor_expected_returns import main as expected_returns_engine
from analytics.live.live_rebalance_engine import main as live_rebalance_engine
from orchestration.models.pipeline_result import PipelineResult
from orchestration.pipelines.base_pipeline import BasePipeline

# ==========================================================
# LIVE PIPELINE
# ==========================================================


class LivePipeline(BasePipeline):
    """
    Institutional Live Trading Pipeline.
    """

    NAME = "LivePipeline"

    #
    # Live execution is sequential.
    #
    EXECUTOR = "sequential"

    ENGINES: ClassVar[list[tuple[str, Callable]]] = [
        (
            "Expected Returns",
            expected_returns_engine,
        ),
        (
            "Live Rebalance",
            live_rebalance_engine,
        ),
    ]

    # =====================================================
    # OPTIONAL HOOKS
    # =====================================================

    def before_run(self) -> None:

        print("\nStarting Live Pipeline...")

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

    return LivePipeline.main()


# ==========================================================
# CLI
# ==========================================================

if __name__ == "__main__":
    result = main()

    print(result)
