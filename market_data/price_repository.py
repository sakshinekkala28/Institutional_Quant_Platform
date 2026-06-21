# ==========================================================
# PRICE REPOSITORY
# Institutional Quant Platform
# ==========================================================

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import logging
import numpy as np
import pandas as pd

# ==========================================================
# LOGGING
# ==========================================================

logger = logging.getLogger(__name__)

# ==========================================================
# CONFIG
# ==========================================================

@dataclass(slots=True)
class PriceRepositoryConfig:

    DATE_COLUMN: str = "Date"

    SYMBOL_COLUMN: str = "Symbol"

    CLOSE_COLUMN: str = "Close"

    MIN_HISTORY_DAYS: int = 252

    ALLOW_DUPLICATES: bool = False

# ==========================================================
# PRICE REPOSITORY
# ==========================================================

class PriceRepository:

    def __init__(
        self,
        config: Optional[
            PriceRepositoryConfig
        ] = None
    ):

        self.config = (
            config
            or
            PriceRepositoryConfig()
        )

        self.prices: Optional[
            pd.DataFrame
        ] = None

    # ======================================================
    # LOAD DATA
    # ======================================================

    def load_csv(
        self,
        file_path: str | Path
    ) -> pd.DataFrame:

        logger.info(
            f"Loading Prices: {file_path}"
        )

        df = pd.read_csv(
            file_path
        )

        self.validate(
            df
        )

        self.prices = (

            self.standardize(
                df
            )

        )

        logger.info(
            f"Loaded "
            f"{len(self.prices):,} rows"
        )

        return self.prices

    # ======================================================
    # STANDARDIZATION
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
            self.config.SYMBOL_COLUMN
        ] = (

            df[
                self.config.SYMBOL_COLUMN
            ]

            .astype(str)

            .str.upper()

            .str.strip()

        )

        df.sort_values(

            [

                self.config.SYMBOL_COLUMN,

                self.config.DATE_COLUMN

            ],

            inplace=True

        )

        df.reset_index(

            drop=True,

            inplace=True

        )

        return df

    # ======================================================
    # VALIDATION
    # ======================================================

    def validate(
        self,
        df: pd.DataFrame
    ) -> None:

        required = {

            self.config.DATE_COLUMN,

            self.config.SYMBOL_COLUMN,

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
                "Price Dataset Empty"
            )

        duplicates = (

            df.duplicated(

                [

                    self.config.DATE_COLUMN,

                    self.config.SYMBOL_COLUMN

                ]

            ).sum()

        )

        if (

            duplicates > 0

            and

            not self.config.ALLOW_DUPLICATES

        ):

            raise ValueError(

                f"Duplicate Price Records: "
                f"{duplicates}"

            )

    # ======================================================
    # SYMBOL LIST
    # ======================================================

    def get_symbols(
        self
    ) -> list[str]:

        self._check_loaded()

        return sorted(

            self.prices[
                self.config.SYMBOL_COLUMN
            ]

            .unique()

            .tolist()

        )

    # ======================================================
    # PRICE HISTORY
    # ======================================================

    def get_price_history(
        self,
        symbol: str
    ) -> pd.DataFrame:

        self._check_loaded()

        symbol = symbol.upper()

        return (

            self.prices.loc[

                self.prices[
                    self.config.SYMBOL_COLUMN
                ]

                == symbol

            ]

            .copy()

        )

    # ======================================================
    # MULTI SYMBOL HISTORY
    # ======================================================

    def get_price_history_batch(
        self,
        symbols: list[str]
    ) -> pd.DataFrame:

        self._check_loaded()

        symbols = [

            s.upper()

            for s in symbols

        ]

        return (

            self.prices.loc[

                self.prices[
                    self.config.SYMBOL_COLUMN
                ]

                .isin(symbols)

            ]

            .copy()

        )

    # ======================================================
    # RETURNS
    # ======================================================

    def get_returns(
        self
    ) -> pd.DataFrame:

        self._check_loaded()

        df = self.prices.copy()

        df["Return"] = (

            df

            .groupby(

                self.config.SYMBOL_COLUMN

            )[

                self.config.CLOSE_COLUMN

            ]

            .pct_change()

        )

        return df

    # ======================================================
    # LOG RETURNS
    # ======================================================

    def get_log_returns(
        self
    ) -> pd.DataFrame:

        self._check_loaded()

        df = self.prices.copy()

        df["Log_Return"] = (

            np.log(

                df.groupby(

                    self.config.SYMBOL_COLUMN

                )[

                    self.config.CLOSE_COLUMN

                ]

                .transform(

                    lambda x:
                    x / x.shift(1)

                )

            )

        )

        return df

    # ======================================================
    # RETURN MATRIX
    # ======================================================

    def get_return_matrix(
        self
    ) -> pd.DataFrame:

        returns = (

            self.get_returns()

        )

        matrix = (

            returns.pivot(

                index=self.config.DATE_COLUMN,

                columns=self.config.SYMBOL_COLUMN,

                values="Return"

            )

        )

        return matrix

    # ======================================================
    # PRICE MATRIX
    # ======================================================

    def get_price_matrix(
        self
    ) -> pd.DataFrame:

        self._check_loaded()

        matrix = (

            self.prices.pivot(

                index=self.config.DATE_COLUMN,

                columns=self.config.SYMBOL_COLUMN,

                values=self.config.CLOSE_COLUMN

            )

        )

        return matrix

    # ======================================================
    # LATEST PRICES
    # ======================================================

    def get_latest_prices(
        self
    ) -> pd.DataFrame:

        self._check_loaded()

        latest = (

            self.prices

            .sort_values(

                self.config.DATE_COLUMN

            )

            .groupby(

                self.config.SYMBOL_COLUMN

            )

            .tail(1)

        )

        return latest

    # ======================================================
    # COVERAGE REPORT
    # ======================================================

    def coverage_report(
        self
    ) -> pd.DataFrame:

        self._check_loaded()

        report = (

            self.prices

            .groupby(

                self.config.SYMBOL_COLUMN

            )

            .agg(

                First_Date=(

                    self.config.DATE_COLUMN,

                    "min"

                ),

                Last_Date=(

                    self.config.DATE_COLUMN,

                    "max"

                ),

                Observations=(

                    self.config.CLOSE_COLUMN,

                    "count"

                )

            )

            .reset_index()

        )

        return report

    # ======================================================
    # HISTORY FILTER
    # ======================================================

    def filter_min_history(
        self
    ) -> pd.DataFrame:

        self._check_loaded()

        coverage = (

            self.coverage_report()

        )

        valid = coverage.loc[

            coverage[
                "Observations"
            ]

            >=

            self.config.MIN_HISTORY_DAYS,

            self.config.SYMBOL_COLUMN

        ]

        return (

            self.prices.loc[

                self.prices[
                    self.config.SYMBOL_COLUMN
                ]

                .isin(valid)

            ]

            .copy()

        )

    # ======================================================
    # INTERNAL
    # ======================================================

    def _check_loaded(
        self
    ) -> None:

        if self.prices is None:

            raise RuntimeError(

                "Price Data Not Loaded"

            )