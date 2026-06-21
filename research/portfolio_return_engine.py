# ==========================================================
# PORTFOLIO RETURN ENGINE
# Institutional Quant Platform
# ==========================================================

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import logging
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ==========================================================
# CONFIG
# ==========================================================

@dataclass(slots=True)
class ReturnEngineConfig:

    INITIAL_CAPITAL: float = 100_000_000

    TRADING_DAYS: int = 252

    ENABLE_COSTS: bool = True

    ENABLE_BENCHMARK: bool = True

    ENABLE_DRIFT_TRACKING: bool = True

# ==========================================================
# RETURN ENGINE
# ==========================================================

class PortfolioReturnEngine:

    def __init__(
        self,
        config: Optional[
            ReturnEngineConfig
        ] = None
    ):

        self.config = (
            config
            or
            ReturnEngineConfig()
        )

    # ======================================================
    # VALIDATION
    # ======================================================

    @staticmethod
    def validate_inputs(
        portfolio: pd.DataFrame,
        prices: pd.DataFrame
    ) -> None:

        portfolio_cols = {

            "Symbol",

            "Target_Weight"

        }

        price_cols = {

            "Date",

            "Symbol",

            "Close"

        }

        missing_portfolio = (

            portfolio_cols

            - set(
                portfolio.columns
            )

        )

        missing_prices = (

            price_cols

            - set(
                prices.columns
            )

        )

        if missing_portfolio:

            raise ValueError(
                f"Missing Portfolio Columns: "
                f"{missing_portfolio}"
            )

        if missing_prices:

            raise ValueError(
                f"Missing Price Columns: "
                f"{missing_prices}"
            )

    # ======================================================
    # SECURITY RETURNS
    # ======================================================

    @staticmethod
    def build_security_returns(
        prices: pd.DataFrame
    ) -> pd.DataFrame:

        prices = prices.copy()

        prices["Date"] = pd.to_datetime(

            prices["Date"]

        )

        prices.sort_values(

            [

                "Symbol",

                "Date"

            ],

            inplace=True

        )

        prices["Return"] = (

            prices

            .groupby("Symbol")

            ["Close"]

            .pct_change()

        )

        return prices

    # ======================================================
    # DAILY PORTFOLIO RETURNS
    # ======================================================

    def build_returns(
        self,
        portfolio: pd.DataFrame,
        prices: pd.DataFrame
    ) -> pd.DataFrame:

        self.validate_inputs(

            portfolio,

            prices

        )

        logger.info(

            "Building Portfolio Returns"

        )

        prices = (

            self.build_security_returns(

                prices

            )

        )

        weights = (

            portfolio[

                [

                    "Symbol",

                    "Target_Weight"

                ]

            ]

            .copy()

        )

        merged = (

            prices.merge(

                weights,

                on="Symbol",

                how="inner"

            )

        )

        merged["Weighted_Return"] = (

            merged["Return"]

            *

            merged["Target_Weight"]

        )

        returns = (

            merged

            .groupby("Date")

            ["Weighted_Return"]

            .sum()

            .reset_index()

        )

        returns.rename(

            columns={

                "Weighted_Return":

                "Portfolio_Return"

            },

            inplace=True

        )

        return returns

    # ======================================================
    # COST ADJUSTED RETURNS
    # ======================================================

    @staticmethod
    def apply_transaction_costs(
        returns: pd.DataFrame,
        annual_cost_bps: float = 50
    ) -> pd.DataFrame:

        returns = returns.copy()

        daily_cost = (

            annual_cost_bps

            / 10000

            / 252

        )

        returns[

            "Net_Return"

        ] = (

            returns[
                "Portfolio_Return"
            ]

            -

            daily_cost

        )

        return returns

    # ======================================================
    # EQUITY CURVE
    # ======================================================

    def build_equity_curve(
        self,
        returns: pd.DataFrame
    ) -> pd.DataFrame:

        returns = returns.copy()

        series = (

            returns.get(

                "Net_Return",

                returns[
                    "Portfolio_Return"
                ]

            )

        )

        returns["Equity"] = (

            self.config

            .INITIAL_CAPITAL

            *

            (

                1 + series

            )

            .cumprod()

        )

        return returns

    # ======================================================
    # DRIFT TRACKING
    # ======================================================

    @staticmethod
    def calculate_weight_drift(
        portfolio: pd.DataFrame,
        current_prices: pd.DataFrame
    ) -> pd.DataFrame:

        result = portfolio.copy()

        result["Drift"] = 0.0

        return result

    # ======================================================
    # BENCHMARK RELATIVE
    # ======================================================

    @staticmethod
    def benchmark_relative_returns(
        portfolio_returns: pd.DataFrame,
        benchmark_returns: pd.DataFrame
    ) -> pd.DataFrame:

        merged = (

            portfolio_returns.merge(

                benchmark_returns,

                on="Date",

                how="inner"

            )

        )

        merged["Active_Return"] = (

            merged["Portfolio_Return"]

            -

            merged["Benchmark_Return"]

        )

        return merged

    # ======================================================
    # ATTRIBUTION HOOK
    # ======================================================

    @staticmethod
    def build_attribution_frame(
        portfolio: pd.DataFrame
    ) -> pd.DataFrame:

        if "Sector" not in portfolio.columns:

            return pd.DataFrame()

        return (

            portfolio

            .groupby("Sector")

            ["Target_Weight"]

            .sum()

            .reset_index()

        )

    # ======================================================
    # MASTER PIPELINE
    # ======================================================

    def run(
        self,
        portfolio: pd.DataFrame,
        prices: pd.DataFrame,
        benchmark_returns: Optional[
            pd.DataFrame
        ] = None
    ) -> dict:

        returns = (

            self.build_returns(

                portfolio,

                prices

            )

        )

        if self.config.ENABLE_COSTS:

            returns = (

                self.apply_transaction_costs(

                    returns

                )

            )

        equity_curve = (

            self.build_equity_curve(

                returns

            )

        )

        result = {

            "returns":

                returns,

            "equity_curve":

                equity_curve,

            "attribution":

                self.build_attribution_frame(

                    portfolio

                )

        }

        if (

            benchmark_returns is not None

            and

            self.config.ENABLE_BENCHMARK

        ):

            result[

                "benchmark"

            ] = (

                self.benchmark_relative_returns(

                    returns,

                    benchmark_returns

                )

            )

        logger.info(

            "Portfolio Return Engine Complete"

        )

        return result