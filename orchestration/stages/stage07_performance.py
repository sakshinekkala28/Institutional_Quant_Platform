"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Stage 07

Performance Stage

Responsibilities
----------------
• Portfolio performance analysis
• Return attribution
• Benchmark comparison
• Performance statistics
• Performance reporting

=========================================================
"""

from __future__ import annotations

# ==========================================================
# IMPORTS
# ==========================================================
# Replace this import once a dedicated performance pipeline
# has been implemented.
from orchestration.pipelines.reporting_pipeline import (
    main as performance_pipeline,
)

# ==========================================================
# PERFORMANCE STAGE
# ==========================================================


class PerformanceStage:
    """
    Stage 07 - Performance Analysis.
    """

    STAGE = 7

    NAME = "Performance"

    DESCRIPTION = "Portfolio performance analysis."

    PIPELINE = performance_pipeline

    DEPENDENCIES = (6,)

    ENABLED = True

    # =====================================================
    # EXECUTION
    # =====================================================

    @classmethod
    def execute(cls):

        return cls.PIPELINE()

    # =====================================================
    # VALIDATION
    # =====================================================

    @classmethod
    def validate(cls) -> bool:

        return cls.ENABLED and callable(cls.PIPELINE)

    # =====================================================
    # METADATA
    # =====================================================

    @classmethod
    def metadata(cls) -> dict:

        return {
            "stage": cls.STAGE,
            "name": cls.NAME,
            "description": cls.DESCRIPTION,
            "dependencies": cls.DEPENDENCIES,
            "enabled": cls.ENABLED,
        }

    # =====================================================
    # SUMMARY
    # =====================================================

    @classmethod
    def summary(cls) -> dict:

        return {
            "stage": cls.STAGE,
            "pipeline": cls.PIPELINE.__name__,
            "enabled": cls.ENABLED,
        }

    # =====================================================
    # DUNDER
    # =====================================================

    def __repr__(self) -> str:

        return f"{self.__class__.__name__}(stage={self.STAGE}, name='{self.NAME}')"
