"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Stage 02

Factor Pipeline Stage

Responsibilities
----------------
• Execute Factor Pipeline
• Generate factor exposures
• Validate factor outputs

=========================================================
"""

from __future__ import annotations

from orchestration.pipelines.factor_pipeline import (
    main as factor_pipeline,
)


# ==========================================================
# STAGE
# ==========================================================

class FactorStage:
    """
    Stage 02 - Factor Pipeline.
    """

    STAGE = 2

    NAME = "Factors"

    DESCRIPTION = (
        "Factor generation and normalization."
    )

    PIPELINE = factor_pipeline

    DEPENDENCIES = (1,)

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

        return (

            f"{self.__class__.__name__}("

            f"stage={self.STAGE})"

        )