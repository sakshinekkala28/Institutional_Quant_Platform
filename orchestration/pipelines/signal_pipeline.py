"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Signal Pipeline

Responsibilities
----------------
1. Generate Alpha Signals
2. Build Security Price History
3. Build Expected Returns

=========================================================
"""

from __future__ import annotations

from collections.abc import Callable
from typing import ClassVar

from analytics.alpha.price_history_engine import main as price_history_engine
from analytics.live.build_factor_expected_returns import main as expected_returns_engine
# ==========================================================
# SIGNAL ENGINES
# ==========================================================
from analytics.signals.signal_engine import main as signal_engine
from orchestration.models.pipeline_result import PipelineResult
from orchestration.pipelines.base_pipeline import BasePipeline

# ==========================================================
# SIGNAL PIPELINE
# ==========================================================


class SignalPipeline(BasePipeline):
    """
    Institutional Signal Pipeline.
    """

    NAME = "SignalPipeline"

    #
    # Signal generation is sequential.
    #
    EXECUTOR = "sequential"

    ENGINES: ClassVar[list[tuple[str, Callable]]] = [
        (
            "Signal Engine",
            signal_engine,
        ),
        (
            "Price History Engine",
            price_history_engine,
        ),
        (
            "Expected Returns",
            expected_returns_engine,
        ),
    ]

    # =====================================================
    # OPTIONAL HOOKS
    # =====================================================

    def before_run(self) -> None:

        print("\nStarting Signal Pipeline...")

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

    return SignalPipeline.main()


# ==========================================================
# CLI
# ==========================================================

if __name__ == "__main__":
    result = main()

    print(result)
