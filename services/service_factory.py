"""
======================================================================

Institutional Quant Platform

Service Factory

Author
------
Institutional Quant Platform

Purpose
-------
Enterprise Dependency Injection Container.

Responsibilities
----------------
• Service Registration
• Singleton Management
• Dependency Injection
• Service Discovery
• Lifecycle Management
• Startup / Shutdown
• Health Monitoring

======================================================================
"""

from __future__ import annotations

from threading import Lock, RLock
from typing import Any

from core.services.base_service import BaseService

# ============================================================
# Exceptions
# ============================================================


class ServiceFactoryError(Exception):
    """Base service factory exception."""


class ServiceAlreadyRegistered(ServiceFactoryError):
    """Service already exists."""


class ServiceNotRegistered(ServiceFactoryError):
    """Unknown service."""


# ============================================================
# Service Descriptor
# ============================================================


class ServiceDescriptor:
    def __init__(
        self, name: str, service_type: type[BaseService], singleton: bool = True
    ):

        self.name = name

        self.service_type = service_type

        self.singleton = singleton

        self.instance: BaseService | None = None


# ============================================================
# Service Factory
# ============================================================


class ServiceFactory:
    """
    Enterprise Dependency Injection Container.
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

        self._lock = RLock()

        self._services: dict[str, ServiceDescriptor] = {}

        self._initialized = True

    # =====================================================
    # Registration
    # =====================================================

    def register(
        self, name: str, service: type[BaseService], singleton: bool = True
    ) -> None:
        """
        Register service.
        """

        with self._lock:
            if name in self._services:
                raise ServiceAlreadyRegistered(name)

            self._services[name] = ServiceDescriptor(name, service, singleton)

    # =====================================================
    # Resolution
    # =====================================================

    def get(self, name: str) -> BaseService:
        """
        Resolve service.
        """

        if name not in self._services:
            raise ServiceNotRegistered(name)

        descriptor = self._services[name]

        if descriptor.singleton:
            if descriptor.instance is None:
                descriptor.instance = descriptor.service_type()

            return descriptor.instance

        return descriptor.service_type()

    # =====================================================
    # Discovery
    # =====================================================

    def exists(self, name: str) -> bool:

        return name in self._services

    def services(self) -> list[str]:

        return sorted(self._services.keys())

    # =====================================================
    # Base Operations
    # =====================================================

    def clear(self) -> None:

        self._services.clear()

    def __len__(self) -> int:

        return len(self._services)

    # =====================================================
    # Dependency Registration
    # =====================================================

    def register_dependency(self, service: str, dependency: str) -> None:
        """
        Register a service dependency.
        """

        if service not in self._services:
            raise ServiceNotRegistered(service)

        if dependency not in self._services:
            raise ServiceNotRegistered(dependency)

        descriptor = self._services[service]

        if not hasattr(descriptor, "dependencies"):
            descriptor.dependencies = []

        if dependency not in descriptor.dependencies:
            descriptor.dependencies.append(dependency)

    # -----------------------------------------------------

    def dependencies(self, service: str) -> list[str]:

        descriptor = self._services[service]

        return list(getattr(descriptor, "dependencies", []))

    # =====================================================
    # Resolve By Type
    # =====================================================

    def get_by_type(self, service_type: type[BaseService]) -> BaseService:
        """
        Resolve service by class.
        """

        for descriptor in self._services.values():
            if descriptor.service_type is service_type:
                return self.get(descriptor.name)

        raise ServiceNotRegistered(service_type.__name__)

    # =====================================================
    # Startup
    # =====================================================

    def startup(self) -> None:
        """
        Start all registered services.
        """

        for descriptor in self._services.values():
            service = self.get(descriptor.name)

            startup = getattr(service, "startup", None)

            if callable(startup):
                startup()

    # =====================================================
    # Shutdown
    # =====================================================

    def shutdown(self) -> None:
        """
        Shutdown all services.
        """

        services = list(self._services.values())

        services.reverse()

        for descriptor in services:
            service = self.get(descriptor.name)

            shutdown = getattr(service, "shutdown", None)

            if callable(shutdown):
                shutdown()

    # =====================================================
    # Health
    # =====================================================

    def health(self) -> dict[str, Any]:
        """
        Aggregate service health.
        """

        report = {}

        for descriptor in self._services.values():
            service = self.get(descriptor.name)

            health = getattr(service, "health", None)

            if callable(health):
                report[descriptor.name] = health()

            else:
                report[descriptor.name] = {"status": "UNKNOWN"}

        return report

    # =====================================================
    # Statistics
    # =====================================================

    def statistics(self) -> dict[str, Any]:
        """
        Factory statistics.
        """

        singleton_count = sum(
            1 for descriptor in self._services.values() if descriptor.singleton
        )

        instantiated = sum(
            1
            for descriptor in self._services.values()
            if descriptor.instance is not None
        )

        return {
            "registered_services": len(self._services),
            "singleton_services": singleton_count,
            "instantiated_services": instantiated,
        }

    # =====================================================
    # Diagnostics
    # =====================================================

    def diagnostics(self) -> dict[str, Any]:
        """
        Complete factory diagnostics.
        """

        return {
            "services": self.services(),
            "statistics": self.statistics(),
            "health": self.health(),
        }

    # =====================================================
    # Replace Service
    # =====================================================

    def replace(self, name: str, service_type: type[BaseService]) -> None:
        """
        Replace registered service.
        """

        if name not in self._services:
            raise ServiceNotRegistered(name)

        descriptor = self._services[name]

        descriptor.service_type = service_type

        descriptor.instance = None

    # =====================================================
    # Warmup
    # =====================================================

    def warmup(self) -> None:
        """
        Instantiate all singleton services.
        """

        for descriptor in self._services.values():
            if descriptor.singleton:
                self.get(descriptor.name)

    # =====================================================
    # Magic Methods
    # =====================================================

    def __contains__(self, service: str) -> bool:

        return self.exists(service)

    def __iter__(self):

        return iter(self._services.keys())

    def __repr__(self) -> str:

        return f"{self.__class__.__name__}(services={len(self._services)})"


# ============================================================
# Global Factory
# ============================================================

service_factory = ServiceFactory()
