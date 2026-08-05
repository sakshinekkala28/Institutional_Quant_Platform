"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Health Manager

Central health monitoring service for the platform.

Responsibilities
----------------
• Resource health checks
• Adapter health checks
• Plugin health checks
• Engine health checks
• Platform readiness
• Platform liveness

=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
import logging
from typing import Any

logger = logging.getLogger(__name__)


# =========================================================
# HEALTH STATUS
# =========================================================


class HealthStatus(StrEnum):
    HEALTHY = "HEALTHY"

    WARNING = "WARNING"

    UNHEALTHY = "UNHEALTHY"

    UNKNOWN = "UNKNOWN"


# =========================================================
# HEALTH RECORD
# =========================================================


@dataclass(slots=True)
class HealthRecord:
    component: str

    status: HealthStatus

    message: str = ""

    timestamp: datetime = datetime.utcnow()

    metadata: dict[str, Any] | None = None


# =========================================================
# HEALTH MANAGER
# =========================================================


class HealthManager:
    """
    Platform health manager.
    """

    def __init__(self) -> None:

        self._checks: dict[
            str,
            callable,
        ] = {}

        self._results: dict[
            str,
            HealthRecord,
        ] = {}

    # =====================================================
    # REGISTRATION
    # =====================================================

    def register(
        self,
        name: str,
        check,
    ) -> None:
        """
        Register health check.
        """

        self._checks[name] = check

    # =====================================================
    # RUN SINGLE
    # =====================================================

    def check(
        self,
        name: str,
    ) -> HealthRecord:

        if name not in self._checks:
            raise KeyError(f"Unknown health check '{name}'.")

        try:
            result = self._checks[name]()

            if isinstance(
                result,
                HealthRecord,
            ):
                record = result

            elif result:
                record = HealthRecord(
                    component=name,
                    status=HealthStatus.HEALTHY,
                )

            else:
                record = HealthRecord(
                    component=name,
                    status=HealthStatus.UNHEALTHY,
                )

        except Exception as exc:
            logger.exception("Health check failed.")

            record = HealthRecord(
                component=name,
                status=HealthStatus.UNHEALTHY,
                message=str(exc),
            )

        self._results[name] = record

        return record

    # =====================================================
    # RUN ALL
    # =====================================================

    def check_all(
        self,
    ) -> list[HealthRecord]:

        return [self.check(name) for name in sorted(self._checks)]

    # =====================================================
    # READY
    # =====================================================

    def is_ready(
        self,
    ) -> bool:

        self.check_all()

        return all(
            record.status == HealthStatus.HEALTHY for record in self._results.values()
        )

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(
        self,
    ) -> dict:

        healthy = sum(
            1
            for record in self._results.values()
            if record.status == HealthStatus.HEALTHY
        )

        unhealthy = sum(
            1
            for record in self._results.values()
            if record.status == HealthStatus.UNHEALTHY
        )

        warning = sum(
            1
            for record in self._results.values()
            if record.status == HealthStatus.WARNING
        )

        return {
            "registered": len(
                self._checks,
            ),
            "healthy": healthy,
            "warning": warning,
            "unhealthy": unhealthy,
            "ready": self.is_ready(),
        }

    # =====================================================
    # RESULTS
    # =====================================================

    @property
    def results(
        self,
    ) -> dict[str, HealthRecord]:

        return dict(self._results)

    # =====================================================
    # DUNDER
    # =====================================================

    def __len__(
        self,
    ) -> int:

        return len(self._checks)

    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}(checks={len(self)}, healthy={self.is_ready()})"
        )
