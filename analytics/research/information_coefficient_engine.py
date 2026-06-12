"""
=========================================================
INFORMATION COEFFICIENT ENGINE
=========================================================

Purpose:
Institutional Factor Predictive Power Analysis

Inputs:
data/factors/factor_snapshot_master.csv

Outputs:
factor_ic.csv
factor_ic_summary.csv
factor_rankings.csv

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
    / "information_coefficient_report.csv"
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

if "Close" in df.columns:

    df["Forward_Return"] = (

        df.groupby("Symbol")[
            "Close"
        ]

        .shift(-1)

        / df["Close"]

        - 1
    )

elif "Last_Close" in df.columns:

    df["Forward_Return"] = (

        df.groupby("Symbol")[
            "Last_Close"
        ]

        .shift(-1)

        / df["Last_Close"]

        - 1
    )

else:

    raise ValueError(
        "Need Close or Last_Close"
    )

# =========================================================
# MONTHLY IC
# =========================================================

ic_records = []

dates = sorted(
    df["Snapshot_Date"]
    .dropna()
    .unique()
)

print(
    "\n📊 Calculating IC..."
)

for factor in factors:

    for date in dates:

        tmp = df[

            df["Snapshot_Date"]
            == date

        ][

            [
                factor,
                "Forward_Return",
            ]

        ].dropna()

        if len(tmp) < MIN_CROSS_SECTION:

            continue

        try:

            ic = spearmanr(

                tmp[factor],

                tmp[
                    "Forward_Return"
                ]

            )[0]

            ic_records.append({

                "Date":
                date,

                "Factor":
                factor,

                "IC":
                ic,
            })

        except Exception:

            continue

# =========================================================
# IC DATAFRAME
# =========================================================

ic_df = pd.DataFrame(
    ic_records
)

if ic_df.empty:

    raise ValueError(
        "No IC observations"
    )

# =========================================================
# SUMMARY
# =========================================================

summary = (

    ic_df

    .groupby("Factor")

    ["IC"]

    .agg(

        Avg_IC="mean",

        IC_Std="std",

        IC_Min="min",

        IC_Max="max",

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
# FACTOR GRADING
# =========================================================

def grade(ic):

    ic = abs(ic)

    if ic >= 0.10:
        return "Exceptional"

    if ic >= 0.07:
        return "Strong"

    if ic >= 0.05:
        return "Good"

    if ic >= 0.03:
        return "Moderate"

    if ic >= 0.01:
        return "Weak"

    return "Noise"

summary["Grade"] = (
    summary["Avg_IC"]
    .apply(grade)
)

# =========================================================
# RANKINGS
# =========================================================

rankings = (

    summary

    .sort_values(
        "Abs_IC",
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

ic_df.to_csv(

    OUTPUT_DIR
    / "factor_ic.csv",

    index=False,
)

summary.to_csv(

    OUTPUT_DIR
    / "factor_ic_summary.csv",

    index=False,
)

rankings.to_csv(

    OUTPUT_DIR
    / "factor_rankings.csv",

    index=False,
)

report = pd.DataFrame({

    "Metric": [

        "Factors_Analyzed",

        "IC_Observations",

        "Best_Factor",

        "Best_IC",

        "Run_Date",

        "Engine_Version",
    ],

    "Value": [

        len(rankings),

        len(ic_df),

        rankings.iloc[0][
            "Factor"
        ],

        rankings.iloc[0][
            "Avg_IC"
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
    "🏁 INFORMATION COEFFICIENT ENGINE COMPLETE"
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
    f"Average IC       : "
    f"{best['Avg_IC']:.4f}"
)

print(
    f"IC Grade         : "
    f"{best['Grade']}"
)

print(
    f"\nOutput Directory:\n"
    f"{OUTPUT_DIR}"
)

print("=" * 70)