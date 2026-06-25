"""
====================================================================
Institutional Quant Platform

Base Validator

Author : Institutional Quant Platform

Purpose
-------
Common validation framework for all datasets.

Responsibilities

• Structural Validation
• Business Rule Validation
• Quality Validation
• Logging
• Validation Lifecycle

Inherited By

• DataFrameValidator
• SchemaValidator
• QualityValidator

====================================================================
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from dataclasses import dataclass
from dataclasses import field

from typing import Any
from typing import Generic
from typing import TypeVar

import pandas as pd

from core.logging_manager import LoggingManager

# ==========================================================
# GENERICS
# ==========================================================

T = TypeVar(
    "T"
)

# ==========================================================
# LOGGER
# ==========================================================

logger = LoggingManager.get_logger(
    __name__
)

# ==========================================================
# VALIDATION ISSUE
# ==========================================================


@dataclass(slots=True)
class ValidationIssue:

    severity: str

    message: str

    field: str | None = None

# ==========================================================
# VALIDATION RESULT
# ==========================================================


@dataclass(slots=True)
class ValidationResult(Generic[T]):

    passed: bool

    data: T

    issues: list[ValidationIssue] = field(

        default_factory=list

    )

# ==========================================================
# BASE VALIDATOR
# ==========================================================


class BaseValidator(

    ABC

):

    """
    Institutional Base Validator.

    Every validator inherits this class.
    """

    # ======================================================
    # PUBLIC
    # ======================================================

    def validate(

        self,

        data: pd.DataFrame

    ) -> ValidationResult[pd.DataFrame]:

        """
        Standard validation pipeline.

        before_validate()

            ↓

        _validate()

            ↓

        after_validate()

            ↓

        ValidationResult
        """

        self.before_validate(

            data

        )

        issues = self._validate(

            data

        )

        self.after_validate(

            data,

            issues

        )

        passed = (

            len(

                issues

            )

            == 0

        )

        logger.info(

            "Validation completed | "

            "Passed=%s | "

            "Issues=%d",

            passed,

            len(

                issues

            )

        )

        return ValidationResult(

            passed=passed,

            data=data,

            issues=issues

        )

    # ======================================================
    # ABSTRACT
    # ======================================================

    @abstractmethod

    def _validate(

        self,

        data: pd.DataFrame

    ) -> list[ValidationIssue]:

        """
        Concrete validators implement
        validation rules here.
        """

        raise NotImplementedError
    
    # ======================================================
    # CALLBACKS
    # ======================================================

    def before_validate(

        self,

        data: pd.DataFrame

    ) -> None:

        """
        Executed before validation.

        Override if required.
        """

        return None

    def after_validate(

        self,

        data: pd.DataFrame,

        issues: list[ValidationIssue]

    ) -> None:

        """
        Executed after validation.

        Override if required.
        """

        logger.info(

            "Validation Summary | "

            "Rows=%d | "

            "Columns=%d | "

            "Issues=%d",

            len(

                data

            ),

            len(

                data.columns

            ),

            len(

                issues

            )

        )

    # ======================================================
    # ISSUE HELPERS
    # ======================================================

    @staticmethod

    def error(

        message: str,

        field: str | None = None

    ) -> ValidationIssue:

        return ValidationIssue(

            severity="ERROR",

            message=message,

            field=field

        )

    @staticmethod

    def warning(

        message: str,

        field: str | None = None

    ) -> ValidationIssue:

        return ValidationIssue(

            severity="WARNING",

            message=message,

            field=field

        )

    @staticmethod

    def info(

        message: str,

        field: str | None = None

    ) -> ValidationIssue:

        return ValidationIssue(

            severity="INFO",

            message=message,

            field=field

        )

    # ======================================================
    # COMMON VALIDATIONS
    # ======================================================

    @staticmethod

    def require_columns(

        data: pd.DataFrame,

        required_columns: list[str]

    ) -> list[ValidationIssue]:

        """
        Validate required columns.
        """

        issues: list[ValidationIssue] = []

        for column in required_columns:

            if column not in data.columns:

                issues.append(

                    ValidationIssue(

                        severity="ERROR",

                        message=f"Missing required column: {column}",

                        field=column

                    )

                )

        return issues

    @staticmethod

    def duplicate_columns(

        data: pd.DataFrame

    ) -> list[ValidationIssue]:

        """
        Detect duplicate column names.
        """

        issues: list[ValidationIssue] = []

        duplicates = data.columns[

            data.columns.duplicated()

        ]

        for column in duplicates:

            issues.append(

                ValidationIssue(

                    severity="ERROR",

                    message=f"Duplicate column: {column}",

                    field=column

                )

            )

        return issues

    @staticmethod

    def empty_dataframe(

        data: pd.DataFrame

    ) -> list[ValidationIssue]:

        """
        Detect empty dataframe.
        """

        if data.empty:

            return [

                ValidationIssue(

                    severity="ERROR",

                    message="Dataset is empty."

                )

            ]

        return []

    # ======================================================
    # SUMMARY
    # ======================================================

    @staticmethod

    def summarize(

        issues: list[ValidationIssue]

    ) -> dict[str, int]:

        """
        Validation statistics.
        """

        summary = {

            "ERROR": 0,

            "WARNING": 0,

            "INFO": 0

        }

        for issue in issues:

            summary[

                issue.severity

            ] += 1

        return summary

    # ======================================================
    # REPRESENTATION
    # ======================================================

    def __repr__(

        self

    ) -> str:

        return (

            f"{self.__class__.__name__}()"

        )

    __str__ = __repr__