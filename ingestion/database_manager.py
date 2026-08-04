# ==========================================================
# DATABASE MANAGER
# Institutional Data Persistence Layer
# ==========================================================

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import duckdb
import pandas as pd

# ==========================================================
# DATABASE CONFIG
# ==========================================================


@dataclass(frozen=True)
class DatabaseConfig:
    DATABASE_NAME: str = "institutional_quant.db"

    READ_ONLY: bool = False


# ==========================================================
# DATABASE PATHS
# ==========================================================


class DatabasePaths:
    def __init__(self):

        self.root = Path.cwd()

    @property
    def database_file(self):

        return self.root / "data" / "database" / "institutional_quant.db"


# ==========================================================
# CONNECTION MANAGER
# ==========================================================


class ConnectionManager:
    def __init__(self, config=None):

        self.config = config or DatabaseConfig()

        self.paths = DatabasePaths()

        self.paths.database_file.parent.mkdir(parents=True, exist_ok=True)

        self.connection = None

    def connect(self):

        self.connection = duckdb.connect(str(self.paths.database_file))

        return self.connection

    def close(self):

        if self.connection:
            self.connection.close()


# ==========================================================
# TABLE MANAGER
# ==========================================================


class TableManager:
    @staticmethod
    def save_dataframe(
        connection,
        dataframe,
        table_name,
    ):
        """
        Save a pandas DataFrame into DuckDB with robust dtype normalization.
        """

        import numpy as np

        df = dataframe.copy()

        # --------------------------------------------------
        # Normalize extension dtypes
        # --------------------------------------------------

        df = df.convert_dtypes()

        for col in df.columns:
            # Category -> string
            if pd.api.types.is_categorical_dtype(df[col]):
                df[col] = df[col].astype(str)

            # Pandas StringDtype -> object
            elif pd.api.types.is_string_dtype(df[col]):
                df[col] = df[col].astype(object)

            # Timezone-aware datetime -> naive datetime
            elif pd.api.types.is_datetime64tz_dtype(df[col]):
                df[col] = df[col].dt.tz_localize(None)

            # Object columns containing NumPy scalar types
            elif df[col].dtype == object:
                df[col] = df[col].apply(
                    lambda x: x.item() if isinstance(x, np.generic) else x
                )

        # Replace infinities with NULL
        df = df.replace(
            [np.inf, -np.inf],
            np.nan,
        )

        connection.register(
            "temp_df",
            df,
        )

        try:
            connection.execute(f"""
                CREATE OR REPLACE TABLE {table_name}
                AS
                SELECT *
                FROM temp_df
                """)

        finally:
            connection.unregister("temp_df")

    @staticmethod
    def read_table(
        connection,
        table_name,
    ):
        """
        Read a DuckDB table into a pandas DataFrame.
        """

        return connection.execute(f"""
                SELECT *
                FROM {table_name}
                """).fetchdf()

    @staticmethod
    def table_exists(
        connection,
        table_name,
    ):
        """
        Check whether a DuckDB table exists.
        """

        result = connection.execute(
            """
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name = ?
            """,
            [table_name],
        ).fetchone()

        return result[0] > 0


# ==========================================================
# DATABASE MANAGER
# ==========================================================


class DatabaseManager:
    def __init__(self):

        self.connection_manager = ConnectionManager()

        self.connection = self.connection_manager.connect()

    def save(self, dataframe, table_name):

        TableManager.save_dataframe(self.connection, dataframe, table_name)

    def load(self, table_name):

        # -------------------------
        # Try DuckDB first
        # -------------------------
        if self.exists(table_name):
            return TableManager.read_table(
                self.connection,
                table_name,
            )

        # -------------------------
        # CSV fallback
        # -------------------------
        root = Path(__file__).resolve().parents[1]

        csv_map = {
            "signal_master": (root / "data" / "signals" / "signal_master.csv"),
            # Live portfolio
            "target_portfolio": (root / "data" / "live" / "target_portfolio.csv"),
            "rebalance_dashboard": (root / "data" / "live" / "rebalance_dashboard.csv"),
            "trade_list": (root / "data" / "live" / "trade_list.csv"),
            # Performance
            "performance_report": (
                root / "data" / "performance" / "performance_dashboard.csv"
            ),
            "performance_dashboard": (
                root / "data" / "performance" / "performance_dashboard.csv"
            ),
            "performance_summary": (
                root / "data" / "performance" / "performance_summary.csv"
            ),
            "executive_dashboard": (
                root / "data" / "performance" / "executive_dashboard.csv"
            ),
        }

        csv_file = csv_map.get(table_name)

        if csv_file and csv_file.exists():
            return pd.read_csv(csv_file)

        raise FileNotFoundError(
            f"No DuckDB table or CSV found for '{table_name}'. Expected CSV: {csv_file}"
        )

    def exists(self, table_name):

        return TableManager.table_exists(self.connection, table_name)

    def close(self):

        self.connection_manager.close()
