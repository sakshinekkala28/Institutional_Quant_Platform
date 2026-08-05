"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Event Subscribers

Common subscriber implementations.

Responsibilities
----------------
• Event subscriber abstraction
• Logging subscriber
• Metrics subscriber
• Audit subscriber
• Monitoring subscriber

=========================================================
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Any

logger = logging.getLogger(__name__)


# ==========================================================
# BASE SUBSCRIBER
# ==========================================================


class BaseSubscriber(ABC):
    """
    Base class for all event subscribers.
    """

    @abstractmethod
    def notify(
        self,
        event: str,
        **payload: Any,
    ) -> None:
        """
        Handle published event.
        """
        raise NotImplementedError


# ==========================================================
# LOGGING SUBSCRIBER
# ==========================================================


class LoggingSubscriber(BaseSubscriber):
    """
    Logs every published event.
    """

    def notify(
        self,
        event: str,
        **payload: Any,
    ) -> None:

        logger.info(
            "EVENT %-30s %s",
            event,
            payload,
        )


# ==========================================================
# METRICS SUBSCRIBER
# ==========================================================


class MetricsSubscriber(BaseSubscriber):
    """
    Records metrics events.

    Intended to integrate with
    MetricsCollector.
    """

    def notify(
        self,
        event: str,
        **payload: Any,
    ) -> None:

        logger.debug(
            "Metrics Event: %s",
            event,
        )


# ==========================================================
# AUDIT SUBSCRIBER
# ==========================================================


class AuditSubscriber(BaseSubscriber):
    """
    Records audit trail.

    Intended to integrate with
    AuditLogger.
    """

    def notify(
        self,
        event: str,
        **payload: Any,
    ) -> None:

        logger.debug(
            "Audit Event: %s",
            event,
        )


# ==========================================================
# MONITORING SUBSCRIBER
# ==========================================================


class MonitoringSubscriber(BaseSubscriber):
    """
    Platform monitoring subscriber.
    """

    def notify(
        self,
        event: str,
        **payload: Any,
    ) -> None:

        logger.debug(
            "Monitoring Event: %s",
            event,
        )


# ==========================================================
# NOTIFICATION SUBSCRIBER
# ==========================================================


class NotificationSubscriber(BaseSubscriber):
    """
    Placeholder for Slack, Email,
    Teams, Webhook notifications.
    """

    def notify(
        self,
        event: str,
        **payload: Any,
    ) -> None:

        logger.debug(
            "Notification Event: %s",
            event,
        )


# ==========================================================
# SUBSCRIBER REGISTRY
# ==========================================================


class SubscriberRegistry:
    """
    Stores subscribers and dispatches
    events to all of them.
    """

    def __init__(self) -> None:

        self._subscribers: list[BaseSubscriber] = []

    # ------------------------------------------------------

    def register(
        self,
        subscriber: BaseSubscriber,
    ) -> None:

        self._subscribers.append(subscriber)

    # ------------------------------------------------------

    def unregister(
        self,
        subscriber: BaseSubscriber,
    ) -> None:

        if subscriber in self._subscribers:
            self._subscribers.remove(subscriber)

    # ------------------------------------------------------

    def notify(
        self,
        event: str,
        **payload: Any,
    ) -> None:

        for subscriber in self._subscribers:
            subscriber.notify(
                event,
                **payload,
            )

    # ------------------------------------------------------

    def clear(
        self,
    ) -> None:

        self._subscribers.clear()

    # ------------------------------------------------------

    def __len__(
        self,
    ) -> int:

        return len(self._subscribers)

    # ------------------------------------------------------

    def __iter__(
        self,
    ):

        return iter(self._subscribers)

    # ------------------------------------------------------

    def __repr__(
        self,
    ) -> str:

        return f"{self.__class__.__name__}(subscribers={len(self)})"
