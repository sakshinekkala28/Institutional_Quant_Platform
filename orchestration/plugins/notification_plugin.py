"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Notification Plugin

Base notification plugin.

Responsibilities
----------------
• Notification abstraction
• Severity filtering
• Channel management
• Common notification interface

=========================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from enum import Enum
import logging
from typing import Any

from orchestration.plugins.base_plugin import (
    BasePlugin,
)

logger = logging.getLogger(__name__)


# ==========================================================
# SEVERITY
# ==========================================================


class NotificationSeverity(str, Enum):
    INFO = "INFO"

    WARNING = "WARNING"

    ERROR = "ERROR"

    CRITICAL = "CRITICAL"


# ==========================================================
# BASE NOTIFICATION PLUGIN
# ==========================================================


class NotificationPlugin(
    BasePlugin,
    ABC,
):
    """
    Base notification plugin.

    SlackPlugin
    EmailPlugin
    WebhookPlugin

    inherit from this class.
    """

    NAME = "Notification"

    VERSION = "1.0.0"

    ENABLED = True

    def __init__(self) -> None:

        super().__init__()

        self.notifications_sent = 0

    # =====================================================
    # ABSTRACT
    # =====================================================

    @abstractmethod
    def send(
        self,
        title: str,
        message: str,
        severity: NotificationSeverity = (NotificationSeverity.INFO),
        **kwargs: Any,
    ) -> bool:
        """
        Send notification.

        Must be implemented by subclasses.
        """
        raise NotImplementedError

    # =====================================================
    # HELPERS
    # =====================================================

    def info(
        self,
        title: str,
        message: str,
    ) -> bool:

        return self.send(
            title,
            message,
            NotificationSeverity.INFO,
        )

    # -----------------------------------------------------

    def warning(
        self,
        title: str,
        message: str,
    ) -> bool:

        return self.send(
            title,
            message,
            NotificationSeverity.WARNING,
        )

    # -----------------------------------------------------

    def error(
        self,
        title: str,
        message: str,
    ) -> bool:

        return self.send(
            title,
            message,
            NotificationSeverity.ERROR,
        )

    # -----------------------------------------------------

    def critical(
        self,
        title: str,
        message: str,
    ) -> bool:

        return self.send(
            title,
            message,
            NotificationSeverity.CRITICAL,
        )

    # =====================================================
    # PLATFORM EVENTS
    # =====================================================

    def on_platform_failed(
        self,
        **payload: Any,
    ) -> None:

        self.critical(
            "Platform Failure",
            str(payload),
        )

    # -----------------------------------------------------

    def on_pipeline_failed(
        self,
        pipeline: str,
        **payload: Any,
    ) -> None:

        self.error(
            f"Pipeline Failed: {pipeline}",
            str(payload),
        )

    # -----------------------------------------------------

    def on_engine_failed(
        self,
        engine: str,
        **payload: Any,
    ) -> None:

        self.error(
            f"Engine Failed: {engine}",
            str(payload),
        )

    # =====================================================
    # STATISTICS
    # =====================================================

    def increment(self) -> None:

        self.notifications_sent += 1

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(self) -> dict:

        return {
            "plugin": self.NAME,
            "version": self.VERSION,
            "enabled": self.ENABLED,
            "notifications": self.notifications_sent,
        }

    # =====================================================
    # DUNDER
    # =====================================================

    def __repr__(self) -> str:

        return f"{self.__class__.__name__}(notifications={self.notifications_sent})"
