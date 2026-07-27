"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Email Plugin

Email notification transport.

Responsibilities
----------------
• Send email notifications
• SMTP delivery
• HTML/Text email support
• Delivery failure handling

=========================================================
"""

from __future__ import annotations

from email.message import EmailMessage
import logging
import smtplib
from typing import Any

from orchestration.plugins.notification_plugin import (
    NotificationPlugin,
    NotificationSeverity,
)

logger = logging.getLogger(__name__)


# ==========================================================
# EMAIL PLUGIN
# ==========================================================


class EmailPlugin(NotificationPlugin):
    """
    SMTP Email notification plugin.
    """

    NAME = "Email"

    VERSION = "1.0.0"

    ENABLED = False

    def __init__(
        self,
        *,
        smtp_server: str = "",
        smtp_port: int = 587,
        username: str = "",
        password: str = "",
        sender: str = "",
        recipients: list[str] | None = None,
        use_tls: bool = True,
    ) -> None:

        super().__init__()

        self.smtp_server = smtp_server

        self.smtp_port = smtp_port

        self.username = username

        self.password = password

        self.sender = sender

        self.recipients = recipients or []

        self.use_tls = use_tls

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

        if not self.ENABLED or not self.configured:
            return False

        email = EmailMessage()

        email["Subject"] = f"[{severity.value}] {title}"

        email["From"] = self.sender

        email["To"] = ", ".join(self.recipients)

        email.set_content(message)

        try:
            with smtplib.SMTP(
                self.smtp_server,
                self.smtp_port,
            ) as smtp:
                if self.use_tls:
                    smtp.starttls()

                smtp.login(
                    self.username,
                    self.password,
                )

                smtp.send_message(email)

            self.increment()

            logger.info("Email notification sent.")

            return True

        except Exception:
            logger.exception("Failed to send email.")

            return False

    # =====================================================
    # CONFIGURATION
    # =====================================================

    @property
    def configured(
        self,
    ) -> bool:

        return all(
            [
                self.smtp_server,
                self.sender,
                self.username,
                self.password,
                self.recipients,
            ]
        )

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(
        self,
    ) -> dict:

        return {
            **super().summary(),
            "configured": self.configured,
            "smtp_server": self.smtp_server,
            "smtp_port": self.smtp_port,
            "recipients": len(
                self.recipients,
            ),
        }

    # =====================================================
    # DUNDER
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}("
            f"configured={self.configured}, "
            f"recipients={len(self.recipients)})"
        )
