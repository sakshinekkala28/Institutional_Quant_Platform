"""
====================================================================
Institutional Quant Platform

Monitoring Dependencies

Author : Institutional Quant Platform

Purpose
-------
FastAPI dependency providers for monitoring services.

Provides

• Monitoring Service
• Health Checker
• Metrics Collector
• Alert Manager
• Audit Service
• System Diagnostics
• Performance Monitor
• Event Logger

Used By

• Monitoring Router
• Portfolio Router
• Risk Router
• Execution Router
• API Middleware

====================================================================
"""

from __future__ import annotations

from functools import lru_cache

from monitoring.monitoring_service import (
    MonitoringService,
)

from monitoring.health_checker import (
    HealthChecker,
)

from monitoring.metrics_collector import (
    MetricsCollector,
)

from monitoring.alert_manager import (
    AlertManager,
)

from monitoring.audit_service import (
    AuditService,
)

from monitoring.system_diagnostics import (
    SystemDiagnostics,
)

from monitoring.performance_monitor import (
    PerformanceMonitor,
)

from monitoring.event_logger import (
    EventLogger,
)


# ==========================================================
# MONITORING SERVICE
# ==========================================================


@lru_cache
def get_monitoring_service(

) -> MonitoringService:
    """
    Primary monitoring service.
    """

    return MonitoringService()


# ==========================================================
# HEALTH CHECKER
# ==========================================================


@lru_cache
def get_health_checker(

) -> HealthChecker:
    """
    Health checker.
    """

    return HealthChecker()


# ==========================================================
# METRICS COLLECTOR
# ==========================================================


@lru_cache
def get_metrics_collector(

) -> MetricsCollector:
    """
    Metrics collector.
    """

    return MetricsCollector()


# ==========================================================
# ALERT MANAGER
# ==========================================================


@lru_cache
def get_alert_manager(

) -> AlertManager:
    """
    Alert manager.
    """

    return AlertManager()


# ==========================================================
# AUDIT SERVICE
# ==========================================================


@lru_cache
def get_audit_service(

) -> AuditService:
    """
    Audit service.
    """

    return AuditService()


# ==========================================================
# SYSTEM DIAGNOSTICS
# ==========================================================


@lru_cache
def get_system_diagnostics(

) -> SystemDiagnostics:
    """
    System diagnostics.
    """

    return SystemDiagnostics()


# ==========================================================
# PERFORMANCE MONITOR
# ==========================================================


@lru_cache
def get_performance_monitor(

) -> PerformanceMonitor:
    """
    Performance monitor.
    """

    return PerformanceMonitor()


# ==========================================================
# EVENT LOGGER
# ==========================================================


@lru_cache
def get_event_logger(

) -> EventLogger:
    """
    Event logger.
    """

    return EventLogger()


# ==========================================================
# HEALTH
# ==========================================================


def monitoring_health(

) -> dict:
    """
    Dependency health.
    """

    return {

        "engine": "MonitoringService",

        "status": "healthy",

        "singleton": True,

    }


# ==========================================================
# SUMMARY
# ==========================================================


def monitoring_summary(

) -> dict:
    """
    Registered monitoring services.
    """

    return {

        "services": [

            "MonitoringService",

            "HealthChecker",

            "MetricsCollector",

            "AlertManager",

            "AuditService",

            "SystemDiagnostics",

            "PerformanceMonitor",

            "EventLogger",

        ],

        "count": 8,

    }


# ==========================================================
# EXPORTS
# ==========================================================


__all__ = [

    "get_monitoring_service",

    "get_health_checker",

    "get_metrics_collector",

    "get_alert_manager",

    "get_audit_service",

    "get_system_diagnostics",

    "get_performance_monitor",

    "get_event_logger",

    "monitoring_health",

    "monitoring_summary",

]