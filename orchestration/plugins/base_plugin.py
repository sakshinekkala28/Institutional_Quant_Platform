"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Base Plugin

Abstract interface implemented by every orchestration
plugin.

Responsibilities
----------------
• Plugin lifecycle
• Event handling
• Metadata
• Enable / Disable
• Health checks

Implemented By
--------------
• MonitoringPlugin
• MetricsPlugin
• AuditPlugin
• NotificationPlugin
• SlackPlugin
• EmailPlugin
• WebhookPlugin

=========================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

# =========================================================
# BASE PLUGIN
# =========================================================


class BasePlugin(ABC):
    """
    Abstract base class for all orchestration plugins.
    """

    NAME = "base"

    VERSION = "1.0.0"

    DESCRIPTION = ""

    ENABLED = True

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(
        self,
        **config: Any,
    ) -> None:

        self.config = config

        self.started = False

    # =====================================================
    # LIFECYCLE
    # =====================================================

    def initialize(
        self,
    ) -> None:
        """
        Initialize plugin resources.
        """

        self.started = True

    # -----------------------------------------------------

    def shutdown(
        self,
    ) -> None:
        """
        Shutdown plugin.
        """

        self.started = False

    # =====================================================
    # EVENTS
    # =====================================================

    @abstractmethod
    def on_platform_started(
        self,
        context,
    ) -> None:
        """
        Platform startup event.
        """
        raise NotImplementedError

    # -----------------------------------------------------

    @abstractmethod
    def on_platform_finished(
        self,
        report,
    ) -> None:
        """
        Platform completion event.
        """
        raise NotImplementedError

    # -----------------------------------------------------

    @abstractmethod
    def on_engine_started(
        self,
        engine,
    ) -> None:
        """
        Engine started.
        """
        raise NotImplementedError

    # -----------------------------------------------------

    @abstractmethod
    def on_engine_finished(
        self,
        result,
    ) -> None:
        """
        Engine completed.
        """
        raise NotImplementedError

    # -----------------------------------------------------

    @abstractmethod
    def on_pipeline_started(
        self,
        pipeline,
    ) -> None:
        """
        Pipeline started.
        """
        raise NotImplementedError

    # -----------------------------------------------------

    @abstractmethod
    def on_pipeline_finished(
        self,
        result,
    ) -> None:
        """
        Pipeline completed.
        """
        raise NotImplementedError

    # =====================================================
    # HEALTH
    # =====================================================

    def health_check(
        self,
    ) -> bool:

        return self.started

    # =====================================================
    # METADATA
    # =====================================================

    @classmethod
    def metadata(
        cls,
    ) -> dict:

        return {
            "name": cls.NAME,
            "version": cls.VERSION,
            "description": cls.DESCRIPTION,
            "enabled": cls.ENABLED,
        }

    # =====================================================
    # DUNDER
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return f"{self.__class__.__name__}(name='{self.NAME}', started={self.started})"
