"""
====================================================================
Institutional Quant Platform

Database Dependency

Author : Institutional Quant Platform

Purpose
-------
Database dependency providers.

Provides

• DuckDB Connection
• SQLAlchemy Session (Future Ready)
• Database Health Check
• Transaction Management
• Automatic Cleanup

Used By

• Portfolio Engine
• Signal Engine
• Risk Engine
• Execution Engine
• Backtest Engine

====================================================================
"""

from __future__ import annotations

from contextlib import contextmanager
from pathlib import Path

import duckdb

from api.dependencies.config import database_url


# ==========================================================
# DATABASE PATH
# ==========================================================


def database_path() -> str:
    """
    Resolve DuckDB database path.
    """

    url = database_url()

    if url.startswith("sqlite:///"):

        return url.replace(

            "sqlite:///",

            "",

        )

    if url.startswith("duckdb:///"):

        return url.replace(

            "duckdb:///",

            "",

        )

    return url


# ==========================================================
# CONNECTION
# ==========================================================


def get_connection() -> duckdb.DuckDBPyConnection:
    """
    Create database connection.
    """

    path = database_path()

    return duckdb.connect(

        database=path,

        read_only=False,

    )


# ==========================================================
# FASTAPI DEPENDENCY
# ==========================================================


def get_database():
    """
    FastAPI dependency.

    Usage

        db = Depends(get_database)
    """

    connection = get_connection()

    try:

        yield connection

    finally:

        connection.close()


# ==========================================================
# TRANSACTION
# ==========================================================


@contextmanager
def transaction():
    """
    Database transaction.
    """

    connection = get_connection()

    try:

        connection.execute(

            "BEGIN TRANSACTION"

        )

        yield connection

        connection.execute(

            "COMMIT"

        )

    except Exception:

        connection.execute(

            "ROLLBACK"

        )

        raise

    finally:

        connection.close()


# ==========================================================
# HEALTH
# ==========================================================


def database_health() -> dict:
    """
    Database health check.
    """

    try:

        connection = get_connection()

        connection.execute(

            "SELECT 1"

        )

        version = connection.execute(

            "SELECT version()"

        ).fetchone()[0]

        connection.close()

        return {

            "healthy": True,

            "engine": "DuckDB",

            "version": version,

        }

    except Exception as exc:

        return {

            "healthy": False,

            "error": str(exc),

        }


# ==========================================================
# EXISTS
# ==========================================================


def database_exists() -> bool:
    """
    Check database existence.
    """

    return Path(

        database_path(),

    ).exists()


# ==========================================================
# EXECUTE
# ==========================================================


def execute(

    sql: str,

    parameters: tuple | None = None,

):
    """
    Execute SQL.
    """

    with transaction() as connection:

        if parameters:

            return connection.execute(

                sql,

                parameters,

            )

        return connection.execute(

            sql,

        )


# ==========================================================
# FETCH ALL
# ==========================================================


def fetch_all(

    sql: str,

    parameters: tuple | None = None,

):

    with transaction() as connection:

        if parameters:

            return connection.execute(

                sql,

                parameters,

            ).fetchall()

        return connection.execute(

            sql,

        ).fetchall()


# ==========================================================
# FETCH ONE
# ==========================================================


def fetch_one(

    sql: str,

    parameters: tuple | None = None,

):

    with transaction() as connection:

        if parameters:

            return connection.execute(

                sql,

                parameters,

            ).fetchone()

        return connection.execute(

            sql,

        ).fetchone()


# ==========================================================
# EXPORTS
# ==========================================================


__all__ = [

    "database_path",

    "get_connection",

    "get_database",

    "transaction",

    "database_health",

    "database_exists",

    "execute",

    "fetch_all",

    "fetch_one",

]