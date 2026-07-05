"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Audit Logger

Immutable audit trail for platform execution.

Responsibilities
----------------
• Engine audit
• Pipeline audit
• Platform audit
• Configuration snapshots
• Error recording
• Execution history

=========================================================
"""

from __future__ import annotations

import json
import logging

from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field

from datetime import datetime
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List

logger = logging.getLogger(__name__)


# =========================================================
# AUDIT EVENT
# =========================================================

@dataclass(slots=True)
class AuditEvent:
    """
    Immutable audit event.
    """

    event: str

    component: str

    timestamp: datetime = field(
        default_factory=datetime.utcnow
    )

    metadata: Dict[
        str,
        Any,
    ] = field(
        default_factory=dict
    )


# =========================================================
# AUDIT LOGGER
# =========================================================

class AuditLogger:
    """
    Platform audit logger.
    """

    def __init__(
        self,
        directory: str | Path = "audit",
    ) -> None:

        self.directory = Path(directory)

        self.directory.mkdir(

            parents=True,

            exist_ok=True,

        )

        self._events: List[
            AuditEvent
        ] = []

    # =====================================================
    # RECORD
    # =====================================================

    def record(
        self,
        event: str,
        component: str,
        **metadata: Any,
    ) -> None:
        """
        Record audit event.
        """

        self._events.append(

            AuditEvent(

                event=event,

                component=component,

                metadata=metadata,

            )

        )

    # =====================================================
    # HELPERS
    # =====================================================

    def engine_started(
        self,
        engine: str,
    ) -> None:

        self.record(

            "ENGINE_STARTED",

            engine,

        )

    # -----------------------------------------------------

    def engine_finished(
        self,
        engine: str,
        status: str,
        duration: float,
    ) -> None:

        self.record(

            "ENGINE_FINISHED",

            engine,

            status=status,

            duration=duration,

        )

    # -----------------------------------------------------

    def pipeline_started(
        self,
        pipeline: str,
    ) -> None:

        self.record(

            "PIPELINE_STARTED",

            pipeline,

        )

    # -----------------------------------------------------

    def pipeline_finished(
        self,
        pipeline: str,
        status: str,
    ) -> None:

        self.record(

            "PIPELINE_FINISHED",

            pipeline,

            status=status,

        )

    # -----------------------------------------------------

    def platform_started(
        self,
    ) -> None:

        self.record(

            "PLATFORM_STARTED",

            "platform",

        )

    # -----------------------------------------------------

    def platform_finished(
        self,
        status: str,
    ) -> None:

        self.record(

            "PLATFORM_FINISHED",

            "platform",

            status=status,

        )

    # -----------------------------------------------------

    def exception(
        self,
        component: str,
        exception: Exception,
    ) -> None:

        self.record(

            "EXCEPTION",

            component,

            message=str(exception),

        )

    # =====================================================
    # EXPORT
    # =====================================================

    def save(
        self,
        filename: str | None = None,
    ) -> Path:
        """
        Save audit log.
        """

        if filename is None:

            filename = (

                datetime.utcnow()

                .strftime(

                    "%Y%m%d_%H%M%S.json"

                )

            )

        path = self.directory / filename

        payload = [

            {

                **asdict(event),

                "timestamp":

                    event.timestamp.isoformat(),

            }

            for event

            in self._events

        ]

        path.write_text(

            json.dumps(

                payload,

                indent=4,

            ),

            encoding="utf-8",

        )

        logger.info(

            "Audit log written to %s",

            path,

        )

        return path

    # =====================================================
    # ACCESS
    # =====================================================

    @property
    def events(
        self,
    ) -> List[AuditEvent]:

        return list(

            self._events

        )

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(
        self,
    ) -> dict:

        return {

            "events":

                len(

                    self._events,

                ),

            "directory":

                str(

                    self.directory,

                ),

        }

    # =====================================================
    # RESET
    # =====================================================

    def clear(
        self,
    ) -> None:

        self._events.clear()

    # =====================================================
    # DUNDER
    # =====================================================

    def __len__(
        self,
    ) -> int:

        return len(

            self._events

        )

    def __repr__(
        self,
    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"events={len(self)})"

        )