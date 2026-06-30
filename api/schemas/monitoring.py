"""
====================================================================
Institutional Quant Platform

Monitoring API Schemas

Author : Institutional Quant Platform

Purpose
-------
Monitoring request/response schemas.

Provides

• Health Status
• System Metrics
• Telemetry
• Alerts
• Events
• Monitoring Summary
• Resource Usage

====================================================================
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from api.schemas.base import APIModel
from api.schemas.base import BaseResponse
from api.schemas.base import SuccessResponse


# ==========================================================
# HEALTH
# ==========================================================


class HealthStatus(
    APIModel,
):
    """
    Service health.
    """

    service: str

    status: Literal[
        "Healthy",
        "Warning",
        "Critical",
    ]

    timestamp: datetime = Field(

        default_factory=datetime.utcnow,

    )


# ==========================================================
# SYSTEM METRICS
# ==========================================================


class SystemMetrics(
    APIModel,
):
    """
    System resource usage.
    """

    cpu_percent: float

    memory_percent: float

    disk_percent: float

    network_sent_mb: float

    network_received_mb: float

    uptime_seconds: float


# ==========================================================
# TELEMETRY METRIC
# ==========================================================


class TelemetryMetric(
    APIModel,
):
    """
    Telemetry metric.
    """

    name: str

    value: float

    unit: str

    timestamp: datetime


# ==========================================================
# ALERT
# ==========================================================


class Alert(
    APIModel,
):
    """
    Monitoring alert.
    """

    alert_id: str

    severity: Literal[

        "INFO",

        "WARNING",

        "ERROR",

        "CRITICAL",

    ]

    component: str

    message: str

    created_at: datetime


# ==========================================================
# EVENT
# ==========================================================


class MonitoringEvent(
    APIModel,
):
    """
    Monitoring event.
    """

    event_id: str

    category: str

    message: str

    timestamp: datetime


# ==========================================================
# RESOURCE USAGE
# ==========================================================


class ResourceUsage(
    APIModel,
):
    """
    Resource usage.
    """

    cpu_percent: float

    memory_mb: float

    threads: int

    open_files: int


# ==========================================================
# MONITORING SUMMARY
# ==========================================================


class MonitoringSummary(
    APIModel,
):
    """
    Monitoring summary.
    """

    status: str

    total_alerts: int

    active_alerts: int

    warning_alerts: int

    critical_alerts: int

    services_online: int

    services_total: int

    updated_at: datetime = Field(

        default_factory=datetime.utcnow,

    )


# ==========================================================
# REQUEST
# ==========================================================


class MonitoringRequest(
    APIModel,
):
    """
    Monitoring request.
    """

    include_system_metrics: bool = True

    include_alerts: bool = True

    include_events: bool = True

    include_telemetry: bool = True


# ==========================================================
# RESPONSE
# ==========================================================


class MonitoringResponse(
    BaseResponse,
):
    """
    Monitoring response.
    """

    monitoring_id: str

    status: str


class HealthResponse(
    SuccessResponse,
):
    """
    Health response.
    """

    data: list[
        HealthStatus
    ]


class MonitoringSummaryResponse(
    SuccessResponse,
):
    """
    Summary response.
    """

    data: MonitoringSummary


class SystemMetricsResponse(
    SuccessResponse,
):
    """
    System metrics response.
    """

    data: SystemMetrics


class TelemetryResponse(
    SuccessResponse,
):
    """
    Telemetry response.
    """

    data: list[
        TelemetryMetric
    ]


class AlertResponse(
    SuccessResponse,
):
    """
    Alert response.
    """

    data: list[
        Alert
    ]


class EventResponse(
    SuccessResponse,
):
    """
    Event response.
    """

    data: list[
        MonitoringEvent
    ]


class ResourceUsageResponse(
    SuccessResponse,
):
    """
    Resource usage response.
    """

    data: ResourceUsage


# ==========================================================
# EXPORTS
# ==========================================================


__all__ = [

    "HealthStatus",

    "SystemMetrics",

    "TelemetryMetric",

    "Alert",

    "MonitoringEvent",

    "ResourceUsage",

    "MonitoringSummary",

    "MonitoringRequest",

    "MonitoringResponse",

    "HealthResponse",

    "MonitoringSummaryResponse",

    "SystemMetricsResponse",

    "TelemetryResponse",

    "AlertResponse",

    "EventResponse",

    "ResourceUsageResponse",

]