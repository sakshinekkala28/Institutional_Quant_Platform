"""
====================================================================
INSTITUTIONAL QUANT PLATFORM

Base Pipeline

Institutional pipeline abstraction.

Responsibilities

• Pipeline lifecycle
• Executor selection
• Engine execution
• Metadata collection
• Pipeline result generation
• Exception handling

====================================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable
from time import perf_counter
from typing import Any, ClassVar

from orchestration.engine_registry import EngineRegistry
from orchestration.execution_context import ExecutionContext
from orchestration.executors.executor_factory import ExecutorFactory
from orchestration.models.engine_result import EngineResult
from orchestration.models.engine_status import EngineStatus
from orchestration.models.pipeline_result import PipelineResult


class BasePipeline(ABC):
    """
    Base class for all orchestration pipelines.
    """

    NAME = "BasePipeline"

    EXECUTOR = "sequential"

    ENGINES: ClassVar[
        list[tuple[str, Callable]]
    ] = []

    def __init__(self) -> None:
        """
        Initialize the pipeline runtime.
        """

        self.registry = EngineRegistry()

        self.context = ExecutionContext()

        self.registry.discover()

        self.executor = ExecutorFactory.create(
            self.EXECUTOR,
            registry=self.registry,
            context=self.context,
        )

    # =====================================================
    # PRE / POST HOOKS
    # =====================================================

    def before_run(self) -> None:
        """
        Execute pre-run pipeline hook.
        """

        return

    def after_run(
        self,
        result: PipelineResult,
    ) -> None:
        """
        Execute post-run pipeline hook.
        """

        return

    # =====================================================
    # VALIDATION
    # =====================================================

    def validate(self) -> None:
        """
        Validate pipeline configuration.
        """

        if not self.ENGINES:

            raise ValueError(
                f"{self.NAME} contains no engines."
            )

    # =====================================================
    # RUN
    # =====================================================

    def run(
        self,
    ) -> PipelineResult:
        """
        Execute the pipeline.
        """

        self.validate()

        self.before_run()

        started = perf_counter()

        result = PipelineResult(
            pipeline=self.NAME,
            status=EngineStatus.RUNNING,
            duration=0.0,
        )

        try:

            engine_names = [
                name
                for name, _ in self.ENGINES
            ]

            execution_results = (
                self.executor.execute(
                    engine_names
                )
            )

            for engine_result in execution_results:

                if not isinstance(
                    engine_result,
                    EngineResult,
                ):

                    raise TypeError(
                        "Executor returned "
                        f"{type(engine_result)} "
                        "instead of EngineResult."
                    )

                result.add_engine(
                    engine_result
                )

            if result.failed_engines:

                result.status = (
                    EngineStatus.FAILED
                )

            else:

                result.status = (
                    EngineStatus.SUCCESS
                )

        except Exception as exc:

            result.status = (
                EngineStatus.FAILED
            )

            result.metadata["error"] = str(
                exc
            )

            self.context.errors.append(
                str(exc)
            )

        finally:

            result.duration = (
                perf_counter()
                - started
            )

            self.context.finish()

            result.metadata.update(
                self.build_metadata(
                    result
                )
            )

            result.metadata[
                "context"
            ] = self.context.summary()

            self.after_run(
                result
            )

        return result

    # =====================================================
    # METADATA
    # =====================================================

    def build_metadata(
        self,
        result: PipelineResult,
    ) -> dict[str, Any]:
        """
        Build pipeline execution metadata.
        """

        records = sum(
            getattr(
                engine,
                "records",
                0,
            )
            for engine in result.engines
        )

        return {
            "pipeline": self.NAME,
            "executor": self.EXECUTOR,
            "total_engines": result.total_engines,
            "successful_engines": (
                result.successful_engines
            ),
            "failed_engines": (
                result.failed_engines
            ),
            "records_processed": records,
            "success_rate": result.success_rate,
        }

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(
        self,
    ) -> dict[str, Any]:
        """
        Return pipeline configuration summary.
        """

        return {
            "pipeline": self.NAME,
            "executor": self.EXECUTOR,
            "engines": len(
                self.ENGINES
            ),
        }

    # =====================================================
    # ABSTRACT
    # =====================================================

    @classmethod
    @abstractmethod
    def main(
        cls,
    ) -> PipelineResult:
        """
        Pipeline entry point.
        """

    # =====================================================
    # DUNDER
    # =====================================================

    def __repr__(
        self,
    ) -> str:
        """
        Return pipeline representation.
        """

        return (
            f"{self.__class__.__name__}"
            f"(name='{self.NAME}')"
        )