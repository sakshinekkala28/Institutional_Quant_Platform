"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Factor Pipeline

Responsibilities
----------------
1. Build Fundamental Factor Master
2. Factor Engine
3. Factor Ranking
4. Factor Snapshot

=========================================================
"""

from __future__ import annotations

# ==========================================================
# FACTOR ENGINES
# ==========================================================
from analytics.factors.build_fundamental_factor_master import (
    main as build_factor_master_engine,
)
from analytics.factors.factor_engine import (
    main as factor_engine,
)
from analytics.factors.factor_rank_engine import (
    main as factor_rank_engine,
)
from analytics.factors.factor_snapshot_engine import (
    main as factor_snapshot_engine,
)
from orchestration.models.pipeline_result import (
    PipelineResult,
)
from orchestration.pipelines.base_pipeline import (
    BasePipeline,
)

# ==========================================================
# FACTOR PIPELINE
# ==========================================================


class FactorPipeline(BasePipeline):
    """
    Institutional Factor Pipeline.
    """

    NAME = "FactorPipeline"

    #
    # Factor generation has strict dependencies.
    #
    EXECUTOR = "sequential"

    ENGINES = [
        (
            "Fundamental Factor Master",
            build_factor_master_engine,
        ),
        (
            "Factor Engine",
            factor_engine,
        ),
        (
            "Factor Ranking",
            factor_rank_engine,
        ),
        (
            "Factor Snapshot",
            factor_snapshot_engine,
        ),
    ]

    # =====================================================
    # OPTIONAL HOOKS
    # =====================================================

    def before_run(self) -> None:

        print("\nStarting Factor Pipeline...")

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

    return FactorPipeline.main()


# ==========================================================
# CLI
# ==========================================================

if __name__ == "__main__":
    result = main()

    print(result)
