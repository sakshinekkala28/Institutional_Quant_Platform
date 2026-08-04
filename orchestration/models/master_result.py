"""
=========================================================
MASTER RESULT
=========================================================

Purpose
-------
Standard execution result returned by the Master
Orchestrator.

Aggregates all PipelineResult objects executed during
a platform run.

=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from orchestration.models.engine_status import EngineStatus
from orchestration.models.pipeline_result import PipelineResult


@dataclass(slots=True)
class MasterResult:
    """
    Standard execution result returned by the
    Master Orchestrator.
    """

    platform: str = "Institutional Quant Platform"

    status: EngineStatus = EngineStatus.RUNNING

    duration: float = 0.0

    pipelines: list[PipelineResult] = field(
        default_factory=list,
    )

    outputs: list[Path] = field(
        default_factory=list,
    )

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    # =====================================================
    # PIPELINE METRICS
    # =====================================================

    @property
    def total_pipelines(self) -> int:
        return len(self.pipelines)

    @property
    def successful_pipelines(self) -> int:
        return sum(
            1 for pipeline in self.pipelines if pipeline.status == EngineStatus.SUCCESS
        )

    @property
    def failed_pipelines(self) -> int:
        return sum(
            1 for pipeline in self.pipelines if pipeline.status == EngineStatus.FAILED
        )

    @property
    def success_rate(self) -> float:
        if self.total_pipelines == 0:
            return 0.0

        return round(
            (self.successful_pipelines / self.total_pipelines) * 100,
            2,
        )

    # =====================================================
    # ENGINE METRICS
    # =====================================================

    @property
    def total_engines(self) -> int:
        return sum(pipeline.total_engines for pipeline in self.pipelines)

    @property
    def successful_engines(self) -> int:
        return sum(pipeline.successful_engines for pipeline in self.pipelines)

    @property
    def failed_engines(self) -> int:
        return sum(pipeline.failed_engines for pipeline in self.pipelines)

    # =====================================================
    # MUTATORS
    # =====================================================

    def add_pipeline(
        self,
        result: PipelineResult,
    ) -> None:
        """
        Register a completed pipeline.
        """

        self.pipelines.append(result)

        self.outputs.extend(result.outputs)

    def add_output(
        self,
        output: Path,
    ) -> None:
        """
        Register an output artifact.
        """

        self.outputs.append(output)

    def update_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Update execution metadata.
        """

        self.metadata[key] = value

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(self) -> dict[str, Any]:
        """
        Return execution summary.
        """

        return {
            "platform": self.platform,
            "status": self.status.value,
            "duration": round(self.duration, 3),
            "pipelines": self.total_pipelines,
            "successful_pipelines": self.successful_pipelines,
            "failed_pipelines": self.failed_pipelines,
            "pipeline_success_rate": self.success_rate,
            "engines": self.total_engines,
            "successful_engines": self.successful_engines,
            "failed_engines": self.failed_engines,
            "outputs": [str(path) for path in self.outputs],
            "metadata": self.metadata,
        }

    # =====================================================
    # DUNDER
    # =====================================================

    def __bool__(self) -> bool:
        return self.status == EngineStatus.SUCCESS

    def __len__(self) -> int:
        return self.total_pipelines

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"platform='{self.platform}', "
            f"status='{self.status.value}', "
            f"pipelines={self.total_pipelines}, "
            f"engines={self.total_engines}, "
            f"duration={self.duration:.3f}s)"
        )
