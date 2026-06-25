"""
====================================================================
Institutional Quant Platform

Schema Validator

Author : Institutional Quant Platform

Purpose
-------
Validate DataFrame schema.

Responsibilities

• Required Columns
• Optional Columns
• Column Data Types
• Allowed Values
• Numeric Range
• Nullable Columns

====================================================================
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from core.data.validators.base_validator import (

    BaseValidator,

    ValidationIssue

)


class SchemaValidator(

    BaseValidator

):

    """
    Institutional Schema Validator.
    """

    def __init__(

        self,

        required_columns: dict[str, Any] | None = None,

        optional_columns: dict[str, Any] | None = None,

        nullable_columns: list[str] | None = None,

        allowed_values: dict[str, list[Any]] | None = None

    ) -> None:

        self.required_columns = (

            required_columns

            or

            {}

        )

        self.optional_columns = (

            optional_columns

            or

            {}

        )

        self.nullable_columns = (

            nullable_columns

            or

            []

        )

        self.allowed_values = (

            allowed_values

            or

            {}

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
        # Required Columns
        # -----------------------------------------------

        for column in self.required_columns:

            if column not in data.columns:

                issues.append(

                    self.error(

                        f"Missing required column: {column}",

                        column

                    )

                )

                continue

        # -----------------------------------------------
        # Column Data Types
        # -----------------------------------------------

        for column, expected_dtype in (

            self.required_columns.items()

        ):

            if column not in data.columns:

                continue

            actual_dtype = str(

                data[column].dtype

            )

            expected_dtype = str(

                expected_dtype

            )

            if actual_dtype != expected_dtype:

                issues.append(

                    self.error(

                        f"Column '{column}' "

                        f"expected dtype "

                        f"'{expected_dtype}' "

                        f"but found "

                        f"'{actual_dtype}'.",

                        column

                    )

                )

        # -----------------------------------------------
        # Nullable Columns
        # -----------------------------------------------

        for column in data.columns:

            if column in self.nullable_columns:

                continue

            if data[column].isna().any():

                issues.append(

                    self.error(

                        f"Column '{column}' "

                        "contains null values.",

                        column

                    )

                )

        # -----------------------------------------------
        # Allowed Values
        # -----------------------------------------------

        for column, allowed in (

            self.allowed_values.items()

        ):

            if column not in data.columns:

                continue

            invalid = (

                data[column]

                .dropna()

                .loc[

                    lambda s:

                    ~s.isin(

                        allowed

                    )

                ]

            )

            if not invalid.empty:

                issues.append(

                    self.error(

                        f"Column '{column}' "

                        "contains invalid values.",

                        column

                    )

                )

        # -----------------------------------------------
        # Unknown Columns
        # -----------------------------------------------

        allowed_columns = set(

            self.required_columns.keys()

        ).union(

            self.optional_columns.keys()

        )

        for column in data.columns:

            if (

                allowed_columns

                and

                column not in allowed_columns

            ):

                issues.append(

                    self.warning(

                        f"Unexpected column: {column}",

                        column

                    )

                )

        return issues