"""
=========================================================
LIVE REBALANCE ENGINE
=========================================================

Purpose:
Institutional Portfolio Rebalancing Engine

Inputs:
data/portfolios/live_portfolio.csv
data/signals/signal_master.csv
data/regime/market_regime.csv
data/risk/risk_budget.csv
data/capacity/capacity_summary.csv
data/execution/portfolio_cost_summary.csv

Outputs:
data/live/target_portfolio.csv
data/live/rebalance_orders.csv
data/live/trade_list.csv
data/live/rebalance_summary.csv

=========================================================
"""

from pathlib import Path
from datetime import datetime
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings(
    "ignore"
)

# =========================================================
# CONFIG
# =========================================================

ENGINE_VERSION = "2.0.0"

# Position Sizing

MAX_POSITION_WEIGHT = 0.05

STRONG_BUY_WEIGHT = 0.040
BUY_WEIGHT = 0.025

MIN_ORDER_CHANGE = 0.0025

# Risk Controls

MAX_SECTOR_RISK = 0.30

# Capacity Controls

MIN_CAPACITY_SCORE = 40

# Transaction Cost Controls

MAX_COST_BPS = 100

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

SIGNAL_FILE = (
    ROOT
    / "data"
    / "signals"
    / "signal_master.csv"
)

REGIME_FILE = (
    ROOT
    / "data"
    / "regime"
    / "market_regime.csv"
)

RISK_FILE = (
    ROOT
    / "data"
    / "risk"
    / "risk_budget.csv"
)

CAPACITY_FILE = (
    ROOT
    / "data"
    / "capacity"
    / "capacity_summary.csv"
)

TCOST_FILE = (
    ROOT
    / "data"
    / "execution"
    / "portfolio_cost_summary.csv"
)

OUTPUT_DIR = (
    ROOT
    / "data"
    / "live"
)

