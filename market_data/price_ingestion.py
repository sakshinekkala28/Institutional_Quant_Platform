# ==========================================================
# PRICE INGESTION ENGINE
# Institutional Quant Platform
# ==========================================================

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

import logging
import warnings

import duckdb
import numpy as np
import pandas as pd
import yfinance as yf

warnings.filterwarnings(
    "ignore"
)

# ==========================================================
# CONFIGURATION
# ==========================================================

@dataclass(slots=True)
class PriceIngestionConfig:

    # ------------------------------------------------------
    # SOURCE FILES
    # ------------------------------------------------------

    SECURITY_MASTER_FILE: str = (
        "data/raw/security_master.csv"
    )

    PRICE_HISTORY_FILE: str = (
        "data/raw/security_price_history.parquet"
    )

    BENCHMARK_FILE: str = (
        "data/raw/benchmark_prices.csv"
    )

    # ------------------------------------------------------
    # OUTPUT FILES
    # ------------------------------------------------------

    PRICE_COVERAGE_REPORT: str = (
        "data/raw/price_coverage_report.csv"
    )

    MISSING_SYMBOL_REPORT: str = (
        "data/raw/missing_symbol_report.csv"
    )

    INGESTION_AUDIT_LOG: str = (
        "data/raw/ingestion_audit_log.csv"
    )

    BENCHMARK_PARQUET: str = (
        "data/raw/benchmark_prices.parquet"
    )

    # ------------------------------------------------------
    # DATABASE
    # ------------------------------------------------------

    DUCKDB_FILE: str = (
        "data/database/institutional_quant.db"
    )

    # ------------------------------------------------------
    # DOWNLOAD
    # ------------------------------------------------------

    DOWNLOAD_BATCH_SIZE: int = 100

    MAX_RETRIES: int = 3

    LOOKBACK_DAYS: int = 5

    START_DATE: str = "2010-01-01"

    # ------------------------------------------------------
    # QUALITY CONTROL
    # ------------------------------------------------------

    MIN_HISTORY_DAYS: int = 252

    MIN_VOLUME: int = 0

    MAX_MISSING_RATIO: float = 0.20


# ==========================================================
# LOGGING
# ==========================================================

logging.basicConfig(

    level=logging.INFO,

    format=(

        "%(asctime)s | "

        "%(levelname)s | "

        "%(message)s"

    )

)

logger = logging.getLogger(
    __name__
)

# ==========================================================
# DATA VALIDATOR
# ==========================================================

class PriceDataValidator:

    REQUIRED_PRICE_COLUMNS = [

        "Date",

        "Open",

        "High",

        "Low",

        "Close",

        "Volume",

        "Symbol"

    ]

    @classmethod
    def validate_price_frame(
        cls,
        df: pd.DataFrame
    ) -> bool:

        missing = [

            col

            for col

            in cls.REQUIRED_PRICE_COLUMNS

            if col not in df.columns

        ]

        if missing:

            raise ValueError(

                f"Missing Columns: "

                f"{missing}"

            )

        if df.empty:

            raise ValueError(
                "Price Dataset Empty"
            )

        return True

    @staticmethod
    def validate_dates(
        df: pd.DataFrame
    ) -> bool:

        if df["Date"].isna().any():

            raise ValueError(
                "Null Dates Found"
            )

        return True

    @staticmethod
    def validate_prices(
        df: pd.DataFrame
    ) -> bool:

        invalid = (

            df["Close"]

            <= 0

        ).sum()

        if invalid > 0:

            raise ValueError(

                f"Invalid Prices: "

                f"{invalid}"

            )

        return True

    @staticmethod
    def validate_volume(
        df: pd.DataFrame
    ) -> bool:

        invalid = (

            df["Volume"]

            < 0

        ).sum()

        if invalid > 0:

            raise ValueError(

                f"Negative Volume: "

                f"{invalid}"

            )

        return True

    @classmethod
    def run(
        cls,
        df: pd.DataFrame
    ) -> bool:

        cls.validate_price_frame(
            df
        )

        cls.validate_dates(
            df
        )

        cls.validate_prices(
            df
        )

        cls.validate_volume(
            df
        )

        return True


