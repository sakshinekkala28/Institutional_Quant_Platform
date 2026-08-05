"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Execution Report

Central reporting component for the orchestration
framework.

Responsibilities
----------------
• Collect engine execution results
• Collect pipeline execution results
• Generate execution metrics
• Aggregate platform statistics
• Track artifacts and outputs
• Export execution reports
• Provide execution audit trail

Author
------
Institutional Quant Platform

=========================================================
"""

from __future__ import annotations

import csv
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from threading import RLock
from typing import Any

from orchestration.models.engine_result import EngineResult
from orchestration.models.engine_status import EngineStatus
from orchestration.models.master_result import MasterResult
from orchestration.models.pipeline_result import PipelineResult

# =========================================================
# EXECUTION REPORT
# =========================================================


@dataclass(slots=True)
class ExecutionReport:
    """
    Platform execution report.

    Collects execution information from every
    engine, pipeline and orchestrator.
    """

    # -----------------------------------------------------
    # Results
    # -----------------------------------------------------

    engine_results: list[EngineResult] = field(default_factory=list)

    pipeline_results: list[PipelineResult] = field(default_factory=list)

    master_result: MasterResult | None = None

    # -----------------------------------------------------
    # Runtime Metadata
    # -----------------------------------------------------

    metadata: dict[
        str,
        Any,
    ] = field(default_factory=dict)

    # -----------------------------------------------------
    # Outputs
    # -----------------------------------------------------

    outputs: list[str] = field(default_factory=list)

    artifacts: list[str] = field(default_factory=list)

    # -----------------------------------------------------
    # Diagnostics
    # -----------------------------------------------------

    warnings: list[str] = field(default_factory=list)

    errors: list[str] = field(default_factory=list)

    # -----------------------------------------------------
    # Runtime
    # -----------------------------------------------------

    started_at: datetime = field(default_factory=datetime.utcnow)

    finished_at: datetime | None = None

    # -----------------------------------------------------
    # Synchronization
    # -----------------------------------------------------

    _lock: RLock = field(
        default_factory=RLock,
        init=False,
        repr=False,
        compare=False,
    )

    # =====================================================
    # PROPERTIES
    # =====================================================

    @property
    def runtime_seconds(
        self,
    ) -> float:

        if self.finished_at is None:
            return (datetime.utcnow() - self.started_at).total_seconds()

        return (self.finished_at - self.started_at).total_seconds()

    # -----------------------------------------------------

    @property
    def finished(
        self,
    ) -> bool:

        return self.finished_at is not None

    # -----------------------------------------------------

    @property
    def total_engines(
        self,
    ) -> int:

        return len(self.engine_results)

    # -----------------------------------------------------

    @property
    def total_pipelines(
        self,
    ) -> int:

        return len(self.pipeline_results)

    # =====================================================
    # ENGINE STATISTICS
    # =====================================================

    @property
    def successful_engines(
        self,
    ) -> int:

        return sum(
            result.status == EngineStatus.SUCCESS for result in self.engine_results
        )

    # -----------------------------------------------------

    @property
    def failed_engines(
        self,
    ) -> int:

        return sum(
            result.status == EngineStatus.FAILED for result in self.engine_results
        )

    # -----------------------------------------------------

    @property
    def skipped_engines(
        self,
    ) -> int:

        return sum(
            result.status == EngineStatus.SKIPPED for result in self.engine_results
        )

    # =====================================================
    # PIPELINE STATISTICS
    # =====================================================

    @property
    def successful_pipelines(
        self,
    ) -> int:

        return sum(
            pipeline.status == EngineStatus.SUCCESS
            for pipeline in self.pipeline_results
        )

    # -----------------------------------------------------

    @property
    def failed_pipelines(
        self,
    ) -> int:

        return sum(
            pipeline.status == EngineStatus.FAILED for pipeline in self.pipeline_results
        )

    # -----------------------------------------------------

    @property
    def pipeline_success_rate(
        self,
    ) -> float:

        if not self.pipeline_results:
            return 0.0

        return round(
            100 * self.successful_pipelines / len(self.pipeline_results),
            2,
        )

    # =====================================================
    # RUNTIME
    # =====================================================

    def finish(
        self,
    ) -> None:
        """
        Mark report as complete.
        """

        self.finished_at = datetime.utcnow()

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(
        self,
    ) -> dict[str, Any]:

        return {
            "runtime": round(
                self.runtime_seconds,
                3,
            ),
            "pipelines": self.total_pipelines,
            "engines": self.total_engines,
            "success_rate": self.pipeline_success_rate,
            "warnings": len(self.warnings),
            "errors": len(self.errors),
        }

    # =====================================================
    # DUNDER
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}("
            f"pipelines={self.total_pipelines}, "
            f"engines={self.total_engines})"
        )

    # =====================================================
    # ENGINE RESULTS
    # =====================================================

    def add_engine_result(
        self,
        result: EngineResult,
    ) -> None:
        """
        Record an engine execution result.
        """

        with self._lock:
            self.engine_results.append(result)

    # -----------------------------------------------------

    def add_engine_results(
        self,
        results: list[EngineResult],
    ) -> None:
        """
        Record multiple engine results.
        """

        with self._lock:
            self.engine_results.extend(results)

    # =====================================================
    # PIPELINE RESULTS
    # =====================================================

    def add_pipeline_result(
        self,
        result: PipelineResult,
    ) -> None:
        """
        Record pipeline result.
        """

        with self._lock:
            self.pipeline_results.append(result)

    # -----------------------------------------------------

    def add_pipeline_results(
        self,
        results: list[PipelineResult],
    ) -> None:
        """
        Record multiple pipeline results.
        """

        with self._lock:
            self.pipeline_results.extend(results)

    # =====================================================
    # MASTER RESULT
    # =====================================================

    def set_master_result(
        self,
        result: MasterResult,
    ) -> None:
        """
        Set platform execution result.
        """

        self.master_result = result

    # =====================================================
    # METADATA
    # =====================================================

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:

        with self._lock:
            self.metadata[key] = value

    # -----------------------------------------------------

    def get_metadata(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self.metadata.get(
            key,
            default,
        )

        # =====================================================

    # OUTPUTS
    # =====================================================

    def add_output(
        self,
        output: str,
    ) -> None:

        with self._lock:
            self.outputs.append(output)

    # -----------------------------------------------------

    def add_outputs(
        self,
        outputs: list[str],
    ) -> None:

        with self._lock:
            self.outputs.extend(outputs)

    # =====================================================
    # ARTIFACTS
    # =====================================================

    def add_artifact(
        self,
        artifact: str,
    ) -> None:

        with self._lock:
            self.artifacts.append(artifact)

    # -----------------------------------------------------

    def add_artifacts(
        self,
        artifacts: list[str],
    ) -> None:

        with self._lock:
            self.artifacts.extend(artifacts)

    # =====================================================
    # WARNINGS
    # =====================================================

    def add_warning(
        self,
        warning: str,
    ) -> None:

        with self._lock:
            self.warnings.append(warning)

    # -----------------------------------------------------

    def add_error(
        self,
        error: str,
    ) -> None:

        with self._lock:
            self.errors.append(error)

    # =====================================================
    # MERGE
    # =====================================================

    def merge(
        self,
        other: ExecutionReport,
    ) -> None:
        """
        Merge another report.
        """

        with self._lock:
            self.engine_results.extend(other.engine_results)

            self.pipeline_results.extend(other.pipeline_results)

            self.outputs.extend(other.outputs)

            self.artifacts.extend(other.artifacts)

            self.warnings.extend(other.warnings)

            self.errors.extend(other.errors)

            self.metadata.update(other.metadata)

            if other.master_result:
                self.master_result = other.master_result

    # =====================================================
    # CLEAR
    # =====================================================

    def clear(
        self,
    ) -> None:
        """
        Reset report.
        """

        with self._lock:
            self.engine_results.clear()

            self.pipeline_results.clear()

            self.outputs.clear()

            self.artifacts.clear()

            self.warnings.clear()

            self.errors.clear()

            self.metadata.clear()

            self.master_result = None

            self.started_at = datetime.utcnow()

            self.finished_at = None

    # =====================================================
    # SUCCESS RATES
    # =====================================================

    @property
    def engine_success_rate(
        self,
    ) -> float:
        """
        Engine success percentage.
        """

        if not self.engine_results:
            return 0.0

        return round(
            100.0 * self.successful_engines / self.total_engines,
            2,
        )

    # -----------------------------------------------------

    @property
    def overall_status(
        self,
    ) -> EngineStatus:
        """
        Overall platform status.
        """

        if self.master_result:
            return self.master_result.status

        if self.failed_engines:
            return EngineStatus.FAILED

        if self.failed_pipelines:
            return EngineStatus.FAILED

        return EngineStatus.SUCCESS

    # =====================================================
    # RUNTIME ANALYTICS
    # =====================================================

    @property
    def total_runtime(
        self,
    ) -> float:

        return round(
            sum(engine.duration for engine in self.engine_results),
            3,
        )

    # -----------------------------------------------------

    @property
    def average_engine_runtime(
        self,
    ) -> float:

        if not self.engine_results:
            return 0.0

        return round(
            self.total_runtime / len(self.engine_results),
            3,
        )

    # -----------------------------------------------------

    @property
    def average_pipeline_runtime(
        self,
    ) -> float:

        if not self.pipeline_results:
            return 0.0

        return round(
            sum(pipeline.duration for pipeline in self.pipeline_results)
            / len(self.pipeline_results),
            3,
        )

    # =====================================================
    # ENGINE RANKINGS
    # =====================================================

    def slowest_engines(
        self,
        limit: int = 10,
    ) -> list[EngineResult]:
        """
        Slowest executed engines.
        """

        return sorted(
            self.engine_results,
            key=lambda result: result.duration,
            reverse=True,
        )[:limit]

    # -----------------------------------------------------

    def fastest_engines(
        self,
        limit: int = 10,
    ) -> list[EngineResult]:
        """
        Fastest engines.
        """

        return sorted(
            self.engine_results,
            key=lambda result: result.duration,
        )[:limit]

    # =====================================================
    # PIPELINE RANKINGS
    # =====================================================

    def slowest_pipelines(
        self,
        limit: int = 10,
    ) -> list[PipelineResult]:

        return sorted(
            self.pipeline_results,
            key=lambda result: result.duration,
            reverse=True,
        )[:limit]

    # -----------------------------------------------------

    def fastest_pipelines(
        self,
        limit: int = 10,
    ) -> list[PipelineResult]:

        return sorted(
            self.pipeline_results,
            key=lambda result: result.duration,
        )[:limit]

    # =====================================================
    # FAILURES
    # =====================================================

    def failed_engine_results(
        self,
    ) -> list[EngineResult]:

        return [
            result
            for result in self.engine_results
            if (result.status == EngineStatus.FAILED)
        ]

    # -----------------------------------------------------

    def failed_pipeline_results(
        self,
    ) -> list[PipelineResult]:

        return [
            result
            for result in self.pipeline_results
            if (result.status == EngineStatus.FAILED)
        ]

    # =====================================================
    # TIMELINE
    # =====================================================

    def timeline(
        self,
    ) -> list[dict[str, Any]]:
        """
        Execution timeline.
        """

        timeline = []

        for engine in self.engine_results:
            timeline.append(
                {
                    "type": "engine",
                    "name": engine.engine,
                    "status": engine.status.value,
                    "duration": engine.duration,
                }
            )

        for pipeline in self.pipeline_results:
            timeline.append(
                {
                    "type": "pipeline",
                    "name": pipeline.pipeline,
                    "status": pipeline.status.value,
                    "duration": pipeline.duration,
                }
            )

        return timeline

    # =====================================================
    # STATISTICS
    # =====================================================

    def statistics(
        self,
    ) -> dict[str, Any]:

        return {
            "runtime": round(
                self.runtime_seconds,
                3,
            ),
            "engine_success_rate": self.engine_success_rate,
            "pipeline_success_rate": self.pipeline_success_rate,
            "engines": self.total_engines,
            "pipelines": self.total_pipelines,
            "successful_engines": self.successful_engines,
            "failed_engines": self.failed_engines,
            "successful_pipelines": self.successful_pipelines,
            "failed_pipelines": self.failed_pipelines,
            "warnings": len(self.warnings),
            "errors": len(self.errors),
            "outputs": len(self.outputs),
            "artifacts": len(self.artifacts),
        }

    # =====================================================
    # AUDIT REPORT
    # =====================================================

    def audit_report(
        self,
    ) -> dict[str, Any]:
        """
        Comprehensive execution audit.
        """

        return {
            "summary": self.summary(),
            "statistics": self.statistics(),
            "timeline": self.timeline(),
            "metadata": self.metadata,
            "warnings": self.warnings,
            "errors": self.errors,
            "outputs": self.outputs,
            "artifacts": self.artifacts,
        }

    # =====================================================
    # EXPORT
    # =====================================================

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Convert execution report to dictionary.
        """

        return {
            "started_at": self.started_at.isoformat(),
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "runtime": round(
                self.runtime_seconds,
                3,
            ),
            "master_result": (
                self.master_result.to_dict() if self.master_result else None
            ),
            "statistics": self.statistics(),
            "metadata": dict(self.metadata),
            "outputs": list(self.outputs),
            "artifacts": list(self.artifacts),
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "engines": [engine.to_dict() for engine in self.engine_results],
            "pipelines": [pipeline.to_dict() for pipeline in self.pipeline_results],
        }

    # -----------------------------------------------------

    def to_json(
        self,
        *,
        indent: int = 4,
    ) -> str:
        """
        JSON serialization.
        """

        return json.dumps(
            self.to_dict(),
            indent=indent,
            default=str,
        )

    # =====================================================
    # PERSISTENCE
    # =====================================================

    def save(
        self,
        path: Path,
    ) -> None:
        """
        Save report to disk.
        """

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        path.write_text(
            self.to_json(),
            encoding="utf-8",
        )

    # -----------------------------------------------------

    @classmethod
    def load(
        cls,
        path: Path,
    ) -> ExecutionReport:
        """
        Restore report from JSON.

        NOTE:
        EngineResult/PipelineResult reconstruction
        requires their corresponding from_dict()
        implementations.
        """

        data = json.loads(path.read_text(encoding="utf-8"))

        report = cls()

        report.metadata.update(
            data.get(
                "metadata",
                {},
            )
        )

        report.outputs.extend(
            data.get(
                "outputs",
                [],
            )
        )

        report.artifacts.extend(
            data.get(
                "artifacts",
                [],
            )
        )

        report.warnings.extend(
            data.get(
                "warnings",
                [],
            )
        )

        report.errors.extend(
            data.get(
                "errors",
                [],
            )
        )

        return report

    # =====================================================
    # MARKDOWN
    # =====================================================

    def to_markdown(
        self,
    ) -> str:
        """
        Generate Markdown execution report.
        """

        lines = [
            "# Execution Report",
            "",
            f"**Runtime:** {self.runtime_seconds:.2f}s",
            f"**Status:** {self.overall_status.value}",
            "",
            "## Statistics",
            "",
        ]

        for key, value in self.statistics().items():
            lines.append(f"- **{key}** : {value}")

        lines.extend(
            [
                "",
                "## Pipelines",
                "",
            ]
        )

        for pipeline in self.pipeline_results:
            lines.append(
                f"- {pipeline.pipeline}"
                f" ({pipeline.status.value})"
                f" [{pipeline.duration:.2f}s]"
            )

        lines.extend(
            [
                "",
                "## Engines",
                "",
            ]
        )

        for engine in self.engine_results:
            lines.append(
                f"- {engine.engine} ({engine.status.value}) [{engine.duration:.2f}s]"
            )

        return "\n".join(lines)

    # =====================================================
    # CSV
    # =====================================================

    def export_csv(
        self,
        path: Path,
    ) -> None:
        """
        Export engine execution results.
        """

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with path.open(
            "w",
            newline="",
            encoding="utf-8",
        ) as fp:
            writer = csv.writer(fp)

            writer.writerow(
                [
                    "Engine",
                    "Status",
                    "Duration",
                ]
            )

            for result in self.engine_results:
                writer.writerow(
                    [
                        result.engine,
                        result.status.value,
                        result.duration,
                    ]
                )

    # =====================================================
    # CONTAINER
    # =====================================================

    def __len__(
        self,
    ) -> int:

        return len(self.engine_results) + len(self.pipeline_results)

    # -----------------------------------------------------

    def __iter__(
        self,
    ):

        return iter(self.engine_results)

    # -----------------------------------------------------

    def __contains__(
        self,
        engine_name: str,
    ) -> bool:

        return any(result.engine == engine_name for result in self.engine_results)

    # -----------------------------------------------------

    def __str__(
        self,
    ) -> str:

        return (
            f"ExecutionReport("
            f"engines={self.total_engines}, "
            f"pipelines={self.total_pipelines}, "
            f"runtime={self.runtime_seconds:.2f}s)"
        )
