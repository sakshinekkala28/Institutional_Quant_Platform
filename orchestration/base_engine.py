"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Base Engine

Every executable analytics engine must inherit from
BaseEngine.

Responsibilities

• Standard execution lifecycle
• Runtime measurement
• Validation hooks
• Pre/Post execution hooks
• Dependency declaration
• Metadata exposure
• Retry configuration
• Timeout configuration
• Output registration
• Execution summary

=========================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from time import perf_counter
from typing import Any, ClassVar


class BaseEngine(ABC):
    """
    Base class for every engine in the platform.
    """

    # =====================================================
    # ENGINE METADATA
    # =====================================================

    NAME: str = "base_engine"

    DESCRIPTION: str = ""

    VERSION: str = "1.0.0"

    CATEGORY: str = "general"

    STAGE: str = "general"

    OWNER: str = "Institutional Quant Platform"

    ENABLED: bool = True

    CRITICAL: bool = True

    PRIORITY: int = 100

    PARALLELIZABLE: bool = False

    SUPPORTS_INCREMENTAL: bool = False

    CACHEABLE: bool = False

    MAX_RETRIES: int = 0

    RETRY_DELAY: int = 0

    TIMEOUT: int = 3600

    # =====================================================
    # DEPENDENCIES
    # =====================================================

    TAGS: ClassVar[list[str]] = []

    DEPENDS_ON: ClassVar[list[str]] = []

    INPUTS: ClassVar[list[str]] = []

    OUTPUTS: ClassVar[list[str]] = []

    # =====================================================
    # CONSTRUCTOR
    # =====================================================

    def __init__(self) -> None:

        self.started_at: datetime | None = None

        self.finished_at: datetime | None = None

        self.runtime_seconds: float = 0.0

        self.status: str = "PENDING"

    # =====================================================
    # REQUIRED IMPLEMENTATION
    # =====================================================

    @abstractmethod
    def execute(self, context) -> Any:
        """
        Execute engine logic.
        """
        raise NotImplementedError

    # =====================================================
    # OPTIONAL HOOKS
    # =====================================================

    def pre_execute(self, context) -> None:
        """
        Executed before execute().
        """
        return

    def post_execute(
        self,
        context,
        result: Any,
    ) -> None:
        """
        Executed after execute().
        """
        return

    def validate_inputs(self, context) -> None:
        """
        Optional input validation.
        """
        return

    def validate_outputs(self, context) -> None:
        """
        Optional output validation.
        """
        return

    # =====================================================
    # EXECUTION
    # =====================================================

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

            self.post_execute(
                context,
                result,
            )

            self.validate_outputs(context)

            self.status = "SUCCESS"

            return result

        except Exception:
            self.status = "FAILED"

            raise

        finally:
            self.runtime_seconds = perf_counter() - timer

            self.finished_at = datetime.utcnow()

    # =====================================================
    # METADATA
    # =====================================================

    @classmethod
    def metadata(cls) -> dict[str, Any]:
        """
        Return engine metadata.
        """

        return {
            "name": cls.NAME,
            "description": cls.DESCRIPTION,
            "version": cls.VERSION,
            "category": cls.CATEGORY,
            "stage": cls.STAGE,
            "owner": cls.OWNER,
            "tags": cls.TAGS,
            "enabled": cls.ENABLED,
            "critical": cls.CRITICAL,
            "priority": cls.PRIORITY,
            "parallelizable": cls.PARALLELIZABLE,
            "supports_incremental": cls.SUPPORTS_INCREMENTAL,
            "cacheable": cls.CACHEABLE,
            "max_retries": cls.MAX_RETRIES,
            "retry_delay": cls.RETRY_DELAY,
            "timeout": cls.TIMEOUT,
            "depends_on": cls.DEPENDS_ON,
            "inputs": cls.INPUTS,
            "outputs": cls.OUTPUTS,
        }

    # =====================================================
    # OUTPUT PATHS
    # =====================================================

    @classmethod
    def output_paths(cls) -> list[Path]:
        """
        Return outputs as pathlib objects.
        """

        return [Path(path) for path in cls.OUTPUTS]

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(self) -> dict[str, Any]:
        """
        Runtime summary.
        """

        return {
            "engine": self.NAME,
            "status": self.status,
            "started_at": (self.started_at.isoformat() if self.started_at else None),
            "finished_at": (self.finished_at.isoformat() if self.finished_at else None),
            "runtime_seconds": round(
                self.runtime_seconds,
                3,
            ),
        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}("
            f"name='{self.NAME}', "
            f"category='{self.CATEGORY}', "
            f"stage='{self.STAGE}', "
            f"status='{self.status}')"
        )
