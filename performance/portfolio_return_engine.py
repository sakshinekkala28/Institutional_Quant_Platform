# ==========================================================
# PORTFOLIO RETURN ENGINE
# Institutional Performance Analytics Framework
# ==========================================================

from __future__ import annotations

import logging

from dataclasses import dataclass

from pathlib import Path

import numpy as np

import pandas as pd


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
# PATH CONFIGURATION
# ==========================================================

ROOT_DIR = Path.cwd()

OPTIMIZED_PORTFOLIO_FILE = (

    ROOT_DIR

    / "data/portfolios/optimized_portfolio.csv"

)

LIVE_PORTFOLIO_FILE = (

    ROOT_DIR

    / "data/portfolios/live_portfolio.csv"

)

PRICE_HISTORY_FILE = (

    ROOT_DIR

    / "data/raw/security_price_history.parquet"

)

BENCHMARK_FILE = (

    ROOT_DIR

    / "data/raw/benchmark_prices.parquet"

)

SECURITY_MASTER_FILE = (

    ROOT_DIR

    / "data/raw/security_master.csv"

)

REBALANCE_FILE = (

    ROOT_DIR

    / "data/live/rebalance_history.csv"

)

SECURITY_ATTRIBUTION_FILE = (

    ROOT_DIR

    / "data/performance/security_attribution.csv"

)

SECTOR_ATTRIBUTION_FILE = (

    ROOT_DIR

    / "data/performance/sector_attribution.csv"

)

FACTOR_ATTRIBUTION_FILE = (

    ROOT_DIR

    / "data/performance/factor_attribution.csv"

)

OUTPUT_DIR = (

    ROOT_DIR

    / "data/performance"

)

OUTPUT_DIR.mkdir(

    parents=True,

    exist_ok=True

)


# ==========================================================
# OUTPUT FILES
# ==========================================================

PORTFOLIO_NAV_FILE = (

    OUTPUT_DIR

    / "portfolio_nav.csv"

)

PORTFOLIO_RETURNS_FILE = (

    OUTPUT_DIR

    / "portfolio_returns.csv"

)

BENCHMARK_RETURNS_FILE = (

    OUTPUT_DIR

    / "benchmark_returns.csv"

)

ROLLING_PERFORMANCE_FILE = (

    OUTPUT_DIR

    / "rolling_performance.csv"

)

PERFORMANCE_SUMMARY_FILE = (

    OUTPUT_DIR

    / "performance_summary.csv"

)

PERFORMANCE_DASHBOARD_FILE = (

    OUTPUT_DIR

    / "performance_dashboard.csv"

)

PERFORMANCE_AUDIT_FILE = (

    OUTPUT_DIR

    / "performance_audit.csv"

)

REGIME_STATISTICS_FILE = (

    OUTPUT_DIR

    / "regime_statistics.csv"

)

REGIME_TRANSITION_FILE = (

    OUTPUT_DIR

    / "regime_transition_matrix.csv"

)

REGIME_PERSISTENCE_FILE = (

    OUTPUT_DIR

    / "regime_persistence.csv"

)

REGIME_SCORECARD_FILE = (

    OUTPUT_DIR

    / "regime_scorecard.csv"

)


# ==========================================================
# CONFIGURATION
# ==========================================================

@dataclass(frozen=True)
class PerformanceConfig:

    TRADING_DAYS: int = 252

    MONTH_DAYS: int = 21

    QUARTER_DAYS: int = 63

    YEAR_DAYS: int = 252

    MIN_OBSERVATIONS: int = 60

    RISK_FREE_RATE: float = 0.06

    INITIAL_NAV: float = 100.0

    ROLLING_WINDOW: int = 63

    MAX_LOOKBACK_DAYS: int = 2520


CONFIG = PerformanceConfig()


# ==========================================================
# PORTFOLIO REPOSITORY
# ==========================================================

class PortfolioRepository:

    @staticmethod
    def load() -> pd.DataFrame:

        logger.info(

            "Loading Portfolio"

        )

        if (

            OPTIMIZED_PORTFOLIO_FILE

            .exists()

        ):

            logger.info(

                "Using Optimized Portfolio"

            )

            portfolio = pd.read_csv(

                OPTIMIZED_PORTFOLIO_FILE

            )

        else:

            logger.info(

                "Using Live Portfolio"

            )

            portfolio = pd.read_csv(

                LIVE_PORTFOLIO_FILE

            )

        weight_col = (

            "Optimized_Weight"

            if

            "Optimized_Weight"

            in portfolio.columns

            else

            "Weight"

        )

        portfolio["Weight"] = (

            pd.to_numeric(

                portfolio[

                    weight_col

                ],

                errors="coerce"

            )

        )

        security_master = (

            SecurityMasterRepository

            .load()

        )

        portfolio = (

            portfolio

            .merge(

                security_master[

                    [

                        "Symbol",

                        "Yahoo_Symbol"

                    ]

                ],

                on="Symbol",

                how="left"

            )

        )

        missing_map = (

            portfolio[

                "Yahoo_Symbol"

            ]

            .isna()

            .sum()

        )

        logger.info(

            f"Missing Yahoo Mappings: "

            f"{missing_map:,}"

        )        

        portfolio = (

            portfolio

            .drop_duplicates(

                subset=[

                    "Symbol"

                ]

            )

        )

        portfolio = (

            portfolio

            .loc[

                portfolio[

                    "Weight"

                ] > 0

            ]

        )

        portfolio["Weight"] = (

            portfolio[

                "Weight"

            ]

            /

            portfolio[

                "Weight"

            ]

            .sum()

        )

        logger.info(

            f"Portfolio Holdings: "

            f"{len(portfolio):,}"

        )

        logger.info(

            f"Weight Source: "

            f"{weight_col}"

        )

        logger.info(

            f"Total Weight: "

            f"{portfolio['Weight'].sum():.6f}"

        )

        return portfolio

# ==========================================================
# SECURITY MASTER REPOSITORY
# ==========================================================

class SecurityMasterRepository:

    @staticmethod
    def load() -> pd.DataFrame:

        logger.info(

            "Loading Security Master"

        )

        return pd.read_csv(

            SECURITY_MASTER_FILE

        )
    
# ==========================================================
# PRICE REPOSITORY
# ==========================================================

class PriceRepository:

    @staticmethod
    def load() -> pd.DataFrame:

        logger.info(

            "Loading Security Prices"

        )

        prices = pd.read_parquet(

            PRICE_HISTORY_FILE

        )

        prices["Date"] = (

            pd.to_datetime(

                prices["Date"]

            )

        )

        prices = (

            prices

            .sort_values(

                [

                    "Symbol",

                    "Date"

                ]

            )

        )

        prices["Daily_Return"] = (

            prices

            .groupby(

                "Symbol"

            )["Close"]

            .pct_change()

        )

        logger.info(

            f"Price Rows: "

            f"{len(prices):,}"

        )

        return prices


# ==========================================================
# BENCHMARK REPOSITORY
# ==========================================================

