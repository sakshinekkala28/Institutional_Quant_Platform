"""
=========================================================
PERFORMANCE ATTRIBUTION ENGINE
=========================================================

Purpose:
Institutional Performance Attribution

Inputs:
data/portfolios/optimized_portfolio.csv
data/factors/factor_master.csv
data/raw/prices/*.parquet

Outputs:
data/performance/performance_attribution.csv
data/performance/sector_attribution.csv
data/performance/position_attribution.csv
data/performance/factor_attribution.csv

data/logs/attribution_report.csv

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

RETURN_LOOKBACK_DAYS = 21

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

PORTFOLIO_FILE = (
    ROOT
    / "data"
    / "portfolios"
    / "optimized_portfolio.csv"
)

FACTOR_FILE = (
    ROOT
    / "data"
    / "factors"
    / "factor_master.csv"
)

PRICE_DIR = (
    ROOT
    / "data"
    / "raw"
    / "prices"
)

PERFORMANCE_FILE = (
    ROOT
    / "data"
    / "performance"
    / "performance_attribution.csv"
)

SECTOR_FILE = (
    ROOT
    / "data"
    / "performance"
    / "sector_attribution.csv"
)

POSITION_FILE = (
    ROOT
    / "data"
    / "performance"
    / "position_attribution.csv"
)

FACTOR_ATTR_FILE = (
    ROOT
    / "data"
    / "performance"
    / "factor_attribution.csv"
)

REPORT_FILE = (
    ROOT
    / "data"
    / "logs"
    / "attribution_report.csv"
)

# =========================================================
# LOAD
# =========================================================

print("\n📥 Loading Portfolio...")

portfolio = pd.read_csv(
    PORTFOLIO_FILE
)

if portfolio.empty:

    raise ValueError(
        "Portfolio is empty."
    )

factors = pd.read_csv(
    FACTOR_FILE
)

# =========================================================
# PRICE RETURNS
# =========================================================

print(
    "\n📊 Calculating Position Returns..."
)

returns_data = []

for symbol in portfolio["Symbol"]:

    try:

        file = (
            PRICE_DIR
            / f"{symbol}.parquet"
        )

        if not file.exists():
            continue

        df = pd.read_parquet(
            file
        )

        if len(df) < RETURN_LOOKBACK_DAYS:
            continue

        close = pd.to_numeric(
            df["Close"],
            errors="coerce"
        )

        latest_price = (
            close.iloc[-1]
        )

        old_price = (
            close.iloc[
                -RETURN_LOOKBACK_DAYS
            ]
        )

        period_return = (

            latest_price
            /
            old_price

            - 1
        )

        returns_data.append(
            {
                "Symbol": symbol,
                "Period_Return":
                period_return,
            }
        )

    except Exception:
        continue

returns_df = pd.DataFrame(
    returns_data
)

# =========================================================
# MERGE
# =========================================================

portfolio = portfolio.merge(
    returns_df,
    on="Symbol",
    how="left",
)

portfolio["Period_Return"] = (
    portfolio["Period_Return"]
    .fillna(0)
)

# =========================================================
# CONTRIBUTION
# =========================================================

portfolio["Contribution"] = (

    portfolio["Optimized_Weight"]

    * portfolio["Period_Return"]

)

portfolio["Contribution_Pct"] = (

    portfolio["Contribution"]

    * 100
)

# =========================================================
# PORTFOLIO RETURN
# =========================================================

portfolio_return = (

    portfolio["Contribution"]

    .sum()
)

# =========================================================
# POSITION ATTRIBUTION
# =========================================================

position_attr = portfolio[

    [

        "Symbol",

        "Sector",

        "Optimized_Weight",

        "Period_Return",

        "Contribution",

        "Contribution_Pct",
    ]
]

position_attr = (
    position_attr
    .sort_values(
        "Contribution",
        ascending=False,
    )
)

# =========================================================
# SECTOR ATTRIBUTION
# =========================================================

sector_attr = (

    portfolio

    .groupby(
        "Sector",
        dropna=False
    )

    .agg(

        Weight=(
            "Optimized_Weight",
            "sum"
        ),

        Contribution=(
            "Contribution",
            "sum"
        )
    )

    .reset_index()

)

sector_attr[
    "Contribution_Pct"
] = (

    sector_attr[
        "Contribution"
    ]

    * 100
)

sector_attr = (
    sector_attr
    .sort_values(
        "Contribution",
        ascending=False,
    )
)

# =========================================================
# FACTOR ATTRIBUTION
# =========================================================

factor_columns = [

    "Momentum_12M",
    "Momentum_6M",

    "Volatility_20D",

    "Dollar_Volume",

]

available_factors = [

    c

    for c in factor_columns

    if c in factors.columns
]

factor_attr = []

if available_factors:

    merged = portfolio.merge(

        factors[
            ["Symbol"]
            +
            available_factors
        ],

        on="Symbol",

        how="left",

        suffixes=("", "_factor")
    
    )

    for factor in available_factors:

        exposure = (

            merged[
                factor
            ]

            * merged[
                "Optimized_Weight"
            ]

        ).sum()

        factor_attr.append(

            {

                "Factor":
                factor,

                "Portfolio_Exposure":
                exposure,

                "Weighted_Mean":
                merged[factor].mean(),

                "Weighted_Exposure":
                (
                    merged[factor]
                    *
                    merged["Optimized_Weight"]
                ).sum(),
            }
        )

factor_attr = pd.DataFrame(
    factor_attr
)

# =========================================================
# TOP CONTRIBUTORS
# =========================================================

top5 = (
    position_attr
    .head(5)
)

bottom5 = (
    position_attr
    .tail(5)
)

# =========================================================
# PERFORMANCE SUMMARY
# =========================================================

summary = pd.DataFrame(

    {

        "Metric": [

            "Portfolio_Return",

            "Top_Contribution",

            "Worst_Contribution",

            "Average_Position_Return",

            "Run_Date",

            "Engine_Version",
        ],

        "Value": [

            portfolio_return,

            position_attr[
                "Contribution"
            ].max(),

            position_attr[
                "Contribution"
            ].min(),

            portfolio[
                "Period_Return"
            ].mean(),

            datetime.now()
            .strftime(
                "%Y-%m-%d"
            ),

            ENGINE_VERSION,
        ]
    }
)

# =========================================================
# SAVE
# =========================================================

PERFORMANCE_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

summary.to_csv(
    PERFORMANCE_FILE,
    index=False,
)

sector_attr.to_csv(
    SECTOR_FILE,
    index=False,
)

position_attr.to_csv(
    POSITION_FILE,
    index=False,
)

factor_attr.to_csv(
    FACTOR_ATTR_FILE,
    index=False,
)

summary.to_csv(
    REPORT_FILE,
    index=False,
)

# =========================================================
# REPORT
# =========================================================

print("\n" + "=" * 70)

print(
    "🏁 PERFORMANCE ATTRIBUTION COMPLETE"
)

print("=" * 70)

print(
    f"Portfolio Return : "
    f"{portfolio_return:.2%}"
)

print(
    f"Positions         : "
    f"{len(position_attr):,}"
)

print(
    f"Top Contributor   : "
    f"{top5.iloc[0]['Symbol']}"
)

print(
    f"Worst Contributor : "
    f"{bottom5.iloc[-1]['Symbol']}"
)

print(
    f"\nOutput Directory:\n"
    f"{PERFORMANCE_FILE.parent}"
)

print("=" * 70)