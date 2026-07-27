"""
=========================================================
FILE UTILITIES
=========================================================

Purpose:
Common filesystem helper functions used throughout the
Institutional Quant Platform.

=========================================================
"""

from __future__ import annotations

from pathlib import Path

# =========================================================
# DIRECTORY HELPERS
# =========================================================


def ensure_directory(
    directory: Path,
) -> None:
    """
    Create a directory if it does not exist.
    """

    directory.mkdir(
        parents=True,
        exist_ok=True,
    )


def ensure_parent_directory(
    file_path: Path,
) -> None:
    """
    Create the parent directory for a file.
    """

    file_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )


# =========================================================
# FILE HELPERS
# =========================================================


def file_exists(
    file_path: Path,
) -> bool:
    """
    Check whether a file exists.
    """

    return file_path.exists()


def directory_exists(
    directory: Path,
) -> bool:
    """
    Check whether a directory exists.
    """

    return directory.exists()


# =========================================================
# FILE INFORMATION
# =========================================================


def file_size(
    file_path: Path,
) -> int:
    """
    Return file size in bytes.
    """

    return file_path.stat().st_size if file_path.exists() else 0


def touch(
    file_path: Path,
) -> None:
    """
    Create an empty file if it does not exist.
    """

    ensure_parent_directory(file_path)

    file_path.touch(exist_ok=True)
