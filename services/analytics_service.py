"""
======================================================================

Institutional Quant Platform

Analytics Service

Author
------
Institutional Quant Platform

Purpose
-------
Enterprise Analytics Orchestration Service.

Responsibilities
----------------
• Factor Analytics
• Performance Attribution
• Forecasting
• Regime Detection
• Optimization Diagnostics
• Risk Analytics
• Engine Orchestration

======================================================================
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from threading import Lock, RLock
from typing import Any

from core.services.base_service import BaseService

# ============================================================
# Exceptions
# ============================================================


class AnalyticsError(Exception):
    """Base analytics exception."""


class AnalyticsProfileNotFoundError(AnalyticsError):
    """Analytics profile not found."""


class AnalyticsEngineNotFoundError(AnalyticsError):
    """Analytics engine not registered."""


# ============================================================
# Analytics Profile
# ============================================================


@dataclass(slots=True)
class AnalyticsProfile:
    name: str

    description: str

    parameters: dict[str, Any] = field(default_factory=dict)

    metadata: dict[str, Any] = field(default_factory=dict)


# ============================================================
# Analytics Service
# ============================================================


class AnalyticsService(BaseService):
    """
    Enterprise Analytics Orchestrator.
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

        self._profiles: dict[str, AnalyticsProfile] = {}

        self._engines: dict[str, Callable] = {}

        self._enabled = True

        self._initialized = True

        self._logger.info("AnalyticsService initialized.")

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
    # Registration
    # =====================================================

    def register(
        self,
        name: str,
        description: str,
        parameters: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Register analytics profile.
        """

        profile = AnalyticsProfile(
            name=name,
            description=description,
            parameters=parameters or {},
            metadata=metadata or {},
        )

        with self._lock:
            self._profiles[name] = profile

    # =====================================================
    # Analytics Engine
    # =====================================================

    def register_engine(self, name: str, engine: Callable) -> None:
        """
        Register analytics engine.
        """

        self._engines[name] = engine

    # =====================================================
    # Retrieval
    # =====================================================

    def get(self, profile: str) -> AnalyticsProfile:

        if profile not in self._profiles:
            raise AnalyticsProfileNotFoundError(profile)

        return self._profiles[profile]

    # =====================================================
    # BaseService
    # =====================================================

    def run(self):

        return self.statistics()

    # =====================================================
    # Parameter Management
    # =====================================================

    def update_parameter(self, profile: str, name: str, value: Any) -> None:
        """
        Update analytics parameter.
        """

        self.get(profile).parameters[name] = value

    def parameter(self, profile: str, name: str, default: Any = None) -> Any:
        """
        Return analytics parameter.
        """

        return self.get(profile).parameters.get(name, default)

    # =====================================================
    # Engine Execution
    # =====================================================

    def execute(self, profile: str, engine: str, *args, **kwargs):
        """
        Execute analytics engine.
        """

        if engine not in self._engines:
            raise AnalyticsEngineNotFoundError(engine)

        analytics_engine = self._engines[engine]

        return analytics_engine(profile=self.get(profile), *args, **kwargs)

    # =====================================================
    # Standard Analytics
    # =====================================================

    def factor_analysis(self, profile: str, *args, **kwargs):

        return self.execute(profile, "factor_analysis", *args, **kwargs)

    def attribution(self, profile: str, *args, **kwargs):

        return self.execute(profile, "attribution", *args, **kwargs)

    def forecasting(self, profile: str, *args, **kwargs):

        return self.execute(profile, "forecasting", *args, **kwargs)

    def regime_detection(self, profile: str, *args, **kwargs):

        return self.execute(profile, "regime_detection", *args, **kwargs)

    def correlation_analysis(self, profile: str, *args, **kwargs):

        return self.execute(profile, "correlation_analysis", *args, **kwargs)

    def optimization_diagnostics(self, profile: str, *args, **kwargs):

        return self.execute(profile, "optimization_diagnostics", *args, **kwargs)

    def risk_analysis(self, profile: str, *args, **kwargs):

        return self.execute(profile, "risk_analysis", *args, **kwargs)

    # =====================================================
    # Validation
    # =====================================================

    def validate(self, profile: str) -> bool:
        """
        Validate analytics profile.
        """

        analytics_profile = self.get(profile)

        if not analytics_profile.name:
            raise AnalyticsError("Analytics profile name missing.")

        return True

    # =====================================================
    # Statistics
    # =====================================================

    def statistics(self) -> dict[str, Any]:
        """
        Analytics statistics.
        """

        return {
            "profiles": len(self._profiles),
            "engines": len(self._engines),
            "enabled": self._enabled,
        }

    # =====================================================
    # Metadata
    # =====================================================

    def metadata(self, profile: str) -> dict[str, Any]:
        """
        Return analytics metadata.
        """

        return dict(self.get(profile).metadata)

    def update_metadata(self, profile: str, **kwargs) -> None:
        """
        Update analytics metadata.
        """

        self.get(profile).metadata.update(kwargs)

    # =====================================================
    # Registry
    # =====================================================

    def exists(self, profile: str) -> bool:
        """
        Check whether profile exists.
        """

        return profile in self._profiles

    def names(self) -> list[str]:
        """
        Return registered analytics profiles.
        """

        return sorted(self._profiles.keys())

    def remove(self, profile: str) -> None:
        """
        Remove analytics profile.
        """

        if profile not in self._profiles:
            raise AnalyticsProfileNotFoundError(profile)

        del self._profiles[profile]

    def clear(self) -> None:
        """
        Clear analytics profiles and engines.
        """

        self._profiles.clear()

        self._engines.clear()

    # =====================================================
    # Snapshot
    # =====================================================

    def snapshot(self, profile: str) -> dict[str, Any]:
        """
        Analytics profile snapshot.
        """

        analytics = self.get(profile)

        return {
            "name": analytics.name,
            "description": analytics.description,
            "parameters": dict(analytics.parameters),
            "metadata": dict(analytics.metadata),
        }

    # =====================================================
    # Health
    # =====================================================

    def health(self) -> dict[str, Any]:
        """
        Analytics service health.
        """

        return {
            "status": "HEALTHY" if self._enabled else "DISABLED",
            "enabled": self._enabled,
            "profiles": len(self._profiles),
            "engines": len(self._engines),
        }

    # =====================================================
    # Lifecycle
    # =====================================================

    def startup(self) -> None:

        self.enable()

        self._logger.info("AnalyticsService started.")

    def shutdown(self) -> None:

        self.clear()

        self.disable()

        self._logger.info("AnalyticsService shutdown.")

    # =====================================================
    # Magic Methods
    # =====================================================

    def __contains__(self, profile: str) -> bool:

        return self.exists(profile)

    def __len__(self) -> int:

        return len(self._profiles)

    def __iter__(self):

        return iter(self._profiles.items())

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(profiles={len(self)}, "
            f"engines={len(self._engines)}, "
            f"enabled={self._enabled})"
        )


# ============================================================
# Global Singleton
# ============================================================

analytics_service = AnalyticsService()
