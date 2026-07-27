"""
======================================================================

Institutional Quant Platform

Report Service

Author
------
Institutional Quant Platform

Purpose
-------
Enterprise Reporting Service.

Responsibilities
----------------
• Performance Reports
• Portfolio Reports
• Risk Reports
• Trade Reports
• Compliance Reports
• Dashboard Exports
• Report Scheduling

======================================================================
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock, RLock
from typing import Any

from core.services.base_service import BaseService

# ============================================================
# Exceptions
# ============================================================


class ReportError(Exception):
    """Base report exception."""


class ReportProfileNotFound(ReportError):
    """Report profile not found."""


class ReportEngineNotFound(ReportError):
    """Report engine not registered."""


# ============================================================
# Report Profile
# ============================================================


@dataclass(slots=True)
class ReportProfile:
    name: str

    report_type: str

    output_format: str = "PDF"

    parameters: dict[str, Any] = field(default_factory=dict)

    metadata: dict[str, Any] = field(default_factory=dict)

    created_at: datetime = field(default_factory=datetime.utcnow)


# ============================================================
# Report Service
# ============================================================


class ReportService(BaseService):
    """
    Enterprise Reporting Manager.
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

        self._profiles: dict[str, ReportProfile] = {}

        self._engines: dict[str, Callable] = {}

        self._enabled = True

        self._initialized = True

        self._logger.info("ReportService initialized.")

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
        report_type: str,
        output_format: str = "PDF",
        parameters: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Register report profile.
        """

        profile = ReportProfile(
            name=name,
            report_type=report_type,
            output_format=output_format,
            parameters=parameters or {},
            metadata=metadata or {},
        )

        with self._lock:
            self._profiles[name] = profile

    # =====================================================
    # Report Engines
    # =====================================================

    def register_engine(self, name: str, engine: Callable) -> None:
        """
        Register report engine.
        """

        self._engines[name] = engine

    # =====================================================
    # Retrieval
    # =====================================================

    def get(self, profile: str) -> ReportProfile:

        if profile not in self._profiles:
            raise ReportProfileNotFound(profile)

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
        Update report parameter.
        """

        self.get(profile).parameters[name] = value

    def parameter(self, profile: str, name: str, default: Any = None) -> Any:
        """
        Return report parameter.
        """

        return self.get(profile).parameters.get(name, default)

    # =====================================================
    # Report Generation
    # =====================================================

    def generate(self, profile: str, engine: str, *args, **kwargs):
        """
        Generate report.
        """

        if engine not in self._engines:
            raise ReportEngineNotFound(engine)

        report_engine = self._engines[engine]

        return report_engine(profile=self.get(profile), *args, **kwargs)

    # =====================================================
    # Standard Reports
    # =====================================================

    def performance_report(self, profile: str, *args, **kwargs):

        return self.generate(profile, "performance", *args, **kwargs)

    def portfolio_report(self, profile: str, *args, **kwargs):

        return self.generate(profile, "portfolio", *args, **kwargs)

    def risk_report(self, profile: str, *args, **kwargs):

        return self.generate(profile, "risk", *args, **kwargs)

    def trade_report(self, profile: str, *args, **kwargs):

        return self.generate(profile, "trade", *args, **kwargs)

    def compliance_report(self, profile: str, *args, **kwargs):

        return self.generate(profile, "compliance", *args, **kwargs)

    def dashboard_report(self, profile: str, *args, **kwargs):

        return self.generate(profile, "dashboard", *args, **kwargs)

    # =====================================================
    # Export
    # =====================================================

    def export(self, profile: str, output_format: str, *args, **kwargs):
        """
        Export report using the requested format.
        """

        engine = f"export_{output_format.lower()}"

        return self.generate(profile, engine, *args, **kwargs)

    # =====================================================
    # Validation
    # =====================================================

    def validate(self, profile: str) -> bool:
        """
        Validate report profile.
        """

        report = self.get(profile)

        if not report.report_type:
            raise ReportError("Report type is required.")

        if not report.output_format:
            raise ReportError("Output format is required.")

        return True

    # =====================================================
    # Statistics
    # =====================================================

    def statistics(self) -> dict[str, Any]:
        """
        Report service statistics.
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
        Return report metadata.
        """

        return dict(self.get(profile).metadata)

    def update_metadata(self, profile: str, **kwargs) -> None:
        """
        Update report metadata.
        """

        self.get(profile).metadata.update(kwargs)

    # =====================================================
    # Registry
    # =====================================================

    def exists(self, profile: str) -> bool:
        """
        Check whether report profile exists.
        """

        return profile in self._profiles

    def names(self) -> list[str]:
        """
        Return registered report profiles.
        """

        return sorted(self._profiles.keys())

    def remove(self, profile: str) -> None:
        """
        Remove report profile.
        """

        if profile not in self._profiles:
            raise ReportProfileNotFound(profile)

        del self._profiles[profile]

    def clear(self) -> None:
        """
        Remove every report profile
        and registered engine.
        """

        self._profiles.clear()

        self._engines.clear()

    # =====================================================
    # Snapshot
    # =====================================================

    def snapshot(self, profile: str) -> dict[str, Any]:
        """
        Report profile snapshot.
        """

        report = self.get(profile)

        return {
            "name": report.name,
            "report_type": report.report_type,
            "output_format": report.output_format,
            "parameters": dict(report.parameters),
            "metadata": dict(report.metadata),
            "created_at": report.created_at.isoformat(),
        }

    # =====================================================
    # Health
    # =====================================================

    def health(self) -> dict[str, Any]:
        """
        Report service health.
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

        self._logger.info("ReportService started.")

    def shutdown(self) -> None:

        self.clear()

        self.disable()

        self._logger.info("ReportService shutdown.")

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

report_service = ReportService()
