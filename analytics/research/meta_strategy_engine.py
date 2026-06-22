"""
=========================================================
META STRATEGY ENGINE
=========================================================

Purpose:
Institutional Dynamic Strategy Allocation

=========================================================
"""

from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd

ENGINE_VERSION = "1.0.0"

ROOT = Path(__file__).resolve().parents[2]

REGIME_FILE = (
    ROOT
    / "data"
    / "regime"
    / "market_regime.csv"
)

STRATEGY_FILE = (
    ROOT
    / "data"
    / "research"
    / "strategy_comparison.csv"
)

OUTPUT_DIR = (
    ROOT
    / "data"
    / "research"
)

REPORT_FILE = (
    ROOT
    / "data"
    / "logs"
    / "meta_strategy_report.csv"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

print(
    "\n📥 Loading Data..."
)

regime = pd.read_csv(
    REGIME_FILE
)

strategy = pd.read_csv(
    STRATEGY_FILE
)

current_regime = (
    regime.iloc[-1]["Regime"]
)

if "Score" not in strategy.columns:

    if "Sharpe" in strategy.columns:

        strategy["Score"] = (
            strategy["Sharpe"]
            .rank(pct=True)
            * 100
        )

    else:

        strategy["Score"] = 50

# Regime Tilt

if "BULL" in current_regime:

    strategy["Score"] *= 1.10

elif "BEAR" in current_regime:

    strategy["Score"] *= 0.90

strategy["Weight"] = (

    strategy["Score"]

    / strategy["Score"].sum()
)

allocation = strategy[

    [
        "Strategy",
        "Score",
        "Weight",
    ]

].sort_values(
    "Weight",
    ascending=False
)

allocation["Weight"] = (
    allocation["Weight"]
    .round(6)
)

top_strategy = (
    allocation
    .sort_values(
        "Weight",
        ascending=False
    )
    .iloc[0]
)

dashboard = pd.DataFrame({

    "Metric": [

        "Current_Regime",

        "Strategy_Count",

        "Top_Strategy",

        "Top_Weight",

        "Average_Score",

        "Run_Date",
    ],

    "Value": [

        current_regime,

        len(allocation),

        top_strategy["Strategy"],

        round(
            top_strategy["Weight"],
            4,
        ),

        round(
            allocation[
                "Score"
            ].mean(),
            2,
        ),

        datetime.now()
        .strftime(
            "%Y-%m-%d"
        ),
    ]
})

dashboard.to_csv(
    OUTPUT_DIR
    / "meta_strategy_dashboard.csv",
    index=False,
)


allocation.to_csv(
    OUTPUT_DIR
    / "meta_strategy_allocation.csv",
    index=False,
)

weights = allocation[
    [
        "Strategy",
        "Weight",
    ]
].copy()

weights.to_csv(
    OUTPUT_DIR
    / "meta_strategy_weights.csv",
    index=False,
)


pd.DataFrame({

    "Metric": [
        "Current_Regime",
        "Strategies",
        "Run_Date",
        "Engine_Version",
    ],

    "Value": [
        current_regime,
        len(allocation),
        datetime.now().strftime(
            "%Y-%m-%d"
        ),
        ENGINE_VERSION,
    ]

}).to_csv(
    REPORT_FILE,
    index=False,
)

print("\n" + "=" * 70)
print("🏁 META STRATEGY ENGINE COMPLETE")
print("=" * 70)
print(
    f"Current Regime : "
    f"{current_regime}"
)
print(
    f"Strategies     : "
    f"{len(allocation)}"
)
print("=" * 70)