"""
=========================================================
ENGINE RESULT
=========================================================

Shared execution result returned by every engine.

=========================================================
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class EngineResult:
    """
    Standard execution result for all platform engines.
    """

    engine: str
    status: str
    records: int = 0

    output: Path | None = None
    report: Path | None = None

    duration: float = 0.0

    metadata: dict[str, Any] = field(
        default_factory=dict
    )