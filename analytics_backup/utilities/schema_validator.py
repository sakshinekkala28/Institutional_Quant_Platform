"""
=========================================================
SCHEMA VALIDATOR
=========================================================

Institutional Data Validation Layer

Used by:
- Research Engines
- Ranking Engines
- Alpha Engines
- Portfolio Engines
- Risk Engines

=========================================================
"""

from pathlib import Path
from typing import Iterable

import pandas as pd

# =========================================================
# VALIDATE FILE EXISTS
# =========================================================


def validate_file_exists(file_path: Path) -> None:
    """
    Ensure file exists before processing.
    """

    if not file_path.exists():
        raise FileNotFoundError(
            f"\n❌ File Not Found:\n{file_path}"
        )


# =========================================================
# VALIDATE EMPTY FILE
# =========================================================


def validate_not_empty(df: pd.DataFrame, file_path: Path) -> None:
    """
    Ensure dataframe contains rows.
    """

    if df.empty:
        raise ValueError(
            f"\n❌ Empty File:\n{file_path}"
        )


# =========================================================
# REQUIRED COLUMN VALIDATION
# =========================================================


def validate_required_columns(
    df: pd.DataFrame,
    required_columns: Iterable[str],
    file_path: Path | str = "",
) -> None:
    """
    Validate required columns exist.
    """

    missing = [
        col
        for col in required_columns
        if col not in df.columns
    ]

    if missing:

        raise ValueError(
            "\n❌ Missing Required Columns\n"
            f"File: {file_path}\n"
            f"Missing: {missing}\n"
            f"Available: {list(df.columns)}"
        )


# =========================================================
# DUPLICATE CHECK
# =========================================================


def validate_no_duplicates(
    df: pd.DataFrame,
    column: str,
) -> None:
    """
    Check duplicate values.
    """

    duplicates = df[column].duplicated().sum()

    if duplicates > 0:

        raise ValueError(
            f"\n❌ Duplicate Values Found\n"
            f"Column: {column}\n"
            f"Count: {duplicates}"
        )


# =========================================================
# NUMERIC COLUMN VALIDATION
# =========================================================


def validate_numeric_columns(
    df: pd.DataFrame,
    columns: list[str],
) -> None:
    """
    Ensure numeric columns are numeric.
    """

    for col in columns:

        if col not in df.columns:
            continue

        try:
            pd.to_numeric(
                df[col],
                errors="raise",
            )

        except Exception as exc:

            raise ValueError(
                f"\n❌ Non-Numeric Values Found\n"
                f"Column: {col}"
            ) from exc


# =========================================================
# MAIN VALIDATOR
# =========================================================


def validate_columns(
    file_path: Path,
    required_columns: list[str],
) -> pd.DataFrame:
    """
    Institutional wrapper.

    Example:
        df = validate_columns(
            INPUT_FILE,
            ["Symbol", "Close"]
        )
    """

    validate_file_exists(file_path)

    df = pd.read_csv(file_path)

    validate_not_empty(
        df,
        file_path,
    )

    validate_required_columns(
        df,
        required_columns,
        file_path,
    )

    return df


# =========================================================
# OPTIONAL UTILITIES
# =========================================================


def standardize_symbol_column(
    df: pd.DataFrame,
    column: str = "Symbol",
) -> pd.DataFrame:
    """
    Standardize symbols.
    """

    if column not in df.columns:
        return df

    df[column] = (
        df[column]
        .astype(str)
        .str.upper()
        .str.strip()
        .str.replace(
            ".NS",
            "",
            regex=False,
        )
    )

    return df


def remove_duplicate_symbols(
    df: pd.DataFrame,
    column: str = "Symbol",
) -> pd.DataFrame:
    """
    Remove duplicate symbols.
    """

    return (
        df.drop_duplicates(
            subset=[column],
            keep="first",
        )
        .reset_index(drop=True)
    )