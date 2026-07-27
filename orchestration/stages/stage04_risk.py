"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Stage 04

Risk Pipeline Stage

Responsibilities
----------------
• Execute Risk Pipeline
• Validate portfolio risk
• Apply risk constraints
• Prepare portfolio construction

=========================================================
"""

from __future__ import annotations

from orchestration.pipelines.risk_pipeline import (
    main as risk_pipeline,
)

# ==========================================================
# STAGE
# ==========================================================


class RiskStage:
    """
    Stage 04 - Risk Pipeline.
    """

    STAGE = 4

    NAME = "Risk"

    DESCRIPTION = "Risk validation and constraint analysis."

    PIPELINE = risk_pipeline

    DEPENDENCIES = (3,)

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
