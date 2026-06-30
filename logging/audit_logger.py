"""
====================================================================
Institutional Quant Platform

Audit Logger

Author : Institutional Quant Platform

Purpose
-------
Institutional immutable audit logger.

Tracks

• User Actions
• Configuration Changes
• Portfolio Changes
• Risk Events
• Order Events
• System Events

Used By

• Compliance
• Governance
• Dashboard
• Monitoring

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path


# ==========================================================
# AUDIT EVENT
# ==========================================================


@dataclass(slots=True)
class AuditEvent:
    """
    Immutable audit event.
    """

    timestamp: datetime

    user: str

    action: str

    resource: str

    details: dict

    success: bool

    source: str

    def summary(

        self,

    ) -> dict:

        return {

            "Timestamp":

                self.timestamp.isoformat(),

            "User":

                self.user,

            "Action":

                self.action,

            "Resource":

                self.resource,

            "Success":

                self.success,

            "Source":

                self.source,

            "Details":

                self.details,

        }


# ==========================================================
# AUDIT LOGGER
# ==========================================================


class AuditLogger:
    """
    Institutional audit logger.
    """

    def __init__(

        self,

    ) -> None:

        self._events: list[AuditEvent] = []

    # =====================================================
    # LOG
    # =====================================================

    def log(

        self,

        user: str,

        action: str,

        resource: str,

        success: bool,

        source: str = "SYSTEM",

        **details,

    ) -> None:

        event = AuditEvent(

            timestamp=datetime.utcnow(),

            user=user,

            action=action,

            resource=resource,

            details=details,

            success=success,

            source=source,

        )

        self._events.append(

            event

        )

    # =====================================================
    # FILTER USER
    # =====================================================

    def by_user(

        self,

        user: str,

    ) -> list[AuditEvent]:

        return [

            event

            for event

            in self._events

            if event.user == user

        ]

    # =====================================================
    # FILTER ACTION
    # =====================================================

    def by_action(

        self,

        action: str,

    ) -> list[AuditEvent]:

        return [

            event

            for event

            in self._events

            if event.action == action

        ]

    # =====================================================
    # FILTER RESOURCE
    # =====================================================

    def by_resource(

        self,

        resource: str,

    ) -> list[AuditEvent]:

        return [

            event

            for event

            in self._events

            if event.resource == resource

        ]

    # =====================================================
    # EXPORT JSON
    # =====================================================

    def export(

        self,

        filename: str | Path,

    ) -> None:

        path = Path(

            filename

        )

        payload = [

            event.summary()

            for event

            in self._events

        ]

        with path.open(

            "w",

            encoding="utf-8",

        ) as file:

            json.dump(

                payload,

                file,

                indent=4,

            )

    # =====================================================
    # CLEAR
    # =====================================================

    def clear(

        self,

    ) -> None:

        self._events.clear()

    # =====================================================
    # PROPERTIES
    # =====================================================

    @property
    def events(

        self,

    ) -> list[AuditEvent]:

        return list(

            self._events

        )

    @property
    def count(

        self,

    ) -> int:

        return len(

            self._events

        )

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self,

    ) -> dict:

        return {

            "Events":

                self.count,

            "Successful":

                sum(

                    event.success

                    for event

                    in self._events

                ),

            "Failed":

                sum(

                    not event.success

                    for event

                    in self._events

                ),

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Events={self.count})"

        )

    __str__ = __repr__