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

        return (

            self.root

            / "data"

            / "database"

            / "institutional_quant.db"

        )
    
# ==========================================================
# CONNECTION MANAGER
# ==========================================================

class ConnectionManager:

    def __init__(

        self,

        config=None

    ):

        self.config = (

            config

            or DatabaseConfig()

        )

        self.paths = DatabasePaths()

        self.paths.database_file.parent.mkdir(

            parents=True,

            exist_ok=True

        )

        self.connection = None

    def connect(self):

        self.connection = duckdb.connect(

            str(
                self.paths.database_file
            )

        )

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

        table_name

    ):

        connection.register(

            "temp_df",

            dataframe

        )

        connection.execute(

            f"""
            CREATE OR REPLACE TABLE
            {table_name}
            AS
            SELECT *
            FROM temp_df
            """
        )

    @staticmethod
    def read_table(

        connection,

        table_name

    ):

        return connection.execute(

            f"""
            SELECT *
            FROM {table_name}
            """

        ).df()

    @staticmethod
    def table_exists(

        connection,

        table_name

    ):

        result = connection.execute(

            f"""
            SELECT COUNT(*)
            FROM information_schema.tables
            WHERE table_name =
            '{table_name}'
            """

        ).fetchone()[0]

        return result > 0
    
# ==========================================================
# DATABASE MANAGER
# ==========================================================

class DatabaseManager:

    def __init__(self):

        self.connection_manager = (

            ConnectionManager()

        )

        self.connection = (

            self.connection_manager

            .connect()

        )

    def save(

        self,

        dataframe,

        table_name

    ):

        TableManager.save_dataframe(

            self.connection,

            dataframe,

            table_name

        )

    def load(

        self,

        table_name

    ):

        return (

            TableManager

            .read_table(

                self.connection,

                table_name

            )

        )

    def exists(

        self,

        table_name

    ):

        return (

            TableManager

            .table_exists(

                self.connection,

                table_name

            )

        )

    def close(self):

        self.connection_manager.close()