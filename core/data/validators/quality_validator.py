"""
====================================================================
Institutional Quant Platform

Quality Validator

Author : Institutional Quant Platform

Purpose
-------
Validate dataset quality.

Responsibilities

• Null Thresholds
• Duplicate Thresholds
• Cardinality
• Memory Usage
• Freshness
• Completeness Score

====================================================================
"""

from __future__ import annotations

import pandas as pd

from core.data.validators.base_validator import (

    BaseValidator,

    ValidationIssue

)


class QualityValidator(

    BaseValidator

):

    """
    Institutional Quality Validator.
    """

    def __init__(

        self,

        max_duplicate_percentage: float = 0.0,

        max_null_percentage: float = 5.0,

        max_memory_mb: float | None = None,

        freshness_column: str | None = None,

        max_age_days: int | None = None

    ) -> None:

        self.max_duplicate_percentage = (

            max_duplicate_percentage

        )

        self.max_null_percentage = (

            max_null_percentage

        )

        self.max_memory_mb = (

            max_memory_mb

        )

        self.freshness_column = (

            freshness_column

        )

        self.max_age_days = (

            max_age_days

        )

    # =====================================================
    # VALIDATION
    # =====================================================

    def _validate(

        self,

        data: pd.DataFrame

    ) -> list[ValidationIssue]:

        issues: list[ValidationIssue] = []

        # -----------------------------------------------
        # Duplicate Percentage
        # -----------------------------------------------

        if len(data) > 0:

            duplicate_pct = (

                data

                .duplicated()

                .sum()

                / len(data)

            ) * 100

            if (

                duplicate_pct

                > self.max_duplicate_percentage

            ):

                issues.append(

                    self.warning(

                        f"Duplicate rows "

                        f"{duplicate_pct:.2f}% "

                        "exceed threshold."

                    )

                )

        # -----------------------------------------------
        # Null Percentage
        # -----------------------------------------------

        total_cells = (

            data.shape[0]

            * data.shape[1]

        )

        if total_cells > 0:

            null_percentage = (

                data

                .isna()

                .sum()

                .sum()

                / total_cells

            ) * 100

            if (

                null_percentage

                > self.max_null_percentage

            ):

                issues.append(

                    self.warning(

                        f"Null percentage "

                        f"{null_percentage:.2f}% "

                        "exceeds threshold."

                    )

                )

        # -----------------------------------------------
        # Memory Usage
        # -----------------------------------------------

        if (

            self.max_memory_mb

            is not None

        ):

            memory_mb = (

                data

                .memory_usage(

                    deep=True

                )

                .sum()

                / 1024

                / 1024

            )

            if (

                memory_mb

                > self.max_memory_mb

            ):

                issues.append(

                    self.warning(

                        f"Memory usage "

                        f"{memory_mb:.2f} MB "

                        "exceeds threshold."

                    )

                )

        # -----------------------------------------------
        # Data Freshness
        # -----------------------------------------------

        if (

            self.freshness_column

            is not None

            and

            self.max_age_days

            is not None

            and

            self.freshness_column

            in data.columns

        ):

            freshness = pd.to_datetime(

                data[

                    self.freshness_column

                ],

                errors="coerce"

            )

            latest = freshness.max()

            if pd.notna(

                latest

            ):

                age_days = (

                    pd.Timestamp.utcnow()

                    - latest

                ).days

                if (

                    age_days

                    > self.max_age_days

                ):

                    issues.append(

                        self.warning(

                            f"Dataset is "

                            f"{age_days} days old.",

                            self.freshness_column

                        )

                    )

        # -----------------------------------------------
        # Completeness Score
        # -----------------------------------------------

        completeness = (

            100.0

            if total_cells == 0

            else

            (

                1

                -

                (

                    data

                    .isna()

                    .sum()

                    .sum()

                    / total_cells

                )

            )

            * 100

        )

        if completeness < 95:

            issues.append(

                self.info(

                    f"Completeness "

                    f"Score "

                    f"{completeness:.2f}%."

                )

            )

        return issues