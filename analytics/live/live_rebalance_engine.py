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

ENGINE_VERSION = "2.2.0"

# Position Sizing

MAX_POSITION_WEIGHT = 0.05

STRONG_BUY_WEIGHT = 0.040
BUY_WEIGHT = 0.025

MIN_ORDER_CHANGE = 0.0025

MAX_PORTFOLIO_TURNOVER = 0.30

# =========================================================
# REBALANCE ANALYTICS
# =========================================================

MAX_CHURN_RATIO = 0.50

MAX_EXECUTION_COMPLEXITY = 100

TOP_TRADE_BUCKET = 10

MIN_ACTIVE_SHARE = 0.20

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

print(
    "\nMarket Cap Column:",
    "Market_Cap" in signals.columns
)

if "Market_Cap" in signals.columns:

    print(
        "Valid Market Cap Records:",
        signals["Market_Cap"]
        .notna()
        .sum()
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
# PORTFOLIO SIZE CONTROL
# =========================================================

TARGET_PORTFOLIO_SIZE = 50

target["Selection_Score"] = (

    target["Signal_Score"]

    +

    target["Current_Weight"] * 200

    +

    np.where(
        target["Current_Weight"] > 0,
        5,
        0
    )
)

target = (

    target

    .sort_values(
        "Selection_Score",
        ascending=False
    )

    .head(
        TARGET_PORTFOLIO_SIZE
    )

    .copy()
    
)

target_holdings = len(target)

current_symbols = set(
    portfolio["Symbol"]
)

target_symbols = set(
    target["Symbol"]
)

new_symbols = (

    target_symbols

    -

    current_symbols
)

exited_symbols = (

    current_symbols

    -

    target_symbols
)

retained_symbols = (

    current_symbols

    &
    
    target_symbols
)

new_holdings = len(
    new_symbols
)

exited_holdings = len(
    exited_symbols
)

retained_holdings = len(
    retained_symbols
)

new_holdings_pct = (

    new_holdings

    /

    max(
        target_holdings,
        1
    )
)

exited_holdings_pct = (

    exited_holdings

    /

    max(
        len(portfolio),
        1
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


print(
    "\nLargest Weights"
)

print(

    target[
        [
            "Symbol",
            "Target_Weight"
        ]
    ]

    .sort_values(
        "Target_Weight",
        ascending=False
    )

    .head(10)
)

# =========================================================
# CONCENTRATION ANALYTICS
# =========================================================

portfolio_hhi = (

    target[
        "Target_Weight"
    ] ** 2

).sum()

effective_holdings = (

    1

    /

    max(
        portfolio_hhi,
        1e-9
    )
)

max_position_weight = (
    target["Target_Weight"].max()
)

average_position_weight = (
    target["Target_Weight"].mean()
)

median_position_weight = (
    target["Target_Weight"].median()
)

top5_weight = (

    target

    .nlargest(
        5,
        "Target_Weight"
    )

    [
        "Target_Weight"
    ]

    .sum()
)

top10_weight = (

    target

    .nlargest(
        10,
        "Target_Weight"
    )

    [
        "Target_Weight"
    ]

    .sum()
)

active_df = pd.DataFrame({

    "Symbol": list(
        set(portfolio["Symbol"])
        |
        set(target["Symbol"])
    )
})

active_df = active_df.merge(
    portfolio[
        ["Symbol","Weight"]
    ],
    on="Symbol",
    how="left"
)

active_df = active_df.merge(
    target[
        ["Symbol","Target_Weight"]
    ],
    on="Symbol",
    how="left"
)

active_df = active_df.fillna(0)

active_share = (

    0.5 *

    (
        active_df["Weight"]

        -

        active_df["Target_Weight"]
    )

    .abs()

    .sum()
)

top_trade_share = (

    target

    .nlargest(
        TOP_TRADE_BUCKET,
        "Target_Weight"
    )

    [
        "Target_Weight"
    ]

    .sum()
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
    f" {target_holdings:,}"
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

    orders["Weight_Change"]

    .abs()

    .sum()

) / 2

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
# TURNOVER GOVERNANCE
# =========================================================

turnover_scaling_factor = 1.0

if portfolio_turnover > MAX_PORTFOLIO_TURNOVER:

    turnover_scaling_factor = (
        MAX_PORTFOLIO_TURNOVER
        / portfolio_turnover
    )

    target["Weight_Change"] *= turnover_scaling_factor

    target["Target_Weight"] = (
        target["Current_Weight"]
        +
        target["Weight_Change"]
    )

    # ----------------------------
    # RE-NORMALIZE TARGET PORTFOLIO
    # ----------------------------

    total_target = (
        target["Target_Weight"]
        .sum()
    )

    if total_target > 0:

        target["Target_Weight"] /= total_target

    # ----------------------------
    # RECALCULATE WEIGHT CHANGE
    # ----------------------------

    target["Weight_Change"] = (
        target["Target_Weight"]
        -
        target["Current_Weight"]
    )

    orders = target[
        target["Action"] != "HOLD"
    ].copy()

    trade_list = orders.copy()

portfolio_turnover = (

    orders["Weight_Change"]

    .abs()

    .sum()

) / 2

buy_turnover = (

    orders.loc[
        orders["Weight_Change"] > 0,
        "Weight_Change"
    ]

    .sum()

) / 2

sell_turnover = abs(

    orders.loc[
        orders["Weight_Change"] < 0,
        "Weight_Change"
    ]

    .sum()

) / 2


if portfolio_turnover < 0.15:

    turnover_flag = "LOW"

elif portfolio_turnover < 0.31:

    turnover_flag = "NORMAL"

elif portfolio_turnover < 0.50:

    turnover_flag = "HIGH"

else:

    turnover_flag = "EXCESSIVE"


net_buy_bias = (

    buy_turnover

    /

    max(
        buy_turnover + sell_turnover,
        1e-9
    )
)

# =========================================================
# PORTFOLIO TRANSITION MATRIX
# =========================================================

market_cap_drift = 0.0

if (
    "Market_Cap" in signals.columns
    and
    signals["Market_Cap"].notna().sum() > 0
):

    current_mcap = (

        portfolio
        .merge(
            signals[
                [
                    "Symbol",
                    "Market_Cap"
                ]
            ],
            on="Symbol",
            how="left"
        )

        .eval(
            "Weight * Market_Cap"
        )

        .sum()
    )

    target_mcap = (

        target
        .merge(
            signals[
                [
                    "Symbol",
                    "Market_Cap"
                ]
            ],
            on="Symbol",
            how="left"
        )

        .eval(
            "Target_Weight * Market_Cap"
        )

        .sum()
    )

    market_cap_drift = (

        target_mcap

        / max(
            current_mcap,
            1e-9
        )

        - 1
    )

target = target.copy()

target["Target_Weight"] = (
    target["Target_Weight"]
    /
    target["Target_Weight"].sum()
)

transition = pd.DataFrame({

    "Symbol":

        list(

            set(
                portfolio["Symbol"]
            )

            |

            set(
                target["Symbol"]
            )
        )
})

transition = transition.merge(

    portfolio[
        [
            "Symbol",
            "Weight"
        ]
    ],

    on="Symbol",

    how="left"
)

transition = transition.rename(

    columns={
        "Weight":
        "Current_Weight"
    }
)

transition = transition.merge(

    target[
        [
            "Symbol",
            "Target_Weight"
        ]
    ],

    on="Symbol",

    how="left"
)

transition = transition.fillna(0)

transition["Holding_Status"] = np.select(

    [

        (
            transition["Current_Weight"] == 0
        )

        &

        (
            transition["Target_Weight"] > 0
        ),

        (
            transition["Current_Weight"] > 0
        )

        &

        (
            transition["Target_Weight"] == 0
        ),

        (
            transition["Current_Weight"] > 0
        )

        &

        (
            transition["Target_Weight"] > 0
        ),
    ],

    [

        "NEW",

        "EXIT",

        "RETAIN",
    ],

    default="OTHER"
)

transition["Weight_Change"] = (

    transition["Target_Weight"]

    -

    transition["Current_Weight"]
)

print("\nDEBUG")

print(
    "Current Sum:",
    transition["Current_Weight"].sum()
)

print(
    "Target Sum:",
    transition["Target_Weight"].sum()
)

print(
    "NEW:",
    (
        transition["Holding_Status"]
        == "NEW"
    ).sum()
)

print(
    "EXIT:",
    (
        transition["Holding_Status"]
        == "EXIT"
    ).sum()
)

print(
    "RETAIN:",
    (
        transition["Holding_Status"]
        == "RETAIN"
    ).sum()
)

# =========================================================
# APPLY TURNOVER SCALING TO TRANSITION
# =========================================================

transition["Holding_Status"] = np.select(

    [
        (
            transition["Current_Weight"] == 0
        )
        &
        (
            transition["Target_Weight"] > 0
        ),

        (
            transition["Current_Weight"] > 0
        )
        &
        (
            transition["Target_Weight"] == 0
        ),

        (
            transition["Current_Weight"] > 0
        )
        &
        (
            transition["Target_Weight"] > 0
        ),
    ],

    [
        "NEW",
        "EXIT",
        "RETAIN"
    ],

    default="OTHER"
)

# =========================================================
# RECONCILED TURNOVER
# =========================================================

transition["Weight_Change"] = (
    transition["Target_Weight"]
    - transition["Current_Weight"]
)
print(
    "Current Weight Sum:",
    round(
        transition["Current_Weight"].sum(),
        6
    )
)

print(
    "Target Weight Sum:",
    round(
        transition["Target_Weight"].sum(),
        6
    )
)

transition_turnover = (
    transition["Weight_Change"]
    .abs()
    .sum()
) / 2

print(
    f"Transition Turnover: "
    f"{transition_turnover:.2%}"
)

new_positions = (

    transition[
        "Holding_Status"
    ] == "NEW"
).sum()

exited_positions = (

    transition[
        "Holding_Status"
    ] == "EXIT"
).sum()

retained_positions = (

    transition[
        "Holding_Status"
    ] == "RETAIN"
).sum()

transition_matrix = pd.DataFrame({

    "Status": [

        "NEW",

        "EXIT",

        "RETAIN",
    ],

    "Count": [

        new_positions,

        exited_positions,

        retained_positions,
    ]
})

new_positions = (

    target[
        (target["Current_Weight"] == 0)
        &
        (
            target["Action"].isin(
                ["BUY", "AGGRESSIVE_BUY"]
            )
        )
    ]

    .shape[0]
)

replacement_rate = (

    new_positions

    /

    max(
        len(portfolio),
        1
    )
)

churn_ratio = (

    (
        new_holdings

        +

        exited_holdings
    )

    /

    max(
        len(portfolio),
        1
    )
)

if churn_ratio < 0.20:

    churn_grade = "LOW"

elif churn_ratio < 0.40:

    churn_grade = "NORMAL"

elif churn_ratio < 0.60:

    churn_grade = "HIGH"

else:

    churn_grade = "EXCESSIVE"


turnover_check = (

    buy_turnover

    +

    sell_turnover
)

turnover_difference = abs(

    turnover_check

    -

    portfolio_turnover
)

if turnover_difference > 0.01:

    print(
        "⚠ Turnover Attribution Mismatch"
    )

turnover_difference = abs(

    turnover_check

    -

    portfolio_turnover
)

turnover_reconciled = (

    turnover_difference

    < 0.01
)

if (
    "Sector" in portfolio.columns
    and
    "Sector" in target.columns
):

    current_sector = (
        portfolio
        .groupby("Sector")
        ["Weight"]
        .sum()
    )

    target_sector = (
        target
        .groupby("Sector")
        ["Target_Weight"]
        .sum()
    )

    sector_drift = (

        pd.concat(
            [
                current_sector,
                target_sector
            ],
            axis=1
        )

        .fillna(0)
    )

    sector_drift.columns = [
        "Current_Weight",
        "Target_Weight"
    ]

    sector_drift["Drift"] = (

        sector_drift["Target_Weight"]

        -

        sector_drift["Current_Weight"]
    )

    sector_drift.to_csv(
        OUTPUT_DIR
        / "sector_drift.csv"
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


retained_positions = len(
    retained_symbols
)

retention_ratio = (
    retained_positions
    /
    max(len(portfolio), 1)
)

portfolio_stability = (

    retained_holdings

    /

    max(
        target_holdings,
        len(portfolio)
    )
)

portfolio_stability = max(
    0,
    portfolio_stability
)

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

if retention_ratio < 0.10:
    execution_score -= 5

if replacement_rate > 0.50:
    execution_score -= 5

if active_share < 0.20:
    execution_score -= 10

elif active_share < 0.40:
    execution_score -= 5

if top10_weight > 0.35:

    execution_score -= 5

execution_score = max(
    0,
    execution_score
)

rebalance_efficiency = (
    active_share
    * portfolio_stability
    * (1 - portfolio_turnover)
)

if rebalance_efficiency >= 0.35:
    efficiency_grade = "A"

elif rebalance_efficiency >= 0.25:
    efficiency_grade = "B"

elif rebalance_efficiency >= 0.15:
    efficiency_grade = "C"

else:
    efficiency_grade = "D"

# =========================================================
# REBALANCE HEALTH SCORE
# =========================================================

rebalance_health_score = (

      active_share * 25

    + portfolio_stability * 30

    + (1 - portfolio_turnover) * 25

    + (1 - replacement_rate) * 20
)

rebalance_health_score = min(

    rebalance_health_score,

    100
)

execution_complexity = (

      buy_orders * 1.0

    + sell_orders * 1.0

    + exited_holdings * 2.0

    + new_holdings * 2.0

    + (
        portfolio_turnover
        * 100
    )
)

execution_complexity = min(

    execution_complexity,

    MAX_EXECUTION_COMPLEXITY
)

if execution_complexity < 25:

    complexity_grade = "LOW"

elif execution_complexity < 50:

    complexity_grade = "MODERATE"

elif execution_complexity < 75:

    complexity_grade = "HIGH"

else:

    complexity_grade = "VERY_HIGH"


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

risk_flags = []

if active_share < 0.40:
    risk_flags.append("LOW_ACTIVE_SHARE")

if churn_ratio > 0.50:
    risk_flags.append("HIGH_CHURN")

if portfolio_turnover > 0.40:
    risk_flags.append("HIGH_TURNOVER")

if top10_weight > 0.35:
    risk_flags.append("CONCENTRATION_RISK")

if portfolio_stability < 0.50:
    risk_flags.append("LOW_STABILITY")


if len(risk_flags) == 0:

    governance_status = "PASS"

elif len(risk_flags) <= 2:

    governance_status = "WATCH"

else:

    governance_status = "FAIL"


breadth_score = (

    effective_holdings

    /

    max(
        target_holdings,
        1
    )
)

liquidity_pressure = (

    portfolio_turnover

    *

    max_position_weight
)

execution_capacity = (

    capacity_score

    *

    (1 - liquidity_pressure)
)

crowding_score = (

    top10_weight

    *

    replacement_rate
)


regime_alignment = 100

if "BEAR" in current_regime:

    if active_share > 0.60:

        regime_alignment -= 20

if replacement_rate > 0.50:

    regime_alignment -= 10

if portfolio_turnover > 0.40:

    regime_alignment -= 10
    
liquidity_drift = np.nan

if "ADV_20D" in signals.columns:

    current_adv = (

        portfolio
        .merge(
            signals[
                [
                    "Symbol",
                    "ADV_20D"
                ]
            ],
            on="Symbol",
            how="left"
        )

        .eval(
            "Weight * ADV_20D"
        )

        .sum()
    )

    target_adv = (

        target
        .merge(
            signals[
                [
                    "Symbol",
                    "ADV_20D"
                ]
            ],
            on="Symbol",
            how="left"
        )

        .eval(
            "Target_Weight * ADV_20D"
        )

        .sum()
    )

    liquidity_drift = (

        target_adv

        / max(
            current_adv,
            1e-9
        )

        - 1
    )

approval_score = 100

approval_score -= (
    len(risk_flags) * 5
)

approval_score -= (
    max(
        0,
        portfolio_turnover - 0.30
    ) * 100
)

approval_score -= (
    max(
        0,
        churn_ratio - 0.50
    ) * 50
)

approval_score = max(
    0,
    min(
        approval_score,
        100
    )
)

if approval_score >= 80:

    approval_status = (
        "APPROVED"
    )

elif approval_score >= 60:

    approval_status = (
        "WATCHLIST"
    )

else:

    approval_status = (
        "REJECTED"
    )

new_position_turnover = (
    transition.loc[
        transition["Holding_Status"] == "NEW",
        "Target_Weight"
    ].sum()
)

exit_turnover = (
    transition.loc[
        transition["Holding_Status"] == "EXIT",
        "Current_Weight"
    ].sum()
)

existing_position_turnover = (
    transition.loc[
        transition["Holding_Status"] == "RETAIN",
        "Weight_Change"
    ]
    .abs()
    .sum()
) / 2

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

        "Buy_Turnover",

        "Sell_Turnover",

        "New Exposure Added",

        "Exposure Exited",

        "Existing Exposure Reallocated",

        "Portfolio_HHI",

        "Effective_Holdings",

        "Active_Share",

        "Portfolio_Stability",

        "Rebalance_Efficiency",

        "Efficiency_Grade",

        "New_Holdings_Pct",

        "Exited_Holdings_Pct",

        "Churn_Ratio",

        "Top_Trade_Share",

        "Execution_Complexity",

        "Turnover_Reconciled",

        "Top5_Weight",

        "Top10_Weight",

        "Gross_Buy_Weight",

        "Gross_Sell_Weight",

        "Net_Flow",

        "Retention_Ratio",

        "Replacement_Rate",

        "Turnover_Flag",

        "Turnover_Scaling_Factor",

        "Capacity_Score",

        "Average_Cost_BPS",

        "Approval_Score",

        "Approval_Status",

        "Execution_Score",

        "Execution_Status",

        "Governance_Status",

        "Rebalance_Health_Score",

        "Breadth_Score",

        "Liquidity_Pressure",

        "Execution_Capacity",

        "Crowding_Score",

        "Regime_Alignment",

        "Risk_Flag_Count",

        "Engine_Version",
    ],

    "Value": [

        current_regime,

        len(portfolio),

        target_holdings,

        buy_orders,

        sell_orders,

        round(
            portfolio_turnover,
            6
        ),

        round(
            buy_turnover,
            6
        ),

        round(
            sell_turnover,
            6
        ),

        round(
            new_position_turnover,
            6
        ),

        round(
            existing_position_turnover,
            6
        ),

        round(
            exit_turnover,
            6
        ),

        round(
            portfolio_hhi,
            6
        ),

        round(
            effective_holdings,
            2
        ),

        round(
            active_share,
            6
        ),

        round(
            portfolio_stability,
            6
        ),

        round(
            rebalance_efficiency,
            4
        ),

        efficiency_grade,

        round(
            new_holdings_pct,
            6
        ),

        round(
            exited_holdings_pct,
            6
        ),

        round(
            churn_ratio,
            6
        ),

        round(
            top_trade_share,
            6
        ),

        round(
            execution_complexity,
            2
        ),

        turnover_reconciled,

        round(
            top5_weight,
            6
        ),

        round(
            top10_weight,
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
            retention_ratio,
            6
        ),

        round(
            replacement_rate,
            6
        ),

        turnover_flag,

        round(
            turnover_scaling_factor,
            4
        ),

        round(
            capacity_score,
            2
        ),

        round(
            avg_cost_bps,
            2
        ),

        approval_score,

        approval_status,

        execution_score,

        execution_status,

        governance_status,

        rebalance_health_score,

        breadth_score,

        liquidity_pressure,

        execution_capacity,

        crowding_score,

        regime_alignment,

        len(risk_flags),

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

        "Portfolio_HHI",

        "Effective_Holdings",

        "Active_Share",

        "Portfolio_Stability",

        "Rebalance_Efficiency",

        "Efficiency_Grade",

        "New_Holdings_Pct",

        "Exited_Holdings_Pct",

        "Churn_Ratio",

        "Execution_Complexity",

        "Top_Trade_Share",

        "Retention_Ratio",

        "Replacement_Rate",

        "Execution_Score",

        "Execution_Status",
        
        "Governance_Status",

        "Rebalance_Health_Score",

        "Breadth_Score",

        "Liquidity_Pressure",

        "Execution_Capacity",

        "Crowding_Score",

        "Regime_Alignment",

        "Risk_Flag_Count",

        "Engine_Version",
    ],

    "Value": [

        datetime.now().strftime(
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

        target_holdings,

        buy_orders,

        sell_orders,

        round(
            portfolio_turnover,
            6
        ),

        round(
            portfolio_hhi,
            6
        ),

        round(
            effective_holdings,
            2
        ),

        round(
            active_share,
            6
        ),

        round(
            portfolio_stability,
            6
        ),

        round(
            rebalance_efficiency,
            4
        ),

        efficiency_grade,

        round(
            new_holdings_pct,
            6
        ),

        round(
            exited_holdings_pct,
            6
        ),

        round(
            churn_ratio,
            6
        ),

        round(
            execution_complexity,
            2
        ),

        round(
            top_trade_share,
            6
        ),

        round(
            retention_ratio,
            6
        ),

        round(
            replacement_rate,
            6
        ),

        execution_score,

        execution_status,

        governance_status,

        rebalance_health_score,

        breadth_score,

        liquidity_pressure,

        execution_capacity,

        crowding_score,

        regime_alignment,
        
        len(risk_flags),

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

institutional_metrics = pd.DataFrame({

    "Metric": [

        "Portfolio_HHI",

        "Effective_Holdings",

        "Active_Share",

        "Portfolio_Stability",

        "Rebalance_Efficiency",

        "Execution_Complexity",

        "Top_Trade_Share",

        "Churn_Ratio",

        "New_Holdings_Pct",

        "Exited_Holdings_Pct",
    ],

    "Value": [

        portfolio_hhi,

        effective_holdings,

        active_share,

        portfolio_stability,

        rebalance_efficiency,

        execution_complexity,

        top_trade_share,

        churn_ratio,

        new_holdings_pct,

        exited_holdings_pct,
    ]
})

institutional_metrics.to_csv(

    OUTPUT_DIR

    / "institutional_rebalance_metrics.csv",

    index=False
)

dashboard.to_csv(
    DASHBOARD_FILE,
    index=False,
)

dashboard.to_csv(
    REPORT_FILE,
    index=False,
)

transition.to_csv(

    OUTPUT_DIR
    / "portfolio_transition_matrix.csv",

    index=False
)

transition_analytics = pd.DataFrame({

    "Metric": [

        "New_Positions",

        "Exited_Positions",

        "Retained_Positions",

        "New_Holdings_Pct",

        "Exited_Holdings_Pct",

        "Churn_Ratio",
    ],

    "Value": [

        new_positions,

        exited_positions,

        retained_positions,

        new_holdings_pct,

        exited_holdings_pct,

        churn_ratio,
    ]
})

transition_analytics.to_csv(

    OUTPUT_DIR

    / "transition_analytics.csv",

    index=False
)

transition_matrix.to_csv(

    OUTPUT_DIR
    / "holdings_transition_summary.csv",

    index=False
)

portfolio_evolution = pd.DataFrame({

    "Metric": [

        "Holdings",
        "HHI",
        "Effective_Holdings",
        "Active_Share",
        "Liquidity_Drift",
        "MarketCap_Drift",
    ],

    "Current": [

        len(portfolio),
        np.nan,
        np.nan,
        np.nan,
        0,
        0,
    ],

    "Target": [

        target_holdings,
        portfolio_hhi,
        effective_holdings,
        active_share,
        liquidity_drift,
        market_cap_drift,
    ]
})

portfolio_evolution.to_csv(

    OUTPUT_DIR
    / "portfolio_evolution.csv",

    index=False
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
    f"{target_holdings}"
)

print(
    f"Portfolio HHI        : "
    f"{portfolio_hhi:.4f}"
)

print(
    f"Effective Holdings   : "
    f"{effective_holdings:.2f}"
)

print(
    f"Top 5 Weight         : "
    f"{top5_weight:.2%}"
)

print(
    f"Top 10 Weight        : "
    f"{top10_weight:.2%}"
)

print(
    f"Active Share         : "
    f"{active_share:.2%}"
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
    f"Buy Turnover         : "
    f"{buy_turnover:.2%}"
)

print(
    f"Sell Turnover        : "
    f"{sell_turnover:.2%}"
)

print(
    f"New Position T/O     : "
    f"{new_position_turnover:.2%}"
)

print(
    f"Existing Position T/O: "
    f"{existing_position_turnover:.2%}"
)

print(
    f"Exit Turnover        : "
    f"{exit_turnover:.2%}"
)

print(
    f"Net Buy Bias       : "
    f"{net_buy_bias:.2%}"
)

print(
    f"Portfolio Stability : "
    f"{portfolio_stability:.2%}"
)

print(
    f"Rebalance Efficiency : "
    f"{rebalance_efficiency:.2f}"
)

print(
    f"Governance Status  : "
    f"{governance_status}"
)

print(
    f"Risk Flags         : "
    f"{len(risk_flags)}"
)

print(
    f"Risk Flag Detail   : "
    f"{risk_flags}"
)

print(
    f"Health Score       : "
    f"{rebalance_health_score:.2f}"
)

print(
    f"Breadth Score      : "
    f"{breadth_score:.2%}"
)

print(
    f"Execution Capacity : "
    f"{execution_capacity:.2f}"
)

print(
    f"Crowding Score     : "
    f"{crowding_score:.4f}"
)

print(
    f"Regime Alignment   : "
    f"{regime_alignment:.0f}"
)

print(
    f"Efficiency Grade     : "
    f"{efficiency_grade}"
)

print(
    f"Retention Ratio      : "
    f"{retention_ratio:.2%}"
)

print(
    f"Replacement Rate     : "
    f"{replacement_rate:.2%}"
)

print(
    f"Turnover Flag        : "
    f"{turnover_flag}"
)

print(
    f"Scaling Factor       : "
    f"{turnover_scaling_factor:.4f}"
)

print(
    f"Approval Score     : "
    f"{approval_score:.0f}"
)

print(
    f"Approval Status    : "
    f"{approval_status}"
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
    f"Market Cap Drift   : "
    f"{market_cap_drift:.2%}"
)

if not np.isnan(liquidity_drift):

    print(
        f"Liquidity Drift    : "
        f"{liquidity_drift:.2%}"
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