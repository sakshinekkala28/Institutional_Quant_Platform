"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Slack Plugin

Slack notification transport.

Responsibilities
----------------
• Send Slack notifications
• Format Slack messages
• Handle Slack delivery failures

=========================================================
"""

from __future__ import annotations

import logging
from typing import Any

import requests

from orchestration.plugins.notification_plugin import (
    NotificationPlugin,
    NotificationSeverity,
)

logger = logging.getLogger(__name__)


# ==========================================================
# SLACK PLUGIN
# ==========================================================


class SlackPlugin(NotificationPlugin):
    """
    Slack notification plugin.

    Uses Slack Incoming Webhooks.
    """

    NAME = "Slack"

    VERSION = "1.0.0"

    ENABLED = False

    def __init__(
        self,
        webhook_url: str | None = None,
        timeout: int = 10,
    ) -> None:

        super().__init__()

        self.webhook_url = webhook_url

        self.timeout = timeout

    # =====================================================
    # SEND
    # =====================================================

    def send(
        self,
        title: str,
        message: str,
        severity: NotificationSeverity = (NotificationSeverity.INFO),
        **kwargs: Any,
    ) -> bool:
        """
        Send Slack notification.
        """

        if not self.ENABLED or not self.webhook_url:
            return False

        payload = {"text": (f"*[{severity.value}]* {title}\n{message}")}

        try:
            response = requests.post(
                self.webhook_url,
                json=payload,
                timeout=self.timeout,
            )

            response.raise_for_status()

            self.increment()

            return True

        except Exception:
            logger.exception("Failed to send Slack notification.")

            return False

    # =====================================================
    # HEALTH
    # =====================================================

    @property
    def configured(
        self,
    ) -> bool:

        return bool(self.webhook_url)

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(
        self,
    ) -> dict:

        return {
            **super().summary(),
            "configured": self.configured,
            "timeout": self.timeout,
        }

    # =====================================================
    # DUNDER
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return f"{self.__class__.__name__}(configured={self.configured})"