# ==========================================================
# UNIVERSE LOADER
# ==========================================================

class UniverseLoader:

    def __init__(
        self,
        config: PriceIngestionConfig
    ):

        self.config = config

    def load(
        self
    ) -> pd.DataFrame:

        logger.info(
            "Loading Security Master"
        )

        universe = pd.read_csv(

            self.config
            .SECURITY_MASTER_FILE

        )

        universe = universe.loc[

            (

                universe[
                    "Universe_Flag"
                ] == 1

            )

            &

            (

                universe[
                    "Is_Active"
                ] == 1

            )

        ].copy()

        universe = universe.dropna(

            subset=[
                "Yahoo_Symbol"
            ]

        )

        logger.info(

            f"Active Securities: "

            f"{len(universe):,}"

        )

        return universe


# ==========================================================
# PARQUET REPOSITORY
# ==========================================================

class PriceHistoryRepository:

    def __init__(
        self,
        config: PriceIngestionConfig
    ):

        self.config = config

    def load_existing_prices(
        self
    ) -> pd.DataFrame:

        path = Path(

            self.config
            .PRICE_HISTORY_FILE

        )

        if not path.exists():

            logger.warning(

                "Price History Missing"

            )

            return pd.DataFrame()

        logger.info(
            "Loading Existing Prices"
        )

        prices = pd.read_parquet(
            path
        )

        logger.info(

            f"Loaded "

            f"{len(prices):,} "

            f"Rows"

        )

        return prices

    def save_prices(
        self,
        prices: pd.DataFrame
    ) -> None:

        path = Path(

            self.config
            .PRICE_HISTORY_FILE

        )

        prices.to_parquet(

            path,

            index=False

        )

        logger.info(

            f"Saved "

            f"{len(prices):,} "

            f"Rows"

        )


# ==========================================================
# DUCKDB MANAGER
# ==========================================================

class DuckDBManager:

    def __init__(
        self,
        config: PriceIngestionConfig
    ):

        self.config = config

        Path(
            self.config.DUCKDB_FILE
        ).parent.mkdir(

            parents=True,

            exist_ok=True

        )

    def connect(
        self
    ) -> duckdb.DuckDBPyConnection:

        return duckdb.connect(

            self.config
            .DUCKDB_FILE

        )

    def register_prices(
        self,
        prices: pd.DataFrame
    ) -> None:

        logger.info(
            "Registering Prices"
        )

        con = self.connect()

        con.register(
            "prices_df",
            prices
        )

        con.execute(

            """
            CREATE OR REPLACE TABLE prices AS

            SELECT *

            FROM prices_df
            """

        )

        con.close()

    def register_security_master(
        self,
        universe: pd.DataFrame
    ) -> None:

        logger.info(
            "Registering Security Master"
        )

        con = self.connect()

        con.register(

            "universe_df",

            universe

        )

        con.execute(

            """
            CREATE OR REPLACE TABLE
            security_master AS

            SELECT *

            FROM universe_df
            """

        )

        con.close()

    def register_symbol_metadata(
        self,
        metadata: pd.DataFrame
    ):

        con = self.connect()

        con.register(

            "metadata_df",

            metadata

        )

        con.execute(

            """
            CREATE OR REPLACE TABLE
            symbol_metadata AS

            SELECT *

            FROM metadata_df
            """

        )

        con.close()

# ==========================================================
# YAHOO DOWNLOAD ENGINE
# ==========================================================

