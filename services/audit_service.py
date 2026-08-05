"""
======================================================================

Institutional Quant Platform

Audit Service

Author
------
Institutional Quant Platform

Purpose
-------
Enterprise audit framework.

Responsibilities
----------------
• Audit logging
• Compliance
• Change tracking
• User activity
• System events
• Portfolio events
• Risk events

======================================================================
"""

from __future__ import annotations

from pathlib import Path

from dataclasses import dataclass, field
from threading import Lock, RLock
import time
from typing import Any
import uuid
import json

from core.services.base_service import BaseService

# ============================================================
# Exceptions
# ============================================================


class AuditError(Exception):
    """Base audit exception."""


# ============================================================
# Audit Event
# ============================================================


@dataclass(slots=True)
class AuditEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    timestamp: float = field(default_factory=time.time)

    event_type: str = ""

    source: str = ""

    actor: str = "SYSTEM"

    severity: str = "INFO"

    action: str = ""

    message: str = ""

    metadata: dict[str, Any] = field(default_factory=dict)


# ============================================================
# Audit Service
# ============================================================


class AuditService(BaseService):
    """
    Enterprise audit manager.
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

        self._events: list[AuditEvent] = []

        self._enabled = True

        self._initialized = True

        self._logger.info("AuditService initialized.")

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
    # Record Event
    # =====================================================

    def record(
        self,
        event_type: str,
        source: str,
        action: str,
        message: str,
        actor: str = "SYSTEM",
        severity: str = "INFO",
        metadata: dict[str, Any] | None = None,
    ) -> AuditEvent:

        event = AuditEvent(
            event_type=event_type,
            source=source,
            actor=actor,
            severity=severity.upper(),
            action=action,
            message=message,
            metadata=metadata or {},
        )

        with self._lock:
            self._events.append(event)

        self._logger.info("[%s] %s - %s", event.event_type, event.source, event.action)

        return event

    # =====================================================
    # BaseService
    # =====================================================

    def run(self):

        return self.statistics()

    # =====================================================
    # Standard Audit Events
    # =====================================================

    def record_user_action(
        self,
        user: str,
        action: str,
        message: str,
        metadata: dict[str, Any] | None = None,
    ) -> AuditEvent:
        """
        Record a user initiated action.
        """

        return self.record(
            event_type="USER_ACTION",
            source="USER",
            actor=user,
            action=action,
            message=message,
            metadata=metadata,
        )

    # -----------------------------------------------------

    def record_system_event(
        self,
        source: str,
        action: str,
        message: str,
        severity: str = "INFO",
        metadata: dict[str, Any] | None = None,
    ) -> AuditEvent:

        return self.record(
            event_type="SYSTEM",
            source=source,
            actor="SYSTEM",
            severity=severity,
            action=action,
            message=message,
            metadata=metadata,
        )

    # -----------------------------------------------------

    def record_trade(
        self,
        trade_id: str,
        symbol: str,
        quantity: float,
        side: str,
        actor: str = "SYSTEM",
    ) -> AuditEvent:

        return self.record(
            event_type="TRADE",
            source="TradeService",
            actor=actor,
            action=f"{side.upper()} {symbol}",
            message=f"Trade executed ({trade_id})",
            metadata={
                "trade_id": trade_id,
                "symbol": symbol,
                "quantity": quantity,
                "side": side.upper(),
            },
        )

    # -----------------------------------------------------

    def record_portfolio_change(
        self,
        portfolio: str,
        description: str,
        actor: str = "SYSTEM",
        metadata: dict[str, Any] | None = None,
    ) -> AuditEvent:

        return self.record(
            event_type="PORTFOLIO",
            source="PortfolioService",
            actor=actor,
            action="PORTFOLIO_CHANGE",
            message=description,
            metadata={"portfolio": portfolio, **(metadata or {})},
        )

    # -----------------------------------------------------

    def record_risk_event(
        self,
        risk_type: str,
        message: str,
        severity: str = "WARNING",
        metadata: dict[str, Any] | None = None,
    ) -> AuditEvent:

        return self.record(
            event_type="RISK",
            source="RiskService",
            severity=severity,
            action=risk_type,
            message=message,
            metadata=metadata,
        )

    # -----------------------------------------------------

    def record_configuration_change(
        self,
        section: str,
        key: str,
        old_value: Any,
        new_value: Any,
        actor: str = "SYSTEM",
    ) -> AuditEvent:

        return self.record(
            event_type="CONFIGURATION",
            source="ConfigService",
            actor=actor,
            action="CONFIG_UPDATE",
            message=f"{section}.{key} updated",
            metadata={
                "section": section,
                "key": key,
                "old_value": old_value,
                "new_value": new_value,
            },
        )

    # =====================================================
    # Query
    # =====================================================

    def events(self) -> list[AuditEvent]:

        return list(self._events)

    # -----------------------------------------------------

    def by_type(self, event_type: str) -> list[AuditEvent]:

        return [event for event in self._events if event.event_type == event_type]

    # -----------------------------------------------------

    def by_source(self, source: str) -> list[AuditEvent]:

        return [event for event in self._events if event.source == source]

    # -----------------------------------------------------

    def by_actor(self, actor: str) -> list[AuditEvent]:

        return [event for event in self._events if event.actor == actor]

    # -----------------------------------------------------

    def by_severity(self, severity: str) -> list[AuditEvent]:

        severity = severity.upper()

        return [event for event in self._events if event.severity == severity]

    # -----------------------------------------------------

    def search(self, keyword: str) -> list[AuditEvent]:

        keyword = keyword.lower()

        return [
            event
            for event in self._events
            if keyword in event.message.lower() or keyword in event.action.lower()
        ]

    # =====================================================
    # Time Queries
    # =====================================================

    def between(self, start_timestamp: float, end_timestamp: float) -> list[AuditEvent]:
        """
        Return events within a time range.
        """

        return [
            event
            for event in self._events
            if start_timestamp <= event.timestamp <= end_timestamp
        ]

    # -----------------------------------------------------

    def latest(self, limit: int = 100) -> list[AuditEvent]:
        """
        Return latest audit events.
        """

        return sorted(self._events, key=lambda x: x.timestamp, reverse=True)[:limit]

    # =====================================================
    # Statistics
    # =====================================================

    def statistics(self) -> dict[str, Any]:
        """
        Audit statistics.
        """

        event_types: dict[str, int] = {}

        severity: dict[str, int] = {}

        sources: dict[str, int] = {}

        for event in self._events:
            event_types[event.event_type] = event_types.get(event.event_type, 0) + 1

            severity[event.severity] = severity.get(event.severity, 0) + 1

            sources[event.source] = sources.get(event.source, 0) + 1

        return {
            "total_events": len(self._events),
            "event_types": event_types,
            "severity": severity,
            "sources": sources,
        }

    # =====================================================
    # Compliance Report
    # =====================================================

    def compliance_report(self) -> dict[str, Any]:
        """
        Compliance summary.
        """

        critical = len(self.by_severity("CRITICAL"))

        errors = len(self.by_severity("ERROR"))

        warnings = len(self.by_severity("WARNING"))

        return {
            "total_events": len(self._events),
            "critical_events": critical,
            "error_events": errors,
            "warning_events": warnings,
            "user_events": len(self.by_type("USER_ACTION")),
            "trade_events": len(self.by_type("TRADE")),
            "risk_events": len(self.by_type("RISK")),
        }

    # =====================================================
    # Export
    # =====================================================

    def snapshot(self) -> list[dict[str, Any]]:
        """
        Export audit log.
        """

        return [
            {
                "event_id": event.event_id,
                "timestamp": event.timestamp,
                "event_type": event.event_type,
                "source": event.source,
                "actor": event.actor,
                "severity": event.severity,
                "action": event.action,
                "message": event.message,
                "metadata": dict(event.metadata),
            }
            for event in self._events
        ]

    def export_json(self, path: str) -> str:
        """
        Export audit log to JSON.
        """

        file = Path(path)

        file.parent.mkdir(parents=True, exist_ok=True)

        with file.open("w", encoding="utf-8") as handle:
            json.dump(self.snapshot(), handle, indent=4, default=str)

        return str(file)

    # =====================================================
    # Retention
    # =====================================================

    def cleanup(self, retention_days: int = 365) -> int:
        """
        Remove expired audit events.
        """

        cutoff = time.time() - retention_days * 24 * 3600

        before = len(self._events)

        self._events = [event for event in self._events if event.timestamp >= cutoff]

        return before - len(self._events)

    def clear(self) -> None:
        """
        Clear audit history.
        """

        self._events.clear()

    # =====================================================
    # Health
    # =====================================================

    def health(self) -> dict[str, Any]:
        """
        Health report.
        """

        return {
            "status": "HEALTHY" if self._enabled else "DISABLED",
            "enabled": self._enabled,
            "events": len(self._events),
        }

    # =====================================================
    # Lifecycle
    # =====================================================

    def startup(self) -> None:

        self.enable()

        self._logger.info("Audit service started.")

    def shutdown(self) -> None:

        self.cleanup()

        self.disable()

        self._logger.info("Audit service shutdown.")

    # =====================================================
    # Magic Methods
    # =====================================================

    def __len__(self) -> int:

        return len(self._events)

    def __iter__(self):

        return iter(self._events)

    def __repr__(self) -> str:

        return f"{self.__class__.__name__}(events={len(self)}, enabled={self._enabled})"


# ============================================================
# Global Singleton
# ============================================================

audit_service = AuditService()
