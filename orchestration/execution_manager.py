"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Execution Manager

Coordinates executor execution and converts raw
engine results into PipelineResult objects.

Responsibilities
----------------
• Execute dependency levels
• Aggregate EngineResult objects
• Build PipelineResult
• Populate ExecutionReport

=========================================================
"""

from __future__ import annotations

from time import perf_counter

from orchestration.execution_report import (
    ExecutionReport,
)
from orchestration.models.engine_status import (
    EngineStatus,
)
from orchestration.models.pipeline_result import (
    PipelineResult,
)


class ExecutionManager:
    """
    Coordinates executor execution.
    """

    def __init__(
        self,
        executor,
        report: ExecutionReport,
    ) -> None:

        self.executor = executor

        self.report = report

    # =====================================================
    # PIPELINE
    # =====================================================

    def execute_pipeline(
        self,
        pipeline,
    ) -> list[PipelineResult]:
        """
        Execute every dependency level.
        """

        results = []

        for level in pipeline.execution_levels:
            result = self.execute_level(level)

            results.append(result)

        return results

    # =====================================================
    # LEVEL
    # =====================================================

    def execute_level(
        self,
        engines: list[str],
    ) -> PipelineResult:

        pipeline = PipelineResult(
            pipeline="Execution Level",
            status=EngineStatus.RUNNING,
        )

        timer = perf_counter()

        engine_results = self.executor.execute(engines)

        pipeline.duration = perf_counter() - timer

        for result in engine_results:
            pipeline.add_engine(result)

            self.report.add_engine_result(result)

        pipeline.status = (
            EngineStatus.SUCCESS
            if pipeline.failed_engines == 0
            else EngineStatus.FAILED
        )

        self.report.add_pipeline_result(pipeline)

        return pipeline
