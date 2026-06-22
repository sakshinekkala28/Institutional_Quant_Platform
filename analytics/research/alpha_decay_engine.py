"""
=========================================================
ALPHA DECAY ENGINE
=========================================================

Purpose:
Institutional Alpha Persistence Analysis

Measures:
1M IC
3M IC
6M IC
12M IC

Inputs:
data/factors/factor_snapshot_master.csv

Outputs:
alpha_decay.csv
alpha_decay_summary.csv
alpha_decay_rankings.csv

=========================================================
"""

from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd

def spearmanr(x, y):
    x = pd.Series(x).rank()
    y = pd.Series(y).rank()
    return x.corr(y), None


# =========================================================
# CONFIG
# =========================================================

ENGINE_VERSION = "1.0.0"

MIN_CROSS_SECTION = 30

FORWARD_HORIZONS = [1, 3, 6, 12]

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    ROOT
    / "data"
    / "factors"
    / "factor_snapshot_master.csv"
)

OUTPUT_DIR = (
    ROOT
    / "data"
    / "research"
)

REPORT_FILE = (
    ROOT
    / "data"
    / "logs"
    / "alpha_decay_report.csv"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

# =========================================================
# LOAD
# =========================================================

print(
    "\n📥 Loading Factor Snapshots..."
)

df = pd.read_csv(
    INPUT_FILE
)

if df.empty:

    raise ValueError(
        "factor_snapshot_master.csv empty"
    )

required = [
    "Snapshot_Date",
    "Symbol",
    "Last_Close",
]

missing = [
    c
    for c in required
    if c not in df.columns
]

if missing:

    raise ValueError(
        f"Missing Columns: {missing}"
    )

# =========================================================
# DATE
# =========================================================

df["Snapshot_Date"] = pd.to_datetime(
    df["Snapshot_Date"]
)

df = df.sort_values(
    [
        "Symbol",
        "Snapshot_Date",
    ]
)

# =========================================================
# FACTORS
# =========================================================

candidate_factors = [

    "Momentum_1M",
    "Momentum_3M",
    "Momentum_6M",
    "Momentum_12M",

    "Volatility_20D",
    "Volatility_60D",

    "ATR_14",

    "Max_Drawdown_252D",

    "Distance_SMA50",
    "Distance_SMA200",

    "Distance_52W_High",

    "ADV_20D",

    "Dollar_Volume",

    "Market_Cap",
]

factors = [

    f

    for f in candidate_factors

    if f in df.columns
]

if not factors:

    raise ValueError(
        "No factor columns found"
    )

# =========================================================
# FORWARD RETURNS
# =========================================================

print(
    "\n📊 Building Forward Returns..."
)

for horizon in FORWARD_HORIZONS:

    df[
        f"Forward_Return_{horizon}M"
    ] = (

        df.groupby("Symbol")[
            "Last_Close"
        ]

        .shift(-horizon)

        / df["Last_Close"]

        - 1
    )

# =========================================================
# DECAY CALCULATION
# =========================================================

print(
    "\n📈 Calculating Alpha Decay..."
)

records = []

dates = sorted(
    df["Snapshot_Date"]
    .dropna()
    .unique()
)

for factor in factors:

    for horizon in FORWARD_HORIZONS:

        future_col = (
            f"Forward_Return_{horizon}M"
        )

        for date in dates:

            tmp = df[

                df["Snapshot_Date"]
                == date

            ][

                [
                    factor,
                    future_col,
                ]

            ].dropna()

            if len(tmp) < MIN_CROSS_SECTION:

                continue

            try:

                ic = spearmanr(

                    tmp[factor],

                    tmp[future_col]

                )[0]

                records.append({

                    "Date":
                    date,

                    "Factor":
                    factor,

                    "Horizon_Months":
                    horizon,

                    "IC":
                    ic,
                })

            except Exception:

                continue

# =========================================================
# MASTER DATA
# =========================================================

decay_df = pd.DataFrame(
    records
)

if decay_df.empty:

    raise ValueError(
        "No alpha decay observations"
    )

# =========================================================
# SUMMARY
# =========================================================

summary = (

    decay_df

    .groupby(
        [
            "Factor",
            "Horizon_Months",
        ]
    )

    ["IC"]

    .agg(

        Avg_IC="mean",

        IC_Std="std",

        Positive_Months=
        lambda x:
        (
            x > 0
        ).mean(),
    )

    .reset_index()
)

summary["ICIR"] = (

    summary["Avg_IC"]

    / summary["IC_Std"]

    .replace(
        0,
        np.nan,
    )
)

summary["Abs_IC"] = (
    summary["Avg_IC"]
    .abs()
)

# =========================================================
# DECAY SCORE
# =========================================================

decay_score = (

    summary

    .pivot_table(

        index="Factor",

        columns="Horizon_Months",

        values="Avg_IC",
    )

    .reset_index()
)

for h in FORWARD_HORIZONS:

    if h not in decay_score.columns:

        decay_score[h] = np.nan

decay_score["Persistence_Score"] = (

      decay_score[1].fillna(0)

    + decay_score[3].fillna(0)

    + decay_score[6].fillna(0)

    + decay_score[12].fillna(0)

)

# =========================================================
# GRADING
# =========================================================

def grade(score):

    score = abs(score)

    if score >= 0.25:
        return "Exceptional"

    if score >= 0.18:
        return "Strong"

    if score >= 0.12:
        return "Good"

    if score >= 0.06:
        return "Moderate"

    return "Weak"

decay_score["Grade"] = (
    decay_score[
        "Persistence_Score"
    ]
    .apply(grade)
)

# =========================================================
# RANKINGS
# =========================================================

rankings = (

    decay_score

    .sort_values(
        "Persistence_Score",
        ascending=False,
    )

    .reset_index(
        drop=True
    )
)

rankings["Rank"] = (
    rankings.index + 1
)

# =========================================================
# SAVE
# =========================================================

decay_df.to_csv(

    OUTPUT_DIR
    / "alpha_decay.csv",

    index=False,
)

summary.to_csv(

    OUTPUT_DIR
    / "alpha_decay_summary.csv",

    index=False,
)

rankings.to_csv(

    OUTPUT_DIR
    / "alpha_decay_rankings.csv",

    index=False,
)

report = pd.DataFrame({

    "Metric": [

        "Factors_Analyzed",

        "Decay_Observations",

        "Best_Factor",

        "Persistence_Score",

        "Run_Date",

        "Engine_Version",
    ],

    "Value": [

        len(rankings),

        len(decay_df),

        rankings.iloc[0][
            "Factor"
        ],

        rankings.iloc[0][
            "Persistence_Score"
        ],

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

best = rankings.iloc[0]

print("\n" + "=" * 70)

print(
    "🏁 ALPHA DECAY ENGINE COMPLETE"
)

print("=" * 70)

print(
    f"Factors Analyzed : "
    f"{len(rankings)}"
)

print(
    f"Best Factor      : "
    f"{best['Factor']}"
)

print(
    f"Persistence Score: "
    f"{best['Persistence_Score']:.4f}"
)

print(
    f"Grade            : "
    f"{best['Grade']}"
)

print(
    f"\nOutput Directory:\n"
    f"{OUTPUT_DIR}"
)

print("=" * 70)