"""
=========================================================
EXPOSURE ENGINE
=========================================================

Purpose:
Institutional Portfolio Exposure Analytics

Outputs:
sector_exposure.csv
industry_exposure.csv
factor_exposure.csv
concentration_report.csv
exposure_dashboard.csv

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

SECURITY_FILE = (
    ROOT
    / "data"
    / "raw"
    / "security_master.csv"
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
    / "exposure_report.csv"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

# =========================================================
# LOAD
# =========================================================

print(
    "\n📥 Loading Portfolio..."
)

portfolio = pd.read_csv(
    PORTFOLIO_FILE
)

security = pd.read_csv(
    SECURITY_FILE
)

factors = pd.read_csv(
    FACTOR_FILE
)

# =========================================================
# VALIDATION
# =========================================================

for col in [
    "Symbol",
    "Weight",
]:

    if col not in portfolio.columns:

        raise ValueError(
            f"Missing Portfolio Column: {col}"
        )

# =========================================================
# LATEST FACTOR SNAPSHOT
# =========================================================

if "Snapshot_Date" in factors.columns:

    factors["Snapshot_Date"] = pd.to_datetime(
        factors["Snapshot_Date"]
    )

    latest = (
        factors["Snapshot_Date"]
        .max()
    )

    factors = factors[
        factors["Snapshot_Date"]
        == latest
    ].copy()

# =========================================================
# MERGE
# =========================================================

merged = (

    portfolio

    .merge(
        security,
        on="Symbol",
        how="left",
    )

    .merge(
        factors,
        on="Symbol",
        how="left",
    )
)

# =========================================================
# SECTOR EXPOSURE
# =========================================================

sector = (

    merged

    .groupby("Sector")

    ["Weight"]

    .sum()

    .reset_index()

    .sort_values(
        "Weight",
        ascending=False,
    )
)

# =========================================================
# INDUSTRY EXPOSURE
# =========================================================

industry_col = None

for col in [

    "Industry",

    "Sub_Industry",

    "Industry_Name",

    "Business_Group",
]:

    if col in merged.columns:

        industry_col = col

        break

if industry_col:

    industry = (

        merged

        .groupby(industry_col)

        ["Weight"]

        .sum()

        .reset_index()

        .sort_values(
            "Weight",
            ascending=False,
        )
    )

else:

    print(
        "\n⚠️ Industry column not available"
    )

    industry = pd.DataFrame({
        "Category": ["N/A"],
        "Weight": [1.0]
    })
    
# =========================================================
# FACTOR EXPOSURE
# =========================================================

candidate_factors = [

    "Momentum_12M",

    "Momentum_6M",

    "Volatility_60D",

    "Market_Cap",

    "ADV_20D",

    "Distance_SMA200",
]

factor_records = []

for factor in candidate_factors:

    if factor not in merged.columns:
        continue

    values = pd.to_numeric(
        merged[factor],
        errors="coerce"
    )

    exposure = (

        values.fillna(
            values.median()
        )

        * merged["Weight"]

    ).sum()

    factor_records.append({

        "Factor":
        factor,

        "Exposure":
        exposure,
    })

factor_exposure = pd.DataFrame(
    factor_records
)

# =========================================================
# CONCENTRATION
# =========================================================

weights = merged[
    "Weight"
].fillna(0)

top10 = (

    weights

    .nlargest(10)

    .sum()
)

hhi = (
    (weights ** 2)
    .sum()
)

concentration = pd.DataFrame({

    "Metric": [

        "Top10_Weight",

        "HHI",

        "Number_of_Holdings",
    ],

    "Value": [

        top10,

        hhi,

        len(merged),
    ]
})

# =========================================================
# DASHBOARD
# =========================================================

dashboard = pd.DataFrame({

    "Metric": [

        "Holdings",

        "Largest_Sector",

        "Largest_Sector_Weight",

        "Top10_Weight",

        "HHI",
    ],

    "Value": [

        len(merged),

        sector.iloc[0]["Sector"],

        sector.iloc[0]["Weight"],

        top10,

        hhi,
    ]
})

# =========================================================
# SAVE
# =========================================================

sector.to_csv(
    OUTPUT_DIR
    / "sector_exposure.csv",
    index=False,
)

industry.to_csv(
    OUTPUT_DIR
    / "industry_exposure.csv",
    index=False,
)

factor_exposure.to_csv(
    OUTPUT_DIR
    / "factor_exposure.csv",
    index=False,
)

concentration.to_csv(
    OUTPUT_DIR
    / "concentration_report.csv",
    index=False,
)

dashboard.to_csv(
    OUTPUT_DIR
    / "exposure_dashboard.csv",
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
    "🏁 EXPOSURE ENGINE COMPLETE"
)

print("=" * 70)

print(
    f"Holdings : {len(merged)}"
)

print(
    f"Largest Sector : "
    f"{sector.iloc[0]['Sector']}"
)

print(
    f"Top10 Weight : "
    f"{top10:.2%}"
)

print(
    f"HHI : "
    f"{hhi:.4f}"
)

print(
    f"\nOutput Directory:\n"
    f"{OUTPUT_DIR}"
)

print("=" * 70)