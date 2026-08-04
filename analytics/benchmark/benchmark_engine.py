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

from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

# =========================================================
# CONFIG
# =========================================================

ENGINE_VERSION = "1.0.0"

TRADING_DAYS = 252

ROLLING_WINDOW = 63

BENCHMARK_SYMBOL = "^CRSLDX"  # NIFTY 500

# Alternatives
#
# ^NSEI      NIFTY 50
# ^CNXMIDCAP NIFTY MIDCAP
#

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

BACKTEST_FILE = ROOT / "data" / "backtests" / "equity_curve.csv"

BENCHMARK_DIR = ROOT / "data" / "benchmark"

REPORT_FILE = BENCHMARK_DIR / "benchmark_report.csv"

TIMESERIES_FILE = BENCHMARK_DIR / "benchmark_timeseries.csv"

ROLLING_FILE = BENCHMARK_DIR / "rolling_metrics.csv"

SUMMARY_FILE = ROOT / "data" / "logs" / "benchmark_summary.csv"

# =========================================================
# LOAD PORTFOLIO RETURNS
# =========================================================

print("\n📥 Loading Backtest...")

portfolio = pd.read_csv(BACKTEST_FILE)

required_cols = [
    "Date",
    "Portfolio_Value",
]

for col in required_cols:
    if col not in portfolio.columns:
        raise ValueError(f"Missing Column: {col}")

portfolio["Date"] = pd.to_datetime(portfolio["Date"])

portfolio = portfolio.sort_values("Date")

portfolio["Portfolio_Return"] = portfolio["Portfolio_Value"].pct_change()

portfolio = portfolio.dropna()

# Remove previously calculated benchmark columns
portfolio = portfolio.drop(
    columns=[
        "Benchmark_Return",
        "Active_Return",
    ],
    errors="ignore",
)

# =========================================================
# DOWNLOAD BENCHMARK
# =========================================================

print("\n📊 Downloading Benchmark...")

start_date = portfolio["Date"].min().strftime("%Y-%m-%d")

end_date = portfolio["Date"].max().strftime("%Y-%m-%d")

benchmark = yf.download(
    BENCHMARK_SYMBOL,
    start=start_date,
    end=end_date,
    auto_adjust=True,
    progress=False,
)

if benchmark.empty:
    raise ValueError(
        f"Unable to download benchmark: {BENCHMARK_SYMBOL}"
    )

benchmark = benchmark.copy()

# Flatten MultiIndex if present
if isinstance(
    benchmark.columns,
    pd.MultiIndex,
):
    benchmark.columns = [
        "_".join(
            str(i)
            for i in col
            if i != ""
        )
        for col in benchmark.columns
    ]

benchmark = benchmark.reset_index()

benchmark.columns = (
    benchmark.columns
    .astype(str)
    .str.strip()
)

print("\nDownloaded Columns:")
print(benchmark.columns.tolist())

# Find Close column automatically
close_cols = [
    c
    for c in benchmark.columns
    if c.startswith("Close")
]

if not close_cols:
    raise ValueError(
        f"No Close column found.\nColumns: {benchmark.columns.tolist()}"
    )

close_col = close_cols[0]

benchmark["Date"] = pd.to_datetime(
    benchmark["Date"]
)

benchmark["Benchmark_Return"] = (
    benchmark[close_col]
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
    raise ValueError("No overlapping dates.")

# =========================================================
# ACTIVE RETURN
# =========================================================

merged["Active_Return"] = merged["Portfolio_Return"] - merged["Benchmark_Return"]

# =========================================================
# PERFORMANCE METRICS
# =========================================================

portfolio_return = (1 + merged["Portfolio_Return"]).prod() - 1

benchmark_return = (1 + merged["Benchmark_Return"]).prod() - 1

alpha = portfolio_return - benchmark_return

tracking_error = merged["Active_Return"].std() * np.sqrt(TRADING_DAYS)

information_ratio = alpha / tracking_error if tracking_error > 0 else np.nan

correlation = merged["Portfolio_Return"].corr(merged["Benchmark_Return"])

covariance = np.cov(merged["Portfolio_Return"], merged["Benchmark_Return"])

beta = covariance[0, 1] / covariance[1, 1] if covariance[1, 1] != 0 else np.nan

hit_rate = (merged["Active_Return"] > 0).mean() * 100

# =========================================================
# ROLLING METRICS
# =========================================================

rolling = pd.DataFrame()

rolling["Date"] = merged["Date"]

rolling["Rolling_Alpha"] = (
    merged["Active_Return"].rolling(ROLLING_WINDOW).mean() * TRADING_DAYS
)

rolling["Rolling_TE"] = merged["Active_Return"].rolling(ROLLING_WINDOW).std() * np.sqrt(
    TRADING_DAYS
)

rolling["Rolling_IR"] = rolling["Rolling_Alpha"] / rolling["Rolling_TE"]

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

report = pd.DataFrame(
    {
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
            datetime.now().strftime("%Y-%m-%d"),
            ENGINE_VERSION,
        ],
    }
)

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

print("🏁 BENCHMARK ENGINE COMPLETE")

print("=" * 70)

print(f"Portfolio Return : {portfolio_return:.2%}")

print(f"Benchmark Return : {benchmark_return:.2%}")

print(f"Alpha            : {alpha:.2%}")

print(f"Tracking Error   : {tracking_error:.2%}")

print(f"Information Ratio: {information_ratio:.2f}")

print(f"Beta             : {beta:.2f}")

print(f"Hit Rate         : {hit_rate:.2f}%")

print(f"\nOutput Directory:\n{BENCHMARK_DIR}")

print("=" * 70)
