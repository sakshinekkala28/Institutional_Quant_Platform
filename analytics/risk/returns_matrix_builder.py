"""
=========================================================
RETURNS MATRIX BUILDER
=========================================================

Purpose:
Institutional Return Matrix Construction Engine

Features:
- Daily Return Matrix
- Log Return Matrix
- Monthly Returns
- Return Statistics
- Winsorization
- Coverage Analytics
- Data Quality Controls

Inputs:
data/raw/benchmark_prices.csv

Outputs:
data/risk/returns_matrix.csv
data/risk/log_returns_matrix.csv
data/risk/security_return_statistics.csv
data/risk/returns_coverage_report.csv
data/risk/returns_dashboard.csv

=========================================================
"""

from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd

# =========================================================
# CONFIGURATION
# =========================================================

ENGINE_VERSION = "1.0.0"

MIN_HISTORY_DAYS = 126

MAX_MISSING_PCT = 0.20

WINSORIZE_LOWER = 0.01
WINSORIZE_UPPER = 0.99

TRADING_DAYS = 252

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

PRICE_FILE = (
    ROOT
    / "data"
    / "raw"
    / "benchmark_prices.csv"
)

OUTPUT_DIR = (
    ROOT
    / "data"
    / "risk"
)

REPORT_FILE = (
    ROOT
    / "data"
    / "logs"
    / "returns_matrix_report.csv"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# =========================================================
# LOAD DATA
# =========================================================

print(
    "\n📥 Loading Price History..."
)

if not PRICE_FILE.exists():

    raise FileNotFoundError(
        f"Missing file: {PRICE_FILE}"
    )

prices = pd.read_csv(
    PRICE_FILE
)

# =========================================================
# SCHEMA VALIDATION
# =========================================================

required_columns = [

    "Date",

    "Symbol",

    "Close"
]

missing_columns = [

    c

    for c in required_columns

    if c not in prices.columns
]

if missing_columns:

    raise ValueError(

        "Missing columns: "

        + ", ".join(
            missing_columns
        )
    )

# =========================================================
# DATE PROCESSING
# =========================================================

prices["Date"] = pd.to_datetime(
    prices["Date"],
    errors="coerce"
)

prices = prices.dropna(
    subset=["Date"]
)

# =========================================================
# PRICE CLEANING
# =========================================================

prices["Close"] = pd.to_numeric(
    prices["Close"],
    errors="coerce"
)

prices = prices.dropna(
    subset=["Close"]
)

prices = prices[
    prices["Close"] > 0
]

# =========================================================
# DUPLICATE CHECK
# =========================================================

duplicate_count = (

    prices

    .duplicated(
        subset=[
            "Date",
            "Symbol"
        ]
    )

    .sum()
)

if duplicate_count > 0:

    print(
        f"⚠ Removing "
        f"{duplicate_count:,} duplicates"
    )

    prices = (

        prices

        .sort_values(
            "Date"
        )

        .drop_duplicates(

            subset=[
                "Date",
                "Symbol"
            ],

            keep="last"
        )
    )

# =========================================================
# SORTING
# =========================================================

prices = (

    prices

    .sort_values(

        [
            "Symbol",
            "Date"
        ]
    )

    .reset_index(
        drop=True
    )
)

# =========================================================
# COVERAGE ANALYSIS
# =========================================================

coverage = (

    prices

    .groupby(
        "Symbol"
    )

    .agg({

        "Date": [

            "min",

            "max",

            "count"
        ]
    })
)

coverage.columns = [

    "Start_Date",

    "End_Date",

    "Observations"
]

coverage = (
    coverage
    .reset_index()
)

coverage[
    "Coverage_Years"
] = (

    coverage[
        "Observations"
    ]

    / TRADING_DAYS
)

# =========================================================
# ELIGIBILITY FILTER
# =========================================================

eligible_symbols = set(

    coverage.loc[

        coverage[
            "Observations"
        ]

        >=

        MIN_HISTORY_DAYS,

        "Symbol"
    ]
)

prices = prices[

    prices[
        "Symbol"
    ]

    .isin(
        eligible_symbols
    )
]

# =========================================================
# UNIVERSE SUMMARY
# =========================================================

print(
    f"Total Securities : "
    f"{coverage['Symbol'].nunique():,}"
)

print(
    f"Eligible Symbols : "
    f"{len(eligible_symbols):,}"
)

print(
    f"Price Records    : "
    f"{len(prices):,}"
)

# =========================================================
# QUALITY REPORT
# =========================================================

coverage_report = coverage.copy()

coverage_report[
    "Eligible"
] = (

    coverage_report[
        "Symbol"
    ]

    .isin(
        eligible_symbols
    )
)

print(
    "\n✓ Data Validation Complete"
)

# =========================================================
# PART 2 STARTS HERE
# =========================================================
#
# Next:
#
# Daily Returns
# Log Returns
# Monthly Returns
# Return Matrix Construction
#
# =========================================================

# =========================================================
# DAILY RETURN CALCULATION
# =========================================================

print(
    "\n📈 Building Daily Returns..."
)

prices["Daily_Return"] = (

    prices

    .groupby(
        "Symbol"
    )["Close"]

    .pct_change()
)

prices["Log_Return"] = (

    prices

    .groupby(
        "Symbol"
    )["Close"]

    .transform(
        lambda x:
        np.log(
            x / x.shift(1)
        )
    )
)

# =========================================================
# REMOVE FIRST OBSERVATION
# =========================================================

returns_df = prices.dropna(
    subset=[
        "Daily_Return",
        "Log_Return"
    ]
).copy()

# =========================================================
# OUTLIER CONTROL
# =========================================================

print(
    "🛡 Applying Return Outlier Controls..."
)

lower_bound = (

    returns_df[
        "Daily_Return"
    ]

    .quantile(
        WINSORIZE_LOWER
    )
)

upper_bound = (

    returns_df[
        "Daily_Return"
    ]

    .quantile(
        WINSORIZE_UPPER
    )
)

returns_df[
    "Daily_Return"
] = (

    returns_df[
        "Daily_Return"
    ]

    .clip(
        lower=lower_bound,
        upper=upper_bound
    )
)

# =========================================================
# REBUILD LOG RETURNS AFTER CLIPPING
# =========================================================

returns_df[
    "Log_Return"
] = np.log(
    1 +
    returns_df[
        "Daily_Return"
    ]
)

# =========================================================
# DAILY RETURN MATRIX
# =========================================================

print(
    "🏗 Building Return Matrix..."
)

returns_matrix = (

    returns_df

    .pivot(
        index="Date",
        columns="Symbol",
        values="Daily_Return"
    )

    .sort_index()
)

# =========================================================
# LOG RETURN MATRIX
# =========================================================

log_returns_matrix = (

    returns_df

    .pivot(
        index="Date",
        columns="Symbol",
        values="Log_Return"
    )

    .sort_index()
)

# =========================================================
# MISSING DATA ANALYSIS
# =========================================================

missing_pct = (

    returns_matrix

    .isna()

    .mean()
)

valid_symbols = set(

    missing_pct[
        missing_pct
        <=
        MAX_MISSING_PCT
    ].index
)

returns_matrix = (

    returns_matrix[
        sorted(
            valid_symbols
        )
    ]
)

log_returns_matrix = (

    log_returns_matrix[
        sorted(
            valid_symbols
        )
    ]
)

# =========================================================
# FORWARD FILL SMALL GAPS
# =========================================================

returns_matrix = (

    returns_matrix

    .ffill(
        limit=3
    )
)

log_returns_matrix = (

    log_returns_matrix

    .ffill(
        limit=3
    )
)

# =========================================================
# DROP ROWS WITH EXCESSIVE MISSING DATA
# =========================================================

returns_matrix = (

    returns_matrix

    .dropna(
        how="all"
    )
)

log_returns_matrix = (

    log_returns_matrix

    .dropna(
        how="all"
    )
)

# =========================================================
# MONTHLY RETURNS
# =========================================================

print(
    "📅 Building Monthly Returns..."
)

monthly_returns = (

    returns_matrix

    .resample(
        "M"
    )

    .apply(
        lambda x:
        (1 + x).prod() - 1
    )
)

# =========================================================
# SECURITY RETURN STATISTICS
# =========================================================

print(
    "📊 Building Security Statistics..."
)

security_stats = pd.DataFrame({

    "Symbol":
    returns_matrix.columns

})

security_stats[
    "Mean_Daily_Return"
] = (

    returns_matrix.mean()
    .values
)

security_stats[
    "Annualized_Return"
] = (

    returns_matrix.mean()
    * TRADING_DAYS
).values

security_stats[
    "Daily_Volatility"
] = (

    returns_matrix.std()
).values

security_stats[
    "Annualized_Volatility"
] = (

    returns_matrix.std()
    * np.sqrt(
        TRADING_DAYS
    )
).values

security_stats[
    "Sharpe_Ratio"
] = (

    security_stats[
        "Annualized_Return"
    ]

    /

    security_stats[
        "Annualized_Volatility"
    ]

    .replace(
        0,
        np.nan
    )
)

# =========================================================
# CUMULATIVE RETURNS
# =========================================================

cumulative_returns = (

    (1 + returns_matrix)

    .cumprod()
)

# =========================================================
# MAX DRAWDOWN
# =========================================================

max_drawdowns = []

for symbol in returns_matrix.columns:

    equity_curve = (
        cumulative_returns[
            symbol
        ]
    )

    rolling_peak = (
        equity_curve
        .cummax()
    )

    drawdown = (

        equity_curve

        /

        rolling_peak

        - 1
    )

    max_drawdowns.append(
        drawdown.min()
    )

security_stats[
    "Max_Drawdown"
] = max_drawdowns

# =========================================================
# RETURN COVERAGE METRICS
# =========================================================

security_stats[
    "Observations"
] = (

    returns_matrix
    .count()
    .values
)

security_stats[
    "Missing_Pct"
] = (

    returns_matrix
    .isna()
    .mean()
    .values
)

# =========================================================
# QUALITY FILTER FLAG
# =========================================================

security_stats[
    "Pass_Quality_Check"
] = (

    security_stats[
        "Missing_Pct"
    ]

    <=

    MAX_MISSING_PCT
)

# =========================================================
# SUMMARY
# =========================================================

print(
    f"Return Matrix Shape : "
    f"{returns_matrix.shape}"
)

print(
    f"Monthly Matrix Shape: "
    f"{monthly_returns.shape}"
)

print(
    f"Valid Securities    : "
    f"{len(valid_symbols):,}"
)

print(
    f"Average Volatility  : "
    f"{security_stats['Annualized_Volatility'].mean():.2%}"
)

# =========================================================
# PART 3 STARTS HERE
# =========================================================
#
# Next:
#
# Coverage Analytics
# Data Quality Dashboard
# Return Diagnostics
# Cross-Sectional Statistics
# Risk Readiness Checks
#
# =========================================================

# =========================================================
# COVERAGE ANALYTICS
# =========================================================

print(
    "\n🔍 Building Coverage Analytics..."
)

coverage_metrics = pd.DataFrame({

    "Symbol":
    returns_matrix.columns

})

coverage_metrics[
    "Observations"
] = (
    returns_matrix
    .count()
    .values
)

coverage_metrics[
    "Missing_Observations"
] = (
    returns_matrix
    .isna()
    .sum()
    .values
)

coverage_metrics[
    "Coverage_Ratio"
] = (

    coverage_metrics[
        "Observations"
    ]

    /

    len(
        returns_matrix
    )
)

coverage_metrics[
    "Missing_Pct"
] = (

    coverage_metrics[
        "Missing_Observations"
    ]

    /

    len(
        returns_matrix
    )
)

coverage_metrics[
    "Coverage_Status"
] = np.where(

    coverage_metrics[
        "Missing_Pct"
    ]

    <=
    MAX_MISSING_PCT,

    "PASS",

    "FAIL"
)

# =========================================================
# RETURN DISTRIBUTION ANALYSIS
# =========================================================

print(
    "📊 Building Return Diagnostics..."
)

distribution_stats = pd.DataFrame({

    "Symbol":
    returns_matrix.columns

})

distribution_stats[
    "Mean"
] = (
    returns_matrix.mean().values
)

distribution_stats[
    "Median"
] = (
    returns_matrix.median().values
)

distribution_stats[
    "Std_Dev"
] = (
    returns_matrix.std().values
)

distribution_stats[
    "Skewness"
] = (
    returns_matrix.skew().values
)

distribution_stats[
    "Kurtosis"
] = (
    returns_matrix.kurt().values
)

distribution_stats[
    "Min_Return"
] = (
    returns_matrix.min().values
)

distribution_stats[
    "Max_Return"
] = (
    returns_matrix.max().values
)

distribution_stats[
    "Positive_Days"
] = (
    (returns_matrix > 0)
    .sum()
    .values
)

distribution_stats[
    "Negative_Days"
] = (
    (returns_matrix < 0)
    .sum()
    .values
)

distribution_stats[
    "Hit_Ratio"
] = (

    distribution_stats[
        "Positive_Days"
    ]

    /

    (

        distribution_stats[
            "Positive_Days"
        ]

        +

        distribution_stats[
            "Negative_Days"
        ]

    )
)

# =========================================================
# CROSS SECTIONAL ANALYTICS
# =========================================================

print(
    "🌐 Building Cross Sectional Analytics..."
)

cross_sectional_stats = pd.DataFrame({

    "Date":
    returns_matrix.index

})

cross_sectional_stats[
    "Mean_Return"
] = (
    returns_matrix.mean(axis=1).values
)

cross_sectional_stats[
    "Median_Return"
] = (
    returns_matrix.median(axis=1).values
)

cross_sectional_stats[
    "Cross_Sectional_Vol"
] = (
    returns_matrix.std(axis=1).values
)

cross_sectional_stats[
    "Positive_Securities"
] = (
    (returns_matrix > 0)
    .sum(axis=1)
    .values
)

cross_sectional_stats[
    "Negative_Securities"
] = (
    (returns_matrix < 0)
    .sum(axis=1)
    .values
)

cross_sectional_stats[
    "Breadth"
] = (

    cross_sectional_stats[
        "Positive_Securities"
    ]

    /

    (

        cross_sectional_stats[
            "Positive_Securities"
        ]

        +

        cross_sectional_stats[
            "Negative_Securities"
        ]

    )
)

# =========================================================
# COVARIANCE READINESS
# =========================================================

print(
    "⚠ Validating Covariance Readiness..."
)

covariance_ready = []

for symbol in returns_matrix.columns:

    series = (
        returns_matrix[
            symbol
        ]
    )

    valid_obs = (
        series
        .dropna()
        .shape[0]
    )

    covariance_ready.append(

        valid_obs

        >=

        MIN_HISTORY_DAYS

    )

covariance_check = pd.DataFrame({

    "Symbol":
    returns_matrix.columns,

    "Covariance_Ready":
    covariance_ready

})

# =========================================================
# FACTOR MODEL READINESS
# =========================================================

factor_readiness = pd.DataFrame({

    "Metric": [

        "Total_Securities",

        "Covariance_Ready",

        "Coverage_Pass",

        "Average_Observations",

        "Average_Missing_Pct"
    ],

    "Value": [

        len(
            returns_matrix.columns
        ),

        covariance_check[
            "Covariance_Ready"
        ].sum(),

        coverage_metrics[
            "Coverage_Status"
        ]
        .eq("PASS")
        .sum(),

        coverage_metrics[
            "Observations"
        ]
        .mean(),

        coverage_metrics[
            "Missing_Pct"
        ]
        .mean()
    ]
})

# =========================================================
# MARKET LEVEL STATISTICS
# =========================================================

print(
    "🏛 Building Market Statistics..."
)

market_return_series = (
    returns_matrix.mean(axis=1)
)

market_statistics = pd.DataFrame({

    "Metric": [

        "Annualized_Return",

        "Annualized_Volatility",

        "Sharpe_Ratio",

        "Best_Day",

        "Worst_Day",

        "Average_Daily_Return"
    ],

    "Value": [

        market_return_series.mean()
        * TRADING_DAYS,

        market_return_series.std()
        * np.sqrt(TRADING_DAYS),

        (

            market_return_series.mean()
            * TRADING_DAYS

        )

        /

        (

            market_return_series.std()
            * np.sqrt(TRADING_DAYS)

        ),

        market_return_series.max(),

        market_return_series.min(),

        market_return_series.mean()

    ]
})

# =========================================================
# DATA QUALITY SCORE
# =========================================================

coverage_score = (

    coverage_metrics[
        "Coverage_Ratio"
    ]

    .mean()

    * 100
)

covariance_score = (

    covariance_check[
        "Covariance_Ready"
    ]

    .mean()

    * 100
)

quality_score = np.mean([

    coverage_score,

    covariance_score

])

# =========================================================
# RETURNS DASHBOARD
# =========================================================

returns_dashboard = pd.DataFrame({

    "Metric": [

        "Universe_Size",

        "Eligible_Securities",

        "Coverage_Score",

        "Covariance_Score",

        "Data_Quality_Score",

        "Avg_Annual_Return",

        "Avg_Annual_Volatility",

        "Avg_Sharpe"
    ],

    "Value": [

        coverage["Symbol"].nunique(),

        len(
            returns_matrix.columns
        ),

        coverage_score,

        covariance_score,

        quality_score,

        security_stats[
            "Annualized_Return"
        ].mean(),

        security_stats[
            "Annualized_Volatility"
        ].mean(),

        security_stats[
            "Sharpe_Ratio"
        ].mean()
    ]
})

# =========================================================
# SUMMARY
# =========================================================

print(
    f"Coverage Score    : "
    f"{coverage_score:.2f}"
)

print(
    f"Covariance Score  : "
    f"{covariance_score:.2f}"
)

print(
    f"Quality Score     : "
    f"{quality_score:.2f}"
)

print(
    f"Avg Sharpe Ratio  : "
    f"{security_stats['Sharpe_Ratio'].mean():.2f}"
)

print(
    f"Covariance Ready  : "
    f"{covariance_check['Covariance_Ready'].sum():,}"
)

# =========================================================
# PART 4 STARTS HERE
# =========================================================
#
# Next:
#
# Output Files
# CSV Persistence
# Dashboard Exports
# Audit Reports
# Final Production Reporting
#
# =========================================================

# =========================================================
# OUTPUT FILES
# =========================================================

print(
    "\n💾 Saving Outputs..."
)

RETURNS_MATRIX_FILE = (
    OUTPUT_DIR
    / "returns_matrix.csv"
)

LOG_RETURNS_MATRIX_FILE = (
    OUTPUT_DIR
    / "log_returns_matrix.csv"
)

MONTHLY_RETURNS_FILE = (
    OUTPUT_DIR
    / "monthly_returns_matrix.csv"
)

SECURITY_STATS_FILE = (
    OUTPUT_DIR
    / "security_return_statistics.csv"
)

COVERAGE_FILE = (
    OUTPUT_DIR
    / "returns_coverage_report.csv"
)

DISTRIBUTION_FILE = (
    OUTPUT_DIR
    / "return_distribution_statistics.csv"
)

CROSS_SECTIONAL_FILE = (
    OUTPUT_DIR
    / "cross_sectional_statistics.csv"
)

COVARIANCE_READY_FILE = (
    OUTPUT_DIR
    / "covariance_readiness.csv"
)

FACTOR_READINESS_FILE = (
    OUTPUT_DIR
    / "factor_model_readiness.csv"
)

MARKET_STATS_FILE = (
    OUTPUT_DIR
    / "market_statistics.csv"
)

DASHBOARD_FILE = (
    OUTPUT_DIR
    / "returns_dashboard.csv"
)

# =========================================================
# SAVE DATASETS
# =========================================================

returns_matrix.to_csv(
    RETURNS_MATRIX_FILE
)

log_returns_matrix.to_csv(
    LOG_RETURNS_MATRIX_FILE
)

monthly_returns.to_csv(
    MONTHLY_RETURNS_FILE
)

security_stats.to_csv(
    SECURITY_STATS_FILE,
    index=False
)

coverage_metrics.to_csv(
    COVERAGE_FILE,
    index=False
)

distribution_stats.to_csv(
    DISTRIBUTION_FILE,
    index=False
)

cross_sectional_stats.to_csv(
    CROSS_SECTIONAL_FILE,
    index=False
)

covariance_check.to_csv(
    COVARIANCE_READY_FILE,
    index=False
)

factor_readiness.to_csv(
    FACTOR_READINESS_FILE,
    index=False
)

market_statistics.to_csv(
    MARKET_STATS_FILE,
    index=False
)

returns_dashboard.to_csv(
    DASHBOARD_FILE,
    index=False
)

# =========================================================
# BUILD AUDIT REPORT
# =========================================================

print(
    "🧾 Building Audit Report..."
)

audit_report = pd.DataFrame({

    "Metric": [

        "Engine_Version",

        "Run_Timestamp",

        "Total_Securities",

        "Eligible_Securities",

        "Return_Matrix_Rows",

        "Return_Matrix_Columns",

        "Monthly_Return_Rows",

        "Coverage_Score",

        "Covariance_Score",

        "Data_Quality_Score",

        "Average_Annual_Return",

        "Average_Annual_Volatility",

        "Average_Sharpe",

        "Average_Max_Drawdown"
    ],

    "Value": [

        ENGINE_VERSION,

        datetime.now(),

        coverage["Symbol"].nunique(),

        len(
            returns_matrix.columns
        ),

        returns_matrix.shape[0],

        returns_matrix.shape[1],

        monthly_returns.shape[0],

        round(
            coverage_score,
            2
        ),

        round(
            covariance_score,
            2
        ),

        round(
            quality_score,
            2
        ),

        round(
            security_stats[
                "Annualized_Return"
            ].mean(),
            6
        ),

        round(
            security_stats[
                "Annualized_Volatility"
            ].mean(),
            6
        ),

        round(
            security_stats[
                "Sharpe_Ratio"
            ].mean(),
            4
        ),

        round(
            security_stats[
                "Max_Drawdown"
            ].mean(),
            4
        )
    ]
})

audit_report.to_csv(
    REPORT_FILE,
    index=False
)

# =========================================================
# FINAL VALIDATION
# =========================================================

print(
    "✔ Running Final Validation..."
)

if returns_matrix.empty:

    raise ValueError(
        "Returns matrix is empty."
    )

if log_returns_matrix.empty:

    raise ValueError(
        "Log returns matrix is empty."
    )

if security_stats.empty:

    raise ValueError(
        "Security statistics are empty."
    )

if len(
    returns_matrix.columns
) == 0:

    raise ValueError(
        "No valid securities found."
    )

if coverage_score < 50:

    print(
        "⚠ Low Coverage Score."
    )

if covariance_score < 50:

    print(
        "⚠ Low Covariance Readiness."
    )

# =========================================================
# FINAL RANKINGS
# =========================================================

top_returners = (

    security_stats

    .sort_values(
        "Annualized_Return",
        ascending=False
    )

    .head(10)
)

top_sharpe = (

    security_stats

    .sort_values(
        "Sharpe_Ratio",
        ascending=False
    )

    .head(10)
)

worst_drawdowns = (

    security_stats

    .sort_values(
        "Max_Drawdown"
    )

    .head(10)
)

# =========================================================
# SAVE RANKINGS
# =========================================================

top_returners.to_csv(

    OUTPUT_DIR
    / "top_returners.csv",

    index=False
)

top_sharpe.to_csv(

    OUTPUT_DIR
    / "top_sharpe_securities.csv",

    index=False
)

worst_drawdowns.to_csv(

    OUTPUT_DIR
    / "worst_drawdowns.csv",

    index=False
)

# =========================================================
# PRODUCTION SUMMARY
# =========================================================

print(
    "\n===================================================="
)

print(
    "🏁 RETURNS MATRIX BUILDER COMPLETE"
)

print(
    "===================================================="
)

print(
    f"Eligible Securities : "
    f"{len(returns_matrix.columns):,}"
)

print(
    f"Trading Days        : "
    f"{len(returns_matrix):,}"
)

print(
    f"Coverage Score      : "
    f"{coverage_score:.2f}"
)

print(
    f"Covariance Score    : "
    f"{covariance_score:.2f}"
)

print(
    f"Quality Score       : "
    f"{quality_score:.2f}"
)

print(
    f"Avg Annual Return   : "
    f"{security_stats['Annualized_Return'].mean():.2%}"
)

print(
    f"Avg Annual Vol      : "
    f"{security_stats['Annualized_Volatility'].mean():.2%}"
)

print(
    f"Avg Sharpe          : "
    f"{security_stats['Sharpe_Ratio'].mean():.2f}"
)

print(
    f"Best Security       : "
    f"{top_returners.iloc[0]['Symbol']}"
)

print(
    f"Best Return         : "
    f"{top_returners.iloc[0]['Annualized_Return']:.2%}"
)

print(
    "\nOutput Directory:"
)

print(
    OUTPUT_DIR
)

print(
    "===================================================="
)

# =========================================================
# END OF FILE
# =========================================================