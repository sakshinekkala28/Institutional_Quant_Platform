"""
=========================================================
FACTOR RANK ENGINE
=========================================================

Purpose:
Convert raw factor values into normalized ranks
and generate Composite Alpha Score.

Input:
data/factors/factor_master.csv

Outputs:
data/factors/factor_rank_master.csv

data/portfolios/top_50.csv
data/portfolios/top_100.csv
data/portfolios/top_250.csv

data/logs/ranking_report.csv

=========================================================
"""

from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd

# =========================================================
# CONFIG
# =========================================================

ENGINE_VERSION = "2.0.0"

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    ROOT
    / "data"
    / "factors"
    / "factor_master.csv"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "factors"
    / "factor_rank_master.csv"
)

PORTFOLIO_DIR = (
    ROOT
    / "data"
    / "portfolios"
)

REPORT_FILE = (
    ROOT
    / "data"
    / "logs"
    / "ranking_report.csv"
)

# =========================================================
# LOAD
# =========================================================

print("\n📥 Loading Factor Master...")

df = pd.read_csv(INPUT_FILE)

if df.empty:
    raise ValueError(
        "factor_master.csv is empty"
    )

print(
    f"Universe Size : {len(df):,}"
)

# =========================================================
# FACTOR DEFINITIONS
# =========================================================

HIGHER_BETTER = [

    "Momentum_1M",
    "Momentum_3M",
    "Momentum_6M",
    "Momentum_12M",

    "ADV_20D",
    "Dollar_Volume",

    "Market_Cap",
    "Log_Market_Cap",

    "Distance_SMA50",
    "Distance_SMA200",

    "Distance_52W_High",
]

LOWER_BETTER = [

    "Volatility_20D",
    "Volatility_60D",

    "ATR_14",

    "Max_Drawdown_252D",
]

# =========================================================
# WINSORIZATION
# =========================================================

def winsorize(series):

    lower = series.quantile(0.01)

    upper = series.quantile(0.99)

    return series.clip(
        lower=lower,
        upper=upper,
    )

# =========================================================
# COVERAGE CHECK
# =========================================================

coverage = []

for col in HIGHER_BETTER + LOWER_BETTER:

    if col not in df.columns:

        raise ValueError(
            f"Missing factor: {col}"
        )

    coverage_pct = (
        df[col]
        .notna()
        .mean()
        * 100
    )

    coverage.append(
        {
            "Factor": col,
            "Coverage_Pct": round(
                coverage_pct,
                2,
            ),
        }
    )

coverage_df = pd.DataFrame(
    coverage
)

# =========================================================
# WINSORIZE
# =========================================================

for col in HIGHER_BETTER + LOWER_BETTER:

    df[col] = winsorize(
        df[col]
    )

# =========================================================
# PERCENTILE RANKS
# =========================================================

for col in HIGHER_BETTER:

    df[f"{col}_Rank"] = (
        df.groupby("Sector")[col]
        .rank(
            pct=True,
            method="average",
        )
    )

for col in LOWER_BETTER:

    df[f"{col}_Rank"] = (

        1

        - df.groupby("Sector")[col]
        .rank(
            pct=True,
            method="average",
        )
    )

# =========================================================
# COMPOSITE ALPHA
# =========================================================

df["Alpha_Score"] = (

      0.30
    * df["Momentum_12M_Rank"]

    + 0.20
    * df["Momentum_6M_Rank"]

    + 0.15
    * df["ADV_20D_Rank"]

    + 0.10
    * df["Distance_52W_High_Rank"]

    + 0.10
    * df["Log_Market_Cap_Rank"]

    + 0.15
    * df["Volatility_20D_Rank"]

)

# =========================================================
# LIQUIDITY ADJUSTMENT
# =========================================================

df["Liquidity_Penalty"] = (

    1
    - df["ADV_20D_Rank"]

)

df["Alpha_Adjusted"] = (

    df["Alpha_Score"]

    - 0.10

    * df["Liquidity_Penalty"]

)

