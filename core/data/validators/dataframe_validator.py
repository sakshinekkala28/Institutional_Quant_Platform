"""
====================================================================
Institutional Quant Platform

DataFrame Validator

Author : Institutional Quant Platform

Purpose
-------
Validate pandas DataFrames.

Responsibilities

• Empty Dataset
• Duplicate Columns
• Required Columns
• Duplicate Rows
• Null Values
• Row Count
• Index Validation

====================================================================
"""

from __future__ import annotations

import pandas as pd

from core.data.validators.base_validator import (

    BaseValidator,

    ValidationIssue

)


class DataFrameValidator(

    BaseValidator

):

    """
    Institutional DataFrame Validator.
    """

    def __init__(

        self,

        required_columns: list[str] | None = None,

        allow_empty: bool = False,

        allow_duplicate_rows: bool = False,

        allow_duplicate_columns: bool = False,

        max_null_percentage: float = 100.0,

        require_unique_index: bool = False,

        min_rows: int | None = None,

        max_rows: int | None = None

    ) -> None:

        self.required_columns = (

            required_columns

            or

            []

        )

        self.allow_empty = allow_empty

        self.allow_duplicate_rows = (

            allow_duplicate_rows

        )

        self.allow_duplicate_columns = (

            allow_duplicate_columns

        )

        self.max_null_percentage = (

            max_null_percentage

        )

        self.require_unique_index = (

            require_unique_index

        )

        self.min_rows = min_rows

        self.max_rows = max_rows

    # =====================================================
    # VALIDATION
    # =====================================================

    def _validate(

        self,

        data: pd.DataFrame

    ) -> list[ValidationIssue]:

        issues: list[ValidationIssue] = []

        # -----------------------------------------------
        # Empty Dataset
        # -----------------------------------------------

        if (

            not self.allow_empty

        ):

            issues.extend(

                self.empty_dataframe(

                    data

                )

            )

        # -----------------------------------------------
        # Required Columns
        # -----------------------------------------------

        issues.extend(

            self.require_columns(

                data,

                self.required_columns

            )

        )

        # -----------------------------------------------
        # Duplicate Columns
        # -----------------------------------------------

        if (

            not self.allow_duplicate_columns

        ):

            issues.extend(

                self.duplicate_columns(

                    data

                )

            )

        # -----------------------------------------------
        # Duplicate Rows
        # -----------------------------------------------

        if (

            not self.allow_duplicate_rows

        ):

            duplicate_rows = int(

                data

                .duplicated()

                .sum()

            )

            if duplicate_rows > 0:

                issues.append(

                    self.error(

                        f"{duplicate_rows} duplicate rows detected."

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

                        "Null percentage "

                        f"{null_percentage:.2f}% "

                        "exceeds allowed "

                        f"{self.max_null_percentage:.2f}%."

                    )

                )

        # -----------------------------------------------
        # Unique Index
        # -----------------------------------------------

        if self.require_unique_index:

            if not data.index.is_unique:

                issues.append(

                    self.error(

                        "DataFrame index "

                        "contains duplicate values."

                    )

                )
        
        # -----------------------------------------------
        # Row Count
        # -----------------------------------------------

        if (

            self.min_rows is not None

            and

            len(data) < self.min_rows

        ):

            issues.append(

                self.error(

                    f"Dataset contains "

                    f"{len(data)} rows. "

                    f"Minimum required "

                    f"is {self.min_rows}."

                )

            )

        if (

            self.max_rows is not None

            and

            len(data) > self.max_rows

        ):

            issues.append(

                self.warning(

                    f"Dataset contains "

                    f"{len(data)} rows. "

                    f"Maximum expected "

                    f"is {self.max_rows}."

                )

            )

        return issues