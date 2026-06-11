"""
=========================================================
BENCHMARK ENGINE
=========================================================

Downloads benchmark history required for:

- Regime Detection
- Relative Strength
- Beta
- Attribution
- Portfolio Analytics

Output:
data/raw/benchmark_prices.csv
=========================================================
"""

from pathlib import Path

import pandas as pd
import yfinance as yf

# =========================================================
# CONFIG
# =========================================================

YEARS_HISTORY = 10

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

OUTPUT_FILE = (
    ROOT
    / "data"
    / "raw"
    / "benchmark_prices.csv"
)

FAILURE_FILE = (
    ROOT
    / "data"
    / "logs"
    / "benchmark_failures.csv"
)

# =========================================================
# BENCHMARKS
# =========================================================

BENCHMARKS = {
    "NIFTY50": "^NSEI",
    "INDIA_VIX": "^INDIAVIX",
}

# =========================================================
# DOWNLOAD
# =========================================================

print("\n📥 Downloading Benchmarks...")

all_data = []
failures = []

for name, ticker in BENCHMARKS.items():

    try:

        print(f"Downloading {name}")

        df = yf.download(
            ticker,
            period=f"{YEARS_HISTORY}y",
            auto_adjust=True,
            progress=False,
            threads=False,
        )

        if df.empty:
            raise ValueError("No Data")

        df = df.reset_index()

        df["Benchmark"] = name

        all_data.append(df)

    except Exception as e:

        failures.append(
            {
                "Benchmark": name,
                "Ticker": ticker,
                "Error": str(e),
            }
        )

# =========================================================
# BUILD DATASET
# =========================================================

if not all_data:
    raise RuntimeError(
        "No benchmark data downloaded."
    )

benchmarks = pd.concat(
    all_data,
    ignore_index=True,
)

# Flatten MultiIndex Columns

if isinstance(
    benchmarks.columns,
    pd.MultiIndex,
):

    benchmarks.columns = [
        col[0]
        if isinstance(col, tuple)
        else col
        for col in benchmarks.columns
    ]

benchmarks.columns = [
    str(c).replace(" ", "_")
    for c in benchmarks.columns
]

benchmarks = benchmarks.sort_values(
    ["Benchmark", "Date"]
)

# =========================================================
# SAVE
# =========================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

benchmarks.to_csv(
    OUTPUT_FILE,
    index=False,
)

# =========================================================
# FAILURES
# =========================================================

if failures:

    FAILURE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    pd.DataFrame(
        failures
    ).to_csv(
        FAILURE_FILE,
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
    f"Benchmarks : {benchmarks['Benchmark'].nunique()}"
)

print(
    f"Rows       : {len(benchmarks):,}"
)

print(
    f"Failures   : {len(failures)}"
)

print(
    f"\nSaved:\n{OUTPUT_FILE}"
)

print("=" * 70)