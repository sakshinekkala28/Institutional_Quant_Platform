"""
======================================================================

Institutional Quant Platform

Notification Service

Author
------
Institutional Quant Platform

Purpose
-------
Enterprise notification framework.

Responsibilities
----------------
• Email Notifications
• Slack Notifications
• Teams Notifications
• SMS Notifications
• Webhooks
• Notification Queue
• Retry Management

======================================================================
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from enum import StrEnum
from threading import Lock, RLock
from typing import Any

from core.services.base_service import BaseService

# ============================================================
# Exceptions
# ============================================================


class NotificationError(Exception):
    """Base notification exception."""


class NotificationNotFoundError(NotificationError):
    """Notification not found."""


# ============================================================
# Notification Channel
# ============================================================


class NotificationChannel(StrEnum):
    EMAIL = "EMAIL"

    SLACK = "SLACK"

    TEAMS = "TEAMS"

    SMS = "SMS"

    WEBHOOK = "WEBHOOK"

    SYSTEM = "SYSTEM"


# ============================================================
# Notification Status
# ============================================================


class NotificationStatus(StrEnum):
    PENDING = "PENDING"

    SENT = "SENT"

    FAILED = "FAILED"

    RETRYING = "RETRYING"


# ============================================================
# Notification Model
# ============================================================


@dataclass(slots=True)
class Notification:
    notification_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    timestamp: float = field(default_factory=time.time)

    channel: NotificationChannel = NotificationChannel.SYSTEM

    recipient: str = ""

    subject: str = ""

    message: str = ""

    status: NotificationStatus = NotificationStatus.PENDING

    retries: int = 0

    metadata: dict[str, Any] = field(default_factory=dict)


# ============================================================
# Notification Service
# ============================================================


class NotificationService(BaseService):
    """
    Enterprise notification manager.
    """

    _instance = None

    _instance_lock = Lock()

    def __new__(cls, *args, **kwargs):

        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):

        if getattr(self, "_initialized", False):
            return

        super().__init__()

        self._lock = RLock()

        self._notifications: list[Notification] = []

        self._enabled = True

        self._initialized = True

        self._logger.info("NotificationService initialized.")

    # =====================================================
    # Lifecycle
    # =====================================================

    def enable(self):

        self._enabled = True

    def disable(self):

        self._enabled = False

    def enabled(self):

        return self._enabled

    # =====================================================
    # Create Notification
    # =====================================================

    def create(
        self,
        channel: NotificationChannel,
        recipient: str,
        subject: str,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> Notification:

        notification = Notification(
            channel=channel,
            recipient=recipient,
            subject=subject,
            message=message,
            metadata=metadata or {},
        )

        with self._lock:
            self._notifications.append(notification)

        return notification

    # =====================================================
    # BaseService
    # =====================================================

    def run(self):

        return self.statistics()

    # =====================================================
    # Delivery
    # =====================================================

    def send(self, notification: Notification) -> Notification:
        """
        Send notification.

        Provider integration (SMTP, Slack API, etc.)
        will be implemented in adapter classes.
        """

        if not self._enabled:
            notification.status = NotificationStatus.FAILED

            return notification

        try:
            notification.status = NotificationStatus.SENT

            self._logger.info(
                "[%s] Notification delivered to %s",
                notification.channel.value,
                notification.recipient,
            )

        except Exception:
            notification.status = NotificationStatus.FAILED

            raise

        return notification

    # =====================================================
    # Email
    # =====================================================

    def send_email(
        self,
        recipient: str,
        subject: str,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> Notification:

        notification = self.create(
            channel=NotificationChannel.EMAIL,
            recipient=recipient,
            subject=subject,
            message=message,
            metadata=metadata,
        )

        return self.send(notification)

    # =====================================================
    # Slack
    # =====================================================

    def send_slack(
        self, channel: str, message: str, metadata: dict[str, Any] | None = None
    ) -> Notification:

        notification = self.create(
            NotificationChannel.SLACK,
            recipient=channel,
            subject="",
            message=message,
            metadata=metadata,
        )

        return self.send(notification)

    # =====================================================
    # Teams
    # =====================================================

    def send_teams(
        self, webhook: str, message: str, metadata: dict[str, Any] | None = None
    ) -> Notification:

        notification = self.create(
            NotificationChannel.TEAMS,
            recipient=webhook,
            subject="",
            message=message,
            metadata=metadata,
        )

        return self.send(notification)

    # =====================================================
    # SMS
    # =====================================================

    def send_sms(
        self, phone_number: str, message: str, metadata: dict[str, Any] | None = None
    ) -> Notification:

        notification = self.create(
            NotificationChannel.SMS,
            recipient=phone_number,
            subject="",
            message=message,
            metadata=metadata,
        )

        return self.send(notification)

    # =====================================================
    # Webhook
    # =====================================================

    def send_webhook(self, endpoint: str, payload: dict[str, Any]) -> Notification:

        notification = self.create(
            NotificationChannel.WEBHOOK,
            recipient=endpoint,
            subject="Webhook",
            message=str(payload),
            metadata=payload,
        )

        return self.send(notification)

    # =====================================================
    # Status
    # =====================================================

    def mark_sent(self, notification_id: str) -> None:

        notification = self.get(notification_id)

        notification.status = NotificationStatus.SENT

    def mark_failed(self, notification_id: str) -> None:

        notification = self.get(notification_id)

        notification.status = NotificationStatus.FAILED

    # =====================================================
    # Retry
    # =====================================================

    def retry(self, notification_id: str) -> Notification:

        notification = self.get(notification_id)

        notification.retries += 1

        notification.status = NotificationStatus.RETRYING

        return self.send(notification)

    # =====================================================
    # Lookup
    # =====================================================

    def get(self, notification_id: str) -> Notification:

        for notification in self._notifications:
            if notification.notification_id == notification_id:
                return notification

        raise NotificationNotFoundError(notification_id)

    def notifications(self) -> list[Notification]:

        return list(self._notifications)

    def pending(self) -> list[Notification]:

        return [
            notification
            for notification in self._notifications
            if notification.status == NotificationStatus.PENDING
        ]

    def failed(self) -> list[Notification]:

        return [
            notification
            for notification in self._notifications
            if notification.status == NotificationStatus.FAILED
        ]

    def sent(self) -> list[Notification]:

        return [
            notification
            for notification in self._notifications
            if notification.status == NotificationStatus.SENT
        ]

    # =====================================================
    # Templates
    # =====================================================

    def register_template(self, name: str, subject: str, message: str) -> None:
        """
        Register notification template.
        """

        if not hasattr(self, "_templates"):
            self._templates = {}

        self._templates[name] = {"subject": subject, "message": message}

    def send_template(
        self, template: str, channel: NotificationChannel, recipient: str, **kwargs
    ) -> Notification:
        """
        Send notification using template.
        """

        if not hasattr(self, "_templates") or template not in self._templates:
            raise NotificationError(f"Unknown template '{template}'.")

        data = self._templates[template]

        subject = data["subject"].format(**kwargs)

        message = data["message"].format(**kwargs)

        notification = self.create(
            channel=channel, recipient=recipient, subject=subject, message=message
        )

        return self.send(notification)

    # =====================================================
    # Batch Notifications
    # =====================================================

    def broadcast(
        self,
        channel: NotificationChannel,
        recipients: list[str],
        subject: str,
        message: str,
    ) -> list[Notification]:
        """
        Broadcast notification.
        """

        notifications = []

        for recipient in recipients:
            notification = self.create(channel, recipient, subject, message)

            notifications.append(self.send(notification))

        return notifications

    # =====================================================
    # Queue Processing
    # =====================================================

    def process_queue(self) -> int:
        """
        Process pending notifications.
        """

        processed = 0

        for notification in self.pending():
            self.send(notification)

            processed += 1

        return processed

    # =====================================================
    # Statistics
    # =====================================================

    def statistics(self) -> dict[str, Any]:
        """
        Notification statistics.
        """

        sent = len(self.sent())

        pending = len(self.pending())

        failed = len(self.failed())

        retries = sum(notification.retries for notification in self._notifications)

        return {
            "total": len(self._notifications),
            "sent": sent,
            "pending": pending,
            "failed": failed,
            "retries": retries,
        }

    # =====================================================
    # Snapshot
    # =====================================================

    def snapshot(self) -> list[dict[str, Any]]:
        """
        Export notifications.
        """

        return [
            {
                "id": notification.notification_id,
                "timestamp": notification.timestamp,
                "channel": notification.channel.value,
                "recipient": notification.recipient,
                "subject": notification.subject,
                "status": notification.status.value,
                "retries": notification.retries,
            }
            for notification in self._notifications
        ]

    # =====================================================
    # Health
    # =====================================================

    def health(self) -> dict[str, Any]:

        return {
            "status": "HEALTHY" if self._enabled else "DISABLED",
            "notifications": len(self._notifications),
            "failed": len(self.failed()),
        }

    # =====================================================
    # Maintenance
    # =====================================================

    def clear(self) -> None:

        self._notifications.clear()

    # =====================================================
    # Lifecycle
    # =====================================================

    def startup(self) -> None:

        self.enable()

        self._logger.info("Notification service started.")

    def shutdown(self) -> None:

        self.disable()

        self._logger.info("Notification service shutdown.")

    # =====================================================
    # Magic Methods
    # =====================================================

    def __len__(self) -> int:

        return len(self._notifications)

    def __iter__(self):

        return iter(self._notifications)

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(notifications={len(self)}, "
            f"enabled={self._enabled})"
        )


# ============================================================
# Global Singleton
# ============================================================

notification_service = NotificationService()
