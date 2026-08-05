"""
=========================================================
ENGINE STATUS
=========================================================

Purpose:
Centralized execution status enumeration used by
EngineResult and PipelineResult.

=========================================================
"""

from enum import StrEnum


class EngineStatus(StrEnum):
    """
    Standard execution lifecycle for platform engines.
    """

    # =====================================================
    # PRE-EXECUTION
    # =====================================================

    PENDING = "PENDING"

    RUNNING = "RUNNING"

    # =====================================================
    # SUCCESS STATES
    # =====================================================

    SUCCESS = "SUCCESS"

    SKIPPED = "SKIPPED"

    WARNING = "WARNING"

    # =====================================================
    # FAILURE STATES
    # =====================================================

    FAILED = "FAILED"

    CANCELLED = "CANCELLED"

    UNKNOWN = "UNKNOWN"

    # =====================================================
    # HELPERS
    # =====================================================

    @property
    def is_terminal(self) -> bool:
        """
        Returns True when execution has completed.
        """

        return self in {
            EngineStatus.SUCCESS,
            EngineStatus.SKIPPED,
            EngineStatus.WARNING,
            EngineStatus.FAILED,
            EngineStatus.CANCELLED,
            EngineStatus.UNKNOWN,
        }

    @property
    def is_success(self) -> bool:
        """
        Returns True when execution completed successfully.
        """

        return self in {
            EngineStatus.SUCCESS,
            EngineStatus.SKIPPED,
            EngineStatus.WARNING,
        }


__all__ = [
    "EngineStatus",
]