class BenchmarkRepository:

    @staticmethod
    def load() -> pd.DataFrame:

        logger.info(

            "Loading Benchmark"

        )

        benchmark = pd.read_parquet(

            BENCHMARK_FILE

        )

        benchmark["Date"] = (

            pd.to_datetime(

                benchmark["Date"]

            )

        )

        benchmark = (

            benchmark

            .sort_values(

                "Date"

            )

        )

        benchmark[
            "Benchmark_Return"
        ] = (

            benchmark[
                "Close"
            ]

            .pct_change()

        )

        logger.info(

            f"Benchmark Rows: "

            f"{len(benchmark):,}"

        )

        return benchmark

# ==========================================================
# VALIDATION
# ==========================================================

class PortfolioValidator:

    @staticmethod
    def validate_portfolio(

        portfolio: pd.DataFrame

    ):

        required_columns = [

            "Symbol",

            "Weight"

        ]

        missing = [

            col

            for col in required_columns

            if col not in portfolio.columns

        ]

        if missing:

            raise ValueError(

                f"Missing Portfolio Columns: "

                f"{missing}"

            )

        if portfolio.empty:

            raise ValueError(

                "Portfolio Empty"

            )

        total_weight = (

            portfolio[
                "Weight"
            ]

            .sum()

        )

        if total_weight <= 0:

            raise ValueError(

                "Invalid Portfolio Weights"

            )

        logger.info(

            "Portfolio Validation Passed"

        )

    @staticmethod
    def validate_prices(

        prices: pd.DataFrame

    ):

        required_columns = [

            "Date",

            "Symbol",

            "Close",

            "Daily_Return"

        ]

        missing = [

            col

            for col in required_columns

            if col not in prices.columns

        ]

        if missing:

            raise ValueError(

                f"Missing Price Columns: "

                f"{missing}"

            )

        logger.info(

            "Price Validation Passed"

        )

    @staticmethod
    def validate_benchmark(

        benchmark: pd.DataFrame

    ):

        required_columns = [

            "Date",

            "Benchmark_Return"

        ]

        missing = [

            col

            for col in required_columns

            if col not in benchmark.columns

        ]

        if missing:

            raise ValueError(

                f"Missing Benchmark Columns: "

                f"{missing}"

            )

        logger.info(

            "Benchmark Validation Passed"

        )


# ==========================================================
# PORTFOLIO RETURN CALCULATOR
# ==========================================================

class PortfolioReturnCalculator:

    @staticmethod
    def build_returns(

        portfolio: pd.DataFrame,

        prices: pd.DataFrame

    ) -> pd.DataFrame:

        logger.info(

            "Building Portfolio Returns"

        )

        portfolio_symbols = (

            portfolio[
                "Yahoo_Symbol"
            ]

            .dropna()

            .unique()

        )

        prices = (

            prices.loc[

                prices[
                    "Symbol"
                ]

                .isin(

                    portfolio_symbols

                )

            ]

            .copy()

        )

        merged = (

            prices

            .merge(

                portfolio[

                    [

                        "Yahoo_Symbol",

                        "Weight",

                        "Sector",

                        "Company_Name"

                    ]

                ],

                left_on="Symbol",

                right_on="Yahoo_Symbol",

                how="inner"

            )

        )

        merged[
            "Weighted_Return"
        ] = (

            merged[
                "Daily_Return"
            ]

            *

            merged[
                "Weight"
            ]

        )

        portfolio_returns = (

            merged

            .groupby(

                "Date",

                as_index=False

            )

            .agg(

                Portfolio_Return=(

                    "Weighted_Return",

                    "sum"

                ),

                Holdings=(

                    "Symbol",

                    "nunique"

                )

            )

        )

        portfolio_returns = (

            portfolio_returns

            .dropna(

                subset=[

                    "Portfolio_Return"

                ]

            )

        )

        logger.info(

            f"Portfolio Return Days: "

            f"{len(portfolio_returns):,}"

        )

        return portfolio_returns


# ==========================================================
# NAV ENGINE
# ==========================================================

class PortfolioNAVEngine:

    @staticmethod
    def build_nav(

        portfolio_returns: pd.DataFrame

    ) -> pd.DataFrame:

        logger.info(

            "Building Portfolio NAV"

        )

        nav = (

            portfolio_returns

            .copy()

        )

        nav[
            "Portfolio_NAV"
        ] = (

            CONFIG
            .INITIAL_NAV

            *

            (

                1

                +

                nav[
                    "Portfolio_Return"
                ]

            )

            .cumprod()

        )

        nav[
            "Cumulative_Return"
        ] = (

            nav[
                "Portfolio_NAV"
            ]

            /

            CONFIG
            .INITIAL_NAV

            -

            1

        )

        logger.info(

            "Portfolio NAV Built"

        )

        return nav


# ==========================================================
# BENCHMARK RETURN ENGINE
# ==========================================================

class BenchmarkReturnCalculator:

    @staticmethod
    def build_returns(

        benchmark: pd.DataFrame

    ) -> pd.DataFrame:

        logger.info(

            "Building Benchmark Returns"

        )

        benchmark_returns = (

            benchmark[

                [

                    "Date",

                    "Benchmark_Return"

                ]

            ]

            .dropna()

            .copy()

        )

        benchmark_returns[
            "Benchmark_NAV"
        ] = (

            CONFIG
            .INITIAL_NAV

            *

            (

                1

                +

                benchmark_returns[
                    "Benchmark_Return"
                ]

            )

            .cumprod()

        )

        benchmark_returns[
            "Benchmark_Cumulative_Return"
        ] = (

            benchmark_returns[
                "Benchmark_NAV"
            ]

            /

            CONFIG
            .INITIAL_NAV

            -

            1

        )

        logger.info(

            f"Benchmark Days: "

            f"{len(benchmark_returns):,}"

        )

        return benchmark_returns


# ==========================================================
# EXCESS RETURN ENGINE
# ==========================================================

class ExcessReturnEngine:

    @staticmethod
    def build(

        portfolio_nav: pd.DataFrame,

        benchmark_returns: pd.DataFrame

    ) -> pd.DataFrame:

        logger.info(

            "Building Excess Returns"

        )

        merged = (

            portfolio_nav

            .merge(

                benchmark_returns,

                on="Date",

                how="inner"

            )

        )

        merged[
            "Excess_Return"
        ] = (

            merged[
                "Portfolio_Return"
            ]

            -

            merged[
                "Benchmark_Return"
            ]

        )

        merged[
            "Excess_Cumulative_Return"
        ] = (

            (

                1

                +

                merged[
                    "Excess_Return"
                ]

            )

            .cumprod()

            -

            1

        )

        logger.info(

            f"Aligned Return Days: "

            f"{len(merged):,}"

        )

        return merged


# ==========================================================
# RETURN REPOSITORY
# ==========================================================

class ReturnRepository:

    @staticmethod
    def build():

        portfolio = (

            PortfolioRepository
            .load()

        )

        prices = (

            PriceRepository
            .load()

        )

        benchmark = (

            BenchmarkRepository
            .load()

        )

        PortfolioValidator.validate_portfolio(

            portfolio

        )

        PortfolioValidator.validate_prices(

            prices

        )

        PortfolioValidator.validate_benchmark(

            benchmark

        )

        portfolio_returns = (

            PortfolioReturnCalculator

            .build_returns(

                portfolio,

                prices

            )

        )

        portfolio_nav = (

            PortfolioNAVEngine

            .build_nav(

                portfolio_returns

            )

        )

        benchmark_returns = (

            BenchmarkReturnCalculator

            .build_returns(

                benchmark

            )

        )

        performance_df = (

            ExcessReturnEngine

            .build(

                portfolio_nav,

                benchmark_returns

            )

        )

        return (

            portfolio,

            performance_df

        )

