"""
=========================================================
BENCHMARK CONSTITUENTS ENGINE
=========================================================

Purpose:
Build Institutional Benchmark Constituents

Input:
data/factors/factor_snapshot_master.csv

Output:
data/benchmark/benchmark_constituents.csv

=========================================================
"""

from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np

# =========================================================
# CONFIG
# =========================================================

ENGINE_VERSION = "1.0.0"

BENCHMARK_SIZE = 100

MIN_ADV = 5_000_000

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

FACTOR_FILE = (
    ROOT
    / "data"
    / "factors"
    / "factor_snapshot_master.csv"
)

OUTPUT_DIR = (
    ROOT
    / "data"
    / "benchmark"
)

REPORT_FILE = (
    ROOT
    / "data"
    / "logs"
    / "benchmark_constituents_report.csv"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

# =========================================================
# LOAD
# =========================================================

print(
    "\n📥 Loading Factor Universe..."
)

df = pd.read_csv(
    FACTOR_FILE
)

if df.empty:

    raise ValueError(
        "Factor universe empty"
    )

required_cols = [

    "Symbol",
    "Company_Name",
    "Sector",
    "Market_Cap",
    "ADV_20D",
]

missing = [

    c

    for c in required_cols

    if c not in df.columns
]

if missing:

    raise ValueError(
        f"Missing Columns: {missing}"
    )

# =========================================================
# LATEST SNAPSHOT
# =========================================================

df["Snapshot_Date"] = pd.to_datetime(
    df["Snapshot_Date"]
)

latest_date = (
    df["Snapshot_Date"]
    .max()
)

df = df[
    df["Snapshot_Date"]
    == latest_date
].copy()

# =========================================================
# CLEAN
# =========================================================

df["Market_Cap"] = pd.to_numeric(
    df["Market_Cap"],
    errors="coerce"
)

df["ADV_20D"] = pd.to_numeric(
    df["ADV_20D"],
    errors="coerce"
)

df = df.dropna(
    subset=[
        "Market_Cap",
        "ADV_20D",
    ]
)

# =========================================================
# LIQUIDITY FILTER
# =========================================================

df = df[
    df["ADV_20D"]
    >= MIN_ADV
]

# =========================================================
# MARKET CAP RANK
# =========================================================

df = df.sort_values(

    "Market_Cap",

    ascending=False
)

benchmark = df.head(
    BENCHMARK_SIZE
).copy()

# =========================================================
# MARKET CAP WEIGHTS
# =========================================================

benchmark["Weight"] = (

    benchmark["Market_Cap"]

    / benchmark["Market_Cap"].sum()
)

# =========================================================
# NORMALIZE
# =========================================================

benchmark["Weight"] = (

    benchmark["Weight"]

    / benchmark["Weight"].sum()
)

# =========================================================
# PERCENT FORMAT
# =========================================================

benchmark["Weight_Pct"] = (

    benchmark["Weight"]

    * 100
)

# =========================================================
# FINAL OUTPUT
# =========================================================

benchmark = benchmark[

    [

        "Snapshot_Date",

        "Symbol",

        "Company_Name",

        "Sector",

        "Market_Cap",

        "ADV_20D",

        "Weight",

        "Weight_Pct",
    ]

]

benchmark = benchmark.rename(
    columns={
        "Snapshot_Date":
        "Date"
    }
)

# =========================================================
# SAVE
# =========================================================

OUTPUT_FILE = (
    OUTPUT_DIR
    / "benchmark_constituents.csv"
)

benchmark.to_csv(
    OUTPUT_FILE,
    index=False,
)

# =========================================================
# REPORT
# =========================================================

report = pd.DataFrame({

    "Metric": [

        "Benchmark_Size",

        "Total_Market_Cap",

        "Average_ADV",

        "Run_Date",

        "Engine_Version",
    ],

    "Value": [

        len(
            benchmark
        ),

        benchmark[
            "Market_Cap"
        ].sum(),

        benchmark[
            "ADV_20D"
        ].mean(),

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

# =========================================================
# REPORT
# =========================================================

print("\n" + "=" * 70)

print(
    "🏁 BENCHMARK CONSTITUENTS ENGINE COMPLETE"
)

print("=" * 70)

print(
    f"Benchmark Stocks : "
    f"{len(benchmark)}"
)

print(
    f"Top Holding      : "
    f"{benchmark.iloc[0]['Symbol']}"
)

print(
    f"Weight           : "
    f"{benchmark.iloc[0]['Weight_Pct']:.2f}%"
)

print(
    f"\nSaved:\n"
    f"{OUTPUT_FILE}"
)

print("=" * 70)