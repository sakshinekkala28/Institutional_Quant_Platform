"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Webhook Plugin

Generic webhook notification transport.

Responsibilities
----------------
• Send webhook notifications
• POST JSON payloads
• Retry-safe delivery
• Generic REST integration

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
# WEBHOOK PLUGIN
# ==========================================================


class WebhookPlugin(NotificationPlugin):
    """
    Generic webhook notification plugin.
    """

    NAME = "Webhook"

    VERSION = "1.0.0"

    ENABLED = False

    def __init__(
        self,
        *,
        endpoint: str = "",
        timeout: int = 10,
        headers: dict[str, str] | None = None,
    ) -> None:

        super().__init__()

        self.endpoint = endpoint

        self.timeout = timeout

        self.headers = headers or {"Content-Type": "application/json"}

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

        if not self.ENABLED or not self.endpoint:
            return False

        payload = {
            "title": title,
            "message": message,
            "severity": severity.value,
            "metadata": kwargs,
        }

        try:
            response = requests.post(
                self.endpoint,
                json=payload,
                headers=self.headers,
                timeout=self.timeout,
            )

            response.raise_for_status()

            self.increment()

            logger.info("Webhook notification delivered.")

            return True

        except Exception:
            logger.exception("Webhook delivery failed.")

            return False

    # =====================================================
    # HEALTH
    # =====================================================

    @property
    def configured(
        self,
    ) -> bool:

        return bool(self.endpoint)

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(
        self,
    ) -> dict:

        return {
            **super().summary(),
            "configured": self.configured,
            "endpoint": self.endpoint,
            "timeout": self.timeout,
        }

    # =====================================================
    # DUNDER
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return f"{self.__class__.__name__}(configured={self.configured})"