# ==========================================================
# DRAWDOWN ENGINE
# ==========================================================

class DrawdownEngine:

    @staticmethod
    def calculate(

        nav_series: pd.Series

    ) -> dict:

        nav_series = (

            pd.to_numeric(

                nav_series,

                errors="coerce"

            )

            .dropna()

        )

        if len(nav_series) == 0:

            logger.warning(

                "NAV Series Empty"

            )

            return {

                "Max_Drawdown": np.nan,

                "Current_Drawdown": np.nan

            }

        running_max = (

            nav_series

            .cummax()

        )

        drawdown = (

            nav_series

            /

            running_max

            -

            1

        )

        return {

            "Max_Drawdown":

                drawdown.min(),

            "Current_Drawdown":

                drawdown.iloc[-1]

        }
    
# ==========================================================
# VOLATILITY ENGINE
# ==========================================================

class VolatilityEngine:

    @staticmethod
    def annualized(

        returns: pd.Series

    ) -> float:

        return (

            returns.std()

            *

            np.sqrt(

                CONFIG
                .TRADING_DAYS

            )

        )


# ==========================================================
# SHARPE ENGINE
# ==========================================================

class SharpeRatioEngine:

    @staticmethod
    def calculate(

        returns: pd.Series

    ) -> float:

        annual_return = (

            returns.mean()

            *

            CONFIG
            .TRADING_DAYS

        )

        annual_vol = (

            VolatilityEngine

            .annualized(

                returns

            )

        )

        if annual_vol == 0:

            return np.nan

        return (

            annual_return

            -

            CONFIG
            .RISK_FREE_RATE

        ) / annual_vol


# ==========================================================
# SORTINO ENGINE
# ==========================================================

class SortinoRatioEngine:

    @staticmethod
    def calculate(

        returns: pd.Series

    ) -> float:

        downside = (

            returns.loc[

                returns < 0

            ]

        )

        downside_vol = (

            downside.std()

            *

            np.sqrt(

                CONFIG
                .TRADING_DAYS

            )

        )

        annual_return = (

            returns.mean()

            *

            CONFIG
            .TRADING_DAYS

        )

        if downside_vol == 0:

            return np.nan

        return (

            annual_return

            -

            CONFIG
            .RISK_FREE_RATE

        ) / downside_vol


# ==========================================================
# CALMAR ENGINE
# ==========================================================

class CalmarRatioEngine:

    @staticmethod
    def calculate(

        annual_return: float,

        max_drawdown: float

    ) -> float:

        if max_drawdown == 0:

            return np.nan

        return (

            annual_return

            /

            abs(

                max_drawdown

            )

        )


# ==========================================================
# ALPHA / BETA ENGINE
# ==========================================================

class AlphaBetaEngine:

    @staticmethod
    def calculate(

        portfolio_returns: pd.Series,

        benchmark_returns: pd.Series

    ):

        covariance = np.cov(

            portfolio_returns,

            benchmark_returns

        )

        beta = (

            covariance[0, 1]

            /

            covariance[1, 1]

        )

        annual_portfolio = (

            portfolio_returns.mean()

            *

            CONFIG
            .TRADING_DAYS

        )

        annual_benchmark = (

            benchmark_returns.mean()

            *

            CONFIG
            .TRADING_DAYS

        )

        alpha = (

            annual_portfolio

            -

            (

                CONFIG
                .RISK_FREE_RATE

                +

                beta

                *

                (

                    annual_benchmark

                    -

                    CONFIG
                    .RISK_FREE_RATE

                )

            )

        )

        return (

            alpha,

            beta

        )


# ==========================================================
# TRACKING ERROR ENGINE
# ==========================================================

class TrackingErrorEngine:

    @staticmethod
    def calculate(

        excess_returns: pd.Series

    ) -> float:

        return (

            excess_returns.std()

            *

            np.sqrt(

                CONFIG
                .TRADING_DAYS

            )

        )

# ==========================================================
# VALUE AT RISK ENGINE
# ==========================================================

class ValueAtRiskEngine:

    @staticmethod
    def historical(

        returns: pd.Series,

        confidence: float

    ) -> float:

        returns = (

            returns

            .dropna()

        )

        if len(

            returns

        ) == 0:

            return np.nan

        percentile = (

            100

            *

            (

                1

                -

                confidence

            )

        )

        return abs(

            np.percentile(

                returns,

                percentile

            )

        )

    @staticmethod
    def parametric(

        returns: pd.Series,

        confidence: float

    ) -> float:

        returns = (

            returns

            .dropna()

        )

        if len(

            returns

        ) == 0:

            return np.nan

        mean = (

            returns.mean()

        )

        std = (

            returns.std()

        )

        z_scores = {

            0.95: 1.645,

            0.99: 2.326

        }

        z = (

            z_scores.get(

                confidence,

                1.645

            )

        )

        var = (

            z

            *

            std

            -

            mean

        )

        return abs(

            var

        )
    
# ==========================================================
# CONDITIONAL VALUE AT RISK ENGINE
# ==========================================================

class ConditionalValueAtRiskEngine:

    @staticmethod
    def historical(

        returns: pd.Series,

        confidence: float

    ) -> float:

        returns = (

            returns

            .dropna()

        )

        if len(

            returns

        ) == 0:

            return np.nan

        percentile = (

            np.percentile(

                returns,

                100

                *

                (

                    1

                    -

                    confidence

                )

            )

        )

        tail_losses = (

            returns[

                returns

                <=

                percentile

            ]

        )

        if len(

            tail_losses

        ) == 0:

            return np.nan

        return abs(

            tail_losses

            .mean()

        )

    @staticmethod
    def parametric(

        returns: pd.Series,

        confidence: float

    ) -> float:

        returns = (

            returns

            .dropna()

        )

        if len(

            returns

        ) == 0:

            return np.nan

        mean = (

            returns.mean()

        )

        std = (

            returns.std()

        )

        if confidence == 0.95:

            z = 1.645

            pdf = 0.103

        elif confidence == 0.99:

            z = 2.326

            pdf = 0.026

        else:

            z = 1.645

            pdf = 0.103

        cvar = (

            mean

            -

            (

                std

                *

                pdf

                /

                (

                    1

                    -

                    confidence

                )

            )

        )

        return abs(

            cvar

        )
    
# ==========================================================
# TAIL RISK ENGINE
# ==========================================================

class TailRiskEngine:

    @staticmethod
    def calculate(

        returns: pd.Series

    ) -> dict:

        returns = (

            returns

            .dropna()

        )

        if len(

            returns

        ) == 0:

            return {

                "Worst_Day":

                    np.nan,

                "Worst_Week":

                    np.nan,

                "Skewness":

                    np.nan,

                "Kurtosis":

                    np.nan

            }

        weekly_returns = (

            returns

            .rolling(

                5

            )

            .sum()

        )

        return {

            "Worst_Day":

                returns.min(),

            "Worst_Week":

                weekly_returns.min(),

            "Skewness":

                returns.skew(),

            "Kurtosis":

                returns.kurt()

        }
    
