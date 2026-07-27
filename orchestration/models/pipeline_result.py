"""
=========================================================
PIPELINE RESULT
=========================================================

Purpose:
Standard return object for orchestration pipelines.

=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from orchestration.models.engine_result import EngineResult
from orchestration.models.engine_status import EngineStatus


@dataclass(slots=True)
class PipelineResult:
    """
    Standard result object returned by orchestration pipelines.
    """

    pipeline: str

    status: EngineStatus

    duration: float

    engines: list[EngineResult] = field(
        default_factory=list,
    )

    outputs: list[Path] = field(
        default_factory=list,
    )

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    # =====================================================
    # METRICS
    # =====================================================

    @property
    def successful_engines(self) -> int:

        return sum(
            1 for engine in self.engines if engine.status == EngineStatus.SUCCESS
        )

    @property
    def failed_engines(self) -> int:

        return sum(1 for engine in self.engines if engine.status == EngineStatus.FAILED)

    @property
    def total_engines(self) -> int:

        return len(self.engines)

    @property
    def success_rate(self) -> float:

        if not self.engines:
            return 0.0

        return round(
            (self.successful_engines / self.total_engines) * 100,
            2,
        )

    # =====================================================
    # HELPERS
    # =====================================================

    def add_engine(
        self,
        result: EngineResult,
    ) -> None:

        self.engines.append(result)

        if result.output is not None:
            self.outputs.append(Path(result.output))

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(
        self,
    ) -> dict[str, Any]:

        return {
            "pipeline": self.pipeline,
            "status": self.status.value,
            "duration": self.duration,
            "engines": self.total_engines,
            "successful": self.successful_engines,
            "failed": self.failed_engines,
            "success_rate": self.success_rate,
            "outputs": [str(path) for path in self.outputs],
            "metadata": self.metadata,
        }
