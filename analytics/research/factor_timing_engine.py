"""
=========================================================
FACTOR TIMING ENGINE
=========================================================

Purpose:
Institutional Factor Regime Analysis

Measures:
Factor IC conditioned on Market Regime

Inputs:
data/factors/factor_snapshot_master.csv
data/regime/market_regime.csv

Outputs:
factor_timing.csv
factor_timing_summary.csv
factor_regime_rankings.csv
factor_timing_heatmap.csv

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

MIN_OBSERVATIONS = 30

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

REGIME_FILE = (
    ROOT
    / "data"
    / "regime"
    / "market_regime.csv"
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
    / "factor_timing_report.csv"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

# =========================================================
# LOAD
# =========================================================

print(
    "\n📥 Loading Data..."
)

factors = pd.read_csv(
    FACTOR_FILE
)

regimes = pd.read_csv(
    REGIME_FILE
)

if factors.empty:
    raise ValueError(
        "Factor snapshot file empty"
    )

if regimes.empty:
    raise ValueError(
        "Regime file empty"
    )

# =========================================================
# DATE HANDLING
# =========================================================

factors["Snapshot_Date"] = pd.to_datetime(
    factors["Snapshot_Date"]
)

regimes["Date"] = pd.to_datetime(
    regimes["Date"]
)

regimes = regimes.rename(
    columns={
        "Date":
        "Snapshot_Date"
    }
)

# =========================================================
# FORWARD RETURNS
# =========================================================

if "Last_Close" not in factors.columns:

    raise ValueError(
        "Last_Close required"
    )

factors = factors.sort_values(
    [
        "Symbol",
        "Snapshot_Date",
    ]
)

factors["Forward_Return"] = (

    factors

    .groupby("Symbol")

    ["Last_Close"]

    .shift(-1)

    / factors["Last_Close"]

    - 1
)

# =========================================================
# MERGE REGIMES
# =========================================================

merged = pd.merge_asof(

    factors.sort_values(
        "Snapshot_Date"
    ),

    regimes.sort_values(
        "Snapshot_Date"
    ),

    on="Snapshot_Date",

    direction="backward"
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

factor_columns = [

    f

    for f in candidate_factors

    if f in merged.columns
]

# =========================================================
# TIMING ANALYSIS
# =========================================================

print(
    "\n📊 Calculating Regime IC..."
)

records = []

for factor in factor_columns:

    for regime in sorted(
        merged["Regime"]
        .dropna()
        .unique()
    ):

        tmp = merged[

            merged["Regime"]
            == regime

        ][

            [
                factor,
                "Forward_Return",
            ]

        ].dropna()

        if len(tmp) < MIN_OBSERVATIONS:
            continue

        try:

            ic = spearmanr(

                tmp[factor],

                tmp[
                    "Forward_Return"
                ]

            )[0]

            records.append({

                "Factor":
                factor,

                "Regime":
                regime,

                "IC":
                ic,

                "Observations":
                len(tmp),
            })

        except Exception:

            continue


print(
    "\nUnique Snapshot Dates:",
    merged["Snapshot_Date"]
    .nunique()
)

print(
    "\nForward Return Count:",
    merged["Forward_Return"]
    .notna()
    .sum()
)

print(
    "\nRegime Counts:"
)

print(
    merged["Regime"]
    .value_counts()
)

# =========================================================
# DATAFRAME
# =========================================================

timing = pd.DataFrame(
    records
)

if timing.empty:

    raise ValueError(
        "No timing observations"
    )

# =========================================================
# HEATMAP TABLE
# =========================================================

heatmap = (

    timing

    .pivot_table(

        index="Factor",

        columns="Regime",

        values="IC",
    )

    .reset_index()
)

# =========================================================
# SUMMARY
# =========================================================

summary = (

    timing

    .groupby("Factor")

    .agg({

        "IC": [
            "mean",
            "std",
            "max",
            "min",
        ]
    })
)

summary.columns = [

    "Avg_IC",
    "IC_Std",
    "Best_IC",
    "Worst_IC",
]

summary = (
    summary
    .reset_index()
)

summary["Timing_Score"] = (

    summary["Best_IC"]

    - summary["Worst_IC"]
)

# =========================================================
# REGIME WINNER
# =========================================================

best_regime = (

    timing

    .sort_values(
        "IC",
        ascending=False,
    )

    .groupby("Factor")

    .first()

    .reset_index()
)

best_regime = best_regime[

    [
        "Factor",
        "Regime",
        "IC",
    ]

].rename(
    columns={
        "Regime":
        "Best_Regime",

        "IC":
        "Best_Regime_IC",
    }
)

summary = summary.merge(
    best_regime,
    on="Factor",
    how="left",
)

# =========================================================
# RANKINGS
# =========================================================

rankings = (

    summary

    .sort_values(
        "Best_Regime_IC",
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

timing.to_csv(

    OUTPUT_DIR
    / "factor_timing.csv",

    index=False,
)

summary.to_csv(

    OUTPUT_DIR
    / "factor_timing_summary.csv",

    index=False,
)

rankings.to_csv(

    OUTPUT_DIR
    / "factor_regime_rankings.csv",

    index=False,
)

heatmap.to_csv(

    OUTPUT_DIR
    / "factor_timing_heatmap.csv",

    index=False,
)

# =========================================================
# REPORT
# =========================================================

best = rankings.iloc[0]

report = pd.DataFrame({

    "Metric": [

        "Factors_Analyzed",

        "Top_Factor",

        "Best_Regime",

        "Best_Regime_IC",

        "Run_Date",

        "Engine_Version",
    ],

    "Value": [

        len(rankings),

        best["Factor"],

        best["Best_Regime"],

        best[
            "Best_Regime_IC"
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

print("\n" + "=" * 70)

print(
    "🏁 FACTOR TIMING ENGINE COMPLETE"
)

print("=" * 70)

print(
    f"Factors Analyzed : "
    f"{len(rankings)}"
)

print(
    f"Top Factor       : "
    f"{best['Factor']}"
)

print(
    f"Best Regime      : "
    f"{best['Best_Regime']}"
)

print(
    f"Regime IC        : "
    f"{best['Best_Regime_IC']:.4f}"
)

print(
    f"\nOutput Directory:\n"
    f"{OUTPUT_DIR}"
)

print("=" * 70)