REPORT_FILE = (
    ROOT
    / "data"
    / "logs"
    / "live_rebalance_report.csv"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

REPORT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

# =========================================================
# SAFE LOAD
# =========================================================

def safe_load(
    path: Path,
) -> pd.DataFrame:
    """
    Production-safe CSV loader.
    """

    try:

        df = pd.read_csv(
            path
        )

        print(
            f"✓ Loaded: {path.name}"
        )

        return df

    except FileNotFoundError:

        print(
            f"⚠ Missing: {path.name}"
        )

        return pd.DataFrame()

    except Exception as e:

        print(
            f"⚠ Error Loading "
            f"{path.name}: {e}"
        )

        return pd.DataFrame()

# =========================================================
# VALIDATION
# =========================================================

def validate_required_columns(
    df: pd.DataFrame,
    required: list,
    file_name: str,
):
    """
    Validate schema.
    """

    missing = [

        c

        for c in required

        if c not in df.columns
    ]

    if missing:

        raise ValueError(

            f"{file_name} missing columns: "

            f"{missing}"
        )

# =========================================================
# LOAD INPUTS
# =========================================================

print(
    "\n📥 Loading Inputs..."
)

portfolio = safe_load(
    PORTFOLIO_FILE
)

signals = safe_load(
    SIGNAL_FILE
)

regime = safe_load(
    REGIME_FILE
)

risk_budget = safe_load(
    RISK_FILE
)

capacity = safe_load(
    CAPACITY_FILE
)

tcost = safe_load(
    TCOST_FILE
)

# =========================================================
# REQUIRED SCHEMA CHECKS
# =========================================================

validate_required_columns(

    portfolio,

    [
        "Symbol",
        "Weight",
    ],

    "live_portfolio.csv",
)

validate_required_columns(

    signals,

    [
        "Symbol",
        "Signal",
        "Signal_Score",
    ],

    "signal_master.csv",
)

validate_required_columns(

    regime,

    [
        "Regime",
    ],

    "market_regime.csv",
)

# =========================================================
# CURRENT REGIME
# =========================================================

current_regime = (

    regime

    .iloc[-1]

    ["Regime"]
)

print(
    f"\nCurrent Regime: "
    f"{current_regime}"
)

# =========================================================
# CAPACITY SCORE
# =========================================================

capacity_score = 50.0

try:

    capacity_score = float(

        capacity.loc[
            capacity["Metric"]
            ==
            "Average_Capacity_Score",

            "Value"
        ].iloc[0]

    )

except Exception:

    pass

# =========================================================
# COST SCORE
# =========================================================

avg_cost_bps = 20.0

try:

    avg_cost_bps = float(

        tcost.loc[
            tcost["Metric"]
            ==
            "Average_Cost_BPS",

            "Value"
        ].iloc[0]

    )

except Exception:

    pass

print(
    f"Capacity Score : "
    f"{capacity_score:.2f}"
)

print(
    f"Avg Cost (bps) : "
    f"{avg_cost_bps:.2f}"
)

# =========================================================
# PORTFOLIO LOOKUP
# =========================================================

current_weights = dict(

    zip(

        portfolio["Symbol"],

        portfolio["Weight"]
    )
)

print(
    f"Portfolio Holdings : "
    f"{len(portfolio):,}"
)

print(
    f"Signal Universe    : "
    f"{len(signals):,}"
)

# =========================================================
# SIGNAL → TARGET WEIGHT ENGINE
# =========================================================

def target_weight_engine(
    signal: str,
    current_weight: float,
) -> float:
    """
    Institutional target weight mapping.
    """

    signal = str(
        signal
    ).upper()

    if signal == "STRONG_BUY":

        return STRONG_BUY_WEIGHT

    elif signal == "BUY":

        return BUY_WEIGHT

    elif signal == "SELL":

        return 0.0

    elif signal == "REDUCE":

        return current_weight * 0.50

    elif signal == "HOLD":

        return current_weight

    return current_weight

# =========================================================
# BUILD TARGET PORTFOLIO
# =========================================================

print(
    "\n⚙ Building Target Portfolio..."
)

records = []

for _, row in signals.iterrows():

    symbol = row["Symbol"]

    signal = row["Signal"]

    signal_score = row[
        "Signal_Score"
    ]

    current_weight = (
        current_weights.get(
            symbol,
            0.0
        )
    )

    tgt_weight = (
        target_weight_engine(
            signal,
            current_weight,
        )
    )

    records.append({

        "Symbol":
        symbol,

        "Signal":
        signal,

        "Signal_Score":
        signal_score,

        "Current_Weight":
        current_weight,

        "Target_Weight":
        tgt_weight,
    })

target = pd.DataFrame(
    records
)

# =========================================================
# REGIME OVERLAY
# =========================================================

print(
    "\n📊 Applying Regime Overlay..."
)

regime_multiplier = 1.0

if (
    "BEAR_HIGH_VOL"
    in current_regime
):

    regime_multiplier = 0.60

elif (
    "BEAR"
    in current_regime
):

    regime_multiplier = 0.75

elif (
    "BULL_LOW_VOL"
    in current_regime
):

    regime_multiplier = 1.15

elif (
    "BULL"
    in current_regime
):

    regime_multiplier = 1.05

target[
    "Target_Weight"
] *= regime_multiplier

# =========================================================
# CAPACITY OVERLAY
# =========================================================

print(
    "📦 Applying Capacity Overlay..."
)

capacity_multiplier = 1.0

if capacity_score < 40:

    capacity_multiplier = 0.80

elif capacity_score < 60:

    capacity_multiplier = 0.90

target[
    "Target_Weight"
] *= capacity_multiplier

# =========================================================
# TRANSACTION COST OVERLAY
# =========================================================

print(
    "💰 Applying Cost Overlay..."
)

cost_multiplier = 1.0

if avg_cost_bps > 100:

    cost_multiplier = 0.80

elif avg_cost_bps > 50:

    cost_multiplier = 0.90

target[
    "Target_Weight"
] *= cost_multiplier

# =========================================================
# RISK BUDGET OVERLAY
# =========================================================

print(
    "🛡 Applying Risk Budget Overlay..."
)

if (

    not risk_budget.empty

    and "Sector" in risk_budget.columns

    and "Risk_Budget_%"
    in risk_budget.columns

):

    high_risk_sectors = (

        risk_budget[

            risk_budget[
                "Risk_Budget_%"
            ] > MAX_SECTOR_RISK

        ]

        ["Sector"]

        .tolist()
    )

    if (
        "Sector"
        in signals.columns
    ):

        target = target.merge(

            signals[
                [
                    "Symbol",
                    "Sector",
                ]
            ],

            on="Symbol",

            how="left",
        )

        target.loc[

            target[
                "Sector"
            ].isin(
                high_risk_sectors
            ),

            "Target_Weight"

        ] *= 0.80

# =========================================================
# POSITION LIMITS
# =========================================================

print(
    "📏 Applying Position Limits..."
)

target[
    "Target_Weight"
] = (

    target[
        "Target_Weight"
    ]

    .clip(
        upper=
        MAX_POSITION_WEIGHT
    )
)

# =========================================================
# REMOVE NEGATIVE WEIGHTS
# =========================================================

target[
    "Target_Weight"
] = (

    target[
        "Target_Weight"
    ]

    .clip(
        lower=0
    )
)

# =========================================================
# NORMALIZE PORTFOLIO
# =========================================================

print(
    "⚖ Normalizing Portfolio..."
)

total_weight = (

    target[
        "Target_Weight"
    ]

    .sum()
)

if total_weight > 0:

    target[
        "Target_Weight"
    ] = (

        target[
            "Target_Weight"
        ]

        / total_weight
    )

# =========================================================
# PORTFOLIO STATISTICS
# =========================================================

print(
    "\nTarget Portfolio Weight:"
    f" {target['Target_Weight'].sum():.4f}"
)

print(
    "Max Position Weight:"
    f" {target['Target_Weight'].max():.2%}"
)

print(
    "Target Holdings:"
    f" {len(target):,}"
)

# =========================================================
# TRADE GENERATION
# =========================================================

print(
    "\n🔄 Generating Trades..."
)

target[
    "Weight_Change"
] = (

    target[
        "Target_Weight"
    ]

    - target[
        "Current_Weight"
    ]
)

# Ignore micro trades

target.loc[

    target[
        "Weight_Change"
    ].abs()

    < MIN_ORDER_CHANGE,

    "Weight_Change"

] = 0.0

# =========================================================
# ACTION ENGINE
# =========================================================

def determine_action(
    signal,
    change,
):

    signal = str(
        signal
    ).upper()

    if signal == "SELL":

        return "EXIT"

    if signal == "REDUCE":

        return "TRIM"

    if change > 0:

        if signal == "STRONG_BUY":

            return "AGGRESSIVE_BUY"

        return "BUY"

    if change < 0:

        return "SELL"

    return "HOLD"

target[
    "Action"
] = target.apply(

    lambda x:

    determine_action(

        x["Signal"],

        x["Weight_Change"]
    ),

    axis=1,
)

# =========================================================
# PRIORITY SCORE
# =========================================================

print(
    "🎯 Calculating Trade Priority..."
)

target[
    "Priority_Score"
] = (

    target[
        "Signal_Score"
    ]

    * target[
        "Weight_Change"
    ].abs()
)

# =========================================================
# TRADE VALUE SCORE
# =========================================================

target[
    "Trade_Size_%"
] = (

    target[
        "Weight_Change"
    ].abs()

    * 100
)

# =========================================================
# REBALANCE LIST
# =========================================================

trade_list = (

    target[

        target[
            "Action"
        ]

        != "HOLD"

    ]

    .copy()
)

# =========================================================
# EXECUTION RANKING
# =========================================================

trade_list = (

    trade_list

    .sort_values(

        [
            "Priority_Score",
            "Trade_Size_%"
        ],

        ascending=[
            False,
            False
        ]
    )

    .reset_index(
        drop=True
    )
)

trade_list[
    "Execution_Rank"
] = (
    trade_list.index
    + 1
)

# =========================================================
# REBALANCE ORDERS
# =========================================================

orders = trade_list[

    [
        "Execution_Rank",

        "Symbol",

        "Signal",

        "Action",

        "Signal_Score",

        "Current_Weight",

        "Target_Weight",

        "Weight_Change",

        "Priority_Score",
    ]

].copy()

# =========================================================
# TURNOVER ANALYSIS
# =========================================================

portfolio_turnover = (

    orders[
        "Weight_Change"
    ]

    .abs()

    .sum()
)

gross_buy = (

    orders.loc[

        orders[
            "Weight_Change"
        ] > 0,

        "Weight_Change"

    ]

    .sum()
)

gross_sell = abs(

    orders.loc[

        orders[
            "Weight_Change"
        ] < 0,

        "Weight_Change"

    ]

    .sum()
)

net_flow = (
    gross_buy
    - gross_sell
)

# =========================================================
# TRADE STATISTICS
# =========================================================

buy_orders = (

    orders[
        "Action"
    ]

    .isin(
        [
            "BUY",
            "AGGRESSIVE_BUY"
        ]
    )

    .sum()
)

sell_orders = (

    orders[
        "Action"
    ]

    .isin(
        [
            "SELL",
            "EXIT",
            "TRIM"
        ]
    )

    .sum()
)

holds = (

    target[
        "Action"
    ]

    == "HOLD"

).sum()

# =========================================================
# EXECUTION READINESS SCORE
# =========================================================

execution_score = 100

if capacity_score < 60:

    execution_score -= 10

if avg_cost_bps > 50:

    execution_score -= 10

if portfolio_turnover > 0.50:

    execution_score -= 10

execution_score = max(
    0,
    execution_score
)

# =========================================================
# EXECUTION STATUS
# =========================================================

if execution_score >= 90:

    execution_status = (
        "READY"
    )

elif execution_score >= 75:

    execution_status = (
        "CAUTION"
    )

else:

    execution_status = (
        "REVIEW_REQUIRED"
    )

# =========================================================
# TRADE SUMMARY
# =========================================================

print(
    "\n📊 Trade Summary"
)

print(
    f"Buy Orders      : "
    f"{buy_orders}"
)

print(
    f"Sell Orders     : "
    f"{sell_orders}"
)

print(
    f"Hold Positions  : "
    f"{holds}"
)

print(
    f"Turnover        : "
    f"{portfolio_turnover:.2%}"
)

print(
    f"Execution Score : "
    f"{execution_score}"
)

print(
    f"Execution Status: "
    f"{execution_status}"
)

# =========================================================
# REBALANCE DASHBOARD
# =========================================================

dashboard = pd.DataFrame({

    "Metric": [

        "Current_Regime",

        "Portfolio_Holdings",

        "Target_Holdings",

        "Buy_Orders",

        "Sell_Orders",

        "Portfolio_Turnover",

        "Gross_Buy_Weight",

        "Gross_Sell_Weight",

        "Net_Flow",

        "Capacity_Score",

        "Average_Cost_BPS",

        "Execution_Score",

        "Execution_Status",

        "Engine_Version",
    ],

    "Value": [

        current_regime,

        len(portfolio),

        len(
            target[
                target[
                    "Target_Weight"
                ] > 0
            ]
        ),

        buy_orders,

        sell_orders,

        round(
            portfolio_turnover,
            6
        ),

        round(
            gross_buy,
            6
        ),

        round(
            gross_sell,
            6
        ),

        round(
            net_flow,
            6
        ),

        round(
            capacity_score,
            2
        ),

        round(
            avg_cost_bps,
            2
        ),

        execution_score,

        execution_status,

        ENGINE_VERSION,
    ]
})

# =========================================================
# REBALANCE SUMMARY
# =========================================================

summary = pd.DataFrame({

    "Metric": [

        "Run_Date",

        "Current_Regime",

        "Capacity_Score",

        "Average_Cost_BPS",

        "Current_Holdings",

        "Target_Holdings",

        "Buy_Orders",

        "Sell_Orders",

        "Portfolio_Turnover",

        "Execution_Score",

        "Execution_Status",

        "Engine_Version",
    ],

    "Value": [

        datetime.now()
        .strftime(
            "%Y-%m-%d"
        ),

        current_regime,

        round(
            capacity_score,
            2
        ),

        round(
            avg_cost_bps,
            2
        ),

        len(portfolio),

        len(
            target[
                target[
                    "Target_Weight"
                ] > 0
            ]
        ),

        buy_orders,

        sell_orders,

        round(
            portfolio_turnover,
            6
        ),

        execution_score,

        execution_status,

        ENGINE_VERSION,
    ]
})

# =========================================================
# ADD TIMESTAMP
# =========================================================

run_timestamp = (
    datetime.now()
)

target[
    "Run_Timestamp"
] = run_timestamp

orders[
    "Run_Timestamp"
] = run_timestamp

trade_list[
    "Run_Timestamp"
] = run_timestamp

# =========================================================
# OUTPUT FILES
# =========================================================

TARGET_FILE = (
    OUTPUT_DIR
    / "target_portfolio.csv"
)

ORDERS_FILE = (
    OUTPUT_DIR
    / "rebalance_orders.csv"
)

TRADE_FILE = (
    OUTPUT_DIR
    / "trade_list.csv"
)

SUMMARY_FILE = (
    OUTPUT_DIR
    / "rebalance_summary.csv"
)

DASHBOARD_FILE = (
    OUTPUT_DIR
    / "rebalance_dashboard.csv"
)

# =========================================================
# SAVE OUTPUTS
# =========================================================

print(
    "\n💾 Saving Outputs..."
)

target.to_csv(
    TARGET_FILE,
    index=False,
)

orders.to_csv(
    ORDERS_FILE,
    index=False,
)

trade_list.to_csv(
    TRADE_FILE,
    index=False,
)

summary.to_csv(
    SUMMARY_FILE,
    index=False,
)

dashboard.to_csv(
    DASHBOARD_FILE,
    index=False,
)

dashboard.to_csv(
    REPORT_FILE,
    index=False,
)

# =========================================================
# TOP TRADES
# =========================================================

top_trades = (

    orders

    .head(10)

    .copy()
)

# =========================================================
# FINAL REPORT
# =========================================================

print(
    "\n"
    + "=" * 80
)

print(
    "🏁 LIVE REBALANCE ENGINE COMPLETE"
)

print(
    "=" * 80
)

print(
    f"Regime               : "
    f"{current_regime}"
)

print(
    f"Capacity Score       : "
    f"{capacity_score:.2f}"
)

print(
    f"Average Cost (bps)   : "
    f"{avg_cost_bps:.2f}"
)

print(
    f"Current Holdings     : "
    f"{len(portfolio)}"
)

print(
    f"Target Holdings      : "
    f"{len(target)}"
)

print(
    f"Buy Orders           : "
    f"{buy_orders}"
)

print(
    f"Sell Orders          : "
    f"{sell_orders}"
)

print(
    f"Portfolio Turnover   : "
    f"{portfolio_turnover:.2%}"
)

print(
    f"Execution Score      : "
    f"{execution_score}"
)

print(
    f"Execution Status     : "
    f"{execution_status}"
)

print(
    "\nTop Rebalance Trades:"
)

if not top_trades.empty:

    print(

        top_trades[

            [
                "Execution_Rank",
                "Symbol",
                "Action",
                "Priority_Score",
            ]

        ]

        .to_string(
            index=False
        )
    )

print(
    "\nSaved Files:"
)

print(
    f"  {TARGET_FILE.name}"
)

print(
    f"  {ORDERS_FILE.name}"
)

print(
    f"  {TRADE_FILE.name}"
)

print(
    f"  {SUMMARY_FILE.name}"
)

print(
    f"  {DASHBOARD_FILE.name}"
)

print(
    "\nOutput Directory:"
)

print(
    OUTPUT_DIR
)

print(
    "=" * 80
)