# ==========================================================
# RISK LIMIT ENGINE
# ==========================================================

class RiskLimitEngine:

    @staticmethod
    def classify(

        var_95: float,

        cvar_95: float

    ) -> str:

        if (

            pd.isna(

                var_95

            )

        ):

            return "UNKNOWN"

        if (

            var_95 <= 0.02

            and

            cvar_95 <= 0.03

        ):

            return "LOW"

        if (

            var_95 <= 0.04

            and

            cvar_95 <= 0.06

        ):

            return "MODERATE"

        if (

            var_95 <= 0.06

            and

            cvar_95 <= 0.08

        ):

            return "ELEVATED"

        return "HIGH"
    
# ==========================================================
# VAR SUMMARY ENGINE
# ==========================================================

class VaRSummaryEngine:

    @staticmethod
    def build(

        returns: pd.Series

    ) -> pd.DataFrame:

        logger.info(

            "Building VaR Summary"

        )

        var_95_hist = (

            ValueAtRiskEngine
            .historical(

                returns,

                0.95

            )

        )

        var_99_hist = (

            ValueAtRiskEngine
            .historical(

                returns,

                0.99

            )

        )

        var_95_param = (

            ValueAtRiskEngine
            .parametric(

                returns,

                0.95

            )

        )

        var_99_param = (

            ValueAtRiskEngine
            .parametric(

                returns,

                0.99

            )

        )

        return pd.DataFrame(

            {

                "Metric": [

                    "Historical_VaR_95",

                    "Historical_VaR_99",

                    "Parametric_VaR_95",

                    "Parametric_VaR_99"

                ],

                "Value": [

                    var_95_hist,

                    var_99_hist,

                    var_95_param,

                    var_99_param

                ]

            }

        )
    
# ==========================================================
# CVAR SUMMARY ENGINE
# ==========================================================

class CVaRSummaryEngine:

    @staticmethod
    def build(

        returns: pd.Series

    ) -> pd.DataFrame:

        logger.info(

            "Building CVaR Summary"

        )

        cvar_95_hist = (

            ConditionalValueAtRiskEngine
            .historical(

                returns,

                0.95

            )

        )

        cvar_99_hist = (

            ConditionalValueAtRiskEngine
            .historical(

                returns,

                0.99

            )

        )

        cvar_95_param = (

            ConditionalValueAtRiskEngine
            .parametric(

                returns,

                0.95

            )

        )

        cvar_99_param = (

            ConditionalValueAtRiskEngine
            .parametric(

                returns,

                0.99

            )

        )

        return pd.DataFrame(

            {

                "Metric": [

                    "Historical_CVaR_95",

                    "Historical_CVaR_99",

                    "Parametric_CVaR_95",

                    "Parametric_CVaR_99"

                ],

                "Value": [

                    cvar_95_hist,

                    cvar_99_hist,

                    cvar_95_param,

                    cvar_99_param

                ]

            }

        )
    
# ==========================================================
# TAIL RISK DASHBOARD
# ==========================================================

class TailRiskDashboardEngine:

    @staticmethod
    def build(

        returns: pd.Series

    ) -> pd.DataFrame:

        logger.info(

            "Building Tail Risk Dashboard"

        )

        tail = (

            TailRiskEngine
            .calculate(

                returns

            )

        )

        return pd.DataFrame(

            {

                "Metric": [

                    "Worst_Day",

                    "Worst_Week",

                    "Skewness",

                    "Kurtosis"

                ],

                "Value": [

                    tail[
                        "Worst_Day"
                    ],

                    tail[
                        "Worst_Week"
                    ],

                    tail[
                        "Skewness"
                    ],

                    tail[
                        "Kurtosis"
                    ]

                ]

            }

        )
    
# ==========================================================
# INSTITUTIONAL RISK DASHBOARD
# ==========================================================

class InstitutionalRiskDashboard:

    @staticmethod
    def build(

        returns: pd.Series

    ) -> pd.DataFrame:

        var95 = (

            ValueAtRiskEngine
            .historical(

                returns,

                0.95

            )

        )

        cvar95 = (

            ConditionalValueAtRiskEngine
            .historical(

                returns,

                0.95

            )

        )

        risk_grade = (

            RiskLimitEngine
            .classify(

                var95,

                cvar95

            )

        )

        tail = (

            TailRiskEngine
            .calculate(

                returns

            )

        )

        return pd.DataFrame(

            {

                "Metric": [

                    "Risk_Grade",

                    "Historical_VaR_95",

                    "Historical_CVaR_95",

                    "Worst_Day",

                    "Worst_Week",

                    "Skewness",

                    "Kurtosis"

                ],

                "Value": [

                    risk_grade,

                    var95,

                    cvar95,

                    tail[
                        "Worst_Day"
                    ],

                    tail[
                        "Worst_Week"
                    ],

                    tail[
                        "Skewness"
                    ],

                    tail[
                        "Kurtosis"
                    ]

                ]

            }

        )
# ==========================================================
# INFORMATION RATIO ENGINE
# ==========================================================

class InformationRatioEngine:

    @staticmethod
    def calculate(

        excess_returns: pd.Series

    ) -> float:

        tracking_error = (

            TrackingErrorEngine

            .calculate(

                excess_returns

            )

        )

        if tracking_error == 0:

            return np.nan

        annual_excess = (

            excess_returns.mean()

            *

            CONFIG
            .TRADING_DAYS

        )

        return (

            annual_excess

            /

            tracking_error

        )


# ==========================================================
# HIT RATIO ENGINE
# ==========================================================

class HitRatioEngine:

    @staticmethod
    def calculate(

        returns: pd.Series

    ) -> float:

        positive_days = (

            returns > 0

        ).sum()

        total_days = len(

            returns

        )

        if total_days == 0:

            return np.nan

        return (

            positive_days

            /

            total_days

        )


# ==========================================================
# ROLLING RISK ANALYTICS ENGINE
# ==========================================================

