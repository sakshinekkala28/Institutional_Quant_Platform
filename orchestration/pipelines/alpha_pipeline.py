"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Alpha Pipeline

Responsibilities
----------------
1. Signal Generation
2. Price History Construction
3. Expected Return Estimation

=========================================================
"""

from __future__ import annotations

from orchestration.models.pipeline_result import (
    PipelineResult,
)

from orchestration.pipelines.base_pipeline import (
    BasePipeline,
)

# ==========================================================
# ALPHA ENGINES
# ==========================================================

from analytics.signals.signal_engine import (
    main as signal_engine,
)

from analytics.alpha.price_history_engine import (
    main as price_history_engine,
)

from analytics.live.build_factor_expected_returns import (
    main as expected_return_engine,
)


# ==========================================================
# ALPHA PIPELINE
# ==========================================================

class AlphaPipeline(BasePipeline):
    """
    Institutional Alpha Pipeline.
    """

    NAME = "AlphaPipeline"

    #
    # Expected returns depend on
    # signals and price history.
    #
    EXECUTOR = "sequential"

    ENGINES = [

        (
            "Signal Engine",
            signal_engine,
        ),

        (
            "Price History Engine",
            price_history_engine,
        ),

        (
            "Expected Return Engine",
            expected_return_engine,
        ),

    ]

    # =====================================================
    # OPTIONAL HOOKS
    # =====================================================

    def before_run(self) -> None:

        print("\nStarting Alpha Pipeline...")

    # -----------------------------------------------------

    def after_run(
        self,
        result: PipelineResult,
    ) -> None:

        print(
            f"\nCompleted {self.NAME}"
        )

        print(
            f"Status   : {result.status.value}"
        )

        print(
            f"Duration : {result.duration:.2f}s"
        )

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

    return AlphaPipeline.main()


# ==========================================================
# CLI
# ==========================================================

if __name__ == "__main__":

    result = main()

    print(result)