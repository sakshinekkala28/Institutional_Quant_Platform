"""
=========================================================
RISK ENGINE
=========================================================

Purpose:
Institutional Portfolio Risk Analytics

Inputs:
data/portfolios/live_portfolio.csv
data/factors/factor_rank_master.csv

Outputs:
data/risk/risk_report.csv
data/risk/sector_risk.csv
data/risk/liquidity_risk.csv
data/risk/concentration_risk.csv
data/risk/factor_exposure.csv

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

PORTFOLIO_NAV = 100_000_000

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
    / "factor_rank_master.csv"
)

RISK_DIR = (
    ROOT
    / "data"
    / "risk"
)

RISK_REPORT = (
    RISK_DIR
    / "risk_report.csv"
)

SECTOR_REPORT = (
    RISK_DIR
    / "sector_risk.csv"
)

LIQUIDITY_REPORT = (
    RISK_DIR
    / "liquidity_risk.csv"
)

CONCENTRATION_REPORT = (
    RISK_DIR
    / "concentration_risk.csv"
)

FACTOR_REPORT = (
    RISK_DIR
    / "factor_exposure.csv"
)

# =========================================================
# LOAD DATA
# =========================================================

print("\n📥 Loading Portfolio...")

portfolio = pd.read_csv(
    PORTFOLIO_FILE
)

factors = pd.read_csv(
    FACTOR_FILE
)

if portfolio.empty:

    raise ValueError(
        "Portfolio is empty"
    )

# =========================================================
# ENRICH
# =========================================================

factor_columns = [

    "Symbol",

    "Momentum_12M_Rank",

    "Momentum_6M_Rank",

    "Volatility_20D_Rank",

    "ADV_20D_Rank",

]

portfolio = portfolio.merge(

    factors[
        factor_columns
    ],

    on="Symbol",

    how="left",
)

# =========================================================
# CONCENTRATION RISK
# =========================================================

portfolio["Weight_Squared"] = (
    portfolio["Weight"] ** 2
)

hhi = (
    portfolio["Weight_Squared"]
    .sum()
)

top5_weight = (
    portfolio
    .nlargest(
        5,
        "Weight"
    )
    ["Weight"]
    .sum()
)

top10_weight = (
    portfolio
    .nlargest(
        10,
        "Weight"
    )
    ["Weight"]
    .sum()
)

concentration = portfolio[
    [

        "Security_ID",

        "Symbol",

        "Company_Name",

        "Weight",

        "Alpha_Adjusted",

        "Market_Cap",

        "ADV_20D",
    ]
]

# =========================================================
# SECTOR RISK
# =========================================================

sector_risk = (

    portfolio

    .groupby("Sector")

    .agg(

        Positions=(
            "Symbol",
            "count"
        ),

        Weight=(
            "Weight",
            "sum"
        ),

        Avg_Alpha=(
            "Alpha_Adjusted",
            "mean"
        ),
    )

    .reset_index()

    .sort_values(
        "Weight",
        ascending=False,
    )
)

# =========================================================
# LIQUIDITY RISK
# =========================================================

liquidity = portfolio.copy()

liquidity["Position_Value"] = (

    liquidity["Weight"]

    * PORTFOLIO_NAV
)

liquidity["Days_To_Liquidate"] = (

    liquidity["Position_Value"]

    / liquidity["ADV_20D"]
)

liquidity_risk = liquidity[

    [

        "Symbol",

        "Company_Name",

        "Weight",

        "ADV_20D",

        "Position_Value",

        "Days_To_Liquidate",
    ]
]

# =========================================================
# MARKET CAP EXPOSURE
# =========================================================

market_cap_exposure = pd.DataFrame(

    {

        "Bucket": [

            "Large_Cap",

            "Mid_Cap",

            "Small_Cap",
        ],

        "Weight": [

            portfolio.loc[
                portfolio["Market_Cap"]
                >= 200_000_000_000,
                "Weight",
            ].sum(),

            portfolio.loc[
                (
                    portfolio["Market_Cap"]
                    >= 50_000_000_000
                )
                &
                (
                    portfolio["Market_Cap"]
                    < 200_000_000_000
                ),
                "Weight",
            ].sum(),

            portfolio.loc[
                portfolio["Market_Cap"]
                < 50_000_000_000,
                "Weight",
            ].sum(),
        ],
    }
)

# =========================================================
# FACTOR EXPOSURE
# =========================================================

factor_exposure = pd.DataFrame(

    {

        "Factor": [

            "Momentum_12M",

            "Momentum_6M",

            "Volatility_20D",

            "Liquidity",
        ],

        "Exposure": [

            (
                portfolio[
                    "Momentum_12M_Rank"
                ]
                * portfolio[
                    "Weight"
                ]
            ).sum(),

            (
                portfolio[
                    "Momentum_6M_Rank"
                ]
                * portfolio[
                    "Weight"
                ]
            ).sum(),

            (
                portfolio[
                    "Volatility_20D_Rank"
                ]
                * portfolio[
                    "Weight"
                ]
            ).sum(),

            (
                portfolio[
                    "ADV_20D_Rank"
                ]
                * portfolio[
                    "Weight"
                ]
            ).sum(),
        ],
    }
)

# =========================================================
# OVERALL RISK REPORT
# =========================================================

effective_positions = (

    1

    / max(
        hhi,
        1e-9
    )
)

largest_sector = (

    sector_risk

    .iloc[0]

    ["Sector"]
)

largest_sector_weight = (

    sector_risk

    .iloc[0]

    ["Weight"]
)

risk_report = pd.DataFrame(

    {

        "Metric": [

            "Portfolio_Size",

            "Top5_Weight",

            "Top10_Weight",

            "HHI",

            "Effective_Positions",

            "Largest_Sector",

            "Largest_Sector_Weight",

            "Average_Days_To_Liquidate",

            "Maximum_Days_To_Liquidate",

            "Run_Date",

            "Engine_Version",
        ],

        "Value": [

            len(portfolio),

            top5_weight,

            top10_weight,

            hhi,

            effective_positions,

            largest_sector,

            largest_sector_weight,

            liquidity_risk[
                "Days_To_Liquidate"
            ].mean(),

            liquidity_risk[
                "Days_To_Liquidate"
            ].max(),

            datetime.now()
            .strftime(
                "%Y-%m-%d"
            ),

            ENGINE_VERSION,
        ],
    }
)

# =========================================================
# SAVE
# =========================================================

RISK_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

risk_report.to_csv(
    RISK_REPORT,
    index=False,
)

sector_risk.to_csv(
    SECTOR_REPORT,
    index=False,
)

liquidity_risk.to_csv(
    LIQUIDITY_REPORT,
    index=False,
)

concentration.to_csv(
    CONCENTRATION_REPORT,
    index=False,
)

factor_exposure.to_csv(
    FACTOR_REPORT,
    index=False,
)

market_cap_exposure.to_csv(
    RISK_DIR
    / "market_cap_exposure.csv",
    index=False,
)

# =========================================================
# REPORT
# =========================================================

print("\n" + "=" * 70)

print(
    "🏁 RISK ENGINE COMPLETE"
)

print("=" * 70)

print(
    f"Portfolio Size        : {len(portfolio):,}"
)

print(
    f"Top 5 Weight          : {top5_weight:.2%}"
)

print(
    f"Top 10 Weight         : {top10_weight:.2%}"
)

print(
    f"HHI                   : {hhi:.4f}"
)

print(
    f"Effective Positions   : "
    f"{effective_positions:.2f}"
)

print(
    f"Largest Sector        : "
    f"{largest_sector}"
)

print(
    f"Largest Sector Weight : "
    f"{largest_sector_weight:.2%}"
)

print("=" * 70)