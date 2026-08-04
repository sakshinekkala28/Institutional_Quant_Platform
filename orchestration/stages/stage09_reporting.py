"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Stage 09

Reporting Stage

Responsibilities
----------------
• Execute Reporting Pipeline
• Generate execution reports
• Export platform artifacts
• Produce audit outputs
• Finalize platform execution

=========================================================
"""

from __future__ import annotations

from orchestration.pipelines.reporting_pipeline import main as reporting_pipeline

# ==========================================================
# REPORTING STAGE
# ==========================================================


class ReportingStage:
    """
    Stage 09 - Reporting Pipeline.
    """

    STAGE = 9

    NAME = "Reporting"

    DESCRIPTION = "Execution reporting and artifact generation."

    PIPELINE = reporting_pipeline

    DEPENDENCIES = (8,)

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
