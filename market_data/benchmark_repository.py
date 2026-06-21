# ==========================================================
# BENCHMARK REPOSITORY
# Institutional Quant Platform
# ==========================================================

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# ==========================================================
# CONFIG
# ==========================================================

@dataclass(slots=True)
class BenchmarkRepositoryConfig:

    DATE_COLUMN: str = "Date"

    BENCHMARK_COLUMN: str = "Benchmark"

    CLOSE_COLUMN: str = "Close"

    RETURN_COLUMN: str = "Benchmark_Return"

# ==========================================================
# BENCHMARK REPOSITORY
# ==========================================================

class BenchmarkRepository:

    SUPPORTED_BENCHMARKS = {

        "NIFTY50",

        "NIFTY100",

        "NIFTY200",

        "NIFTY500",

        "MIDCAP150",

        "SMALLCAP250"

    }

    def __init__(
        self,
        config: Optional[
            BenchmarkRepositoryConfig
        ] = None
    ):

        self.config = (
            config
            or
            BenchmarkRepositoryConfig()
        )

        self.data: Optional[
            pd.DataFrame
        ] = None

    # ======================================================
    # LOAD
    # ======================================================

    def load_csv(
        self,
        file_path: str | Path
    ) -> pd.DataFrame:

        logger.info(
            f"Loading Benchmark Data: "
            f"{file_path}"
        )

        df = pd.read_csv(
            file_path
        )

        self.validate(
            df
        )

        self.data = (
            self.standardize(
                df
            )
        )

        logger.info(
            f"Loaded "
            f"{len(self.data):,} rows"
        )

        return self.data

    # ======================================================
    # STANDARDIZE
    # ======================================================

    def standardize(
        self,
        df: pd.DataFrame
    ) -> pd.DataFrame:

        df = df.copy()

        df[
            self.config.DATE_COLUMN
        ] = pd.to_datetime(
            df[
                self.config.DATE_COLUMN
            ]
        )

        df[
            self.config.BENCHMARK_COLUMN
        ] = (

            df[
                self.config.BENCHMARK_COLUMN
            ]

            .astype(str)

            .str.upper()

            .str.strip()

        )

        df.sort_values(

            [

                self.config.BENCHMARK_COLUMN,

                self.config.DATE_COLUMN

            ],

            inplace=True

        )

        return df

    # ======================================================
    # VALIDATE
    # ======================================================

    def validate(
        self,
        df: pd.DataFrame
    ) -> None:

        required = {

            self.config.DATE_COLUMN,

            self.config.BENCHMARK_COLUMN,

            self.config.CLOSE_COLUMN

        }

        missing = (

            required

            - set(df.columns)

        )

        if missing:

            raise ValueError(
                f"Missing Columns: "
                f"{missing}"
            )

        if df.empty:

            raise ValueError(
                "Benchmark Dataset Empty"
            )

    # ======================================================
    # RETURNS
    # ======================================================

    def get_returns(
        self
    ) -> pd.DataFrame:

        self._check_loaded()

        df = self.data.copy()

        df[
            self.config.RETURN_COLUMN
        ] = (

            df

            .groupby(
                self.config.BENCHMARK_COLUMN
            )[
                self.config.CLOSE_COLUMN
            ]

            .pct_change()

        )

        return df

    # ======================================================
    # BENCHMARK SERIES
    # ======================================================

    def get_benchmark(
        self,
        benchmark: str
    ) -> pd.DataFrame:

        self._check_loaded()

        benchmark = (
            benchmark.upper()
        )

        return (

            self.data.loc[

                self.data[
                    self.config.BENCHMARK_COLUMN
                ]

                == benchmark

            ]

            .copy()

        )

    # ======================================================
    # RETURN SERIES
    # ======================================================

    def get_return_series(
        self,
        benchmark: str
    ) -> pd.DataFrame:

        benchmark_df = (

            self.get_returns()

        )

        benchmark = (
            benchmark.upper()
        )

        return (

            benchmark_df.loc[

                benchmark_df[
                    self.config.BENCHMARK_COLUMN
                ]

                == benchmark

            ]

            [

                [

                    self.config.DATE_COLUMN,

                    self.config.RETURN_COLUMN

                ]

            ]

            .copy()

        )

    # ======================================================
    # EQUITY CURVE
    # ======================================================

    def build_equity_curve(
        self,
        benchmark: str,
        initial_value: float = 100
    ) -> pd.DataFrame:

        returns = (

            self.get_return_series(
                benchmark
            )

        )

        returns[
            "Benchmark_Value"
        ] = (

            initial_value

            *

            (

                1

                +

                returns[
                    self.config.RETURN_COLUMN
                ]

                .fillna(0)

            )

            .cumprod()

        )

        return returns

    # ======================================================
    # LIST
    # ======================================================

    def available_benchmarks(
        self
    ) -> list[str]:

        self._check_loaded()

        return sorted(

            self.data[
                self.config.BENCHMARK_COLUMN
            ]

            .unique()

            .tolist()

        )

    # ======================================================
    # INTERNAL
    # ======================================================

    def _check_loaded(
        self
    ) -> None:

        if self.data is None:

            raise RuntimeError(
                "Benchmark Data Not Loaded"
            )