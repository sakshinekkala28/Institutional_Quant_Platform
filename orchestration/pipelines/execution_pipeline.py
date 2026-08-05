"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Execution Pipeline

Responsibilities
----------------
1. Portfolio Execution
2. Transaction Cost Analysis
3. Execution Quality Analysis

=========================================================
"""

from __future__ import annotations

from collections.abc import Callable
from typing import ClassVar

# ==========================================================
# EXECUTION ENGINES
# ==========================================================
from analytics.execution.execution_engine_v1 import main as execution_engine
from analytics.execution.execution_quality_engine import \
    main as execution_quality_engine
from analytics.execution.transaction_cost_engine import main as transaction_cost_engine
from orchestration.models.pipeline_result import PipelineResult
from orchestration.pipelines.base_pipeline import BasePipeline

# ==========================================================
# EXECUTION PIPELINE
# ==========================================================


class ExecutionPipeline(BasePipeline):
    """
    Institutional Execution Pipeline.
    """

    NAME = "ExecutionPipeline"

    #
    # Execution must always be sequential.
    #
    EXECUTOR = "sequential"

    ENGINES: ClassVar[list[tuple[str, Callable]]] = [
        (
            "Execution Engine",
            execution_engine,
        ),
        (
            "Transaction Cost Engine",
            transaction_cost_engine,
        ),
        (
            "Execution Quality Engine",
            execution_quality_engine,
        ),
    ]

    # =====================================================
    # OPTIONAL HOOKS
    # =====================================================

    def before_run(self) -> None:

        print("\nStarting Execution Pipeline...")

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

    return ExecutionPipeline.main()


# ==========================================================
# CLI
# ==========================================================

if __name__ == "__main__":
    result = main()

    print(result)
