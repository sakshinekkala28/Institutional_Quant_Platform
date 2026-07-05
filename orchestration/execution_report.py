"""
Institutional Quant Platform
============================

Execution Report

Collects execution statistics for every engine and
produces the final pipeline report.

Author: Institutional Quant Platform
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


# ----------------------------------------------------------------------


@dataclass
class EngineReport:
    """
    Execution report for a single engine.
    """

    engine: str

    stage: str

    status: str

    started_at: Optional[str] = None

    finished_at: Optional[str] = None

    runtime_seconds: float = 0.0

    outputs: List[str] = field(default_factory=list)

    warnings: List[str] = field(default_factory=list)

    error: Optional[str] = None

    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):

        return {
            "engine": self.engine,
            "stage": self.stage,
            "status": self.status,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "runtime_seconds": self.runtime_seconds,
            "outputs": self.outputs,
            "warnings": self.warnings,
            "error": self.error,
            "metadata": self.metadata,
        }


# ----------------------------------------------------------------------


class ExecutionReport:
    """
    Pipeline execution report.
    """

    def __init__(self):

        self.pipeline_name = ""

        self.pipeline_id = ""

        self.started_at = datetime.utcnow()

        self.finished_at = None

        self.engine_reports: List[EngineReport] = []

        self.metadata: Dict[str, Any] = {}

    # ------------------------------------------------------------------

    def start_pipeline(
        self,
        pipeline_name: str,
        pipeline_id: str,
    ):

        self.pipeline_name = pipeline_name

        self.pipeline_id = pipeline_id

        self.started_at = datetime.utcnow()

    # ------------------------------------------------------------------

    def finish_pipeline(self):

        self.finished_at = datetime.utcnow()

    # ------------------------------------------------------------------

    def add_engine_report(
        self,
        report: EngineReport,
    ):

        self.engine_reports.append(report)

    # ------------------------------------------------------------------

    @property
    def successful(self):

        return sum(
            r.status == "SUCCESS"
            for r in self.engine_reports
        )

    # ------------------------------------------------------------------

    @property
    def failed(self):

        return sum(
            r.status == "FAILED"
            for r in self.engine_reports
        )

    # ------------------------------------------------------------------

    @property
    def skipped(self):

        return sum(
            r.status == "SKIPPED"
            for r in self.engine_reports
        )

    # ------------------------------------------------------------------

    @property
    def runtime(self):

        if self.finished_at is None:
            return 0.0

        return (
            self.finished_at - self.started_at
        ).total_seconds()

    # ------------------------------------------------------------------

    @property
    def outputs(self):

        files = []

        for report in self.engine_reports:

            files.extend(report.outputs)

        return sorted(files)

    # ------------------------------------------------------------------

    def summary(self):

        return {

            "pipeline_name": self.pipeline_name,

            "pipeline_id": self.pipeline_id,

            "started_at": self.started_at.isoformat(),

            "finished_at": (
                self.finished_at.isoformat()
                if self.finished_at
                else None
            ),

            "runtime_seconds": round(
                self.runtime,
                2,
            ),

            "engines": len(
                self.engine_reports
            ),

            "successful": self.successful,

            "failed": self.failed,

            "skipped": self.skipped,

            "outputs_generated": len(
                self.outputs
            ),

            "metadata": self.metadata,
        }

    # ------------------------------------------------------------------

    def to_dict(self):

        return {

            "summary": self.summary(),

            "engines": [

                report.to_dict()

                for report in self.engine_reports

            ]

        }

    # ------------------------------------------------------------------

    def save(
        self,
        output_directory: Path,
    ) -> Path:

        output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        filename = (

            f"pipeline_report_"

            f"{datetime.utcnow():%Y%m%d_%H%M%S}.json"

        )

        path = output_directory / filename

        with open(
            path,
            "w",
            encoding="utf-8",
        ) as fp:

            json.dump(
                self.to_dict(),
                fp,
                indent=4,
            )

        return path

    # ------------------------------------------------------------------

    def print_summary(self):

        print("=" * 80)
        print("PIPELINE EXECUTION REPORT")
        print("=" * 80)

        print(f"Pipeline : {self.pipeline_name}")
        print(f"ID       : {self.pipeline_id}")
        print(f"Runtime  : {self.runtime:.2f}s")
        print()

        print(f"Successful : {self.successful}")
        print(f"Failed     : {self.failed}")
        print(f"Skipped    : {self.skipped}")
        print(f"Outputs    : {len(self.outputs)}")

        print("=" * 80)

    # ------------------------------------------------------------------

    def __repr__(self):

        return (

            f"ExecutionReport("

            f"pipeline='{self.pipeline_name}', "

            f"engines={len(self.engine_reports)})"

        )