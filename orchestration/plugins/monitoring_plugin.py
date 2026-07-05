"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Monitoring Plugin

Platform monitoring plugin.

Responsibilities
----------------
• Platform health monitoring
• Runtime validation
• Health checks
• Resource monitoring
• Readiness reporting

=========================================================
"""

from __future__ import annotations

from typing import Any

from orchestration.health_manager import (
    HealthManager,
)

from orchestration.plugins.base_plugin import (
    BasePlugin,
)


# ==========================================================
# MONITORING PLUGIN
# ==========================================================

class MonitoringPlugin(BasePlugin):
    """
    Platform monitoring plugin.
    """

    NAME = "Monitoring"

    VERSION = "1.0.0"

    ENABLED = True

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(self) -> None:

        super().__init__()

        self.health = HealthManager()

    # =====================================================
    # LIFECYCLE
    # =====================================================

    def initialize(self) -> None:
        """
        Initialize monitoring.
        """

        pass

    # -----------------------------------------------------

    def shutdown(self) -> None:
        """
        Shutdown monitoring.
        """

        pass

    # =====================================================
    # PLATFORM EVENTS
    # =====================================================

    def on_platform_started(
        self,
        **payload: Any,
    ) -> None:

        self.health.check_all()

    # -----------------------------------------------------

    def on_platform_finished(
        self,
        **payload: Any,
    ) -> None:

        self.health.check_all()

    # -----------------------------------------------------

    def on_platform_failed(
        self,
        **payload: Any,
    ) -> None:

        self.health.check_all()

    # =====================================================
    # PIPELINES
    # =====================================================

    def on_pipeline_started(
        self,
        pipeline: str,
        **payload: Any,
    ) -> None:

        self.health.check_all()

    # -----------------------------------------------------

    def on_pipeline_finished(
        self,
        pipeline: str,
        **payload: Any,
    ) -> None:

        self.health.check_all()

    # =====================================================
    # ENGINES
    # =====================================================

    def on_engine_started(
        self,
        engine: str,
        **payload: Any,
    ) -> None:

        self.health.check_all()

    # -----------------------------------------------------

    def on_engine_finished(
        self,
        engine: str,
        **payload: Any,
    ) -> None:

        self.health.check_all()

    # =====================================================
    # HEALTH
    # =====================================================

    def register_check(
        self,
        name: str,
        check,
    ) -> None:

        self.health.register(

            name,

            check,

        )

    # -----------------------------------------------------

    def run_checks(
        self,
    ):

        return self.health.check_all()

    # -----------------------------------------------------

    def is_ready(
        self,
    ) -> bool:

        return self.health.is_ready()

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

            "health":

                self.health.summary(),

        }

    # =====================================================
    # DUNDER
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"ready={self.health.is_ready()})"

        )