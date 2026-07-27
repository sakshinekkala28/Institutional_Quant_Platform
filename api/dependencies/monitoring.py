"""
====================================================================
Institutional Quant Platform

Monitoring Dependencies

Author : Institutional Quant Platform

Purpose
-------
FastAPI dependency providers for monitoring services.

Provides

• Live Portfolio Monitor
• System Monitor
• Health Monitor
• Risk Monitor
• Signal Monitor
• Execution Monitor
• Portfolio Monitor
• Data Monitor
• Metrics Registry
• Alert Engine

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

from monitoring.alert_engine import (
    AlertEngine,
)
from monitoring.data_monitor import (
    DataMonitor,
)
from monitoring.execution_monitor import (
    ExecutionMonitor,
)
from monitoring.health_monitor import (
    HealthMonitor,
)
from monitoring.live_portfolio_monitor import (
    LivePortfolioMonitor,
)
from monitoring.metrics_registry import (
    MetricsRegistry,
)
from monitoring.portfolio_monitor import (
    PortfolioMonitor,
)
from monitoring.risk_monitor import (
    RiskMonitor,
)
from monitoring.signal_monitor import (
    SignalMonitor,
)
from monitoring.system_monitor import (
    SystemMonitor,
)

# ==========================================================
# LIVE PORTFOLIO MONITOR
# ==========================================================


@lru_cache
def get_live_portfolio_monitor() -> LivePortfolioMonitor:
    """
    Live portfolio monitor.
    """

    return LivePortfolioMonitor()


# ==========================================================
# SYSTEM MONITOR
# ==========================================================


@lru_cache
def get_system_monitor() -> SystemMonitor:
    """
    System monitor.
    """

    return SystemMonitor()


# ==========================================================
# HEALTH MONITOR
# ==========================================================


@lru_cache
def get_health_monitor() -> HealthMonitor:
    """
    Health monitor.
    """

    return HealthMonitor()


# ==========================================================
# RISK MONITOR
# ==========================================================


@lru_cache
def get_risk_monitor() -> RiskMonitor:
    """
    Risk monitor.
    """

    return RiskMonitor()


# ==========================================================
# SIGNAL MONITOR
# ==========================================================


@lru_cache
def get_signal_monitor() -> SignalMonitor:
    """
    Signal monitor.
    """

    return SignalMonitor()


# ==========================================================
# EXECUTION MONITOR
# ==========================================================


@lru_cache
def get_execution_monitor() -> ExecutionMonitor:
    """
    Execution monitor.
    """

    return ExecutionMonitor()


# ==========================================================
# PORTFOLIO MONITOR
# ==========================================================


@lru_cache
def get_portfolio_monitor() -> PortfolioMonitor:
    """
    Portfolio monitor.
    """

    return PortfolioMonitor()


# ==========================================================
# DATA MONITOR
# ==========================================================


@lru_cache
def get_data_monitor() -> DataMonitor:
    """
    Data monitor.
    """

    return DataMonitor()


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
# ALERT ENGINE
# ==========================================================


@lru_cache
def get_alert_engine() -> AlertEngine:
    """
    Alert engine.
    """

    return AlertEngine()


# ==========================================================
# HEALTH
# ==========================================================


def monitoring_health() -> dict:
    """
    Dependency health.
    """

    return {
        "engine": "LivePortfolioMonitor",
        "status": "healthy",
        "singleton": True,
    }


# ==========================================================
# SUMMARY
# ==========================================================


def monitoring_summary() -> dict:
    """
    Registered monitoring services.
    """

    return {
        "services": [
            "LivePortfolioMonitor",
            "SystemMonitor",
            "HealthMonitor",
            "RiskMonitor",
            "SignalMonitor",
            "ExecutionMonitor",
            "PortfolioMonitor",
            "DataMonitor",
            "MetricsRegistry",
            "AlertEngine",
        ],
        "count": 10,
    }


# ==========================================================
# EXPORTS
# ==========================================================


__all__ = [
    "get_alert_engine",
    "get_data_monitor",
    "get_execution_monitor",
    "get_health_monitor",
    "get_live_portfolio_monitor",
    "get_metrics_registry",
    "get_portfolio_monitor",
    "get_risk_monitor",
    "get_signal_monitor",
    "get_system_monitor",
    "monitoring_health",
    "monitoring_summary",
]