class YahooDownloadEngine:

    def __init__(
        self,
        config: PriceIngestionConfig
    ):

        self.config = config

    def download_batch(
        self,
        symbols: list[str],
        start_date: str,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:

        frames = []

        try:

            data = yf.download(

                tickers=symbols,

                start=start_date,

                end=end_date,

                auto_adjust=True,

                progress=False,

                group_by="ticker",

                threads=True

            )

            for symbol in symbols:

                try:

                    symbol_df = (

                        data[symbol]

                        .reset_index()

                        .copy()

                    )

                    if isinstance(
                        symbol_df.columns,
                        pd.MultiIndex
                    ):

                        symbol_df.columns = (

                            symbol_df.columns

                            .get_level_values(0)

                        )

                    symbol_df["Symbol"] = symbol

                    if not symbol_df.empty:

                        frames.append(
                            symbol_df
                        )

                except Exception:

                    logger.warning(

                        f"Failed Symbol: "
                        f"{symbol}"

                    )

        except Exception as ex:

            logger.error(

                f"Batch Download Failed: "
                f"{ex}"

            )

        if not frames:

            return pd.DataFrame()

        prices = pd.concat(

            frames,

            ignore_index=True

        )

        return prices

# ==========================================================
# RETRY FRAMEWORK
# ==========================================================

class RetryDownloadEngine:

    def __init__(
        self,
        config: PriceIngestionConfig
    ):

        self.config = config

        self.yahoo = (
            YahooDownloadEngine(
                config
            )
        )

    def download(
        self,
        symbols: list[str],
        start_date: str
    ) -> pd.DataFrame:

        attempt = 0

        while (

            attempt
            <
            self.config.MAX_RETRIES

        ):

            try:

                result = (

                    self.yahoo
                    .download_batch(

                        symbols,

                        start_date

                    )

                )

                if len(result):

                    return result

            except Exception as ex:

                logger.warning(

                    f"Retry {attempt+1}: "
                    f"{ex}"

                )

            attempt += 1

        logger.error(
            "Max Retries Exhausted"
        )

        return pd.DataFrame()

# ==========================================================
# PRICE STANDARDIZER
# ==========================================================

class PriceStandardizer:

    @staticmethod
    def standardize(
        prices: pd.DataFrame
    ) -> pd.DataFrame:

        if prices.empty:

            return prices

        prices = prices.copy()

        prices.columns = [

            str(col)

            .replace(
                "Adj Close",
                "Close"
            )

            for col

            in prices.columns

        ]

        required = [

            "Date",

            "Open",

            "High",

            "Low",

            "Close",

            "Volume",

            "Symbol"

        ]

        prices = prices[
            required
        ]

        prices["Date"] = pd.to_datetime(

            prices["Date"]

        )

        prices["Symbol"] = (

            prices["Symbol"]

            .astype(str)

            .str.upper()

        )

        prices.sort_values(

            [

                "Symbol",

                "Date"

            ],

            inplace=True

        )

        prices.reset_index(

            drop=True,

            inplace=True

        )

        close_col = prices["Close"]

        if isinstance(
            close_col,
            pd.DataFrame
        ):

            close_col = close_col.iloc[:, 0]

        close_col = pd.to_numeric(

            close_col,

            errors="coerce"

        )

        prices["Daily_Return"] = (

            close_col

            .groupby(
                prices["Symbol"]
            )

            .pct_change()

        )

        return prices

# ==========================================================
# INCREMENTAL UPDATE ENGINE
# ==========================================================

class IncrementalUpdateEngine:

    def __init__(
        self,
        config: PriceIngestionConfig
    ):

        self.config = config

    def latest_dates(
        self,
        prices: pd.DataFrame
    ) -> pd.DataFrame:

        if prices.empty:

            return pd.DataFrame()

        latest = (

            prices

            .groupby(
                "Symbol"
            )["Date"]

            .max()

            .reset_index()

        )

        latest.rename(

            columns={
                "Date":
                "Last_Date"
            },

            inplace=True

        )

        return latest

    def determine_missing_symbols(
        self,
        universe: pd.DataFrame,
        prices: pd.DataFrame
    ) -> pd.DataFrame:

        if prices.empty:

            return universe.copy()

        covered = set(

            prices[
                "Symbol"
            ].unique()

        )

        missing = universe.loc[

            ~

            universe[
                "Yahoo_Symbol"
            ]

            .isin(
                covered
            )

        ]

        return missing

    def merge_prices(
        self,
        existing_prices: pd.DataFrame,
        new_prices: pd.DataFrame
    ) -> pd.DataFrame:

        combined = pd.concat(

            [

                existing_prices,

                new_prices

            ],

            ignore_index=True

        )

        combined.drop_duplicates(

            subset=[

                "Date",

                "Symbol"

            ],

            keep="last",

            inplace=True

        )

        combined.sort_values(

            [

                "Symbol",

                "Date"

            ],

            inplace=True

        )

        combined.reset_index(

            drop=True,

            inplace=True

        )

        return combined

# ==========================================================
# COVERAGE ANALYTICS
# ==========================================================

class CoverageAnalytics:

    @staticmethod
    def build_report(
        prices: pd.DataFrame
    ) -> pd.DataFrame:

        report = (

            prices

            .groupby(
                "Symbol"
            )

            .agg(

                First_Date=(

                    "Date",

                    "min"

                ),

                Last_Date=(

                    "Date",

                    "max"

                ),

                History_Days=(

                    "Date",

                    "count"

                ),

                Last_Close=(

                    "Close",

                    "last"

                )

            )

            .reset_index()

        )

        return report

    @staticmethod
    def save_report(
        report: pd.DataFrame,
        config: PriceIngestionConfig
    ) -> None:

        report.to_csv(

            config
            .PRICE_COVERAGE_REPORT,

            index=False

        )

        logger.info(

            "Coverage Report Saved"

        )

# ==========================================================
# MISSING SYMBOL ANALYTICS
# ==========================================================

class MissingSymbolAnalytics:

    @staticmethod
    def build_report(
        universe: pd.DataFrame,
        prices: pd.DataFrame
    ) -> pd.DataFrame:

        covered = set(

            prices[
                "Symbol"
            ]

            .unique()

        )

        missing = universe.loc[

            ~

            universe[
                "Yahoo_Symbol"
            ]

            .isin(
                covered
            )

        ].copy()

        return missing

    @staticmethod
    def save_report(
        report: pd.DataFrame,
        config: PriceIngestionConfig
    ) -> None:

        report.to_csv(

            config
            .MISSING_SYMBOL_REPORT,

            index=False

        )

        logger.info(

            "Missing Symbol Report Saved"

        )

# ==========================================================
# BENCHMARK CLEANUP ENGINE
# ==========================================================

class BenchmarkCleanupEngine:

    @staticmethod
    def clean(
        benchmark_df: pd.DataFrame
    ) -> pd.DataFrame:

        benchmark_df = (

            benchmark_df.copy()

        )

        duplicate_columns = [

            col

            for col

            in benchmark_df.columns

            if ".1" in col

        ]

        if duplicate_columns:

            benchmark_df.drop(

                columns=
                duplicate_columns,

                inplace=True

            )

        benchmark_df["Date"] = (

            pd.to_datetime(

                benchmark_df["Date"]

            )

        )

        benchmark_df.sort_values(

            "Date",

            inplace=True

        )

        benchmark_df.reset_index(

            drop=True,

            inplace=True

        )

        return benchmark_df

    @staticmethod
    def save(
        benchmark_df: pd.DataFrame,
        config: PriceIngestionConfig
    ) -> None:

        benchmark_df.to_parquet(

            config
            .BENCHMARK_PARQUET,

            index=False

        )

        logger.info(

            "Benchmark Parquet Saved"

        )

# ==========================================================
# AUDIT LOGGER
# ==========================================================

class IngestionAuditLogger:

    def __init__(
        self,
        config: PriceIngestionConfig
    ):

        self.config = config

    def save(
        self,
        audit_record: dict
    ) -> None:

        audit_file = Path(

            self.config
            .INGESTION_AUDIT_LOG

        )

        audit_df = pd.DataFrame(
            [audit_record]
        )

        if audit_file.exists():

            existing = pd.read_csv(
                audit_file
            )

            audit_df = pd.concat(

                [

                    existing,

                    audit_df

                ],

                ignore_index=True

            )

        audit_df.to_csv(

            audit_file,

            index=False

        )

        logger.info(
            "Audit Log Updated"
        )


# ==========================================================
# DATA QUALITY ENGINE
# ==========================================================

class DataQualityEngine:

    @staticmethod
    def remove_invalid_rows(
        prices: pd.DataFrame
    ) -> pd.DataFrame:

        prices = prices.copy()

        prices = prices.loc[

            prices["Close"] > 0

        ]

        prices = prices.loc[

            prices["Volume"] >= 0

        ]

        prices.dropna(

            subset=[

                "Date",

                "Symbol",

                "Close"

            ],

            inplace=True

        )

        return prices

    @staticmethod
    def remove_duplicates(
        prices: pd.DataFrame
    ) -> pd.DataFrame:

        prices = prices.copy()

        prices.drop_duplicates(

            subset=[

                "Date",

                "Symbol"

            ],

            keep="last",

            inplace=True

        )

        return prices

    @staticmethod
    def rebuild_returns(
        prices: pd.DataFrame
    ) -> pd.DataFrame:

        prices = prices.copy()

        prices.sort_values(

            [

                "Symbol",

                "Date"

            ],

            inplace=True

        )

        prices["Daily_Return"] = (

            prices

            .groupby(
                "Symbol"
            )["Close"]

            .pct_change()

        )

        return prices


# ==========================================================
# DUCKDB SYNCHRONIZATION
# ==========================================================

class DuckDBSynchronization:

    def __init__(
        self,
        config: PriceIngestionConfig
    ):

        self.config = config

        self.db = DuckDBManager(
            config
        )

    def sync_prices(
        self,
        prices: pd.DataFrame
    ) -> None:

        self.db.register_prices(
            prices
        )

        logger.info(
            "Price Table Synced"
        )

    def sync_benchmarks(
        self,
        benchmarks: pd.DataFrame
    ) -> None:

        con = self.db.connect()

        con.register(

            "benchmark_df",

            benchmarks

        )

        con.execute(

            """
            CREATE OR REPLACE TABLE
            benchmark_prices AS

            SELECT *

            FROM benchmark_df
            """

        )

        con.close()

        logger.info(
            "Benchmark Table Synced"
        )


# ==========================================================
# TELEMETRY INTEGRATION
# ==========================================================

class TelemetryAdapter:

    @staticmethod
    def track(
        metric_name,
        value
    ):

        try:

            from telemetry.telemetry import (
                PIPELINE_RUNS
            )

            PIPELINE_RUNS.add(
                value
            )

        except Exception:

            pass


# ==========================================================
# MLFLOW INTEGRATION
# ==========================================================

class MLflowAdapter:

    @staticmethod
    def log_metric(
        name,
        value
    ):

        try:

            from mlflow_track.mlflow_manager import (
                MLflowManager
            )

            MLflowManager.log_metric(

                name,

                value

            )

        except Exception:

            pass


# ==========================================================
# PRICE INGESTION ENGINE
# ==========================================================

class PriceIngestionEngine:

    def __init__(

        self,

        config: Optional[
            PriceIngestionConfig
        ] = None

    ):

        self.config = (

            config

            or

            PriceIngestionConfig()

        )

        self.universe_loader = (

            UniverseLoader(
                self.config
            )

        )

        self.repository = (

            PriceHistoryRepository(
                self.config
            )

        )

        self.downloader = (

            RetryDownloadEngine(
                self.config
            )

        )

        self.incremental = (

            IncrementalUpdateEngine(
                self.config
            )

        )

        self.audit = (

            IngestionAuditLogger(
                self.config
            )

        )

        self.duckdb_sync = (

            DuckDBSynchronization(
                self.config
            )

        )

    # ======================================================
    # LOAD BENCHMARKS
    # ======================================================

    def load_benchmarks(
        self
    ) -> pd.DataFrame:

        benchmark_file = Path(

            self.config
            .BENCHMARK_FILE

        )

        if not benchmark_file.exists():

            return pd.DataFrame()

        benchmark_df = pd.read_csv(
            benchmark_file
        )

        benchmark_df = (

            BenchmarkCleanupEngine
            .clean(
                benchmark_df
            )

        )

        BenchmarkCleanupEngine.save(

            benchmark_df,

            self.config

        )

        return benchmark_df

    # ======================================================
    # DOWNLOAD NEW SYMBOLS
    # ======================================================

    def download_missing_symbols(
        self,
        universe,
        existing_prices
    ) -> pd.DataFrame:

        missing = (

            self.incremental
            .determine_missing_symbols(

                universe,

                existing_prices

            )

        )

        if len(missing) == 0:

            logger.info(
                "No Missing Symbols"
            )

            return pd.DataFrame()

        yahoo_symbols = (

            missing[
                "Yahoo_Symbol"
            ]

            .tolist()

        )

        logger.info(

            f"Downloading "
            f"{len(yahoo_symbols)} "
            f"Missing Symbols"

        )

        return (

            self.downloader
            .download(

                yahoo_symbols,

                self.config.START_DATE

            )

        )
    
    def download_incremental_updates(
        self,
        universe,
        existing_prices
    ):

        if existing_prices.empty:

            return pd.DataFrame()

        latest_per_symbol = (

            existing_prices

            .groupby(
                "Symbol"
            )["Date"]

            .max()

            .reset_index()

        )

        latest_per_symbol.rename(

            columns={
                "Date":
                "Last_Date"
            },

            inplace=True

        )

        latest_market_date = (

            latest_per_symbol[
                "Last_Date"
            ]

            .max()

        )

        universe_dates = (

            universe[
                [
                    "Yahoo_Symbol"
                ]
            ]

            .merge(

                latest_per_symbol,

                left_on="Yahoo_Symbol",

                right_on="Symbol",

                how="left"

            )

        )

        stale_symbols = (

            universe_dates.loc[

                universe_dates[
                    "Last_Date"
                ]

                <

                latest_market_date

            ]

        )

        symbols = (

            stale_symbols[
                "Yahoo_Symbol"
            ]

            .dropna()

            .unique()

            .tolist()

        )

        if not symbols:

            logger.info(
                "No Incremental Updates Required"
            )

            return pd.DataFrame()

        logger.info(

            f"Incremental Update Symbols: "

            f"{len(symbols):,}"

        )

        start_date = (

            pd.to_datetime(
                latest_market_date
            )

            +

            pd.Timedelta(days=1)

        ).strftime(
            "%Y-%m-%d"
        )

        return self.downloader.download(

            symbols,

            start_date

        )
    
# ==========================================================
# PRICE INGESTION ENGINE (PART 4/4)
# ==========================================================

    def process_prices(
        self,
        existing_prices: pd.DataFrame,
        new_prices: pd.DataFrame
    ) -> pd.DataFrame:

        if len(new_prices):

            new_prices = (

                PriceStandardizer
                .standardize(
                    new_prices
                )

            )

            PriceDataValidator.run(
                new_prices
            )

        prices = (

            self.incremental
            .merge_prices(

                existing_prices,

                new_prices

            )

        )

        prices = (

            DataQualityEngine
            .remove_invalid_rows(
                prices
            )

        )

        prices = (

            DataQualityEngine
            .remove_duplicates(
                prices
            )

        )

        prices = (

            DataQualityEngine
            .rebuild_returns(
                prices
            )

        )

        PriceDataValidator.run(
            prices
        )

        return prices

    # ======================================================
    # REPORTS
    # ======================================================

    def generate_reports(
        self,
        universe: pd.DataFrame,
        prices: pd.DataFrame
    ) -> tuple[pd.DataFrame, pd.DataFrame]:

        active_symbols = set(

            universe[
                "Yahoo_Symbol"
            ]

        )

        active_prices = prices.loc[

            prices[
                "Symbol"
            ]

            .isin(
                active_symbols
            )

        ].copy()

        coverage_report = (

            CoverageAnalytics
            .build_report(
                active_prices
            )

        )

        CoverageAnalytics.save_report(

            coverage_report,

            self.config

        )

        missing_report = (

            MissingSymbolAnalytics
            .build_report(

                universe,

                prices

            )

        )

        MissingSymbolAnalytics.save_report(

            missing_report,

            self.config

        )

        return (

            coverage_report,

            missing_report

        )

    # ======================================================
    # AUDIT RECORD
    # ======================================================

    def build_audit_record(
        self,
        universe: pd.DataFrame,
        prices: pd.DataFrame,
        coverage_report: pd.DataFrame,
        missing_report: pd.DataFrame
    ) -> dict:

        return {

            "Run_Time":

                datetime.now()

                .strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

            "Universe_Size":

                len(universe),

            "Price_Rows":

                len(prices),
            
            "Covered_Symbols":

                min(

                    coverage_report[
                        "Symbol"
                    ].nunique(),

                    len(universe)

                ),

            "Missing_Symbols":

                len(
                    missing_report
                ),

            "Coverage_Ratio":

                round(

                    coverage_report[
                        "Symbol"
                    ].nunique()

                    /

                    max(
                        len(universe),
                        1
                    ),

                    4

                )

        }

    # ======================================================
    # TRACKING
    # ======================================================

    def track_metrics(
        self,
        audit_record: dict
    ) -> None:

        try:

            for key, value in (

                audit_record.items()

            ):

                if isinstance(

                    value,

                    (
                        int,
                        float
                    )

                ):

                    MLflowAdapter.log_metric(

                        key,

                        float(value)

                    )

        except Exception:

            pass

        try:

            TelemetryAdapter.track(

                "price_ingestion_runs",

                1

            )

        except Exception:

            pass

    # ======================================================
    # SUMMARY
    # ======================================================

    def print_summary(
        self,
        audit_record: dict
    ) -> None:

        print(
            "\n" + "=" * 80
        )

        print(
            "PRICE INGESTION SUMMARY"
        )

        print(
            "=" * 80
        )

        print(

            f"Universe Size: "

            f"{audit_record['Universe_Size']}"

        )

        print(

            f"Price Rows: "

            f"{audit_record['Price_Rows']:,}"

        )

        print(

            f"Covered Symbols: "

            f"{audit_record['Covered_Symbols']}"

        )

        print(

            f"Missing Symbols: "

            f"{audit_record['Missing_Symbols']}"

        )

        print(

            f"Coverage Ratio: "

            f"{audit_record['Coverage_Ratio']:.2%}"

        )

        print(
            "=" * 80
        )

    # ======================================================
    # MAIN RUN
    # ======================================================

    def run(
        self
    ) -> dict:

        logger.info(
            "Starting Price Ingestion"
        )

        universe = (

            self.universe_loader
            .load()

        )

        existing_prices = (

            self.repository
            .load_existing_prices()

        )

        benchmark_df = (

            self.load_benchmarks()

        )

        missing_prices = (

            self.download_missing_symbols(

                universe,

                existing_prices

            )

        )

        incremental_prices = (

            self.download_incremental_updates(

                universe,

                existing_prices

            )

        )

        new_prices = pd.concat(

            [

                missing_prices,

                incremental_prices

            ],

            ignore_index=True

        )

        prices = (

            self.process_prices(

                existing_prices,

                new_prices

            )

        )

        if new_prices.empty:

            logger.info(
                "No New Data Detected"
            )

            prices = existing_prices

        else:

            prices = self.process_prices(
                existing_prices,
                new_prices
            )
        
        if not new_prices.empty:

            self.repository.save_prices(
                prices
            )

        self.duckdb_sync.sync_prices(
            prices
        )

        self.duckdb_sync.db.register_security_master(
            universe
        )

        metadata_file = Path(
            "data/raw/symbol_metadata.csv"
        )

        if metadata_file.exists():

            metadata = pd.read_csv(
                metadata_file
            )

            self.duckdb_sync.db.register_symbol_metadata(
                metadata
            )

        if len(
            benchmark_df
        ):

            self.duckdb_sync.sync_benchmarks(

                benchmark_df

            )

        coverage_report, missing_report = (

            self.generate_reports(

                universe,

                prices

            )

        )

        audit_record = (

            self.build_audit_record(

                universe,

                prices,

                coverage_report,

                missing_report

            )

        )

        self.audit.save(
            audit_record
        )

        self.track_metrics(
            audit_record
        )

        self.print_summary(
            audit_record
        )

        logger.info(
            "Price Ingestion Complete"
        )

        return {

            "prices":
                prices,

            "coverage":
                coverage_report,

            "missing":
                missing_report,

            "audit":
                audit_record

        }


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    engine = PriceIngestionEngine()

    results = engine.run()