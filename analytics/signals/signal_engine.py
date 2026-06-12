"""
=========================================================
SIGNAL ENGINE
=========================================================

Purpose:
Institutional Security Signal Generation

Outputs:
signal_master.csv
buy_list.csv
sell_list.csv
watchlist.csv
signal_dashboard.csv

=========================================================
"""

from pathlib import Path
from datetime import datetime

import pandas as pd
import numpy as np

# =========================================================
# CONFIG
# =========================================================

ENGINE_VERSION = "1.0.0"

BUY_THRESHOLD = 70
STRONG_BUY_THRESHOLD = 85

REDUCE_THRESHOLD = 40
SELL_THRESHOLD = 25

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

FACTOR_FILE = (
    ROOT
    / "data"
    / "factors"
    / "factor_snapshot_master.csv"
)

REGIME_FILE = (
    ROOT
    / "data"
    / "regime"
    / "market_regime.csv"
)

PORTFOLIO_FILE = (
    ROOT
    / "data"
    / "portfolios"
    / "live_portfolio.csv"
)

OUTPUT_DIR = (
    ROOT
    / "data"
    / "signals"
)

REPORT_FILE = (
    ROOT
    / "data"
    / "logs"
    / "signal_report.csv"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

# =========================================================
# LOAD
# =========================================================

print(
    "\n📥 Loading Inputs..."
)

factors = pd.read_csv(
    FACTOR_FILE
)

regime = pd.read_csv(
    REGIME_FILE
)

portfolio = pd.read_csv(
    PORTFOLIO_FILE
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
# CURRENT REGIME
# =========================================================

current_regime = (
    regime.iloc[-1]["Regime"]
)

regime_bonus = 0

if "BULL_LOW_VOL" in current_regime:
    regime_bonus = 15

elif "BULL" in current_regime:
    regime_bonus = 10

elif "BEAR_HIGH_VOL" in current_regime:
    regime_bonus = -15

elif "BEAR" in current_regime:
    regime_bonus = -10

# =========================================================
# RANKS
# =========================================================

factors["MOM12"] = (
    factors["Momentum_12M"]
    .rank(pct=True)
)

factors["MOM6"] = (
    factors["Momentum_6M"]
    .rank(pct=True)
)

factors["MOM3"] = (
    factors["Momentum_3M"]
    .rank(pct=True)
)

factors["TREND"] = (
    factors["Distance_SMA200"]
    .rank(pct=True)
)

factors["LIQ"] = (
    factors["ADV_20D"]
    .rank(pct=True)
)

factors["VOL"] = 1 - (
    factors["Volatility_60D"]
    .rank(pct=True)
)

factors["DD"] = 1 - (
    factors["Max_Drawdown_252D"]
    .rank(pct=True)
)

# =========================================================
# SIGNAL SCORE
# =========================================================

factors["Signal_Score"] = (

      20 * factors["MOM12"]

    + 15 * factors["MOM6"]

    + 10 * factors["MOM3"]

    + 15 * factors["TREND"]

    + 10 * factors["LIQ"]

    + 15 * factors["VOL"]

    + 15 * factors["DD"]

)

factors["Signal_Score"] += (
    regime_bonus
)

factors["Signal_Score"] = (
    factors["Signal_Score"]
    .clip(0, 100)
)

# =========================================================
# PORTFOLIO FLAG
# =========================================================

current_positions = set(
    portfolio["Symbol"]
)

factors["In_Portfolio"] = (
    factors["Symbol"]
    .isin(current_positions)
)

# =========================================================
# CLASSIFICATION
# =========================================================

def classify(score):

    if score >= STRONG_BUY_THRESHOLD:
        return "STRONG_BUY"

    elif score >= BUY_THRESHOLD:
        return "BUY"

    elif score >= REDUCE_THRESHOLD:
        return "HOLD"

    elif score >= SELL_THRESHOLD:
        return "REDUCE"

    return "SELL"

factors["Signal"] = (
    factors["Signal_Score"]
    .apply(classify)
)

# =========================================================
# MASTER
# =========================================================

signal_master = factors[[
    "Symbol",
    "Company_Name",
    "Sector",
    "Signal",
    "Signal_Score",
    "In_Portfolio",
]]

signal_master = signal_master.sort_values(
    "Signal_Score",
    ascending=False,
)

# =========================================================
# BUY LIST
# =========================================================

buy_list = signal_master[
    signal_master["Signal"].isin(
        [
            "STRONG_BUY",
            "BUY",
        ]
    )
]

# =========================================================
# SELL LIST
# =========================================================

sell_list = signal_master[
    signal_master["Signal"].isin(
        [
            "SELL",
            "REDUCE",
        ]
    )
]

# =========================================================
# WATCHLIST
# =========================================================

watchlist = signal_master.head(
    100
)

# =========================================================
# DASHBOARD
# =========================================================

dashboard = pd.DataFrame({

    "Metric": [

        "Regime",

        "Strong_Buys",

        "Buys",

        "Holds",

        "Reduces",

        "Sells",
    ],

    "Value": [

        current_regime,

        (
            signal_master["Signal"]
            == "STRONG_BUY"
        ).sum(),

        (
            signal_master["Signal"]
            == "BUY"
        ).sum(),

        (
            signal_master["Signal"]
            == "HOLD"
        ).sum(),

        (
            signal_master["Signal"]
            == "REDUCE"
        ).sum(),

        (
            signal_master["Signal"]
            == "SELL"
        ).sum(),
    ]
})

# =========================================================
# SAVE
# =========================================================

signal_master.to_csv(
    OUTPUT_DIR
    / "signal_master.csv",
    index=False,
)

buy_list.to_csv(
    OUTPUT_DIR
    / "buy_list.csv",
    index=False,
)

sell_list.to_csv(
    OUTPUT_DIR
    / "sell_list.csv",
    index=False,
)

watchlist.to_csv(
    OUTPUT_DIR
    / "watchlist.csv",
    index=False,
)

dashboard.to_csv(
    OUTPUT_DIR
    / "signal_dashboard.csv",
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
    "🏁 SIGNAL ENGINE COMPLETE"
)

print("=" * 70)

print(
    f"Regime       : {current_regime}"
)

print(
    f"Strong Buys  : "
    f"{(signal_master['Signal']=='STRONG_BUY').sum()}"
)

print(
    f"Buys         : "
    f"{(signal_master['Signal']=='BUY').sum()}"
)

print(
    f"Sells        : "
    f"{(signal_master['Signal']=='SELL').sum()}"
)

print(
    f"\nOutput Directory:\n{OUTPUT_DIR}"
)

print("=" * 70)