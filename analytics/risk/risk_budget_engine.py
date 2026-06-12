"""
=========================================================
RISK BUDGET ENGINE
=========================================================

Purpose:
Institutional Portfolio Risk Budget Analytics

Outputs:
risk_budget.csv
position_risk_contribution.csv
risk_breaches.csv
risk_budget_dashboard.csv

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

MAX_POSITION_RISK = 0.10
MAX_SECTOR_RISK = 0.30

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

PORTFOLIO_FILE = (
    ROOT
    / "data"
    / "portfolios"
    / "live_portfolio.csv"
)

FACTOR_FILE = (
    ROOT
    / "data"
    / "factors"
    / "factor_snapshot_master.csv"
)

OUTPUT_DIR = (
    ROOT
    / "data"
    / "risk"
)

REPORT_FILE = (
    ROOT
    / "data"
    / "logs"
    / "risk_budget_report.csv"
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

portfolio = pd.read_csv(
    PORTFOLIO_FILE
)

factors = pd.read_csv(
    FACTOR_FILE
)

# =========================================================
# LATEST SNAPSHOT
# =========================================================

if "Snapshot_Date" in factors.columns:

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

merged = portfolio.merge(

    factors[[
        "Symbol",
        "Industry",
        "Volatility_20D",
        "Volatility_60D",
        "ATR_14",
        "Max_Drawdown_252D",
    ]],

    on="Symbol",

    how="left",
)

# =========================================================
# CLEAN
# =========================================================

risk_cols = [

    "Volatility_20D",
    "Volatility_60D",
    "ATR_14",
    "Max_Drawdown_252D",
]

for col in risk_cols:

    merged[col] = pd.to_numeric(
        merged[col],
        errors="coerce"
    )

    merged[col] = merged[col].fillna(
        merged[col].median()
    )

# =========================================================
# COMPOSITE RISK SCORE
# =========================================================

merged["Risk_Score"] = (

      0.40
    * merged["Volatility_60D"]

    + 0.30
    * merged["Volatility_20D"]

    + 0.20
    * merged["ATR_14"]

    + 0.10
    * merged["Max_Drawdown_252D"].abs()
)

# =========================================================
# POSITION RISK CONTRIBUTION
# =========================================================

merged["Risk_Contribution"] = (

    merged["Weight"]

    * merged["Risk_Score"]
)

total_risk = max(
    merged[
        "Risk_Contribution"
    ].sum(),
    1e-9,
)

merged["Risk_Budget_%"] = (

    merged[
        "Risk_Contribution"
    ]

    / total_risk
)

# =========================================================
# POSITION RISK REPORT
# =========================================================

position_risk = (

    merged[[
        "Symbol",
        "Weight",
        "Risk_Score",
        "Risk_Contribution",
        "Risk_Budget_%",
    ]]

    .sort_values(
        "Risk_Budget_%",
        ascending=False
    )

    .reset_index(
        drop=True
    )
)

# =========================================================
# SECTOR RISK
# =========================================================

sector_risk = (

    merged

    .groupby("Sector")

    ["Risk_Budget_%"]

    .sum()

    .reset_index()

    .sort_values(
        "Risk_Budget_%",
        ascending=False,
    )
)

# =========================================================
# RISK BREACHES
# =========================================================

breaches = []

for _, row in position_risk.iterrows():

    if row["Risk_Budget_%"] > MAX_POSITION_RISK:

        breaches.append({

            "Type":
            "Position",

            "Name":
            row["Symbol"],

            "Value":
            row["Risk_Budget_%"],

            "Limit":
            MAX_POSITION_RISK,
        })

for _, row in sector_risk.iterrows():

    if row["Risk_Budget_%"] > MAX_SECTOR_RISK:

        breaches.append({

            "Type":
            "Sector",

            "Name":
            row["Sector"],

            "Value":
            row["Risk_Budget_%"],

            "Limit":
            MAX_SECTOR_RISK,
        })

risk_breaches = pd.DataFrame(
    breaches
)

# =========================================================
# HHI
# =========================================================

risk_hhi = (

    merged[
        "Risk_Budget_%"
    ] ** 2

).sum()

top5_risk = (

    position_risk

    .head(5)

    ["Risk_Budget_%"]

    .sum()
)

top10_risk = (

    position_risk

    .head(10)

    ["Risk_Budget_%"]

    .sum()
)

# =========================================================
# DASHBOARD
# =========================================================

largest = position_risk.iloc[0]

dashboard = pd.DataFrame({

    "Metric": [

        "Holdings",

        "Largest_Risk_Position",

        "Largest_Risk_%",

        "Top5_Risk_%",

        "Top10_Risk_%",

        "Risk_HHI",

        "Risk_Breaches",
    ],

    "Value": [

        len(position_risk),

        largest["Symbol"],

        round(
            largest[
                "Risk_Budget_%"
            ] * 100,
            2,
        ),

        round(
            top5_risk * 100,
            2,
        ),

        round(
            top10_risk * 100,
            2,
        ),

        round(
            risk_hhi,
            4,
        ),

        len(
            risk_breaches
        ),
    ]
})

# =========================================================
# SAVE
# =========================================================

position_risk.to_csv(
    OUTPUT_DIR
    / "position_risk_contribution.csv",
    index=False,
)

sector_risk.to_csv(
    OUTPUT_DIR
    / "risk_budget.csv",
    index=False,
)

risk_breaches.to_csv(
    OUTPUT_DIR
    / "risk_breaches.csv",
    index=False,
)

dashboard.to_csv(
    OUTPUT_DIR
    / "risk_budget_dashboard.csv",
    index=False,
)

dashboard.to_csv(
    REPORT_FILE,
    index=False,
)

# =========================================================
# REPORT
# =========================================================

print("\n" + "=" * 70)

print(
    "🏁 RISK BUDGET ENGINE COMPLETE"
)

print("=" * 70)

print(
    f"Holdings           : "
    f"{len(position_risk)}"
)

print(
    f"Largest Risk Name  : "
    f"{largest['Symbol']}"
)

print(
    f"Largest Risk %     : "
    f"{largest['Risk_Budget_%']:.2%}"
)

print(
    f"Top 5 Risk %       : "
    f"{top5_risk:.2%}"
)

print(
    f"Top 10 Risk %      : "
    f"{top10_risk:.2%}"
)

print(
    f"Risk HHI           : "
    f"{risk_hhi:.4f}"
)

print(
    f"Breaches           : "
    f"{len(risk_breaches)}"
)

print(
    f"\nOutput Directory:\n"
    f"{OUTPUT_DIR}"
)

print("=" * 70)