"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Logging Plugin

Platform logging plugin.

Responsibilities
----------------
• Lifecycle logging
• Pipeline logging
• Engine logging
• Exception logging

=========================================================
"""

from __future__ import annotations

import logging
from typing import Any

from orchestration.plugins.base_plugin import BasePlugin

logger = logging.getLogger(__name__)


# ==========================================================
# LOGGING PLUGIN
# ==========================================================


class LoggingPlugin(BasePlugin):
    """
    Platform logging plugin.
    """

    NAME = "Logging"

    VERSION = "1.0.0"

    ENABLED = True

    # =====================================================
    # LIFECYCLE
    # =====================================================

    def initialize(self) -> None:

        logger.info(
            "%s initialized.",
            self.NAME,
        )

    # -----------------------------------------------------

    def shutdown(self) -> None:

        logger.info(
            "%s shutdown.",
            self.NAME,
        )

    # =====================================================
    # PLATFORM
    # =====================================================

    def on_platform_started(
        self,
        **payload: Any,
    ) -> None:

        logger.info("Platform started.")

    # -----------------------------------------------------

    def on_platform_finished(
        self,
        **payload: Any,
    ) -> None:

        logger.info("Platform finished.")

    # -----------------------------------------------------

    def on_platform_failed(
        self,
        **payload: Any,
    ) -> None:

        logger.error("Platform failed.")

    # =====================================================
    # PIPELINES
    # =====================================================

    def on_pipeline_started(
        self,
        pipeline: str,
        **payload: Any,
    ) -> None:

        logger.info(
            "Pipeline started: %s",
            pipeline,
        )

    # -----------------------------------------------------

    def on_pipeline_finished(
        self,
        pipeline: str,
        **payload: Any,
    ) -> None:

        logger.info(
            "Pipeline finished: %s",
            pipeline,
        )

    # -----------------------------------------------------

    def on_pipeline_failed(
        self,
        pipeline: str,
        **payload: Any,
    ) -> None:

        logger.exception(
            "Pipeline failed: %s",
            pipeline,
        )

    # =====================================================
    # ENGINES
    # =====================================================

    def on_engine_started(
        self,
        engine: str,
        **payload: Any,
    ) -> None:

        logger.info(
            "Engine started: %s",
            engine,
        )

    # -----------------------------------------------------

    def on_engine_finished(
        self,
        engine: str,
        **payload: Any,
    ) -> None:

        logger.info(
            "Engine finished: %s",
            engine,
        )

    # -----------------------------------------------------

    def on_engine_failed(
        self,
        engine: str,
        **payload: Any,
    ) -> None:

        logger.exception(
            "Engine failed: %s",
            engine,
        )

    # =====================================================
    # EXCEPTIONS
    # =====================================================

    def on_exception(
        self,
        exception: Exception,
        **payload: Any,
    ) -> None:

        logger.exception(exception)

    # =====================================================
    # STATUS
    # =====================================================

    def summary(self) -> dict:

        return {
            "plugin": self.NAME,
            "version": self.VERSION,
            "enabled": self.ENABLED,
        }

    # =====================================================
    # DUNDER
    # =====================================================

    def __repr__(self) -> str:

        return f"{self.__class__.__name__}(name='{self.NAME}')"
