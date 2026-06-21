"""
=========================================================
EXECUTION ENGINE
=========================================================

Purpose:
Generate institutional trade orders
from optimized portfolio.

Input:
data/portfolios/optimized_portfolio.csv

Outputs:
data/execution/orders.csv
data/execution/trade_blotter.csv
data/logs/execution_report.csv

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

MAX_ADV_PARTICIPATION = 0.10

MIN_TRADE_WEIGHT = 0.001

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    ROOT
    / "data"
    / "portfolios"
    / "optimized_portfolio.csv"
)

ORDERS_FILE = (
    ROOT
    / "data"
    / "execution"
    / "orders.csv"
)

BLOTTER_FILE = (
    ROOT
    / "data"
    / "execution"
    / "trade_blotter.csv"
)

REPORT_FILE = (
    ROOT
    / "data"
    / "logs"
    / "execution_report.csv"
)

# =========================================================
# LOAD
# =========================================================

print("\n📥 Loading Optimized Portfolio...")

df = pd.read_csv(INPUT_FILE)

if df.empty:

    raise ValueError(
        "optimized_portfolio.csv is empty"
    )

required_columns = [

    "Security_ID",
    "Symbol",

    "Current_Weight",
    "Optimized_Weight",

    "Weight_Change",

    "ADV_20D",

    "Last_Close",
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
# TRADE CALCULATIONS
# =========================================================

df["Trade_Value"] = (

    df["Weight_Change"]

    * PORTFOLIO_NAV
)

df["Target_Value"] = (

    df["Optimized_Weight"]

    * PORTFOLIO_NAV
)

df["Current_Value"] = (

    df["Current_Weight"]

    * PORTFOLIO_NAV
)

df["Shares"] = (

    df["Trade_Value"]

    / df["Last_Close"]

)

df["Shares"] = (

    df["Shares"]

    .fillna(0)

    .round()

    .astype(int)
)

# =========================================================
# ACTION
# =========================================================

conditions = [

    df["Weight_Change"]
    > MIN_TRADE_WEIGHT,

    df["Weight_Change"]
    < -MIN_TRADE_WEIGHT,
]

choices = [

    "BUY",

    "SELL",
]

df["Action"] = np.select(

    conditions,

    choices,

    default="HOLD",
)

# =========================================================
# ADV PARTICIPATION
# =========================================================

df["ADV_Pct"] = (

    abs(
        df["Trade_Value"]
    )

    / df["ADV_20D"]
)

df["Liquidity_Flag"] = np.where(

    df["ADV_Pct"]
    > MAX_ADV_PARTICIPATION,

    "BREACH",

    "OK",
)

# =========================================================
# COMPLIANCE
# =========================================================

df["Compliance_Status"] = np.where(

    df["Liquidity_Flag"]
    == "OK",

    "APPROVED",

    "REVIEW",
)

# =========================================================
# TRADE BLOTTER
# =========================================================

trade_blotter = df[

    df["Action"]
    != "HOLD"
]

trade_blotter = trade_blotter[

    [

        "Security_ID",

        "Symbol",

        "Action",

        "Current_Weight",

        "Optimized_Weight",

        "Weight_Change",

        "Current_Value",

        "Target_Value",

        "Trade_Value",

        "Shares",

        "ADV_20D",

        "ADV_Pct",

        "Liquidity_Flag",

        "Compliance_Status",
    ]
]

trade_blotter = trade_blotter.sort_values(

    "Trade_Value",

    ascending=False,
)

# =========================================================
# ORDERS
# =========================================================

orders = trade_blotter[

    [

        "Symbol",

        "Action",

        "Shares",
    ]
]

# =========================================================
# SAVE
# =========================================================

ORDERS_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

orders.to_csv(
    ORDERS_FILE,
    index=False,
)

trade_blotter.to_csv(
    BLOTTER_FILE,
    index=False,
)

# =========================================================
# REPORT
# =========================================================

buy_count = (

    trade_blotter["Action"]
    == "BUY"
).sum()

sell_count = (

    trade_blotter["Action"]
    == "SELL"
).sum()

trade_value = (

    trade_blotter[
        "Trade_Value"
    ]

    .abs()

    .sum()
)

breaches = (

    trade_blotter[
        "Liquidity_Flag"
    ]

    == "BREACH"
).sum()

turnover = (

    trade_blotter[
        "Weight_Change"
    ]

    .abs()

    .sum()
)

report = pd.DataFrame(

    {

        "Metric": [

            "Buy_Orders",

            "Sell_Orders",

            "Total_Trades",

            "Trade_Value",

            "Turnover",

            "Liquidity_Breaches",

            "Run_Date",

            "Engine_Version",
        ],

        "Value": [

            buy_count,

            sell_count,

            len(
                trade_blotter
            ),

            trade_value,

            turnover,

            breaches,

            datetime.now()
            .strftime(
                "%Y-%m-%d"
            ),

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
    "🏁 EXECUTION ENGINE COMPLETE"
)

print("=" * 70)

print(
    f"Buy Orders         : "
    f"{buy_count:,}"
)

print(
    f"Sell Orders        : "
    f"{sell_count:,}"
)

print(
    f"Total Trade Value  : "
    f"{trade_value:,.0f}"
)

print(
    f"Turnover           : "
    f"{turnover:.2%}"
)

print(
    f"Liquidity Breaches : "
    f"{breaches:,}"
)

print("=" * 70)