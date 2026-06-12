"""
=========================================================
TRANSACTION COST ENGINE
=========================================================

Purpose:
Institutional Transaction Cost Modeling

Inputs:
data/portfolios/live_portfolio.csv
data/liquidity/liquidity_master.csv

Outputs:
data/execution/transaction_costs.csv
data/execution/portfolio_cost_summary.csv

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

PORTFOLIO_NAV = 10_000_000

# ---------------------------------------------------------
# INDIA EQUITY COSTS
# ---------------------------------------------------------

BROKERAGE_BPS = 2.0

STT_BPS = 10.0

EXCHANGE_BPS = 0.35

SEBI_BPS = 0.01

GST_RATE = 0.18

STAMP_DUTY_BPS = 3.0

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

LIQUIDITY_FILE = (
    ROOT
    / "data"
    / "liquidity"
    / "liquidity_master.csv"
)

OUTPUT_DIR = (
    ROOT
    / "data"
    / "execution"
)

REPORT_FILE = (
    ROOT
    / "data"
    / "logs"
    / "transaction_cost_report.csv"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

# =========================================================
# LOAD DATA
# =========================================================

print(
    "\n📥 Loading Portfolio..."
)

portfolio = pd.read_csv(
    PORTFOLIO_FILE
)

liquidity = pd.read_csv(
    LIQUIDITY_FILE
)

# =========================================================
# VALIDATION
# =========================================================

required_portfolio = [

    "Symbol",
    "Weight",
]

required_liquidity = [

    "Symbol",
    "ADV_20D",
]

if "ADV_20D" not in liquidity.columns:

    if "ADV" in liquidity.columns:

        liquidity["ADV_20D"] = (
            liquidity["ADV"]
        )

    elif "Dollar_Volume" in liquidity.columns:

        liquidity["ADV_20D"] = (
            liquidity["Dollar_Volume"]
        )

    else:

        raise ValueError(
            "ADV_20D not found in liquidity file"
        )
    
for col in required_portfolio:

    if col not in portfolio.columns:

        raise ValueError(
            f"Missing Portfolio Column: {col}"
        )

for col in required_liquidity:

    if col not in liquidity.columns:

        raise ValueError(
            f"Missing Liquidity Column: {col}"
        )

# =========================================================
# MERGE
# =========================================================

df = portfolio.copy()

# =========================================================
# TRADE VALUE
# =========================================================

df["Trade_Value"] = (

    df["Weight"]

    * PORTFOLIO_NAV

)

# =========================================================
# BASE COSTS
# =========================================================

df["Brokerage_BPS"] = (
    BROKERAGE_BPS
)

df["STT_BPS"] = (
    STT_BPS
)

df["Exchange_BPS"] = (
    EXCHANGE_BPS
)

df["SEBI_BPS"] = (
    SEBI_BPS
)

df["Stamp_Duty_BPS"] = (
    STAMP_DUTY_BPS
)

# =========================================================
# GST
# =========================================================

df["GST_BPS"] = (

    (
        BROKERAGE_BPS
        +
        EXCHANGE_BPS
    )

    * GST_RATE
)

# =========================================================
# SLIPPAGE MODEL
# =========================================================

df["ADV_20D"] = pd.to_numeric(
    df["ADV_20D"],
    errors="coerce"
)

df["ADV_20D"] = (
    df["ADV_20D"]
    .fillna(1)
)

participation = (

    df["Trade_Value"]

    / df["ADV_20D"]

)

df["Slippage_BPS"] = (

    5

    + 50

    * participation

)

# =========================================================
# MARKET IMPACT
# =========================================================

df["Impact_BPS"] = (

    15

    * np.sqrt(

        np.maximum(
            participation,
            0,
        )

    )

)

# =========================================================
# TOTAL COST
# =========================================================

df["Total_Cost_BPS"] = (

      df["Brokerage_BPS"]

    + df["STT_BPS"]

    + df["Exchange_BPS"]

    + df["SEBI_BPS"]

    + df["GST_BPS"]

    + df["Stamp_Duty_BPS"]

    + df["Slippage_BPS"]

    + df["Impact_BPS"]

)

# =========================================================
# COST VALUE
# =========================================================

df["Cost_Value"] = (

    df["Trade_Value"]

    * df["Total_Cost_BPS"]

    / 10000

)

# =========================================================
# EXECUTION QUALITY
# =========================================================

conditions = [

    participation <= 0.02,

    participation <= 0.05,

    participation <= 0.10,
]

choices = [

    "EXCELLENT",

    "GOOD",

    "ACCEPTABLE",
]

df["Execution_Quality"] = np.select(

    conditions,

    choices,

    default="POOR",
)

# =========================================================
# SUMMARY
# =========================================================

total_trade_value = (
    df["Trade_Value"]
    .sum()
)

total_cost = (
    df["Cost_Value"]
    .sum()
)

avg_cost_bps = (

    df["Total_Cost_BPS"]

    .mean()
)

summary = pd.DataFrame({

    "Metric": [

        "Portfolio_NAV",

        "Trade_Value",

        "Transaction_Cost",

        "Average_Cost_BPS",

        "Cost_Pct_NAV",

        "Run_Date",

        "Engine_Version",
    ],

    "Value": [

        PORTFOLIO_NAV,

        total_trade_value,

        total_cost,

        avg_cost_bps,

        total_cost
        / PORTFOLIO_NAV,

        datetime.now()
        .strftime(
            "%Y-%m-%d"
        ),

        ENGINE_VERSION,
    ]
})

# =========================================================
# SAVE
# =========================================================

df.to_csv(

    OUTPUT_DIR
    / "transaction_costs.csv",

    index=False,
)

summary.to_csv(

    OUTPUT_DIR
    / "portfolio_cost_summary.csv",

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
    "🏁 TRANSACTION COST ENGINE COMPLETE"
)

print("=" * 70)

print(
    f"Portfolio NAV      : "
    f"₹{PORTFOLIO_NAV:,.0f}"
)

print(
    f"Trade Value        : "
    f"₹{total_trade_value:,.0f}"
)

print(
    f"Transaction Cost   : "
    f"₹{total_cost:,.0f}"
)

print(
    f"Average Cost (bps) : "
    f"{avg_cost_bps:.2f}"
)

print(
    f"Cost % NAV         : "
    f"{total_cost / PORTFOLIO_NAV:.2%}"
)

print(
    f"\nOutput Directory:\n"
    f"{OUTPUT_DIR}"
)

print("=" * 70)