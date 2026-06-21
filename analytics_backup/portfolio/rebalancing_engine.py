"""
=========================================================
REBALANCING ENGINE
=========================================================

Purpose:
Institutional Portfolio Rebalancing Engine

Outputs:
1. Trade List
2. Buy Orders
3. Sell Orders
4. Turnover Report
5. Rebalance Summary

=========================================================
"""

from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd

# =========================================================
# CONFIGURATION
# =========================================================

ENGINE_VERSION = "1.0.0"

MIN_TRADE_WEIGHT = 0.001

MAX_SINGLE_TRADE = 0.05

TURNOVER_WARNING = 0.30

CASH_BUFFER = 0.01

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

PORTFOLIO_DIR = (
    ROOT
    / "data"
    / "portfolios"
)

LOG_DIR = (
    ROOT
    / "data"
    / "logs"
)

OUTPUT_DIR = (
    ROOT
    / "data"
    / "trades"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

LOG_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# =========================================================
# INPUT FILES
# =========================================================

CURRENT_PORTFOLIO_FILE = (
    PORTFOLIO_DIR
    / "live_portfolio.csv"
)

TARGET_PORTFOLIO_FILE = (
    PORTFOLIO_DIR
    / "institutional_model_portfolio.csv"
)

# =========================================================
# OUTPUT FILES
# =========================================================

TRADE_LIST_FILE = (
    OUTPUT_DIR
    / "trade_list.csv"
)

BUY_FILE = (
    OUTPUT_DIR
    / "buy_orders.csv"
)

SELL_FILE = (
    OUTPUT_DIR
    / "sell_orders.csv"
)

TURNOVER_FILE = (
    OUTPUT_DIR
    / "turnover_report.csv"
)

SUMMARY_FILE = (
    OUTPUT_DIR
    / "rebalance_summary.csv"
)

AUDIT_FILE = (
    LOG_DIR
    / "rebalance_audit.csv"
)

# =========================================================
# LOAD INPUTS
# =========================================================

print(
    "\n📥 Loading Rebalancing Inputs..."
)

if not CURRENT_PORTFOLIO_FILE.exists():

    raise FileNotFoundError(
        CURRENT_PORTFOLIO_FILE
    )

if not TARGET_PORTFOLIO_FILE.exists():

    raise FileNotFoundError(
        TARGET_PORTFOLIO_FILE
    )

current_portfolio = pd.read_csv(
    CURRENT_PORTFOLIO_FILE
)

target_portfolio = pd.read_csv(
    TARGET_PORTFOLIO_FILE
)

# =========================================================
# VALIDATION
# =========================================================

print(
    "✔ Validating Portfolios..."
)

required_cols = [
    "Symbol",
    "Weight"
]

for col in required_cols:

    if col not in current_portfolio.columns:

        raise ValueError(
            f"Missing column in current portfolio: {col}"
        )

    if col not in target_portfolio.columns:

        raise ValueError(
            f"Missing column in target portfolio: {col}"
        )

if current_portfolio.empty:

    raise ValueError(
        "Current portfolio empty."
    )

if target_portfolio.empty:

    raise ValueError(
        "Target portfolio empty."
    )

# =========================================================
# STANDARDIZE SYMBOLS
# =========================================================

current_portfolio["Symbol"] = (

    current_portfolio["Symbol"]

    .astype(str)

    .str.upper()

    .str.strip()
)

target_portfolio["Symbol"] = (

    target_portfolio["Symbol"]

    .astype(str)

    .str.upper()

    .str.strip()
)

# =========================================================
# NORMALIZE WEIGHTS
# =========================================================

current_portfolio["Weight"] = (

    current_portfolio["Weight"]

    /

    current_portfolio["Weight"].sum()
)

target_portfolio["Weight"] = (

    target_portfolio["Weight"]

    /

    target_portfolio["Weight"].sum()
)

# =========================================================
# BUILD MASTER UNIVERSE
# =========================================================

universe = sorted(

    set(
        current_portfolio["Symbol"]
    )

    |

    set(
        target_portfolio["Symbol"]
    )
)

rebalance_frame = pd.DataFrame({

    "Symbol":
    universe
})

rebalance_frame = rebalance_frame.merge(

    current_portfolio[
        [
            "Symbol",
            "Weight"
        ]
    ],

    on="Symbol",

    how="left"
)

rebalance_frame = rebalance_frame.rename(

    columns={
        "Weight":
        "Current_Weight"
    }
)

rebalance_frame = rebalance_frame.merge(

    target_portfolio[
        [
            "Symbol",
            "Weight"
        ]
    ],

    on="Symbol",

    how="left"
)

rebalance_frame = rebalance_frame.rename(

    columns={
        "Weight":
        "Target_Weight"
    }
)

rebalance_frame = rebalance_frame.fillna(0)

# =========================================================
# BASIC DIAGNOSTICS
# =========================================================

print(
    f"Current Holdings : "
    f"{len(current_portfolio):,}"
)

print(
    f"Target Holdings  : "
    f"{len(target_portfolio):,}"
)

print(
    f"Master Universe  : "
    f"{len(rebalance_frame):,}"
)

new_positions = int(

    (
        (rebalance_frame[
            "Current_Weight"
        ] == 0)

        &

        (
            rebalance_frame[
                "Target_Weight"
            ] > 0
        )
    ).sum()
)

closed_positions = int(

    (
        (rebalance_frame[
            "Current_Weight"
        ] > 0)

        &

        (
            rebalance_frame[
                "Target_Weight"
            ] == 0
        )
    ).sum()
)

print(
    f"New Positions    : "
    f"{new_positions:,}"
)

print(
    f"Closed Positions : "
    f"{closed_positions:,}"
)

# =========================================================
# AUDIT CONTAINER
# =========================================================

audit_metrics = {}

audit_metrics[
    "Current_Holdings"
] = len(
    current_portfolio
)

audit_metrics[
    "Target_Holdings"
] = len(
    target_portfolio
)

audit_metrics[
    "Master_Universe"
] = len(
    rebalance_frame
)

audit_metrics[
    "Engine_Version"
] = ENGINE_VERSION

audit_metrics[
    "Run_Date"
] = datetime.now().strftime(
    "%Y-%m-%d"
)

# =========================================================
# PART 2 STARTS HERE
# =========================================================

#
# Trade Calculation
# Buy/Sell Classification
# Turnover Analysis
#
# =========================================================

# =========================================================
# BUILD REBALANCE TRADES
# =========================================================

print(
    "\n🏗 Building Trade List..."
)

rebalance_frame["Trade_Weight"] = (

    rebalance_frame["Target_Weight"]

    -

    rebalance_frame["Current_Weight"]
)

rebalance_frame["Abs_Trade"] = (

    rebalance_frame["Trade_Weight"]
    .abs()
)

# =========================================================
# REMOVE IMMATERIAL TRADES
# =========================================================

rebalance_frame.loc[

    rebalance_frame[
        "Abs_Trade"
    ] < MIN_TRADE_WEIGHT,

    "Trade_Weight"

] = 0

rebalance_frame["Abs_Trade"] = (

    rebalance_frame["Trade_Weight"]
    .abs()
)

# =========================================================
# TRADE DIRECTION
# =========================================================

rebalance_frame["Trade_Action"] = np.where(

    rebalance_frame[
        "Trade_Weight"
    ] > 0,

    "BUY",

    np.where(

        rebalance_frame[
            "Trade_Weight"
        ] < 0,

        "SELL",

        "HOLD"
    )
)

# =========================================================
# POSITION CLASSIFICATION
# =========================================================

rebalance_frame["Position_Type"] = "REBALANCE"

rebalance_frame.loc[

    (
        rebalance_frame[
            "Current_Weight"
        ] == 0
    )

    &

    (
        rebalance_frame[
            "Target_Weight"
        ] > 0
    ),

    "Position_Type"

] = "NEW"

rebalance_frame.loc[

    (
        rebalance_frame[
            "Current_Weight"
        ] > 0
    )

    &

    (
        rebalance_frame[
            "Target_Weight"
        ] == 0
    ),

    "Position_Type"

] = "EXIT"

# =========================================================
# TURNOVER ANALYSIS
# =========================================================

print(
    "⚖ Building Turnover Analytics..."
)

gross_turnover = (

    rebalance_frame[
        "Abs_Trade"
    ].sum()
)

net_turnover = (

    rebalance_frame[
        "Trade_Weight"
    ].abs().sum()
)

buy_turnover = (

    rebalance_frame.loc[
        rebalance_frame[
            "Trade_Action"
        ] == "BUY",

        "Trade_Weight"
    ]
    .sum()
)

sell_turnover = (

    rebalance_frame.loc[
        rebalance_frame[
            "Trade_Action"
        ] == "SELL",

        "Trade_Weight"
    ]
    .abs()
    .sum()
)

print(
    f"Gross Turnover : "
    f"{gross_turnover:.2%}"
)

print(
    f"Buy Turnover   : "
    f"{buy_turnover:.2%}"
)

print(
    f"Sell Turnover  : "
    f"{sell_turnover:.2%}"
)

# =========================================================
# TURNOVER WARNING
# =========================================================

turnover_flag = "NORMAL"

if gross_turnover > TURNOVER_WARNING:

    turnover_flag = "HIGH"

# =========================================================
# CASH IMPACT
# =========================================================

print(
    "💵 Building Cash Analysis..."
)

cash_before = max(

    0,

    1
    -
    current_portfolio[
        "Weight"
    ].sum()
)

cash_after = max(

    0,

    1
    -
    target_portfolio[
        "Weight"
    ].sum()
)

cash_change = (

    cash_after
    -
    cash_before
)

# =========================================================
# TRADE STATISTICS
# =========================================================

buy_count = int(

    (
        rebalance_frame[
            "Trade_Action"
        ] == "BUY"
    ).sum()
)

sell_count = int(

    (
        rebalance_frame[
            "Trade_Action"
        ] == "SELL"
    ).sum()
)

hold_count = int(

    (
        rebalance_frame[
            "Trade_Action"
        ] == "HOLD"
    ).sum()
)

new_count = int(

    (
        rebalance_frame[
            "Position_Type"
        ] == "NEW"
    ).sum()
)

exit_count = int(

    (
        rebalance_frame[
            "Position_Type"
        ] == "EXIT"
    ).sum()
)

largest_trade = (

    rebalance_frame[
        "Abs_Trade"
    ].max()
)

largest_trade_symbol = (

    rebalance_frame

    .sort_values(
        "Abs_Trade",
        ascending=False
    )

    .iloc[0]

    ["Symbol"]
)

print(
    f"BUY Orders      : "
    f"{buy_count:,}"
)

print(
    f"SELL Orders     : "
    f"{sell_count:,}"
)

print(
    f"New Positions   : "
    f"{new_count:,}"
)

print(
    f"Closed Positions: "
    f"{exit_count:,}"
)

print(
    f"Largest Trade   : "
    f"{largest_trade_symbol}"
)

print(
    f"Trade Size      : "
    f"{largest_trade:.2%}"
)

# =========================================================
# TRADE QUALITY SCORE
# =========================================================

trade_quality_score = 100.0

if gross_turnover > 0.50:

    trade_quality_score -= 15

if gross_turnover > 0.75:

    trade_quality_score -= 15

if largest_trade > MAX_SINGLE_TRADE:

    trade_quality_score -= 10

trade_quality_score = max(
    trade_quality_score,
    0
)

# =========================================================
# AUDIT METRICS
# =========================================================

audit_metrics[
    "Gross_Turnover"
] = gross_turnover

audit_metrics[
    "Buy_Turnover"
] = buy_turnover

audit_metrics[
    "Sell_Turnover"
] = sell_turnover

audit_metrics[
    "Buy_Orders"
] = buy_count

audit_metrics[
    "Sell_Orders"
] = sell_count

audit_metrics[
    "New_Positions"
] = new_count

audit_metrics[
    "Closed_Positions"
] = exit_count

audit_metrics[
    "Largest_Trade"
] = largest_trade

audit_metrics[
    "Trade_Quality_Score"
] = trade_quality_score

audit_metrics[
    "Turnover_Flag"
] = turnover_flag

# =========================================================
# PART 3 STARTS HERE
# =========================================================

#
# Buy Orders Export
# Sell Orders Export
# Turnover Report
# Rebalance Summary
# Final Validation
#
# =========================================================

# =========================================================
# BUILD BUY / SELL ORDER FILES
# =========================================================

print(
    "\n📊 Building Order Files..."
)

trade_list = (

    rebalance_frame

    .loc[
        rebalance_frame[
            "Trade_Action"
        ] != "HOLD"
    ]

    .sort_values(
        "Abs_Trade",
        ascending=False
    )

    .copy()
)

buy_orders = (

    trade_list

    .loc[
        trade_list[
            "Trade_Action"
        ] == "BUY"
    ]

    .copy()
)

sell_orders = (

    trade_list

    .loc[
        trade_list[
            "Trade_Action"
        ] == "SELL"
    ]

    .copy()
)

# =========================================================
# TURNOVER REPORT
# =========================================================

turnover_report = pd.DataFrame({

    "Metric": [

        "Gross_Turnover",
        "Buy_Turnover",
        "Sell_Turnover",
        "Cash_Before",
        "Cash_After",
        "Cash_Change",
        "Largest_Trade",
        "Trade_Quality_Score",
        "Turnover_Flag",
    ],

    "Value": [

        gross_turnover,
        buy_turnover,
        sell_turnover,
        cash_before,
        cash_after,
        cash_change,
        largest_trade,
        trade_quality_score,
        turnover_flag,
    ]
})

# =========================================================
# REBALANCE SUMMARY
# =========================================================

summary = pd.DataFrame({

    "Metric": [

        "Current_Holdings",
        "Target_Holdings",
        "Master_Universe",
        "Buy_Orders",
        "Sell_Orders",
        "New_Positions",
        "Closed_Positions",
        "Gross_Turnover",
        "Largest_Trade",
        "Trade_Quality_Score",
        "Run_Date",
        "Engine_Version",
    ],

    "Value": [

        len(current_portfolio),
        len(target_portfolio),
        len(rebalance_frame),
        buy_count,
        sell_count,
        new_count,
        exit_count,
        gross_turnover,
        largest_trade,
        trade_quality_score,
        datetime.now().strftime(
            "%Y-%m-%d"
        ),
        ENGINE_VERSION,
    ]
})

# =========================================================
# AUDIT REPORT
# =========================================================

audit_report = pd.DataFrame({

    "Metric":
    list(
        audit_metrics.keys()
    ),

    "Value":
    list(
        audit_metrics.values()
    )
})

# =========================================================
# SAVE OUTPUTS
# =========================================================

print(
    "💾 Saving Outputs..."
)

trade_list.to_csv(
    TRADE_LIST_FILE,
    index=False
)

buy_orders.to_csv(
    BUY_FILE,
    index=False
)

sell_orders.to_csv(
    SELL_FILE,
    index=False
)

turnover_report.to_csv(
    TURNOVER_FILE,
    index=False
)

summary.to_csv(
    SUMMARY_FILE,
    index=False
)

audit_report.to_csv(
    AUDIT_FILE,
    index=False
)

# =========================================================
# FINAL VALIDATION
# =========================================================

print(
    "✔ Running Final Validation..."
)

required_files = [

    TRADE_LIST_FILE,
    BUY_FILE,
    SELL_FILE,
    TURNOVER_FILE,
    SUMMARY_FILE,
    AUDIT_FILE,
]

for file in required_files:

    if not file.exists():

        raise FileNotFoundError(
            file
        )

if trade_quality_score < 0:

    raise ValueError(
        "Invalid trade quality score."
    )

if gross_turnover < 0:

    raise ValueError(
        "Invalid turnover."
    )

# =========================================================
# COMPLETION REPORT
# =========================================================

print("\n" + "=" * 58)

print(
    "🏁 REBALANCING ENGINE COMPLETE"
)

print("=" * 58)

print(
    f"Current Holdings    : "
    f"{len(current_portfolio):,}"
)

print(
    f"Target Holdings     : "
    f"{len(target_portfolio):,}"
)

print(
    f"Buy Orders          : "
    f"{buy_count:,}"
)

print(
    f"Sell Orders         : "
    f"{sell_count:,}"
)

print(
    f"New Positions       : "
    f"{new_count:,}"
)

print(
    f"Closed Positions    : "
    f"{exit_count:,}"
)

print(
    f"Gross Turnover      : "
    f"{gross_turnover:.2%}"
)

print(
    f"Largest Trade       : "
    f"{largest_trade:.2%}"
)

print(
    f"Trade Quality Score : "
    f"{trade_quality_score:.2f}"
)

print(
    f"Turnover Flag       : "
    f"{turnover_flag}"
)

print("\nOutput Directory:")

print(
    OUTPUT_DIR
)

print("=" * 58)