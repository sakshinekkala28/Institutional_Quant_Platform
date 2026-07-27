"""
======================================================================

Institutional Quant Platform

Monitoring Service

Author
------
Institutional Quant Platform

Purpose
-------
Enterprise monitoring framework.

Responsibilities
----------------
• Health Monitoring
• Service Status
• Alert Registration
• Threshold Monitoring
• Dependency Health
• Incident Tracking

======================================================================
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from threading import Lock, RLock
import time
from typing import Any

from core.services.base_service import BaseService

# ============================================================
# Exceptions
# ============================================================


class MonitoringError(Exception):
    """Base monitoring exception."""


class ServiceAlreadyRegistered(MonitoringError):
    """Raised when service already exists."""


class ServiceNotFound(MonitoringError):
    """Raised when service is unknown."""


# ============================================================
# Models
# ============================================================


@dataclass(slots=True)
class ServiceStatus:
    name: str

    status: str = "UNKNOWN"

    last_check: float = field(default_factory=time.time)

    message: str = ""

    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class AlertRule:
    name: str

    threshold: float

    comparator: Callable[[float, float], bool]

    enabled: bool = True

    description: str = ""


@dataclass(slots=True)
class Incident:
    service: str

    timestamp: float

    severity: str

    message: str


# ============================================================
# Monitoring Service
# ============================================================


class MonitoringService(BaseService):
    """
    Enterprise monitoring service.
    """

    _instance = None

    _instance_lock = Lock()

    def __new__(cls, *args, **kwargs):

        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):

        if getattr(self, "_initialized", False):
            return

        super().__init__()

        self._lock = RLock()

        self._services: dict[str, ServiceStatus] = {}

        self._alerts: dict[str, AlertRule] = {}

        self._incidents: list[Incident] = []

        self._enabled = True

        self._initialized = True

        self._logger.info("MonitoringService initialized.")

    # =====================================================
    # Lifecycle
    # =====================================================

    def enable(self):

        self._enabled = True

    def disable(self):

        self._enabled = False

    def enabled(self):

        return self._enabled

    # =====================================================
    # Service Registry
    # =====================================================

    def register_service(self, name: str):

        with self._lock:
            if name in self._services:
                raise ServiceAlreadyRegistered(name)

            self._services[name] = ServiceStatus(name=name)

    def unregister_service(self, name: str):

        with self._lock:
            self._services.pop(name, None)

    def service(self, name: str) -> ServiceStatus:

        if name not in self._services:
            raise ServiceNotFound(name)

        return self._services[name]

    # =====================================================
    # BaseService
    # =====================================================

    def run(self):

        return self.health()

    # =====================================================
    # Status Management
    # =====================================================

    def update_status(
        self,
        service: str,
        status: str,
        message: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Update service status.
        """

        with self._lock:
            instance = self.service(service)

            instance.status = status.upper()

            instance.message = message

            instance.last_check = time.time()

            if metadata:
                instance.metadata.update(metadata)

    # -----------------------------------------------------

    def heartbeat(self, service: str) -> None:
        """
        Record service heartbeat.
        """

        self.update_status(service, status="HEALTHY")

    # -----------------------------------------------------

    def healthy(self, service: str, message: str = "") -> None:

        self.update_status(service, status="HEALTHY", message=message)

    # -----------------------------------------------------

    def warning(self, service: str, message: str) -> None:

        self.update_status(service, status="WARNING", message=message)

    # -----------------------------------------------------

    def unhealthy(self, service: str, message: str) -> None:

        self.update_status(service, status="UNHEALTHY", message=message)

    # =====================================================
    # Alert Rules
    # =====================================================

    def register_alert(
        self,
        name: str,
        threshold: float,
        comparator: Callable[[float, float], bool],
        description: str = "",
    ) -> None:
        """
        Register alert rule.
        """

        with self._lock:
            self._alerts[name] = AlertRule(
                name=name,
                threshold=threshold,
                comparator=comparator,
                description=description,
            )

    # -----------------------------------------------------

    def enable_alert(self, name: str) -> None:

        if name in self._alerts:
            self._alerts[name].enabled = True

    # -----------------------------------------------------

    def disable_alert(self, name: str) -> None:

        if name in self._alerts:
            self._alerts[name].enabled = False

    # -----------------------------------------------------

    def evaluate_alert(self, name: str, value: float) -> bool:
        """
        Evaluate alert rule.
        """

        if name not in self._alerts:
            return False

        rule = self._alerts[name]

        if not rule.enabled:
            return False

        return rule.comparator(value, rule.threshold)

    # =====================================================
    # Incidents
    # =====================================================

    def create_incident(self, service: str, severity: str, message: str) -> Incident:
        """
        Record monitoring incident.
        """

        incident = Incident(
            service=service,
            timestamp=time.time(),
            severity=severity.upper(),
            message=message,
        )

        with self._lock:
            self._incidents.append(incident)

        self._logger.warning("[%s] %s : %s", severity, service, message)

        return incident

    # -----------------------------------------------------

    def incidents(self) -> list[Incident]:

        return list(self._incidents)

    # -----------------------------------------------------

    def clear_incidents(self) -> None:

        self._incidents.clear()

    # =====================================================
    # Metadata
    # =====================================================

    def update_metadata(self, service: str, **metadata) -> None:
        """
        Update service metadata.
        """

        instance = self.service(service)

        instance.metadata.update(metadata)

    # =====================================================
    # Queries
    # =====================================================

    def services(self) -> dict[str, ServiceStatus]:

        return dict(self._services)

    def service_names(self) -> list[str]:

        return sorted(self._services.keys())

    def status(self, service: str) -> str:

        return self.service(service).status

    def exists(self, service: str) -> bool:

        return service in self._services

    # =====================================================
    # Dependency Monitoring
    # =====================================================

    def register_dependency(self, service: str, dependency: str) -> None:
        """
        Register a service dependency.
        """

        instance = self.service(service)

        dependencies = instance.metadata.setdefault("dependencies", [])

        if dependency not in dependencies:
            dependencies.append(dependency)

    # -----------------------------------------------------

    def dependencies(self, service: str) -> list[str]:

        return list(self.service(service).metadata.get("dependencies", []))

    # =====================================================
    # Health Score
    # =====================================================

    def health_score(self) -> float:
        """
        Calculate overall platform health score.
        """

        if not self._services:
            return 100.0

        score = 0.0

        for service in self._services.values():
            if service.status == "HEALTHY":
                score += 100

            elif service.status == "WARNING":
                score += 60

            elif service.status == "UNHEALTHY":
                score += 0

            else:
                score += 25

        return round(score / len(self._services), 2)

    # =====================================================
    # Uptime
    # =====================================================

    def uptime(self, service: str) -> float:
        """
        Seconds since last heartbeat.
        """

        return time.time() - self.service(service).last_check

    # =====================================================
    # Dashboard
    # =====================================================

    def dashboard(self) -> dict[str, Any]:
        """
        Monitoring dashboard.
        """

        services = []

        for item in self._services.values():
            services.append(
                {
                    "service": item.name,
                    "status": item.status,
                    "message": item.message,
                    "last_check": item.last_check,
                    "uptime_seconds": round(self.uptime(item.name), 2),
                }
            )

        return {
            "health_score": self.health_score(),
            "services": services,
            "incident_count": len(self._incidents),
        }

    # =====================================================
    # Health Report
    # =====================================================

    def health(self) -> dict[str, Any]:
        """
        Platform health.
        """

        return {
            "status": ("HEALTHY" if self.health_score() >= 80 else "WARNING"),
            "health_score": self.health_score(),
            "registered_services": len(self._services),
            "alerts": len(self._alerts),
            "incidents": len(self._incidents),
        }

    # =====================================================
    # Statistics
    # =====================================================

    def statistics(self) -> dict[str, Any]:

        healthy = sum(
            1 for service in self._services.values() if service.status == "HEALTHY"
        )

        warning = sum(
            1 for service in self._services.values() if service.status == "WARNING"
        )

        unhealthy = sum(
            1 for service in self._services.values() if service.status == "UNHEALTHY"
        )

        return {
            "services": len(self._services),
            "healthy": healthy,
            "warning": warning,
            "unhealthy": unhealthy,
            "incidents": len(self._incidents),
            "alerts": len(self._alerts),
        }

    # =====================================================
    # Maintenance
    # =====================================================

    def cleanup(self) -> None:
        """
        Remove stale incidents.
        """

        cutoff = time.time() - 30 * 24 * 3600

        self._incidents = [
            incident for incident in self._incidents if incident.timestamp >= cutoff
        ]

    # =====================================================
    # Lifecycle
    # =====================================================

    def startup(self) -> None:

        self.enable()

        self._logger.info("Monitoring service started.")

    def shutdown(self) -> None:

        self.cleanup()

        self.disable()

        self._logger.info("Monitoring service shutdown.")

    # =====================================================
    # Magic Methods
    # =====================================================

    def __contains__(self, service: str) -> bool:

        return self.exists(service)

    def __len__(self) -> int:

        return len(self._services)

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(services={len(self)}, "
            f"health={self.health_score()}%)"
        )


# ============================================================
# Global Singleton
# ============================================================

monitoring_service = MonitoringService()
