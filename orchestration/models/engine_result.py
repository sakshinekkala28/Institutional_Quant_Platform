"""
=========================================================
ENGINE RESULT
=========================================================

Purpose:
Standard execution result returned by every engine.

=========================================================
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from orchestration.models.engine_status import (
    EngineStatus,
)


@dataclass(slots=True)
class EngineResult:
    """
    Standard execution result for all platform engines.
    """

    engine: str

    status: EngineStatus

    records: int = 0

    output: Path | None = None

    report: Path | None = None

    duration: float = 0.0

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    # =====================================================
    # HELPERS
    # =====================================================

    @property
    def is_success(self) -> bool:

        return self.status == EngineStatus.SUCCESS

    @property
    def is_failed(self) -> bool:

        return self.status == EngineStatus.FAILED

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(
        self,
    ) -> dict[str, Any]:

        return {
            "engine": self.engine,
            "status": self.status.value,
            "records": self.records,
            "output": (str(self.output) if self.output else None),
            "report": (str(self.report) if self.report else None),
            "duration": self.duration,
            "metadata": self.metadata,
        }
