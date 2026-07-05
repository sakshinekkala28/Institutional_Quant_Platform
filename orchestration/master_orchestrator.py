"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Master Orchestrator

Central orchestration coordinator.

Responsibilities
----------------
• Engine discovery
• Dependency graph construction
• Pipeline construction
• Pipeline validation
• Pipeline analysis
• Executor selection
• Execution coordination
• Master result generation

NOTE
----
The MasterOrchestrator NEVER executes engines directly.

Actual execution is delegated to an Executor created by
ExecutorFactory.

=========================================================
"""

from __future__ import annotations

from time import perf_counter
from typing import Optional

from orchestration.engine_registry import (
    EngineRegistry,
)

from orchestration.dependency_graph import (
    DependencyGraph,
)

from orchestration.pipeline_builder import (
    PipelineBuilder,
)

from orchestration.pipeline_validator import (
    PipelineValidator,
)

from orchestration.pipeline_analyzer import (
    PipelineAnalyzer,
)

from orchestration.execution_context import (
    ExecutionContext,
)

from orchestration.execution_report import (
    ExecutionReport,
)

from orchestration.executors.executor_factory import (
    ExecutorFactory,
)

from orchestration.models.master_result import (
    MasterResult,
)

from orchestration.models.pipeline_result import (
    PipelineResult,
)

from orchestration.models.engine_status import (
    EngineStatus,
)


# =========================================================
# MASTER ORCHESTRATOR
# =========================================================


class MasterOrchestrator:
    """
    Institutional platform orchestrator.

    Responsible only for coordinating platform execution.
    """

    DEFAULT_EXECUTOR = "sequential"

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(
        self,
        *,
        executor: str = DEFAULT_EXECUTOR,
    ) -> None:

        self.executor_mode = executor

        self.registry = EngineRegistry()

        self.graph: Optional[
            DependencyGraph
        ] = None

        self.pipeline = None

        self.context = ExecutionContext()

        self.report = ExecutionReport()

        self.result = MasterResult()

    # =====================================================
    # SETUP
    # =====================================================

    def initialize(
        self,
    ) -> None:
        """
        Build and validate the execution pipeline.
        """

        # -------------------------------------------------
        # Discover engines
        # -------------------------------------------------

        self.registry.discover()

        # -------------------------------------------------
        # Build dependency graph
        # -------------------------------------------------

        self.graph = DependencyGraph(

            self.registry

        )

        self.graph.validate()

        # -------------------------------------------------
        # Build execution pipeline
        # -------------------------------------------------

        self.pipeline = PipelineBuilder(

            self.registry,

            self.graph,

        ).build()

        # -------------------------------------------------
        # Validate pipeline
        # -------------------------------------------------

        PipelineValidator(

            self.pipeline

        ).validate()

        # -------------------------------------------------
        # Analyze pipeline
        # -------------------------------------------------

        PipelineAnalyzer(

            self.pipeline

        ).analyze()

        # -------------------------------------------------
        # Execution metadata
        # -------------------------------------------------

        self.context.set_metadata(

            "executor",

            self.executor_mode,

        )

        self.context.set_metadata(

            "initialized",

            True,

        )

    # =====================================================
    # RUN
    # =====================================================

    def run(
        self,
    ) -> MasterResult:
        """
        Execute the complete platform.
        """

        timer = perf_counter()

        self.initialize()

        executor = ExecutorFactory.create(

            mode=self.executor_mode,

            registry=self.registry,

            context=self.context,

        )

        try:

            # ---------------------------------------------
            # Execute dependency levels
            # ---------------------------------------------

            for level in self.pipeline.execution_levels:

                pipeline_result = self._execute_level(

                    executor,

                    level,

                )

                self.result.add_pipeline(

                    pipeline_result

                )

            self.result.status = (

                EngineStatus.SUCCESS

            )

        except Exception as exc:

            self.result.status = (

                EngineStatus.FAILED

            )

            self.result.metadata["error"] = str(

                exc

            )

            raise

        finally:

            self.result.duration = (

                perf_counter()

                - timer

            )

            self.context.finish()

            self.report.finish()

            self._finalize()

        return self.result
    
    # =====================================================
    # EXECUTION LEVEL
    # =====================================================

    def _execute_level(
        self,
        executor,
        engine_names: list[str],
    ) -> PipelineResult:
        """
        Execute a dependency level.

        All engines within the same dependency level are
        independent and may execute sequentially or in
        parallel depending on the configured executor.
        """

        pipeline_result = PipelineResult(

            pipeline=f"Level-{len(self.result.pipelines) + 1}",

            status=EngineStatus.RUNNING,

            duration=0.0,

        )

        timer = perf_counter()

        engine_results = executor.execute(

            engine_names

        )

        pipeline_result.duration = (

            perf_counter()

            - timer

        )

        for engine_result in engine_results:

            pipeline_result.add_engine(

                engine_result

            )

            self.report.add_engine_result(

                engine_result

            )

        if pipeline_result.failed_engines == 0:

            pipeline_result.status = (

                EngineStatus.SUCCESS

            )

        else:

            pipeline_result.status = (

                EngineStatus.FAILED

            )

        self.report.add_pipeline_result(

            pipeline_result

        )

        return pipeline_result

    # =====================================================
    # FINALIZATION
    # =====================================================

    def _finalize(
        self,
    ) -> None:
        """
        Finalize execution metadata and report.
        """

        self.result.metadata.update(

            {

                "executor":

                    self.executor_mode,

                "total_pipelines":

                    self.result.total_pipelines,

                "successful_pipelines":

                    self.result.successful_pipelines,

                "failed_pipelines":

                    self.result.failed_pipelines,

                "total_engines":

                    self.result.total_engines,

                "successful_engines":

                    self.result.successful_engines,

                "failed_engines":

                    self.result.failed_engines,

                "pipeline_success_rate":

                    self.result.success_rate,

            }

        )

        self.report.set_master_result(

            self.result

        )

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(
        self,
    ) -> dict:
        """
        Lightweight orchestration summary.
        """

        return {

            "status":

                self.result.status.value,

            "executor":

                self.executor_mode,

            "pipelines":

                self.result.total_pipelines,

            "engines":

                self.result.total_engines,

            "duration":

                round(

                    self.result.duration,

                    3,

                ),

        }

    # =====================================================
    # DUNDER
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"executor='{self.executor_mode}', "

            f"pipelines={self.result.total_pipelines}, "

            f"engines={self.result.total_engines}, "

            f"status='{self.result.status.value}')"

        )