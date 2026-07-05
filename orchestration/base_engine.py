"""
Institutional Quant Platform
============================

Base Engine Interface

Every engine in the platform must inherit from BaseEngine.

Responsibilities
----------------
- Standard execution lifecycle
- Logging
- Runtime measurement
- Validation hooks
- Output tracking
- Dependency declaration

Author: Institutional Quant Platform
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from datetime import datetime
from time import perf_counter
from typing import Any, Dict, List, Optional


class BaseEngine(ABC):
    """
    Base class for every engine in the platform.

    Example
    -------
    class SignalEngine(BaseEngine):

        NAME = "signal_engine"

        DEPENDS_ON = [
            "factor_engine",
            "security_master"
        ]

        OUTPUTS = [
            "data/factors/signal_master.csv"
        ]

        def execute(self, context):
            ...
    """

    # ------------------------------------------------------------------
    # Engine Metadata
    # ------------------------------------------------------------------

    NAME: str = "base_engine"

    DESCRIPTION: str = ""

    VERSION: str = "1.0.0"

    STAGE: str = "general"

    ENABLED: bool = True

    # ------------------------------------------------------------------
    # Dependency Management
    # ------------------------------------------------------------------

    DEPENDS_ON: List[str] = []

    OUTPUTS: List[str] = []

    INPUTS: List[str] = []

    # ------------------------------------------------------------------

    def __init__(self) -> None:

        self.started_at: Optional[datetime] = None
        self.finished_at: Optional[datetime] = None

        self.runtime_seconds: float = 0.0

        self.status: str = "PENDING"

    # ------------------------------------------------------------------

    @abstractmethod
    def execute(self, context) -> Any:
        """
        Engine implementation.

        Must be implemented by every child engine.
        """
        raise NotImplementedError

    # ------------------------------------------------------------------

    def pre_execute(self, context) -> None:
        """
        Hook executed before execute().
        """

    # ------------------------------------------------------------------

    def post_execute(self, context, result: Any) -> None:
        """
        Hook executed after execute().
        """

    # ------------------------------------------------------------------

    def validate_inputs(self, context) -> None:
        """
        Optional validation hook.
        """

    # ------------------------------------------------------------------

    def validate_outputs(self, context) -> None:
        """
        Optional validation hook.
        """

    # ------------------------------------------------------------------

    def run(self, context) -> Any:
        """
        Standard execution lifecycle.
        """

        self.started_at = datetime.utcnow()

        timer = perf_counter()

        self.status = "RUNNING"

        try:

            self.validate_inputs(context)

            self.pre_execute(context)

            result = self.execute(context)

            self.post_execute(context, result)

            self.validate_outputs(context)

            self.status = "SUCCESS"

            return result

        except Exception:

            self.status = "FAILED"

            raise

        finally:

            self.runtime_seconds = perf_counter() - timer

            self.finished_at = datetime.utcnow()

    # ------------------------------------------------------------------

    @classmethod
    def metadata(cls) -> Dict[str, Any]:
        """
        Returns engine metadata.
        """

        return {
            "name": cls.NAME,
            "description": cls.DESCRIPTION,
            "version": cls.VERSION,
            "stage": cls.STAGE,
            "enabled": cls.ENABLED,
            "depends_on": cls.DEPENDS_ON,
            "inputs": cls.INPUTS,
            "outputs": cls.OUTPUTS,
        }

    # ------------------------------------------------------------------

    @classmethod
    def output_paths(cls) -> List[Path]:
        """
        Returns output paths as pathlib objects.
        """

        return [Path(path) for path in cls.OUTPUTS]

    # ------------------------------------------------------------------

    def summary(self) -> Dict[str, Any]:
        """
        Runtime summary.
        """

        return {
            "engine": self.NAME,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "finished_at": self.finished_at.isoformat() if self.finished_at else None,
            "runtime_seconds": round(self.runtime_seconds, 3),
        }

    # ------------------------------------------------------------------

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"name='{self.NAME}', "
            f"stage='{self.STAGE}', "
            f"status='{self.status}')"
        )