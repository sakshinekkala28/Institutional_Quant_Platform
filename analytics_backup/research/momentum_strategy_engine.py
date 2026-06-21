"""
=========================================================
MOMENTUM STRATEGY ENGINE
=========================================================

Purpose:
Institutional Momentum Portfolio Construction

Methodology:
12M Momentum
6M Momentum
3M Momentum
Distance From 52W High

Output:
data/strategies/momentum.csv

=========================================================
"""

from pathlib import Path
from datetime import datetime

import numpy as np
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
    / "momentum_strategy_report.csv"
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

    "Momentum_3M",

    "Momentum_6M",

    "Momentum_12M",

    "Distance_52W_High",
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
# FACTOR RANKS
# =========================================================

df["MOM12_RANK"] = (
    df["Momentum_12M"]
    .rank(
        pct=True
    )
)

df["MOM6_RANK"] = (
    df["Momentum_6M"]
    .rank(
        pct=True
    )
)

df["MOM3_RANK"] = (
    df["Momentum_3M"]
    .rank(
        pct=True
    )
)

df["HIGH52_RANK"] = (
    df["Distance_52W_High"]
    .rank(
        pct=True
    )
)

# =========================================================
# MOMENTUM SCORE
# =========================================================

df["Momentum_Score"] = (

      0.50
    * df["MOM12_RANK"]

    + 0.30
    * df["MOM6_RANK"]

    + 0.10
    * df["MOM3_RANK"]

    + 0.10
    * df["HIGH52_RANK"]
)

# =========================================================
# PORTFOLIO
# =========================================================

portfolio = (

    df

    .sort_values(
        "Momentum_Score",
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
        "Momentum_Score",
        "Portfolio_Date",
        "Engine_Version",
    ]
]

# =========================================================
# SAVE
# =========================================================

portfolio.to_csv(

    OUTPUT_DIR
    / "momentum.csv",

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
                "Momentum_Score"
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
    "🏁 MOMENTUM STRATEGY COMPLETE"
)

print("=" * 70)

print(
    f"Securities : "
    f"{len(portfolio)}"
)

print(
    f"Average Score : "
    f"{portfolio['Momentum_Score'].mean():.4f}"
)

print(
    f"\nSaved:\n"
    f"{OUTPUT_DIR / 'momentum.csv'}"
)

print("=" * 70)