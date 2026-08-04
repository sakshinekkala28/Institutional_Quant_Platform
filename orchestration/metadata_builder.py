"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Metadata Builder

Builds standardized execution metadata for the
orchestration framework.

Responsibilities
----------------
• Engine metadata
• Pipeline metadata
• Platform metadata
• Runtime statistics
• Execution summaries
• Audit metadata

=========================================================
"""

from __future__ import annotations

from datetime import datetime
from typing import Any

from orchestration.execution_context import ExecutionContext
from orchestration.execution_report import ExecutionReport
from orchestration.models.engine_result import EngineResult
from orchestration.models.master_result import MasterResult
from orchestration.models.pipeline_result import PipelineResult

# =========================================================
# METADATA BUILDER
# =========================================================


class MetadataBuilder:
    """
    Builds standardized metadata objects.
    """

    # =====================================================
    # ENGINE
    # =====================================================

    @staticmethod
    def engine_metadata(
        result: EngineResult,
    ) -> dict[str, Any]:

        return {
            "engine": result.engine,
            "status": result.status.value,
            "duration": result.duration,
            "started_at": result.started_at,
            "finished_at": result.finished_at,
            "outputs": len(result.outputs),
            "warnings": len(result.warnings),
            "errors": len(result.errors),
        }

    # =====================================================
    # PIPELINE
    # =====================================================

    @staticmethod
    def pipeline_metadata(
        result: PipelineResult,
    ) -> dict[str, Any]:

        return {
            "pipeline": result.pipeline,
            "status": result.status.value,
            "duration": result.duration,
            "engines": result.total_engines,
            "successful_engines": result.successful_engines,
            "failed_engines": result.failed_engines,
            "success_rate": result.success_rate,
        }

    # =====================================================
    # CONTEXT
    # =====================================================

    @staticmethod
    def context_metadata(
        context: ExecutionContext,
    ) -> dict[str, Any]:

        return {
            "runtime": round(
                context.runtime_seconds,
                3,
            ),
            "outputs": context.output_count,
            "artifacts": context.artifact_count,
            "warnings": context.warning_count,
            "errors": context.error_count,
        }

    # =====================================================
    # REPORT
    # =====================================================

    @staticmethod
    def report_metadata(
        report: ExecutionReport,
    ) -> dict[str, Any]:

        return {
            "runtime": round(
                report.runtime_seconds,
                3,
            ),
            "engine_success_rate": report.engine_success_rate,
            "pipeline_success_rate": report.pipeline_success_rate,
            "engines": report.total_engines,
            "pipelines": report.total_pipelines,
        }

    # =====================================================
    # MASTER
    # =====================================================

    @staticmethod
    def master_metadata(
        result: MasterResult,
    ) -> dict[str, Any]:

        return {
            "status": result.status.value,
            "duration": result.duration,
            "pipelines": result.total_pipelines,
            "engines": result.total_engines,
            "successful_pipelines": result.successful_pipelines,
            "failed_pipelines": result.failed_pipelines,
            "success_rate": result.success_rate,
            "generated_at": datetime.utcnow().isoformat(),
        }

    # =====================================================
    # BUILD
    # =====================================================

    @staticmethod
    def build(**kwargs) -> dict[str, Any]:
        """
        Merge metadata fragments.
        """

        metadata: dict[str, Any] = {}

        for value in kwargs.values():
            if isinstance(value, dict):
                metadata.update(value)

        return metadata