class RollingAnalyticsEngine:

    @staticmethod
    def build(

        performance_df: pd.DataFrame

    ) -> pd.DataFrame:

        logger.info(

            "Building Rolling Risk Analytics"

        )

        rolling = (

            performance_df

            .copy()

        )

        rolling = (

            rolling

            .sort_values(

                "Date"

            )

            .reset_index(

                drop=True

            )

        )

        rolling[
            "Rolling_Return"
        ] = (

            rolling[
                "Portfolio_Return"
            ]

            .rolling(

                CONFIG
                .ROLLING_WINDOW

            )

            .mean()

            *

            CONFIG
            .TRADING_DAYS

        )

        rolling[
            "Rolling_Volatility"
        ] = (

            rolling[
                "Portfolio_Return"
            ]

            .rolling(

                CONFIG
                .ROLLING_WINDOW

            )

            .std()

            *

            np.sqrt(

                CONFIG
                .TRADING_DAYS

            )

        )

        rolling[
            "Rolling_Tracking_Error"
        ] = (

            rolling[
                "Excess_Return"
            ]

            .rolling(

                CONFIG
                .ROLLING_WINDOW

            )

            .std()

            *

            np.sqrt(

                CONFIG
                .TRADING_DAYS

            )

        )

        rolling[
            "Rolling_Sharpe"
        ] = (

            rolling[
                "Rolling_Return"
            ]

            -

            CONFIG
            .RISK_FREE_RATE

        ) / (

            rolling[
                "Rolling_Volatility"
            ]

        )

        rolling[
            "Rolling_Information_Ratio"
        ] = (

            rolling[
                "Excess_Return"
            ]

            .rolling(

                CONFIG
                .ROLLING_WINDOW

            )

            .mean()

            *

            CONFIG
            .TRADING_DAYS

        ) / (

            rolling[
                "Rolling_Tracking_Error"
            ]

        )

        rolling[
            "Rolling_Beta"
        ] = np.nan

        rolling[
            "Rolling_Alpha"
        ] = np.nan

        window = (

            CONFIG
            .ROLLING_WINDOW

        )

        for idx in range(

            window,

            len(

                rolling

            )

        ):

            sample = (

                rolling

                .iloc[

                    idx - window:

                    idx

                ]

            )

            sample = (

                sample

                .dropna(

                    subset=[

                        "Portfolio_Return",

                        "Benchmark_Return"

                    ]

                )

            )

            if len(

                sample

            ) < (

                window * 0.80

            ):

                continue

            covariance = np.cov(

                sample[
                    "Portfolio_Return"
                ],

                sample[
                    "Benchmark_Return"
                ]

            )

            benchmark_variance = (

                covariance[
                    1,
                    1
                ]

            )

            if benchmark_variance <= 0:

                continue

            beta = (

                covariance[
                    0,
                    1
                ]

                /

                benchmark_variance

            )

            annual_portfolio = (

                sample[
                    "Portfolio_Return"
                ]

                .mean()

                *

                CONFIG
                .TRADING_DAYS

            )

            annual_benchmark = (

                sample[
                    "Benchmark_Return"
                ]

                .mean()

                *

                CONFIG
                .TRADING_DAYS

            )

            alpha = (

                annual_portfolio

                -

                (

                    CONFIG
                    .RISK_FREE_RATE

                    +

                    beta

                    *

                    (

                        annual_benchmark

                        -

                        CONFIG
                        .RISK_FREE_RATE

                    )

                )

            )

            rolling.loc[

                rolling.index[
                    idx
                ],

                "Rolling_Beta"

            ] = beta

            rolling.loc[

                rolling.index[
                    idx
                ],

                "Rolling_Alpha"

            ] = alpha

        rolling[
            "Rolling_Max_Drawdown"
        ] = np.nan

        rolling[
            "Rolling_Current_Drawdown"
        ] = np.nan

        rolling[
            "Rolling_Hit_Ratio"
        ] = np.nan

        rolling[
            "Rolling_Recovery_Score"
        ] = np.nan

        for idx in range(

            window,

            len(

                rolling

            )

        ):

            sample = (

                rolling

                .iloc[

                    idx - window:

                    idx

                ]

                .copy()

            )

            nav_series = (

                (

                    1

                    +

                    sample[
                        "Portfolio_Return"
                    ]

                )

                .cumprod()

            )

            running_max = (

                nav_series

                .cummax()

            )

            drawdown = (

                nav_series

                /

                running_max

                -

                1

            )

            max_drawdown = (

                drawdown.min()

            )

            current_drawdown = (

                drawdown.iloc[-1]

            )

            hit_ratio = (

                (

                    sample[
                        "Portfolio_Return"
                    ]

                    > 0

                )

                .mean()

            )

            recovery_score = (

                100

                *

                (

                    1

                    -

                    abs(

                        current_drawdown

                    )

                )

            )

            recovery_score = max(

                0,

                min(

                    100,

                    recovery_score

                )

            )

            rolling.loc[

                rolling.index[
                    idx
                ],

                "Rolling_Max_Drawdown"

            ] = max_drawdown

            rolling.loc[

                rolling.index[
                    idx
                ],

                "Rolling_Current_Drawdown"

            ] = current_drawdown

            rolling.loc[

                rolling.index[
                    idx
                ],

                "Rolling_Hit_Ratio"

            ] = hit_ratio

            rolling.loc[

                rolling.index[
                    idx
                ],

                "Rolling_Recovery_Score"

            ] = recovery_score

        rolling[
            "Rolling_Risk_Grade"
        ] = "UNKNOWN"

        rolling[
            "Rolling_Performance_Score"
        ] = np.nan

        for idx in range(

            len(

                rolling

            )

        ):

            sharpe = (

                rolling.at[

                    rolling.index[
                        idx
                    ],

                    "Rolling_Sharpe"

                ]

            )

            info_ratio = (

                rolling.at[

                    rolling.index[
                        idx
                    ],

                    "Rolling_Information_Ratio"

                ]

            )

            hit_ratio = (

                rolling.at[

                    rolling.index[
                        idx
                    ],

                    "Rolling_Hit_Ratio"

                ]

            )

            drawdown = abs(

                rolling.at[

                    rolling.index[
                        idx
                    ],

                    "Rolling_Max_Drawdown"

                ]

            )

            if pd.isna(

                sharpe

            ):

                continue

            sharpe_score = (

                max(

                    0,

                    min(

                        100,

                        sharpe * 25

                    )

                )

            )

            ir_score = (

                max(

                    0,

                    min(

                        100,

                        info_ratio * 25

                    )

                )

            )

            hit_score = (

                max(

                    0,

                    min(

                        100,

                        hit_ratio * 100

                    )

                )

            )

            drawdown_score = (

                max(

                    0,

                    min(

                        100,

                        (

                            1

                            -

                            drawdown

                        )

                        * 100

                    )

                )

            )

            performance_score = (

                0.35

                *

                sharpe_score

                +

                0.25

                *

                ir_score

                +

                0.20

                *

                hit_score

                +

                0.20

                *

                drawdown_score

            )

            rolling.at[

                rolling.index[
                    idx
                ],

                "Rolling_Performance_Score"

            ] = round(

                performance_score,

                2

            )

            if performance_score >= 85:

                grade = "INSTITUTIONAL"

            elif performance_score >= 70:

                grade = "STRONG"

            elif performance_score >= 55:

                grade = "ACCEPTABLE"

            elif performance_score >= 40:

                grade = "WEAK"

            else:

                grade = "HIGH_RISK"

            rolling.at[

                rolling.index[
                    idx
                ],

                "Rolling_Risk_Grade"

            ] = grade

        logger.info(

            "Rolling Risk Analytics Complete"

        )

        return rolling

        

# ==========================================================
# PERFORMANCE STATISTICS ENGINE
# ==========================================================

