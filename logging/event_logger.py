"""
====================================================================
Institutional Quant Platform

Event Logger

Author : Institutional Quant Platform

Purpose
-------
Institutional application event logger.

Tracks

• Application Startup
• Application Shutdown
• Workflow Execution
• Pipeline Events
• Warnings
• Errors
• Exceptions
• Informational Events

Used By

• Monitoring
• Dashboard
• Telemetry
• Alert Engine

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import json
from pathlib import Path
import traceback


# ==========================================================
# EVENT
# ==========================================================


@dataclass(slots=True)
class ApplicationEvent:
    """
    Application event.
    """

    timestamp: datetime

    level: str

    component: str

    event: str

    message: str

    metadata: dict

    def summary(

        self,

    ) -> dict:

        return {

            "Timestamp":

                self.timestamp.isoformat(),

            "Level":

                self.level,

            "Component":

                self.component,

            "Event":

                self.event,

            "Message":

                self.message,

            "Metadata":

                self.metadata,

        }


# ==========================================================
# EVENT LOGGER
# ==========================================================


class EventLogger:
    """
    Institutional event logger.
    """

    def __init__(

        self,

    ) -> None:

        self._events: list[ApplicationEvent] = []

    # =====================================================
    # LOG
    # =====================================================

    def log(

        self,

        level: str,

        component: str,

        event: str,

        message: str,

        **metadata,

    ) -> None:

        self._events.append(

            ApplicationEvent(

                timestamp=datetime.utcnow(),

                level=level.upper(),

                component=component,

                event=event,

                message=message,

                metadata=metadata,

            )

        )

    # =====================================================
    # INFO
    # =====================================================

    def info(

        self,

        component: str,

        event: str,

        message: str,

        **metadata,

    ) -> None:

        self.log(

            "INFO",

            component,

            event,

            message,

            **metadata,

        )

    # =====================================================
    # WARNING
    # =====================================================

    def warning(

        self,

        component: str,

        event: str,

        message: str,

        **metadata,

    ) -> None:

        self.log(

            "WARNING",

            component,

            event,

            message,

            **metadata,

        )

    # =====================================================
    # ERROR
    # =====================================================

    def error(

        self,

        component: str,

        event: str,

        message: str,

        exception: Exception | None = None,

        **metadata,

    ) -> None:

        if exception is not None:

            metadata[

                "Exception"

            ] = str(

                exception

            )

            metadata[

                "Traceback"

            ] = traceback.format_exc()

        self.log(

            "ERROR",

            component,

            event,

            message,

            **metadata,

        )

    # =====================================================
    # CRITICAL
    # =====================================================

    def critical(

        self,

        component: str,

        event: str,

        message: str,

        **metadata,

    ) -> None:

        self.log(

            "CRITICAL",

            component,

            event,

            message,

            **metadata,

        )

    # =====================================================
    # FILTER LEVEL
    # =====================================================

    def by_level(

        self,

        level: str,

    ) -> list[ApplicationEvent]:

        return [

            event

            for event

            in self._events

            if event.level

            ==

            level.upper()

        ]

    # =====================================================
    # FILTER COMPONENT
    # =====================================================

    def by_component(

        self,

        component: str,

    ) -> list[ApplicationEvent]:

        return [

            event

            for event

            in self._events

            if event.component

            ==

            component

        ]

    # =====================================================
    # EXPORT
    # =====================================================

    def export(

        self,

        filename: str | Path,

    ) -> None:

        payload = [

            event.summary()

            for event

            in self._events

        ]

        with Path(

            filename

        ).open(

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

    ) -> list[ApplicationEvent]:

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

            "Info":

                len(

                    self.by_level(

                        "INFO"

                    )

                ),

            "Warnings":

                len(

                    self.by_level(

                        "WARNING"

                    )

                ),

            "Errors":

                len(

                    self.by_level(

                        "ERROR"

                    )

                ),

            "Critical":

                len(

                    self.by_level(

                        "CRITICAL"

                    )

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