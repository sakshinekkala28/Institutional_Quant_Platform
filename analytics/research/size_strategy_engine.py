"""
=========================================================
SIZE STRATEGY ENGINE
=========================================================

Purpose:
Institutional Large Cap Portfolio

Methodology:
Market Cap
Liquidity Overlay

Output:
data/strategies/size.csv

=========================================================
"""

from pathlib import Path
from datetime import datetime

import pandas as pd

# =========================================================
# CONFIG
# =========================================================

TOP_N = 50

ENGINE_VERSION = "1.0.0"

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
    / "strategies"
)

REPORT_FILE = (
    ROOT
    / "data"
    / "logs"
    / "size_strategy_report.csv"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

# =========================================================
# LOAD
# =========================================================

print(
    "\n📥 Loading Factor Snapshot..."
)

df = pd.read_csv(
    FACTOR_FILE
)

required = [

    "Symbol",

    "Market_Cap",

    "ADV_20D",
]

for col in required:

    if col not in df.columns:

        raise ValueError(
            f"Missing Column: {col}"
        )

# =========================================================
# LATEST SNAPSHOT
# =========================================================

if "Snapshot_Date" in df.columns:

    df["Snapshot_Date"] = pd.to_datetime(
        df["Snapshot_Date"]
    )

    latest = (
        df["Snapshot_Date"]
        .max()
    )

    df = df[
        df["Snapshot_Date"]
        == latest
    ].copy()

# =========================================================
# CLEAN
# =========================================================

for col in [

    "Market_Cap",

    "ADV_20D",
]:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

    df[col] = df[col].fillna(
        df[col].median()
    )

# =========================================================
# RANKS
# =========================================================

df["MCAP_RANK"] = (
    df["Market_Cap"]
    .rank(
        pct=True
    )
)

df["ADV_RANK"] = (
    df["ADV_20D"]
    .rank(
        pct=True
    )
)

# =========================================================
# SIZE SCORE
# =========================================================

df["Size_Score"] = (

      0.80
    * df["MCAP_RANK"]

    + 0.20
    * df["ADV_RANK"]
)

# =========================================================
# PORTFOLIO
# =========================================================

portfolio = (

    df

    .sort_values(
        "Size_Score",
        ascending=False
    )

    .head(TOP_N)

    .copy()
)

portfolio["Weight"] = (
    1 / len(portfolio)
)

portfolio = portfolio.reset_index(
    drop=True
)

portfolio["Rank"] = (
    portfolio.index + 1
)

portfolio["Portfolio_Date"] = (
    datetime.now()
    .strftime("%Y-%m-%d")
)

portfolio["Engine_Version"] = (
    ENGINE_VERSION
)

portfolio = portfolio[

    [
        "Rank",
        "Symbol",
        "Weight",
        "Size_Score",
        "Portfolio_Date",
        "Engine_Version",
    ]
]

# =========================================================
# SAVE
# =========================================================

portfolio.to_csv(

    OUTPUT_DIR
    / "size.csv",

    index=False,
)

pd.DataFrame({

    "Metric": [

        "Securities",

        "Average_Score",

        "Run_Date",

        "Engine_Version",
    ],

    "Value": [

        len(portfolio),

        round(
            portfolio[
                "Size_Score"
            ].mean(),
            4,
        ),

        datetime.now()
        .strftime(
            "%Y-%m-%d"
        ),

        ENGINE_VERSION,
    ]

}).to_csv(

    REPORT_FILE,

    index=False,
)

# =========================================================
# REPORT
# =========================================================

print("\n" + "=" * 70)

print(
    "🏁 SIZE STRATEGY COMPLETE"
)

print("=" * 70)

print(
    f"Securities : "
    f"{len(portfolio)}"
)

print(
    f"Average Score : "
    f"{portfolio['Size_Score'].mean():.4f}"
)

print(
    f"\nSaved:\n"
    f"{OUTPUT_DIR / 'size.csv'}"
)

print("=" * 70)