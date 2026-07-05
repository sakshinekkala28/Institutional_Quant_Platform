"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Metrics Plugin

Platform metrics plugin.

Responsibilities
----------------
• Collect execution metrics
• Measure engine runtime
• Measure pipeline runtime
• Measure platform runtime
• Track processed records
• Export execution metrics

=========================================================
"""

from __future__ import annotations

from typing import Any

from orchestration.metrics_collector import (
    MetricsCollector,
)
from orchestration.plugins.base_plugin import (
    BasePlugin,
)


# ==========================================================
# METRICS PLUGIN
# ==========================================================

class MetricsPlugin(BasePlugin):
    """
    Platform metrics plugin.
    """

    NAME = "Metrics"

    VERSION = "1.0.0"

    ENABLED = True

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self) -> None:

        super().__init__()

        self.metrics = MetricsCollector()

    # =====================================================
    # LIFECYCLE
    # =====================================================

    def initialize(self) -> None:

        self.metrics.record(

            "plugin.initialized",

            1,

            plugin=self.NAME,

        )

    # -----------------------------------------------------

    def shutdown(self) -> None:

        self.metrics.record(

            "plugin.shutdown",

            1,

            plugin=self.NAME,

        )

    # =====================================================
    # PLATFORM EVENTS
    # =====================================================

    def on_platform_started(
        self,
        **payload: Any,
    ) -> None:

        self.metrics.record(

            "platform.started",

            1,

        )

    # -----------------------------------------------------

    def on_platform_finished(
        self,
        **payload: Any,
    ) -> None:

        duration = payload.get(

            "duration",

            0.0,

        )

        self.metrics.platform_runtime(

            duration

        )

    # =====================================================
    # PIPELINE EVENTS
    # =====================================================

    def on_pipeline_started(
        self,
        pipeline: str,
        **payload: Any,
    ) -> None:

        self.metrics.record(

            "pipeline.started",

            1,

            pipeline=pipeline,

        )

    # -----------------------------------------------------

    def on_pipeline_finished(
        self,
        pipeline: str,
        **payload: Any,
    ) -> None:

        duration = payload.get(

            "duration",

            0.0,

        )

        self.metrics.pipeline_runtime(

            pipeline,

            duration,

        )

    # =====================================================
    # ENGINE EVENTS
    # =====================================================

    def on_engine_started(
        self,
        engine: str,
        **payload: Any,
    ) -> None:

        self.metrics.record(

            "engine.started",

            1,

            engine=engine,

        )

    # -----------------------------------------------------

    def on_engine_finished(
        self,
        engine: str,
        **payload: Any,
    ) -> None:

        duration = payload.get(

            "duration",

            0.0,

        )

        self.metrics.engine_runtime(

            engine,

            duration,

        )

    # =====================================================
    # RECORDS
    # =====================================================

    def on_records_processed(
        self,
        records: int,
        **payload: Any,
    ) -> None:

        self.metrics.records_processed(

            records

        )

    # =====================================================
    # RESOURCE USAGE
    # =====================================================

    def on_memory_usage(
        self,
        memory_mb: float,
        **payload: Any,
    ) -> None:

        self.metrics.memory_usage(

            memory_mb

        )

    # -----------------------------------------------------

    def on_cpu_usage(
        self,
        cpu_percent: float,
        **payload: Any,
    ) -> None:

        self.metrics.cpu_usage(

            cpu_percent

        )

    # =====================================================
    # RETRIES
    # =====================================================

    def on_retry(
        self,
        **payload: Any,
    ) -> None:

        self.metrics.retry()

    # =====================================================
    # EXPORT
    # =====================================================

    def save(
        self,
        path: str,
    ) -> None:

        self.metrics.save(

            path

        )

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(
        self,
    ) -> dict:

        return {

            "plugin":

                self.NAME,

            "version":

                self.VERSION,

            "enabled":

                self.ENABLED,

            "metrics":

                self.metrics.summary(),

        }

    # =====================================================
    # DUNDER
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"metrics={len(self.metrics)})"

        )