class PerformanceStatisticsEngine:

    @staticmethod
    def calculate(

        performance_df: pd.DataFrame

    ) -> dict:

        returns = (

            performance_df[
                "Portfolio_Return"
            ]

            .dropna()

        )

        benchmark = (

            performance_df[
                "Benchmark_Return"
            ]

            .dropna()

        )

        excess = (

            performance_df[
                "Excess_Return"
            ]

            .dropna()

        )

        annual_return = (

            returns.mean()

            *

            CONFIG
            .TRADING_DAYS

        )

        annual_volatility = (

            VolatilityEngine

            .annualized(

                returns

            )

        )

        drawdown_metrics = (

            DrawdownEngine

            .calculate(

                performance_df[
                    "Portfolio_NAV"
                ]

            )

        )

        alpha, beta = (

            AlphaBetaEngine

            .calculate(

                returns,

                benchmark

            )

        )

        return {

            "Annual_Return":

                annual_return,

            "Annual_Volatility":

                annual_volatility,

            "Sharpe_Ratio":

                SharpeRatioEngine

                .calculate(

                    returns

                ),

            "Sortino_Ratio":

                SortinoRatioEngine

                .calculate(

                    returns

                ),

            "Calmar_Ratio":

                CalmarRatioEngine

                .calculate(

                    annual_return,

                    drawdown_metrics[
                        "Max_Drawdown"
                    ]

                ),

            "Alpha":

                alpha,

            "Beta":

                beta,

            "Tracking_Error":

                TrackingErrorEngine

                .calculate(

                    excess

                ),

            "Information_Ratio":

                InformationRatioEngine

                .calculate(

                    excess

                ),

            "Hit_Ratio":

                HitRatioEngine

                .calculate(

                    returns

                ),

            "Max_Drawdown":

                drawdown_metrics[
                    "Max_Drawdown"
                ],

            "Current_Drawdown":

                drawdown_metrics[
                    "Current_Drawdown"
                ]

        }

# ==========================================================
# ATTRIBUTION REPOSITORY
# ==========================================================

class AttributionRepository:

    @staticmethod
    def load_security():

        if not SECURITY_ATTRIBUTION_FILE.exists():

            return pd.DataFrame()

        return pd.read_csv(

            SECURITY_ATTRIBUTION_FILE

        )

    @staticmethod
    def load_sector():

        if not SECTOR_ATTRIBUTION_FILE.exists():

            return pd.DataFrame()

        return pd.read_csv(

            SECTOR_ATTRIBUTION_FILE

        )

    @staticmethod
    def load_factor():

        if not FACTOR_ATTRIBUTION_FILE.exists():

            return pd.DataFrame()

        return pd.read_csv(

            FACTOR_ATTRIBUTION_FILE

        )


# ==========================================================
# PERFORMANCE DASHBOARD ENGINE
# ==========================================================

class PerformanceDashboardEngine:

    @staticmethod
    def build(

        statistics: dict

    ) -> pd.DataFrame:

        dashboard = pd.DataFrame(

            {

                "Metric":

                    list(

                        statistics.keys()

                    ),

                "Value":

                    list(

                        statistics.values()

                    )

            }

        )

        return dashboard


# ==========================================================
# PERFORMANCE AUDIT ENGINE
# ==========================================================

class PerformanceAuditEngine:

    @staticmethod
    def build(

        portfolio: pd.DataFrame,

        performance_df: pd.DataFrame,

        statistics: dict

    ) -> pd.DataFrame:

        audit = pd.DataFrame(

            {

                "Timestamp":

                    [

                        pd.Timestamp.now()

                    ],

                "Holdings":

                    [

                        len(

                            portfolio

                        )

                    ],

                "Observations":

                    [

                        len(

                            performance_df

                        )

                    ],

                "Annual_Return":

                    [

                        statistics[
                            "Annual_Return"
                        ]

                    ],

                "Annual_Volatility":

                    [

                        statistics[
                            "Annual_Volatility"
                        ]

                    ],

                "Sharpe_Ratio":

                    [

                        statistics[
                            "Sharpe_Ratio"
                        ]

                    ],

                "Max_Drawdown":

                    [

                        statistics[
                            "Max_Drawdown"
                        ]

                    ]

            }

        )

        return audit

# ==========================================================
# REGIME CLASSIFIER
# ==========================================================

class RegimeClassifier:

    BULL = "BULL"

    BEAR = "BEAR"

    SIDEWAYS = "SIDEWAYS"

    @staticmethod
    def classify(

        benchmark_returns: pd.Series

    ) -> pd.Series:

        rolling_return = (

            benchmark_returns

            .rolling(

                126

            )

            .sum()

        )

        regime = pd.Series(

            RegimeClassifier
            .SIDEWAYS,

            index=benchmark_returns.index

        )

        regime.loc[

            rolling_return > 0.10

        ] = (

            RegimeClassifier
            .BULL

        )

        regime.loc[

            rolling_return < -0.10

        ] = (

            RegimeClassifier
            .BEAR

        )

        return regime
    
# ==========================================================
# REGIME RETURN BUILDER
# ==========================================================

class RegimeReturnBuilder:

    @staticmethod
    def build(

        performance_df: pd.DataFrame

    ) -> pd.DataFrame:

        logger.info(

            "Building Regime Returns"

        )

        df = (

            performance_df

            .copy()

        )

        df[
            "Market_Regime"
        ] = (

            RegimeClassifier

            .classify(

                df[
                    "Benchmark_Return"
                ]

            )

        )

        df[
            "Excess_Return"
        ] = (

            df[
                "Portfolio_Return"
            ]

            -

            df[
                "Benchmark_Return"
            ]

        )

        logger.info(

            f"Regime Days: "

            f"{len(df):,}"

        )

        return df

# ==========================================================
# REGIME STATISTICS ENGINE
# ==========================================================

