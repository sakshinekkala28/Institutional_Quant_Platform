"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Lifecycle Manager

Coordinates the complete platform lifecycle.

Responsibilities
----------------
• Platform initialization
• Startup
• Shutdown
• Restart
• Cleanup
• State management

=========================================================
"""

from __future__ import annotations

import logging
from enum import StrEnum

from orchestration.orchestrator import Orchestrator

logger = logging.getLogger(__name__)


# =========================================================
# LIFECYCLE STATE
# =========================================================


class LifecycleState(StrEnum):
    CREATED = "CREATED"

    INITIALIZED = "INITIALIZED"

    STARTED = "STARTED"

    RUNNING = "RUNNING"

    STOPPED = "STOPPED"

    SHUTDOWN = "SHUTDOWN"


# =========================================================
# LIFECYCLE MANAGER
# =========================================================


class LifecycleManager:
    """
    Coordinates platform lifecycle.
    """

    def __init__(
        self,
        orchestrator: Orchestrator | None = None,
    ) -> None:

        self.orchestrator = orchestrator or Orchestrator()

        self.state = LifecycleState.CREATED

    # =====================================================
    # INITIALIZE
    # =====================================================

    def initialize(
        self,
    ) -> None:

        logger.info("Initializing platform.")

        self.state = LifecycleState.INITIALIZED

    # =====================================================
    # START
    # =====================================================

    def start(
        self,
    ) -> None:

        if self.state == LifecycleState.CREATED:
            self.initialize()

        logger.info("Starting platform.")

        self.state = LifecycleState.STARTED

    # =====================================================
    # RUN
    # =====================================================

    def run(
        self,
    ):

        if self.state != LifecycleState.STARTED:
            self.start()

        self.state = LifecycleState.RUNNING

        return self.orchestrator.run()

    # =====================================================
    # STOP
    # =====================================================

    def stop(
        self,
    ) -> None:

        logger.info("Stopping platform.")

        self.state = LifecycleState.STOPPED

    # =====================================================
    # SHUTDOWN
    # =====================================================

    def shutdown(
        self,
    ) -> None:

        logger.info("Shutting down platform.")

        self.stop()

        self.state = LifecycleState.SHUTDOWN

    # =====================================================
    # RESTART
    # =====================================================

    def restart(
        self,
    ):

        self.shutdown()

        self.initialize()

        self.start()

        return self.run()

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(
        self,
    ) -> dict:

        return {
            "state": self.state.value,
            "executor": self.orchestrator._orchestrator.executor_mode,
        }

    # =====================================================
    # DUNDER
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return f"{self.__class__.__name__}(state={self.state.value})"
