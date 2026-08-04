"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Stage 03

Alpha Pipeline Stage

Responsibilities
----------------
• Execute Alpha Pipeline
• Generate alpha signals
• Validate signal quality
• Produce alpha universe

=========================================================
"""

from __future__ import annotations

from orchestration.pipelines.alpha_pipeline import main as alpha_pipeline

# ==========================================================
# STAGE
# ==========================================================


class AlphaStage:
    """
    Stage 03 - Alpha Pipeline.
    """

    STAGE = 3

    NAME = "Alpha"

    DESCRIPTION = "Alpha signal generation."

    PIPELINE = alpha_pipeline

    DEPENDENCIES = (2,)

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