class RegimeStatisticsEngine:

    @staticmethod
    def build(

        regime_df: pd.DataFrame

    ) -> pd.DataFrame:

        logger.info(

            "Building Regime Statistics"

        )

        results = []

        for regime in [

            RegimeClassifier.BULL,

            RegimeClassifier.BEAR,

            RegimeClassifier.SIDEWAYS

        ]:

            sample = (

                regime_df

                .loc[

                    regime_df[
                        "Market_Regime"
                    ]

                    ==

                    regime

                ]

                .copy()

            )

            if sample.empty:

                continue

            annual_return = (

                sample[
                    "Portfolio_Return"
                ]

                .mean()

                *

                CONFIG
                .TRADING_DAYS

            )

            annual_volatility = (

                sample[
                    "Portfolio_Return"
                ]

                .std()

                *

                np.sqrt(

                    CONFIG
                    .TRADING_DAYS

                )

            )

            sharpe = (

                annual_return

                -

                CONFIG
                .RISK_FREE_RATE

            ) / max(

                annual_volatility,

                1e-9

            )

            hit_ratio = (

                (

                    sample[
                        "Portfolio_Return"
                    ] > 0

                )

                .mean()

            )

            benchmark_return = (

                sample[
                    "Benchmark_Return"
                ]

                .mean()

                *

                CONFIG
                .TRADING_DAYS

            )

            benchmark_volatility = (

                sample[
                    "Benchmark_Return"
                ]

                .std()

                *

                np.sqrt(

                    CONFIG
                    .TRADING_DAYS

                )

            )

            excess_return = (

                annual_return

                -

                benchmark_return

            )

            tracking_error = (

                sample[
                    "Excess_Return"
                ]

                .std()

                *

                np.sqrt(

                    CONFIG
                    .TRADING_DAYS

                )

            )

            information_ratio = (

                excess_return

                /

                max(

                    tracking_error,

                    1e-9

                )

            )

            covariance = np.cov(

                sample[
                    "Portfolio_Return"
                ],

                sample[
                    "Benchmark_Return"
                ]

            )

            benchmark_variance = (

                covariance[
                    1,
                    1
                ]

            )

            if benchmark_variance > 0:

                beta = (

                    covariance[
                        0,
                        1
                    ]

                    /

                    benchmark_variance

                )

            else:

                beta = np.nan

            alpha = (

                annual_return

                -

                (

                    CONFIG
                    .RISK_FREE_RATE

                    +

                    beta

                    *

                    (

                        benchmark_return

                        -

                        CONFIG
                        .RISK_FREE_RATE

                    )

                )

            )

            nav = (

                (

                    1

                    +

                    sample[
                        "Portfolio_Return"
                    ]

                )

                .cumprod()

            )

            running_max = (

                nav

                .cummax()

            )

            drawdown = (

                nav

                /

                running_max

                -

                1

            )

            max_drawdown = (

                drawdown.min()

            )

            current_drawdown = (

                drawdown.iloc[-1]

                if len(

                    drawdown

                ) > 0

                else np.nan

            )

            results.append(

                {

                    "Regime":
                        regime,

                    "Days":
                        len(sample),

                    "Annual_Return":
                        annual_return,

                    "Annual_Volatility":
                        annual_volatility,

                    "Sharpe":
                        sharpe,

                    "Hit_Ratio":
                        hit_ratio,

                    "Benchmark_Return":
                        benchmark_return,

                    "Benchmark_Volatility":
                        benchmark_volatility,

                    "Excess_Return":
                        excess_return,

                    "Tracking_Error":
                        tracking_error,

                    "Information_Ratio":
                        information_ratio,

                    "Alpha":
                        alpha,

                    "Beta":
                        beta,

                    "Max_Drawdown":
                        max_drawdown,

                    "Current_Drawdown":
                        current_drawdown
                }

            )

        return pd.DataFrame(

            results

        )

# ==========================================================
# REGIME TRANSITION ENGINE
# ==========================================================

class RegimeTransitionEngine:

    @staticmethod
    def build(

        regime_df: pd.DataFrame

    ) -> pd.DataFrame:

        logger.info(

            "Building Regime Transition Matrix"

        )

        df = (

            regime_df

            .copy()

        )

        df[
            "Next_Regime"
        ] = (

            df[
                "Market_Regime"
            ]

            .shift(

                -1

            )

        )

        transitions = (

            df

            .dropna(

                subset=[

                    "Next_Regime"

                ]

            )

        )

        matrix = pd.crosstab(

            transitions[
                "Market_Regime"
            ],

            transitions[
                "Next_Regime"
            ]

        )

        probability_matrix = (

            matrix

            .div(

                matrix.sum(

                    axis=1

                ),

                axis=0

            )

        )

        probability_matrix = (

            probability_matrix

            .round(

                4

            )

        )

        return probability_matrix

# ==========================================================
# REGIME PERSISTENCE ENGINE
# ==========================================================

class RegimePersistenceEngine:

    @staticmethod
    def build(

        transition_matrix: pd.DataFrame

    ) -> pd.DataFrame:

        results = []

        for regime in [

            RegimeClassifier.BULL,

            RegimeClassifier.BEAR,

            RegimeClassifier.SIDEWAYS

        ]:

            persistence = 0.0

            if (

                regime

                in transition_matrix.index

                and

                regime

                in transition_matrix.columns

            ):

                persistence = (

                    transition_matrix.loc[

                        regime,

                        regime

                    ]

                )

            results.append(

                {

                    "Regime":

                        regime,

                    "Persistence":

                        persistence

                }

            )

        return pd.DataFrame(

            results

        )
    
# ==========================================================
# REGIME SCORECARD ENGINE
# ==========================================================

class RegimeScorecardEngine:

    @staticmethod
    def build(

        regime_stats: pd.DataFrame

    ) -> pd.DataFrame:

        scorecard = (

            regime_stats

            .copy()

        )

        scorecard[
            "Regime_Score"
        ] = (

            (

                scorecard[
                    "Sharpe"
                ]

                .clip(

                    lower=0

                )

                * 25

            )

            +

            (

                scorecard[
                    "Hit_Ratio"
                ]

                * 25

            )

            +

            (

                scorecard[
                    "Information_Ratio"
                ]

                .clip(

                    lower=0

                )

                * 25

            )

            +

            (

                (

                    1

                    -

                    scorecard[
                        "Max_Drawdown"
                    ]

                    .abs()

                )

                * 25

            )

        )

        scorecard[
            "Regime_Score"
        ] = (

            scorecard[
                "Regime_Score"
            ]

            .clip(

                upper=100

            )

        )

        return scorecard
# ==========================================================
# EXPORT ENGINE
# ==========================================================

class ExportEngine:

    @staticmethod
    def save(

        performance_df: pd.DataFrame,

        rolling_df: pd.DataFrame,

        statistics: dict,

        audit_df: pd.DataFrame,

        var_report: pd.DataFrame,

        cvar_report: pd.DataFrame,

        tail_risk_report: pd.DataFrame,

        risk_dashboard: pd.DataFrame,

        regime_stats: pd.DataFrame,

        transition_matrix: pd.DataFrame,

        persistence_df: pd.DataFrame,

        regime_scorecard: pd.DataFrame

    ):

        logger.info(

            "Exporting Reports"

        )

        performance_df[
            [

                "Date",

                "Portfolio_NAV",

                "Cumulative_Return"

            ]

        ].to_csv(

            PORTFOLIO_NAV_FILE,

            index=False

        )

        performance_df[
            [

                "Date",

                "Portfolio_Return"

            ]

        ].to_csv(

            PORTFOLIO_RETURNS_FILE,

            index=False

        )

        performance_df[
            [

                "Date",

                "Benchmark_Return"

            ]

        ].to_csv(

            BENCHMARK_RETURNS_FILE,

            index=False

        )

        rolling_df.to_csv(

            ROLLING_PERFORMANCE_FILE,

            index=False

        )

        pd.DataFrame(

            [

                statistics

            ]

        ).to_csv(

            PERFORMANCE_SUMMARY_FILE,

            index=False

        )

        PerformanceDashboardEngine \
            .build(

                statistics

            ) \
            .to_csv(

                PERFORMANCE_DASHBOARD_FILE,

                index=False

            )

        audit_df.to_csv(

            PERFORMANCE_AUDIT_FILE,

            index=False

        )

        var_report.to_csv(

            OUTPUT_DIR

            / "var_report.csv",

            index=False

        )

        cvar_report.to_csv(

            OUTPUT_DIR

            / "cvar_report.csv",

            index=False

        )

        tail_risk_report.to_csv(

            OUTPUT_DIR

            / "tail_risk_report.csv",

            index=False

        )

        risk_dashboard.to_csv(

            OUTPUT_DIR

            / "risk_dashboard.csv",

            index=False

        )

        regime_stats.to_csv(

            REGIME_STATISTICS_FILE,

            index=False

        )

        transition_matrix.to_csv(

            REGIME_TRANSITION_FILE

        )

        persistence_df.to_csv(

            REGIME_PERSISTENCE_FILE,

            index=False

        )

        regime_scorecard.to_csv(

            REGIME_SCORECARD_FILE,

            index=False

        )

        logger.info(

            "Performance Reports Exported"

        )

        logger.info(

            "VaR Reports Exported"

        )

        logger.info(

            "CVaR Reports Exported"

        )

        logger.info(

            "Tail Risk Reports Exported"

        )

        logger.info(

            "Institutional Risk Dashboard Exported"

        )
        logger.info(

            "Regime Statistics Exported"

        )

        logger.info(

            "Regime Transition Matrix Exported"

        )

        logger.info(

            "Regime Persistence Exported"

        )

        logger.info(

            "Regime Scorecard Exported"

        )

