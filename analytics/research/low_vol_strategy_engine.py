"""
=========================================================
LOW VOLATILITY STRATEGY ENGINE
=========================================================

Purpose:
Institutional Low Volatility Portfolio

Methodology:
20D Volatility
60D Volatility
ATR
Historical Drawdown

Output:
data/strategies/low_vol.csv

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
    / "low_vol_strategy_report.csv"
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

    "Volatility_20D",

    "Volatility_60D",

    "ATR_14",

    "Max_Drawdown_252D",
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

factor_cols = [

    "Volatility_20D",

    "Volatility_60D",

    "ATR_14",

    "Max_Drawdown_252D",
]

for col in factor_cols:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

    df[col] = df[col].fillna(
        df[col].median()
    )

# =========================================================
# RANKS
# LOWER = BETTER
# =========================================================

df["VOL20_RANK"] = 1 - (
    df["Volatility_20D"]
    .rank(pct=True)
)

df["VOL60_RANK"] = 1 - (
    df["Volatility_60D"]
    .rank(pct=True)
)

df["ATR_RANK"] = 1 - (
    df["ATR_14"]
    .rank(pct=True)
)

df["DD_RANK"] = 1 - (
    df["Max_Drawdown_252D"]
    .rank(pct=True)
)

# =========================================================
# LOW VOL SCORE
# =========================================================

df["LowVol_Score"] = (

      0.40
    * df["VOL60_RANK"]

    + 0.30
    * df["VOL20_RANK"]

    + 0.20
    * df["ATR_RANK"]

    + 0.10
    * df["DD_RANK"]
)

# =========================================================
# PORTFOLIO
# =========================================================

portfolio = (

    df

    .sort_values(
        "LowVol_Score",
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
        "LowVol_Score",
        "Portfolio_Date",
        "Engine_Version",
    ]
]

# =========================================================
# SAVE
# =========================================================

portfolio.to_csv(

    OUTPUT_DIR
    / "low_vol.csv",

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
                "LowVol_Score"
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
    "🏁 LOW VOL STRATEGY COMPLETE"
)

print("=" * 70)

print(
    f"Securities : "
    f"{len(portfolio)}"
)

print(
    f"Average Score : "
    f"{portfolio['LowVol_Score'].mean():.4f}"
)

print(
    f"\nSaved:\n"
    f"{OUTPUT_DIR / 'low_vol.csv'}"
)

print("=" * 70)