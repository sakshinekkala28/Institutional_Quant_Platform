"""
=========================================================
PORTFOLIO ENGINE
=========================================================

Purpose:
Generate institutional investable portfolio
from ranked alpha factors.

Input:
data/factors/factor_rank_master.csv

Outputs:
data/portfolios/live_portfolio.csv
data/portfolios/portfolio_summary.csv
data/logs/portfolio_report.csv

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

TARGET_PORTFOLIO_SIZE = 50

MIN_ADV = 5e7              # ₹5 Crore

MAX_POSITION_WEIGHT = 0.05

MAX_SECTOR_WEIGHT = 0.25

MIN_ALPHA_SCORE = 0.60

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    ROOT
    / "data"
    / "factors"
    / "factor_rank_master.csv"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "portfolios"
    / "live_portfolio.csv"
)

SUMMARY_FILE = (
    ROOT
    / "data"
    / "portfolios"
    / "portfolio_summary.csv"
)

REPORT_FILE = (
    ROOT
    / "data"
    / "logs"
    / "portfolio_report.csv"
)

# =========================================================
# LOAD
# =========================================================

print("\n📥 Loading Ranked Universe...")

df = pd.read_csv(INPUT_FILE)

if df.empty:

    raise ValueError(
        "factor_rank_master.csv is empty"
    )

# =========================================================
# VALIDATION
# =========================================================

required_columns = [

    "Security_ID",
    "Symbol",
    "Company_Name",
    "Sector",

    "Alpha_Adjusted",
    "Rank",

    "ADV_20D",
    "Market_Cap",

    "Last_Close",

    "Log_Market_Cap_Rank",
    "ADV_20D_Rank",
]

missing = [

    c

    for c in required_columns

    if c not in df.columns
]

if missing:

    raise ValueError(
        f"Missing Columns: {missing}"
    )

# =========================================================
# INVESTABILITY FILTERS
# =========================================================

portfolio = df.copy()

portfolio = portfolio[
    portfolio["ADV_20D"]
    >= MIN_ADV
]

portfolio = portfolio[
    portfolio["Alpha_Adjusted"]
    >= MIN_ALPHA_SCORE
]

portfolio = portfolio.sort_values(
    "Alpha_Adjusted",
    ascending=False,
)

portfolio = portfolio.head(
    TARGET_PORTFOLIO_SIZE
)

if portfolio.empty:

    raise ValueError(
        "No investable securities remain."
    )

# =========================================================
# RAW WEIGHTS
# =========================================================

portfolio["Raw_Weight"] = (

    portfolio["Alpha_Adjusted"]

    * portfolio["ADV_20D_Rank"]

    * portfolio["Log_Market_Cap_Rank"]

)

portfolio["Weight"] = (

    portfolio["Raw_Weight"]

    / portfolio["Raw_Weight"].sum()

)

# =========================================================
# POSITION CAP
# =========================================================

portfolio["Weight"] = np.minimum(

    portfolio["Weight"],

    MAX_POSITION_WEIGHT

)

portfolio["Weight"] = (

    portfolio["Weight"]

    / portfolio["Weight"].sum()

)

# =========================================================
# SECTOR CAP
# =========================================================

sector_weights = (

    portfolio

    .groupby("Sector")

    ["Weight"]

    .sum()

)

for sector, weight in sector_weights.items():

    if weight <= MAX_SECTOR_WEIGHT:
        continue

    scale_factor = (

        MAX_SECTOR_WEIGHT

        / weight
    )

    mask = (

        portfolio["Sector"]
        == sector
    )

    portfolio.loc[
        mask,
        "Weight"
    ] *= scale_factor

portfolio["Weight"] = (

    portfolio["Weight"]

    / portfolio["Weight"].sum()

)

# =========================================================
# FINAL SORT
# =========================================================

portfolio = portfolio.sort_values(
    "Weight",
    ascending=False,
).reset_index(
    drop=True
)

portfolio["Portfolio_Date"] = (
    datetime.now()
    .strftime("%Y-%m-%d")
)

portfolio["Engine_Version"] = (
    ENGINE_VERSION
)

# =========================================================
# OUTPUT COLUMNS
# =========================================================

portfolio = portfolio[

    [

        "Security_ID",

        "Symbol",

        "Company_Name",

        "Sector",

        "Rank",

        "Alpha_Adjusted",

        "Weight",

        "Last_Close",

        "Market_Cap",

        "ADV_20D",

        "Portfolio_Date",

        "Engine_Version",
    ]
]

# =========================================================
# SAVE PORTFOLIO
# =========================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

portfolio.to_csv(
    OUTPUT_FILE,
    index=False,
)

# =========================================================
# PORTFOLIO SUMMARY
# =========================================================

largest_sector = (

    portfolio

    .groupby("Sector")

    ["Weight"]

    .sum()

    .idxmax()
)

summary = pd.DataFrame(

    {

        "Metric": [

            "Total_Positions",

            "Top_Weight",

            "Average_Weight",

            "Largest_Sector",

            "Portfolio_MarketCap",

            "Portfolio_ADV",

            "Average_Alpha",

            "Run_Date",
        ],

        "Value": [

            len(portfolio),

            portfolio[
                "Weight"
            ].max(),

            portfolio[
                "Weight"
            ].mean(),

            largest_sector,

            portfolio[
                "Market_Cap"
            ].mean(),

            portfolio[
                "ADV_20D"
            ].mean(),

            portfolio[
                "Alpha_Adjusted"
            ].mean(),

            datetime.now()
            .strftime("%Y-%m-%d"),
        ],
    }
)

SUMMARY_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

summary.to_csv(
    SUMMARY_FILE,
    index=False,
)

# =========================================================
# PORTFOLIO REPORT
# =========================================================

report = pd.DataFrame(

    {

        "Metric": [

            "Universe_Input",

            "Portfolio_Size",

            "Average_Alpha",

            "Average_ADV",

            "Engine_Version",
        ],

        "Value": [

            len(df),

            len(portfolio),

            portfolio[
                "Alpha_Adjusted"
            ].mean(),

            portfolio[
                "ADV_20D"
            ].mean(),

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
    "🏁 PORTFOLIO ENGINE COMPLETE"
)

print("=" * 70)

print(
    f"Portfolio Size : "
    f"{len(portfolio):,}"
)

print(
    f"Top Weight     : "
    f"{portfolio['Weight'].max():.2%}"
)

print(
    f"Average Alpha  : "
    f"{portfolio['Alpha_Adjusted'].mean():.4f}"
)

print(
    f"\nPortfolio:\n"
    f"{OUTPUT_FILE}"
)

print("=" * 70)