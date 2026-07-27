"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Stage 01

Data Pipeline Stage

Responsibilities
----------------
• Execute Data Pipeline
• Validate execution
• Define stage metadata

=========================================================
"""

from __future__ import annotations

from orchestration.pipelines.data_pipeline import (
    main as data_pipeline,
)

# ==========================================================
# STAGE
# ==========================================================


class DataStage:
    """
    Stage 01 - Data Pipeline.
    """

    STAGE = 1

    NAME = "Data"

    DESCRIPTION = "Data acquisition and preprocessing."

    PIPELINE = data_pipeline

    DEPENDENCIES: tuple[int, ...] = ()

    ENABLED = True

    # =====================================================
    # EXECUTION
    # =====================================================

    @classmethod
    def execute(cls):

        return cls.PIPELINE()

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
    # DUNDER
    # =====================================================

    def __repr__(self) -> str:

        return f"{self.__class__.__name__}(stage={self.STAGE})"
