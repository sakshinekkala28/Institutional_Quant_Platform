"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Audit Plugin

Platform audit plugin.

Responsibilities
----------------
• Record platform lifecycle
• Record pipeline execution
• Record engine execution
• Record failures
• Persist audit trail

=========================================================
"""

from __future__ import annotations

from typing import Any

from orchestration.audit_logger import AuditLogger
from orchestration.plugins.base_plugin import BasePlugin

# ==========================================================
# AUDIT PLUGIN
# ==========================================================


class AuditPlugin(BasePlugin):
    """
    Platform audit plugin.
    """

    NAME = "Audit"

    VERSION = "1.0.0"

    ENABLED = True

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self) -> None:

        super().__init__()

        self.audit = AuditLogger()

    # =====================================================
    # LIFECYCLE
    # =====================================================

    def initialize(self) -> None:

        self.audit.record(
            event="PLUGIN_INITIALIZED",
            component=self.NAME,
        )

    # -----------------------------------------------------

    def shutdown(self) -> None:

        self.audit.record(
            event="PLUGIN_SHUTDOWN",
            component=self.NAME,
        )

        self.audit.save()

    # =====================================================
    # PLATFORM
    # =====================================================

    def on_platform_started(
        self,
        **payload: Any,
    ) -> None:

        self.audit.platform_started()

    # -----------------------------------------------------

    def on_platform_finished(
        self,
        **payload: Any,
    ) -> None:

        self.audit.platform_finished(
            payload.get(
                "status",
                "SUCCESS",
            )
        )

    # -----------------------------------------------------

    def on_platform_failed(
        self,
        **payload: Any,
    ) -> None:

        self.audit.record(
            event="PLATFORM_FAILED",
            component="Platform",
            **payload,
        )

    # =====================================================
    # PIPELINES
    # =====================================================

    def on_pipeline_started(
        self,
        pipeline: str,
        **payload: Any,
    ) -> None:

        self.audit.pipeline_started(pipeline)

    # -----------------------------------------------------

    def on_pipeline_finished(
        self,
        pipeline: str,
        **payload: Any,
    ) -> None:

        self.audit.pipeline_finished(
            pipeline,
            payload.get(
                "status",
                "SUCCESS",
            ),
        )

    # -----------------------------------------------------

    def on_pipeline_failed(
        self,
        pipeline: str,
        **payload: Any,
    ) -> None:

        self.audit.record(
            event="PIPELINE_FAILED",
            component=pipeline,
            **payload,
        )

    # =====================================================
    # ENGINES
    # =====================================================

    def on_engine_started(
        self,
        engine: str,
        **payload: Any,
    ) -> None:

        self.audit.engine_started(engine)

    # -----------------------------------------------------

    def on_engine_finished(
        self,
        engine: str,
        **payload: Any,
    ) -> None:

        self.audit.engine_finished(
            engine,
            payload.get(
                "status",
                "SUCCESS",
            ),
            payload.get(
                "duration",
                0.0,
            ),
        )

    # -----------------------------------------------------

    def on_engine_failed(
        self,
        engine: str,
        **payload: Any,
    ) -> None:

        self.audit.record(
            event="ENGINE_FAILED",
            component=engine,
            **payload,
        )

    # =====================================================
    # EXCEPTION
    # =====================================================

    def on_exception(
        self,
        exception: Exception,
        **payload: Any,
    ) -> None:

        self.audit.exception(
            payload.get(
                "component",
                "Unknown",
            ),
            exception,
        )

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(self) -> dict:

        return {
            "plugin": self.NAME,
            "version": self.VERSION,
            "enabled": self.ENABLED,
            "events": len(
                self.audit,
            ),
        }

    # =====================================================
    # DUNDER
    # =====================================================

    def __repr__(self) -> str:

        return f"{self.__class__.__name__}(events={len(self.audit)})"
