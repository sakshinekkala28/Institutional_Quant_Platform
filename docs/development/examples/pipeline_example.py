"""
Institutional Quant Platform
Production Reference Pipeline

This file demonstrates the recommended implementation pattern
for all pipelines.

Pipelines orchestrate multiple engines while remaining
independent of engine implementations.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import logging
import time
from typing import Any, Protocol

logger = logging.getLogger(__name__)


# ----------------------------------------------------------------------
# Contracts
# ----------------------------------------------------------------------


class Engine(Protocol):
    """Pipeline engine contract."""

    @property
    def name(self) -> str: ...

    def execute(self) -> Any: ...


# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------


@dataclass(frozen=True)
class PipelineConfig:
    """Pipeline configuration."""

    name: str
    version: str
    stop_on_failure: bool = True


# ----------------------------------------------------------------------
# Result Objects
# ----------------------------------------------------------------------


@dataclass(slots=True)
class StageResult:
    stage: str
    success: bool
    execution_time: float
    payload: Any | None = None
    message: str = ""


@dataclass(slots=True)
class PipelineResult:
    success: bool
    pipeline: str
    execution_time: float
    stages: list[StageResult] = field(default_factory=list)


# ----------------------------------------------------------------------
# Base Pipeline
# ----------------------------------------------------------------------


class BasePipeline(ABC):
    """Abstract pipeline."""

    def __init__(self, config: PipelineConfig):
        self.config = config

    @abstractmethod
    def run(self) -> PipelineResult: ...


# ----------------------------------------------------------------------
# Example Engine
# ----------------------------------------------------------------------


class ExampleEngine:
    """Reference engine."""

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def execute(self) -> dict[str, Any]:

        time.sleep(0.05)

        return {
            "engine": self.name,
            "status": "SUCCESS",
        }


# ----------------------------------------------------------------------
# Example Pipeline
# ----------------------------------------------------------------------


class ExamplePipeline(BasePipeline):
    """
    Reference pipeline implementation.
    """

    def __init__(
        self,
        config: PipelineConfig,
        engines: list[Engine],
    ):
        super().__init__(config)
        self.engines = engines

    def run(self) -> PipelineResult:

        logger.info(
            "Starting pipeline: %s",
            self.config.name,
        )

        pipeline_start = time.perf_counter()

        stage_results: list[StageResult] = []

        for engine in self.engines:
            stage_start = time.perf_counter()

            try:
                logger.info(
                    "Running engine: %s",
                    engine.name,
                )

                payload = engine.execute()

                elapsed = time.perf_counter() - stage_start

                stage_results.append(
                    StageResult(
                        stage=engine.name,
                        success=True,
                        execution_time=elapsed,
                        payload=payload,
                    )
                )

            except Exception as exc:
                elapsed = time.perf_counter() - stage_start

                logger.exception(exc)

                stage_results.append(
                    StageResult(
                        stage=engine.name,
                        success=False,
                        execution_time=elapsed,
                        message=str(exc),
                    )
                )

                if self.config.stop_on_failure:
                    break

        pipeline_elapsed = time.perf_counter() - pipeline_start

        success = all(stage.success for stage in stage_results)

        logger.info(
            "Pipeline completed in %.3f sec",
            pipeline_elapsed,
        )

        return PipelineResult(
            success=success,
            pipeline=self.config.name,
            execution_time=pipeline_elapsed,
            stages=stage_results,
        )


# ----------------------------------------------------------------------
# Example Usage
# ----------------------------------------------------------------------


def main() -> None:

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    config = PipelineConfig(
        name="ReferencePipeline",
        version="1.0.0",
    )

    engines = [
        ExampleEngine("FactorEngine"),
        ExampleEngine("RiskEngine"),
        ExampleEngine("PortfolioEngine"),
    ]

    pipeline = ExamplePipeline(
        config=config,
        engines=engines,
    )

    result = pipeline.run()

    logger.info(result)


if __name__ == "__main__":
    main()
