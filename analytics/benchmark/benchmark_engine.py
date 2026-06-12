"""
=========================================================
BENCHMARK ENGINE
=========================================================

Purpose:
Institutional Benchmark Analytics

Inputs:
data/backtests/backtest_results.csv

Outputs:
data/benchmark/benchmark_report.csv
data/benchmark/benchmark_timeseries.csv
data/benchmark/rolling_metrics.csv

=========================================================
"""

from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
import yfinance as yf

# =========================================================
# CONFIG
# =========================================================

ENGINE_VERSION = "1.0.0"

TRADING_DAYS = 252

ROLLING_WINDOW = 63

BENCHMARK_SYMBOL = "^CRSLDX"   # NIFTY 500

# Alternatives
#
# ^NSEI      NIFTY 50
# ^CNXMIDCAP NIFTY MIDCAP
#

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

BACKTEST_FILE = (
    ROOT
    / "data"
    / "backtests"
    / "equity_curve.csv"
)

BENCHMARK_DIR = (
    ROOT
    / "data"
    / "benchmark"
)

REPORT_FILE = (
    BENCHMARK_DIR
    / "benchmark_report.csv"
)

TIMESERIES_FILE = (
    BENCHMARK_DIR
    / "benchmark_timeseries.csv"
)

ROLLING_FILE = (
    BENCHMARK_DIR
    / "rolling_metrics.csv"
)

SUMMARY_FILE = (
    ROOT
    / "data"
    / "logs"
    / "benchmark_summary.csv"
)

# =========================================================
# LOAD PORTFOLIO RETURNS
# =========================================================

print(
    "\n📥 Loading Backtest..."
)

portfolio = pd.read_csv(
    BACKTEST_FILE
)

required_cols = [
    "Date",
    "Portfolio_Value",
]

for col in required_cols:

    if col not in portfolio.columns:

        raise ValueError(
            f"Missing Column: {col}"
        )

portfolio["Date"] = pd.to_datetime(
    portfolio["Date"]
)

portfolio = portfolio.sort_values(
    "Date"
)

portfolio["Portfolio_Return"] = (
    portfolio["Portfolio_Value"]
    .pct_change()
)

portfolio = portfolio.dropna()

# =========================================================
# DOWNLOAD BENCHMARK
# =========================================================

print(
    "\n📊 Downloading Benchmark..."
)

start_date = (
    portfolio["Date"]
    .min()
    .strftime("%Y-%m-%d")
)

end_date = (
    portfolio["Date"]
    .max()
    .strftime("%Y-%m-%d")
)

benchmark = yf.download(
    BENCHMARK_SYMBOL,
    start=start_date,
    end=end_date,
    auto_adjust=True,
    progress=False,
)

if benchmark.empty:

    raise ValueError(
        "Benchmark download failed."
    )

if isinstance(
    benchmark.columns,
    pd.MultiIndex
):

    benchmark.columns = [
        c[0]
        for c in benchmark.columns
    ]

benchmark = (
    benchmark
    .reset_index()
)

benchmark.columns = [
    str(c).strip()
    for c in benchmark.columns
]

benchmark["Date"] = pd.to_datetime(
    benchmark["Date"]
)

benchmark["Benchmark_Return"] = (
    benchmark["Close"]
    .pct_change()
)

benchmark = benchmark[
    [
        "Date",
        "Benchmark_Return",
    ]
].dropna()

# =========================================================
# MERGE
# =========================================================

merged = portfolio.merge(

    benchmark,

    on="Date",

    how="inner",
)

if merged.empty:

    raise ValueError(
        "No overlapping dates."
    )

# =========================================================
# ACTIVE RETURN
# =========================================================

merged["Active_Return"] = (

    merged["Portfolio_Return"]

    -

    merged["Benchmark_Return"]
)

# =========================================================
# PERFORMANCE METRICS
# =========================================================

portfolio_return = (

    (
        1
        +
        merged[
            "Portfolio_Return"
        ]
    )

    .prod()

    - 1
)

benchmark_return = (

    (
        1
        +
        merged[
            "Benchmark_Return"
        ]
    )

    .prod()

    - 1
)

alpha = (

    portfolio_return

    -

    benchmark_return
)

tracking_error = (

    merged[
        "Active_Return"
    ]

    .std()

    * np.sqrt(
        TRADING_DAYS
    )
)

information_ratio = (

    alpha

    /

    tracking_error

    if tracking_error > 0

    else np.nan
)

correlation = (

    merged[
        "Portfolio_Return"
    ]

    .corr(

        merged[
            "Benchmark_Return"
        ]
    )
)

covariance = np.cov(

    merged[
        "Portfolio_Return"
    ],

    merged[
        "Benchmark_Return"
    ]
)

beta = (

    covariance[0, 1]

    /

    covariance[1, 1]

    if covariance[1, 1] != 0

    else np.nan
)

hit_rate = (

    (
        merged[
            "Active_Return"
        ]

        > 0
    )

    .mean()

    * 100
)

# =========================================================
# ROLLING METRICS
# =========================================================

rolling = pd.DataFrame()

rolling["Date"] = merged["Date"]

rolling["Rolling_Alpha"] = (

    merged[
        "Active_Return"
    ]

    .rolling(
        ROLLING_WINDOW
    )

    .mean()

    * TRADING_DAYS
)

rolling["Rolling_TE"] = (

    merged[
        "Active_Return"
    ]

    .rolling(
        ROLLING_WINDOW
    )

    .std()

    * np.sqrt(
        TRADING_DAYS
    )
)

rolling["Rolling_IR"] = (

    rolling[
        "Rolling_Alpha"
    ]

    /

    rolling[
        "Rolling_TE"
    ]
)

# =========================================================
# SAVE TIMESERIES
# =========================================================

BENCHMARK_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

merged.to_csv(
    TIMESERIES_FILE,
    index=False,
)

rolling.to_csv(
    ROLLING_FILE,
    index=False,
)

# =========================================================
# REPORT
# =========================================================

report = pd.DataFrame({

    "Metric": [

        "Portfolio_Return",

        "Benchmark_Return",

        "Alpha",

        "Tracking_Error",

        "Information_Ratio",

        "Beta",

        "Correlation",

        "Hit_Rate",

        "Run_Date",

        "Engine_Version",
    ],

    "Value": [

        portfolio_return,

        benchmark_return,

        alpha,

        tracking_error,

        information_ratio,

        beta,

        correlation,

        hit_rate,

        datetime.now()
        .strftime(
            "%Y-%m-%d"
        ),

        ENGINE_VERSION,
    ]
})

report.to_csv(
    REPORT_FILE,
    index=False,
)

report.to_csv(
    SUMMARY_FILE,
    index=False,
)

# =========================================================
# REPORT
# =========================================================

print("\n" + "=" * 70)

print(
    "🏁 BENCHMARK ENGINE COMPLETE"
)

print("=" * 70)

print(
    f"Portfolio Return : "
    f"{portfolio_return:.2%}"
)

print(
    f"Benchmark Return : "
    f"{benchmark_return:.2%}"
)

print(
    f"Alpha            : "
    f"{alpha:.2%}"
)

print(
    f"Tracking Error   : "
    f"{tracking_error:.2%}"
)

print(
    f"Information Ratio: "
    f"{information_ratio:.2f}"
)

print(
    f"Beta             : "
    f"{beta:.2f}"
)

print(
    f"Hit Rate         : "
    f"{hit_rate:.2f}%"
)

print(
    f"\nOutput Directory:\n"
    f"{BENCHMARK_DIR}"
)

print("=" * 70)