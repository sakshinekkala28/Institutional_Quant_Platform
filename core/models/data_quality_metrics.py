"""
====================================================================
Institutional Quant Platform

Data Quality Metrics

Author : Institutional Quant Platform

Purpose
-------
Standardized data quality metrics used across

• Validators
• Loaders
• Repositories
• Monitoring
• Audit
• Dashboards

====================================================================
"""

from __future__ import annotations

from dataclasses import asdict
from dataclasses import dataclass


@dataclass(slots=True)
class DataQualityMetrics:

    """
    Standard data quality metrics.
    """

    row_count: int

    column_count: int

    duplicate_percentage: float

    null_percentage: float

    completeness_score: float

    memory_usage_mb: float

    # =====================================================
    # EXPORT
    # =====================================================

    def to_dict(

        self

    ) -> dict:

        """
        Convert metrics
        to dictionary.
        """

        return asdict(

            self

        )

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self

    ) -> str:

        """
        Human-readable summary.
        """

        return (

            f"Rows={self.row_count:,} | "

            f"Columns={self.column_count} | "

            f"Duplicates={self.duplicate_percentage:.2f}% | "

            f"Nulls={self.null_percentage:.2f}% | "

            f"Completeness={self.completeness_score:.2f}% | "

            f"Memory={self.memory_usage_mb:.2f} MB"

        )

    # =====================================================
    # HEALTH SCORE
    # =====================================================

    @property

    def health_score(

        self

    ) -> float:

        """
        Overall data quality score.

        Returns

        0 - 100
        """

        score = 100.0

        score -= min(

            self.duplicate_percentage,

            100.0

        ) * 0.30

        score -= min(

            self.null_percentage,

            100.0

        ) * 0.50

        score -= max(

            0.0,

            100.0

            - self.completeness_score

        ) * 0.20

        return round(

            max(

                score,

                0.0

            ),

            2

        )

    # =====================================================
    # FLAGS
    # =====================================================

    @property

    def is_healthy(

        self

    ) -> bool:

        """
        Dataset health.
        """

        return (

            self.health_score >= 90.0

        )

    @property

    def is_warning(

        self

    ) -> bool:

        """
        Warning threshold.
        """

        return (

            75.0

            <= self.health_score

            < 90.0

        )

    @property

    def is_critical(

        self

    ) -> bool:

        """
        Critical threshold.
        """

        return (

            self.health_score

            < 75.0

        )

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self

    ) -> str:

        return (

            f"{self.__class__.__name__}"

            "("

            f"{self.summary()}"

            ")"

        )

    __str__ = __repr__