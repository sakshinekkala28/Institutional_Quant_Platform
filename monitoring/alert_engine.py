"""
====================================================================
Institutional Quant Platform

Alert Engine

Author : Institutional Quant Platform

Purpose
-------
Institutional alert management engine.

Supports

• Health Alerts
• Risk Alerts
• Execution Alerts
• Data Alerts
• Signal Alerts
• System Alerts

Used By

• Health Monitor
• Dashboard
• Telemetry
• Scheduler

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from datetime import datetime


# ==========================================================
# ALERT
# ==========================================================


@dataclass(slots=True)
class Alert:
    """
    Institutional alert.
    """

    level: str

    source: str

    title: str

    message: str

    timestamp: datetime = field(

        default_factory=datetime.utcnow

    )

    acknowledged: bool = False

    metadata: dict = field(

        default_factory=dict

    )

    # =====================================================
    # ACKNOWLEDGE
    # =====================================================

    def acknowledge(

        self,

    ) -> None:

        self.acknowledged = True

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self,

    ) -> dict:

        return {

            "Level":

                self.level,

            "Source":

                self.source,

            "Title":

                self.title,

            "Message":

                self.message,

            "Timestamp":

                self.timestamp.isoformat(),

            "Acknowledged":

                self.acknowledged,

        }


# ==========================================================
# ALERT ENGINE
# ==========================================================


@dataclass(slots=True)
class AlertEngine:
    """
    Institutional alert engine.
    """

    alerts: list[Alert] = field(

        default_factory=list

    )

    __hash__ = None

    # =====================================================
    # CREATE ALERT
    # =====================================================

    def create(

        self,

        level: str,

        source: str,

        title: str,

        message: str,

        metadata: dict | None = None,

    ) -> Alert:

        alert = Alert(

            level=level.upper(),

            source=source,

            title=title,

            message=message,

            metadata=metadata or {},

        )

        self.alerts.append(

            alert

        )

        return alert

    # =====================================================
    # ACKNOWLEDGE
    # =====================================================

    def acknowledge(

        self,

        index: int,

    ) -> None:

        self.alerts[

            index

        ].acknowledge()

    # =====================================================
    # CLEAR
    # =====================================================

    def clear(

        self,

    ) -> None:

        self.alerts.clear()

    # =====================================================
    # FILTER
    # =====================================================

    def by_level(

        self,

        level: str,

    ) -> list[Alert]:

        level = level.upper()

        return [

            alert

            for alert

            in self.alerts

            if alert.level == level

        ]

    def by_source(

        self,

        source: str,

    ) -> list[Alert]:

        return [

            alert

            for alert

            in self.alerts

            if alert.source == source

        ]

    @property
    def active(

        self,

    ) -> list[Alert]:

        return [

            alert

            for alert

            in self.alerts

            if not alert.acknowledged

        ]

    # =====================================================
    # COUNTS
    # =====================================================

    @property
    def total(

        self,

    ) -> int:

        return len(

            self.alerts

        )

    @property
    def critical(

        self,

    ) -> int:

        return len(

            self.by_level(

                "CRITICAL"

            )

        )

    @property
    def warning(

        self,

    ) -> int:

        return len(

            self.by_level(

                "WARNING"

            )

        )

    @property
    def info(

        self,

    ) -> int:

        return len(

            self.by_level(

                "INFO"

            )

        )

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self,

    ) -> dict:

        return {

            "TotalAlerts":

                self.total,

            "Critical":

                self.critical,

            "Warnings":

                self.warning,

            "Information":

                self.info,

            "Active":

                len(

                    self.active

                ),

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ):

        return (

            f"{self.__class__.__name__}("

            f"Alerts={self.total}, "

            f"Critical={self.critical})"

        )

    __str__ = __repr__