# ==========================================================
# PERFORMANCE HEALTH ENGINE
# ==========================================================

class PerformanceHealthEngine:

    @staticmethod
    def evaluate(

        statistics: dict

    ) -> str:

        sharpe = (

            statistics[
                "Sharpe_Ratio"
            ]

        )

        drawdown = abs(

            statistics[
                "Max_Drawdown"
            ]

        )

        if (

            sharpe >= 2.0

            and

            drawdown < 0.15

        ):

            return "EXCELLENT"

        if (

            sharpe >= 1.25

            and

            drawdown < 0.25

        ):

            return "GOOD"

        if (

            sharpe >= 0.75

        ):

            return "ACCEPTABLE"

        return "WEAK"


# ==========================================================
# PORTFOLIO RETURN ENGINE
# ==========================================================

class PortfolioReturnEngine:

    def run(

        self

    ):

        logger.info(

            "Starting Portfolio Return Engine"

        )

        (
            portfolio,

            performance_df

        ) = (

            ReturnRepository

            .build()

        )

        regime_df = (

            RegimeReturnBuilder

            .build(

                performance_df

            )

        )

        regime_stats = (

            RegimeStatisticsEngine

            .build(

                regime_df

            )

        )

        transition_matrix = (

            RegimeTransitionEngine

            .build(

                regime_df

            )

        )

        persistence_df = (

            RegimePersistenceEngine

            .build(

                transition_matrix

            )

        )

        statistics = (

            PerformanceStatisticsEngine

            .calculate(

                performance_df

            )

        )

        statistics[

            "Historical_VaR_95"

        ] = (

            ValueAtRiskEngine

            .historical(

                performance_df[
                    "Portfolio_Return"
                ],

                0.95

            )

        )

        statistics[

            "Historical_VaR_99"

        ] = (

            ValueAtRiskEngine

            .historical(

                performance_df[
                    "Portfolio_Return"
                ],

                0.99

            )

        )

        statistics[

            "Historical_CVaR_95"

        ] = (

            ConditionalValueAtRiskEngine

            .historical(

                performance_df[
                    "Portfolio_Return"
                ],

                0.95

            )

        )

        statistics[

            "Historical_CVaR_99"

        ] = (

            ConditionalValueAtRiskEngine

            .historical(

                performance_df[
                    "Portfolio_Return"
                ],

                0.99

            )

        )
        
        regime_scorecard = (

            RegimeScorecardEngine

            .build(

                regime_stats

            )

        )

        statistics[

            "Regime_Count"

        ] = (

            len(

                regime_stats

            )

        )

        statistics[

            "Best_Regime"

        ] = (

            regime_scorecard

            .sort_values(

                "Regime_Score",

                ascending=False

            )

            .iloc[0][

                "Regime"

            ]

            if len(

                regime_scorecard

            ) > 0

            else np.nan

        )

        tail_risk = (

            TailRiskEngine

            .calculate(

                performance_df[
                    "Portfolio_Return"
                ]

            )

        )

        statistics[

            "Worst_Day"

        ] = (

            tail_risk[
                "Worst_Day"
            ]

        )

        statistics[

            "Worst_Week"

        ] = (

            tail_risk[
                "Worst_Week"
            ]

        )

        statistics[

            "Skewness"

        ] = (

            tail_risk[
                "Skewness"
            ]

        )

        statistics[

            "Kurtosis"

        ] = (

            tail_risk[
                "Kurtosis"
            ]

        )

        statistics[

            "Risk_Grade"

        ] = (

            RiskLimitEngine

            .classify(

                statistics[
                    "Historical_VaR_95"
                ],

                statistics[
                    "Historical_CVaR_95"
                ]

            )

        )

        var_report = (

            VaRSummaryEngine

            .build(

                performance_df[
                    "Portfolio_Return"
                ]

            )

        )

        cvar_report = (

            CVaRSummaryEngine

            .build(

                performance_df[
                    "Portfolio_Return"
                ]

            )

        )

        tail_risk_report = (

            TailRiskDashboardEngine

            .build(

                performance_df[
                    "Portfolio_Return"
                ]

            )

        )

        risk_dashboard = (

            InstitutionalRiskDashboard

            .build(

                performance_df[
                    "Portfolio_Return"
                ]

            )

        )        

        statistics[
            "Performance_Health"
        ] = (

            PerformanceHealthEngine

            .evaluate(

                statistics

            )

        )

        security_attr = (

            AttributionRepository

            .load_security()

        )

        sector_attr = (

            AttributionRepository

            .load_sector()

        )

        factor_attr = (

            AttributionRepository

            .load_factor()

        )

        statistics[
            "Security_Attribution_Rows"
        ] = (

            len(

                security_attr

            )

        )

        statistics[
            "Sector_Attribution_Rows"
        ] = (

            len(

                sector_attr

            )

        )

        statistics[
            "Factor_Attribution_Rows"
        ] = (

            len(

                factor_attr

            )

        )

        rolling_df = (

            RollingAnalyticsEngine

            .build(

                performance_df

            )

        )

        audit_df = (

            PerformanceAuditEngine

            .build(

                portfolio,

                performance_df,

                statistics

            )

        )

        ExportEngine.save(

            performance_df,

            rolling_df,

            statistics,

            audit_df,

            var_report,

            cvar_report,

            tail_risk_report,

            risk_dashboard,

            regime_stats,

            transition_matrix,

            persistence_df,

            regime_scorecard

        )

        logger.info(

            "Portfolio Return Engine Complete"

        )

        return {

            "Statistics":

                statistics,

            "Performance":

                performance_df,

            "Rolling":

                rolling_df

        }


# ==========================================================
# CLI RUNNER
# ==========================================================

def run_example():

    engine = (

        PortfolioReturnEngine()

    )

    results = (

        engine.run()

    )

    summary = (

        results[
            "Statistics"
        ]

    )

    print()

    print(

        "=" * 80

    )

    print(

        "INSTITUTIONAL PERFORMANCE & RISK SUMMARY"

    )

    print(

        "=" * 80

    )

    for key, value in (

        summary.items()

    ):

        print(

            f"{key}: "

            f"{value}"

        )

    print(

        "=" * 80

    )


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    run_example()