# =========================================================
# FINAL RANK
# =========================================================

df["Rank"] = (

    df["Alpha_Adjusted"]

    .rank(
        ascending=False,
        method="dense",
    )

    .astype(float)

)

# =========================================================
# METADATA
# =========================================================

today = datetime.now().strftime(
    "%Y-%m-%d"
)

df["Ranking_Date"] = today

df["Engine_Version"] = (
    ENGINE_VERSION
)

# =========================================================
# SORT
# =========================================================

ranked = (

    df

    .sort_values(
        "Alpha_Adjusted",
        ascending=False,
    )

    .reset_index(
        drop=True
    )
)

# =========================================================
# SAVE MASTER
# =========================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

ranked.to_csv(
    OUTPUT_FILE,
    index=False,
)

# =========================================================
# TOP PORTFOLIOS
# =========================================================

PORTFOLIO_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

top50 = ranked.head(50)

top100 = ranked.head(100)

top250 = ranked.head(250)

top50.to_csv(
    PORTFOLIO_DIR / "top_50.csv",
    index=False,
)

top100.to_csv(
    PORTFOLIO_DIR / "top_100.csv",
    index=False,
)

top250.to_csv(
    PORTFOLIO_DIR / "top_250.csv",
    index=False,
)

# =========================================================
# FACTOR EXPOSURE REPORT
# =========================================================

top50 = ranked.head(50)

factor_exposure = pd.DataFrame(
    {
        "Factor": [

            "Momentum_12M",

            "Momentum_6M",

            "Volatility_20D",

            "ADV_20D",

            "Log_Market_Cap",
        ],

        "Exposure": [

            top50[
                "Momentum_12M_Rank"
            ].mean(),

            top50[
                "Momentum_6M_Rank"
            ].mean(),

            top50[
                "Volatility_20D_Rank"
            ].mean(),

            top50[
                "ADV_20D_Rank"
            ].mean(),

            top50[
                "Log_Market_Cap_Rank"
            ].mean(),
        ],
    }
)

factor_exposure.to_csv(
    ROOT
    / "data"
    / "logs"
    / "factor_exposure.csv",
    index=False,
)

# =========================================================
# SECTOR EXPOSURE
# =========================================================

sector_report = (

    top50

    .groupby("Sector")

    .size()

    .reset_index(
        name="Count"
    )

    .sort_values(
        "Count",
        ascending=False,
    )
)

sector_report.to_csv(

    ROOT
    / "data"
    / "logs"
    / "sector_exposure.csv",

    index=False,
)

# =========================================================
# REPORT
# =========================================================

report = pd.DataFrame(

    {
        "Metric": [

            "Universe_Size",

            "Top50_Min_Alpha",

            "Top100_Min_Alpha",

            "Average_Alpha",

            "Top50_Avg_ADV",

            "Top50_Avg_MarketCap",

            "Run_Date",

            "Engine_Version",
        ],

        "Value": [

            len(ranked),

            top50["Alpha_Score"].min(),

            top100["Alpha_Score"].min(),

            ranked["Alpha_Score"].mean(),

            top50["ADV_20D"].mean(),

            top50["Market_Cap"].mean(),

            today,

            ENGINE_VERSION,
        ],
    }
)

REPORT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

report.to_csv(
    REPORT_FILE,
    index=False,
)

# =========================================================
# REPORT
# =========================================================

print("\n" + "=" * 70)

print(
    "🏁 FACTOR RANK ENGINE COMPLETE"
)

print("=" * 70)

print(
    f"Universe Size : "
    f"{len(ranked):,}"
)

print(
    f"Top Alpha     : "
    f"{ranked['Alpha_Score'].max():.4f}"
)

print(
    f"Median Alpha  : "
    f"{ranked['Alpha_Score'].median():.4f}"
)

print(
    f"\nOutput:\n"
    f"{OUTPUT_FILE}"
)

print("=" * 70)