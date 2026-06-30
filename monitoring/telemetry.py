"""
====================================================================
Institutional Quant Platform

Telemetry

Author : Institutional Quant Platform

Purpose
-------
Central telemetry collection engine.

Collects

• System Metrics
• Performance Metrics
• Risk Metrics
• Execution Metrics
• Health Metrics
• Events

Used By

• Dashboard
• Alert Engine
• Monitoring
• Metrics Registry

====================================================================
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime

import statistics


# ==========================================================
# METRIC
# ==========================================================


@dataclass(slots=True)
class Metric:
    """
    Telemetry metric.
    """

    name: str

    value: float

    timestamp: datetime

    tags: dict


# ==========================================================
# EVENT
# ==========================================================


@dataclass(slots=True)
class Event:
    """
    Telemetry event.
    """

    name: str

    message: str

    severity: str

    timestamp: datetime

    metadata: dict


# ==========================================================
# TELEMETRY
# ==========================================================


class Telemetry:
    """
    Institutional telemetry engine.
    """

    def __init__(

        self,

    ) -> None:

        self._metrics = defaultdict(

            list

        )

        self._events = []

    # =====================================================
    # RECORD METRIC
    # =====================================================

    def record_metric(

        self,

        name: str,

        value: float,

        **tags,

    ) -> None:

        self._metrics[

            name

        ].append(

            Metric(

                name=name,

                value=float(

                    value

                ),

                timestamp=datetime.utcnow(),

                tags=tags,

            )

        )

    # =====================================================
    # RECORD EVENT
    # =====================================================

    def record_event(

        self,

        name: str,

        message: str,

        severity: str = "INFO",

        **metadata,

    ) -> None:

        self._events.append(

            Event(

                name=name,

                message=message,

                severity=severity.upper(),

                timestamp=datetime.utcnow(),

                metadata=metadata,

            )

        )

    # =====================================================
    # GET METRIC
    # =====================================================

    def metric(

        self,

        name: str,

    ) -> list[Metric]:

        return list(

            self._metrics.get(

                name,

                [],

            )

        )

    # =====================================================
    # LATEST
    # =====================================================

    def latest_metric(

        self,

        name: str,

    ) -> float | None:

        metrics = self.metric(

            name

        )

        if not metrics:

            return None

        return metrics[-1].value

    # =====================================================
    # STATISTICS
    # =====================================================

    def statistics(

        self,

        name: str,

    ) -> dict:

        metrics = [

            m.value

            for m

            in self.metric(

                name

            )

        ]

        if not metrics:

            return {}

        return {

            "Count":

                len(

                    metrics

                ),

            "Minimum":

                min(

                    metrics

                ),

            "Maximum":

                max(

                    metrics

                ),

            "Average":

                statistics.mean(

                    metrics

                ),

            "Median":

                statistics.median(

                    metrics

                ),

            "StdDev":

                statistics.pstdev(

                    metrics

                ),

        }

    # =====================================================
    # EVENTS
    # =====================================================

    @property
    def events(

        self,

    ) -> list[Event]:

        return list(

            self._events

        )

    # =====================================================
    # METRIC NAMES
    # =====================================================

    @property
    def metric_names(

        self,

    ) -> list[str]:

        return sorted(

            self._metrics.keys()

        )

    # =====================================================
    # CLEAR
    # =====================================================

    def clear(

        self,

    ) -> None:

        self._metrics.clear()

        self._events.clear()

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self,

    ) -> dict:

        return {

            "Metrics":

                len(

                    self.metric_names

                ),

            "Events":

                len(

                    self._events

                ),

            "MetricNames":

                self.metric_names,

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Metrics={len(self.metric_names)}, "

            f"Events={len(self._events)})"

        )

    __str__ = __repr__