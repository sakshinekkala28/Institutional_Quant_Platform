"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Performance Pipeline

Responsibilities
----------------
1. Portfolio Performance Attribution
2. Security Attribution
3. Brinson Attribution
4. Capacity Analysis
5. Benchmark Performance

=========================================================
"""

from __future__ import annotations

from analytics.benchmark.benchmark_constituents_engine import (
    main as benchmark_constituents_engine,
)
from analytics.benchmark.benchmark_engine import main as benchmark_engine
from analytics.capacity.capacity_engine import main as capacity_engine
from analytics.performance.brinson_attribution_engine import (
    main as brinson_attribution_engine,
)

# ==========================================================
# PERFORMANCE ENGINES
# ==========================================================
from analytics.performance.performance_attribution_engine import (
    main as performance_attribution_engine,
)
from analytics.performance.security_attribution_engine import (
    main as security_attribution_engine,
)
from orchestration.models.pipeline_result import PipelineResult
from orchestration.pipelines.base_pipeline import BasePipeline

# ==========================================================
# PERFORMANCE PIPELINE
# ==========================================================


class PerformancePipeline(BasePipeline):
    """
    Institutional Performance Analytics Pipeline.
    """

    NAME = "PerformancePipeline"

    #
    # Performance attribution is sequential.
    #
    EXECUTOR = "sequential"

    ENGINES = [
        (
            "Benchmark Constituents",
            benchmark_constituents_engine,
        ),
        (
            "Benchmark Engine",
            benchmark_engine,
        ),
        (
            "Performance Attribution",
            performance_attribution_engine,
        ),
        (
            "Security Attribution",
            security_attribution_engine,
        ),
        (
            "Brinson Attribution",
            brinson_attribution_engine,
        ),
        (
            "Capacity Analysis",
            capacity_engine,
        ),
    ]

    # =====================================================
    # OPTIONAL HOOKS
    # =====================================================

    def before_run(self) -> None:

        print("\nStarting Performance Pipeline...")

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

    return PerformancePipeline.main()


# ==========================================================
# CLI
# ==========================================================

if __name__ == "__main__":
    result = main()

    print(result)
