"""
====================================================================
Institutional Quant Platform

Telemetry Dependencies

Author : Institutional Quant Platform

Purpose
-------
FastAPI dependency providers for telemetry services.

Provides

• Telemetry
• Metrics Registry
• Metric
• Event
• Cost Telemetry
• Logging Manager
• Audit Logger

Used By

• API Middleware
• Monitoring Router
• All Services
• Background Jobs

====================================================================
"""

from __future__ import annotations

from functools import lru_cache

from monitoring.telemetry import (
    Telemetry,
    Metric,
    Event,
)

from monitoring.metrics_registry import (
    MetricsRegistry,
)

from execution.transaction_cost_engine import (
    CostTelemetry,
)

from core.logging_manager import (
    LoggingManager,
)

from core.audit_logger import (
    AuditLogger,
)


# ==========================================================
# TELEMETRY
# ==========================================================


@lru_cache
def get_telemetry() -> Telemetry:
    """
    Primary telemetry service.
    """

    return Telemetry()


# ==========================================================
# METRICS REGISTRY
# ==========================================================


@lru_cache
def get_metrics_registry() -> MetricsRegistry:
    """
    Metrics registry.
    """

    return MetricsRegistry()


# ==========================================================
# METRIC
# ==========================================================


@lru_cache
def get_metric() -> Metric:
    """
    Metric model.
    """

    return Metric()


# ==========================================================
# EVENT
# ==========================================================


@lru_cache
def get_event() -> Event:
    """
    Telemetry event.
    """

    return Event()


# ==========================================================
# COST TELEMETRY
# ==========================================================


@lru_cache
def get_cost_telemetry() -> CostTelemetry:
    """
    Transaction-cost telemetry.
    """

    return CostTelemetry()


# ==========================================================
# LOGGING MANAGER
# ==========================================================


@lru_cache
def get_logging_manager() -> LoggingManager:
    """
    Platform logging manager.
    """

    return LoggingManager()


# ==========================================================
# AUDIT LOGGER
# ==========================================================


@lru_cache
def get_audit_logger() -> AuditLogger:
    """
    Audit logger.
    """

    return AuditLogger()


# ==========================================================
# HEALTH
# ==========================================================


def telemetry_health() -> dict:
    """
    Dependency health.
    """

    return {

        "engine": "Telemetry",

        "status": "healthy",

        "singleton": True,

    }


# ==========================================================
# SUMMARY
# ==========================================================


def telemetry_summary() -> dict:
    """
    Registered telemetry services.
    """

    return {

        "services": [

            "Telemetry",

            "MetricsRegistry",

            "Metric",

            "Event",

            "CostTelemetry",

            "LoggingManager",

            "AuditLogger",

        ],

        "count": 7,

    }


# ==========================================================
# EXPORTS
# ==========================================================


__all__ = [

    "get_telemetry",

    "get_metrics_registry",

    "get_metric",

    "get_event",

    "get_cost_telemetry",

    "get_logging_manager",

    "get_audit_logger",

    "telemetry_health",

    "telemetry_summary",

]