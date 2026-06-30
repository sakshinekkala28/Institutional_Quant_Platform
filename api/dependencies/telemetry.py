"""
====================================================================
Institutional Quant Platform

Telemetry Dependencies

Author : Institutional Quant Platform

Purpose
-------
FastAPI dependency providers for telemetry services.

Provides

• Telemetry Service
• Metrics Registry
• OpenTelemetry Provider
• Trace Manager
• Span Manager
• Performance Collector
• Metrics Exporter
• Distributed Tracing

Used By

• API Middleware
• Monitoring Router
• All Services
• Background Jobs

====================================================================
"""

from __future__ import annotations

from functools import lru_cache

from telemetry.telemetry_service import (
    TelemetryService,
)

from telemetry.metrics_registry import (
    MetricsRegistry,
)

from telemetry.opentelemetry_provider import (
    OpenTelemetryProvider,
)

from telemetry.trace_manager import (
    TraceManager,
)

from telemetry.span_manager import (
    SpanManager,
)

from telemetry.performance_collector import (
    PerformanceCollector,
)

from telemetry.metrics_exporter import (
    MetricsExporter,
)

from telemetry.distributed_tracing import (
    DistributedTracing,
)


# ==========================================================
# TELEMETRY SERVICE
# ==========================================================


@lru_cache
def get_telemetry(

) -> TelemetryService:
    """
    Primary telemetry service.
    """

    return TelemetryService()


# ==========================================================
# METRICS REGISTRY
# ==========================================================


@lru_cache
def get_metrics_registry(

) -> MetricsRegistry:
    """
    Metrics registry.
    """

    return MetricsRegistry()


# ==========================================================
# OPENTELEMETRY
# ==========================================================


@lru_cache
def get_opentelemetry(

) -> OpenTelemetryProvider:
    """
    OpenTelemetry provider.
    """

    return OpenTelemetryProvider()


# ==========================================================
# TRACE MANAGER
# ==========================================================


@lru_cache
def get_trace_manager(

) -> TraceManager:
    """
    Trace manager.
    """

    return TraceManager()


# ==========================================================
# SPAN MANAGER
# ==========================================================


@lru_cache
def get_span_manager(

) -> SpanManager:
    """
    Span manager.
    """

    return SpanManager()


# ==========================================================
# PERFORMANCE COLLECTOR
# ==========================================================


@lru_cache
def get_performance_collector(

) -> PerformanceCollector:
    """
    Performance collector.
    """

    return PerformanceCollector()


# ==========================================================
# METRICS EXPORTER
# ==========================================================


@lru_cache
def get_metrics_exporter(

) -> MetricsExporter:
    """
    Metrics exporter.
    """

    return MetricsExporter()


# ==========================================================
# DISTRIBUTED TRACING
# ==========================================================


@lru_cache
def get_distributed_tracing(

) -> DistributedTracing:
    """
    Distributed tracing service.
    """

    return DistributedTracing()


# ==========================================================
# HEALTH
# ==========================================================


def telemetry_health(

) -> dict:
    """
    Dependency health.
    """

    return {

        "engine": "TelemetryService",

        "status": "healthy",

        "singleton": True,

    }


# ==========================================================
# SUMMARY
# ==========================================================


def telemetry_summary(

) -> dict:
    """
    Registered telemetry services.
    """

    return {

        "services": [

            "TelemetryService",

            "MetricsRegistry",

            "OpenTelemetryProvider",

            "TraceManager",

            "SpanManager",

            "PerformanceCollector",

            "MetricsExporter",

            "DistributedTracing",

        ],

        "count": 8,

    }


# ==========================================================
# EXPORTS
# ==========================================================


__all__ = [

    "get_telemetry",

    "get_metrics_registry",

    "get_opentelemetry",

    "get_trace_manager",

    "get_span_manager",

    "get_performance_collector",

    "get_metrics_exporter",

    "get_distributed_tracing",

    "telemetry_health",

    "telemetry_summary",

]