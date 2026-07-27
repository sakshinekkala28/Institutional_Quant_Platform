"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Stage 05

Portfolio Pipeline Stage

Responsibilities
----------------
• Execute Portfolio Pipeline
• Portfolio optimization
• Position sizing
• Weight normalization
• Portfolio validation

=========================================================
"""

from __future__ import annotations

from orchestration.pipelines.portfolio_pipeline import (
    main as portfolio_pipeline,
)

# ==========================================================
# STAGE
# ==========================================================


class PortfolioStage:
    """
    Stage 05 - Portfolio Pipeline.
    """

    STAGE = 5

    NAME = "Portfolio"

    DESCRIPTION = "Portfolio construction and optimization."

    PIPELINE = portfolio_pipeline

    DEPENDENCIES = (4,)

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
    # VALIDATION
    # =====================================================

    @classmethod
    def validate(cls) -> bool:
        """
        Validate stage configuration.
        """

        return cls.ENABLED and callable(cls.PIPELINE)

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
