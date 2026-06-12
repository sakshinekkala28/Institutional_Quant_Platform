"""
=========================================================
FACTOR ATTRIBUTION ENGINE
=========================================================

Purpose:
Institutional Factor Performance Attribution

Inputs:
data/factors/factor_snapshot_master.csv
data/portfolios/live_portfolio.csv

Outputs:
factor_exposures.csv
factor_contributions.csv
factor_attribution_summary.csv
factor_attribution_rankings.csv

=========================================================
"""

from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd

# =========================================================
# CONFIG
# =========================================================

ENGINE_VERSION = "1.0.0"

MIN_SECURITIES = 20

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

PORTFOLIO_FILE = (
    ROOT
    / "data"
    / "portfolios"
    / "live_portfolio.csv"
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
    / "factor_attribution_report.csv"
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

portfolio = pd.read_csv(
    PORTFOLIO_FILE
)

if factors.empty:

    raise ValueError(
        "Factor snapshot file empty"
    )

if portfolio.empty:

    raise ValueError(
        "Portfolio file empty"
    )

# =========================================================
# LATEST SNAPSHOT
# =========================================================

if "Snapshot_Date" not in factors.columns:

    raise ValueError(
        "Missing Snapshot_Date"
    )

factors["Snapshot_Date"] = pd.to_datetime(
    factors["Snapshot_Date"]
)

latest_date = (
    factors["Snapshot_Date"]
    .max()
)

factors = factors[
    factors["Snapshot_Date"]
    == latest_date
].copy()

# =========================================================
# MERGE
# =========================================================

required_portfolio_cols = [
    "Symbol",
    "Weight",
]

for col in required_portfolio_cols:

    if col not in portfolio.columns:

        raise ValueError(
            f"Missing Portfolio Column: {col}"
        )

merged = portfolio.merge(
    factors,
    on="Symbol",
    how="inner"
)

if len(merged) < MIN_SECURITIES:

    raise ValueError(
        "Insufficient merged securities"
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

    "Last_Close",
]

factor_columns = [

    c

    for c in candidate_factors

    if c in merged.columns
]

if not factor_columns:

    raise ValueError(
        "No factor columns available"
    )

# =========================================================
# FORWARD RETURNS
# =========================================================

if "Last_Close" not in merged.columns:

    if "Last_Close_x" in merged.columns:

        merged["Last_Close"] = (
            merged["Last_Close_x"]
        )

    elif "Last_Close_y" in merged.columns:

        merged["Last_Close"] = (
            merged["Last_Close_y"]
        )

    else:

        raise ValueError(
            f"Last_Close missing. Columns: "
            f"{merged.columns.tolist()}"
        )
    
# Approximate next-period return
# (replace with actual realized returns
# if available later)

portfolio_return_proxy = (

    merged["Alpha_Adjusted"]

    if "Alpha_Adjusted"
    in merged.columns

    else np.ones(
        len(merged)
    )
)

# =========================================================
# EXPOSURES
# =========================================================

exposure_records = []

contribution_records = []

for factor in factor_columns:

    values = pd.to_numeric(

        merged[factor],

        errors="coerce"
    )

    values = values.fillna(
        values.median()
    )

    zscore = (

        values
        - values.mean()

    ) / max(
        values.std(),
        1e-9,
    )

    exposure = (

        zscore

        * merged[
            "Weight"
        ]

    ).sum()

    contribution = (

        exposure

        * portfolio_return_proxy.mean()
    )

    exposure_records.append({

        "Factor":
        factor,

        "Exposure":
        exposure,
    })

    contribution_records.append({

        "Factor":
        factor,

        "Contribution":
        contribution,
    })

# =========================================================
# DATAFRAMES
# =========================================================

exposures = pd.DataFrame(
    exposure_records
)

contributions = pd.DataFrame(
    contribution_records
)

summary = exposures.merge(
    contributions,
    on="Factor",
    how="inner",
)

summary["Abs_Contribution"] = (
    summary[
        "Contribution"
    ].abs()
)

# =========================================================
# NORMALIZED %
# =========================================================

total_abs = max(

    summary[
        "Abs_Contribution"
    ].sum(),

    1e-9,
)

summary[
    "Contribution_%"
] = (

    summary[
        "Abs_Contribution"
    ]

    / total_abs

    * 100
)

# =========================================================
# RANKING
# =========================================================

rankings = (

    summary

    .sort_values(
        "Contribution_%",
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
# FACTOR TYPE
# =========================================================

def classify_factor(
    factor,
):

    if "Momentum" in factor:
        return "Momentum"

    if "Volatility" in factor:
        return "Risk"

    if "Drawdown" in factor:
        return "Risk"

    if "ADV" in factor:
        return "Liquidity"

    if "Volume" in factor:
        return "Liquidity"

    if "Cap" in factor:
        return "Size"

    return "Technical"

rankings[
    "Factor_Group"
] = rankings[
    "Factor"
].apply(
    classify_factor
)

# =========================================================
# SAVE
# =========================================================

exposures.to_csv(

    OUTPUT_DIR
    / "factor_exposures.csv",

    index=False,
)

contributions.to_csv(

    OUTPUT_DIR
    / "factor_contributions.csv",

    index=False,
)

summary.to_csv(

    OUTPUT_DIR
    / "factor_attribution_summary.csv",

    index=False,
)

rankings.to_csv(

    OUTPUT_DIR
    / "factor_attribution_rankings.csv",

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

        "Top_Contribution_%",

        "Run_Date",

        "Engine_Version",
    ],

    "Value": [

        len(rankings),

        best["Factor"],

        best[
            "Contribution_%"
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
    "🏁 FACTOR ATTRIBUTION ENGINE COMPLETE"
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
    f"Contribution     : "
    f"{best['Contribution_%']:.2f}%"
)

print(
    f"\nOutput Directory:\n"
    f"{OUTPUT_DIR}"
)

print("=" * 70)