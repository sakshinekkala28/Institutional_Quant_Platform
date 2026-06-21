"""
=========================================================
STRESS TEST ENGINE
=========================================================

Purpose:
Institutional Portfolio Stress Testing

Inputs:
data/portfolios/live_portfolio.csv
data/liquidity/liquidity_master.csv
data/capacity/capacity_master.csv

Outputs:
data/stress_tests/stress_results.csv
data/stress_tests/stress_summary.csv
data/stress_tests/stress_dashboard.csv

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

# =========================================================
# STRESS SCENARIOS
# =========================================================

SCENARIOS = {

    "MARKET_CRASH_30": {
        "market_shock": -0.30,
        "liquidity_shock": 1.00,
    },

    "MARKET_CRASH_50": {
        "market_shock": -0.50,
        "liquidity_shock": 1.00,
    },

    "COVID_STYLE_CRASH": {
        "market_shock": -0.35,
        "liquidity_shock": 0.50,
    },

    "LIQUIDITY_FREEZE": {
        "market_shock": -0.15,
        "liquidity_shock": 0.25,
    },

    "SMALL_CAP_CRASH": {
        "market_shock": -0.20,
        "liquidity_shock": 0.75,
    },

    "RATE_SHOCK": {
        "market_shock": -0.12,
        "liquidity_shock": 0.80,
    }
}

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

CAPACITY_FILE = (
    ROOT
    / "data"
    / "capacity"
    / "capacity_master.csv"
)

OUTPUT_DIR = (
    ROOT
    / "data"
    / "stress_tests"
)

REPORT_FILE = (
    ROOT
    / "data"
    / "logs"
    / "stress_test_report.csv"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

# =========================================================
# LOAD
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

capacity = pd.read_csv(
    CAPACITY_FILE
)

# =========================================================
# NORMALIZE
# =========================================================

for df in [
    portfolio,
    liquidity,
    capacity,
]:

    df["Symbol"] = (
        df["Symbol"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

# =========================================================
# MERGE
# =========================================================

merged = portfolio.merge(

    liquidity[
        [
            "Symbol",
            "Liquidity_Score",
        ]
    ],

    on="Symbol",
    how="left",
)

merged = merged.merge(

    capacity[
        [
            "Symbol",
            "Capacity_Score",
            "Days_To_Exit",
        ]
    ],

    on="Symbol",
    how="left",
)

# =========================================================
# POSITION VALUE
# =========================================================

merged["Position_Value"] = (

    merged["Weight"]

    * PORTFOLIO_NAV
)

# =========================================================
# STRESS TEST LOOP
# =========================================================

results = []

for scenario_name, scenario in SCENARIOS.items():

    market_shock = scenario[
        "market_shock"
    ]

    liquidity_shock = scenario[
        "liquidity_shock"
    ]

    scenario_df = merged.copy()

    # =====================================
    # BASE LOSS
    # =====================================

    scenario_df["Loss"] = (

        scenario_df[
            "Position_Value"
        ]

        * abs(
            market_shock
        )
    )

    # =====================================
    # SMALL CAP CRASH
    # =====================================

    if scenario_name == "SMALL_CAP_CRASH":

        small_cap = (
            scenario_df[
                "Market_Cap"
            ]

            < scenario_df[
                "Market_Cap"
            ].median()
        )

        scenario_df.loc[
            small_cap,
            "Loss"
        ] *= 1.5

    # =====================================
    # LIQUIDITY SHOCK
    # =====================================

    scenario_df[
        "Stressed_ADV"
    ] = (

        scenario_df[
            "ADV_20D"
        ]

        * liquidity_shock
    )

    scenario_df[
        "Stressed_Days_To_Exit"
    ] = (

        scenario_df[
            "Days_To_Exit"
        ]

        / np.maximum(
            liquidity_shock,
            0.01,
        )
    )

    # =====================================
    # PORTFOLIO METRICS
    # =====================================

    total_loss = (
        scenario_df[
            "Loss"
        ].sum()
    )

    stressed_nav = (

        PORTFOLIO_NAV

        - total_loss
    )

    portfolio_return = (

        stressed_nav

        / PORTFOLIO_NAV

        - 1
    )

    avg_days_exit = (

        scenario_df[
            "Stressed_Days_To_Exit"
        ].mean()
    )

    results.append({

        "Scenario":
        scenario_name,

        "Portfolio_NAV":
        PORTFOLIO_NAV,

        "Stressed_NAV":
        stressed_nav,

        "Portfolio_Return":
        portfolio_return,

        "Total_Loss":
        total_loss,

        "Average_Days_To_Exit":
        avg_days_exit,

        "Liquidity_Shock":
        liquidity_shock,

        "Market_Shock":
        market_shock,
    })

# =========================================================
# RESULTS
# =========================================================

stress_results = pd.DataFrame(
    results
)

stress_results = (
    stress_results
    .sort_values(
        "Portfolio_Return"
    )
)

# =========================================================
# DASHBOARD
# =========================================================

dashboard = pd.DataFrame({

    "Metric": [

        "Worst_Scenario",

        "Worst_Return",

        "Worst_Loss",

        "Average_Stress_Return",

        "Run_Date",

        "Engine_Version",
    ],

    "Value": [

        stress_results.iloc[
            0
        ]["Scenario"],

        stress_results.iloc[
            0
        ]["Portfolio_Return"],

        stress_results.iloc[
            0
        ]["Total_Loss"],

        stress_results[
            "Portfolio_Return"
        ].mean(),

        datetime.now()
        .strftime(
            "%Y-%m-%d"
        ),

        ENGINE_VERSION,
    ]
})

# =========================================================
# SUMMARY
# =========================================================

summary = stress_results.copy()

summary["Loss_Pct"] = (

    summary[
        "Total_Loss"
    ]

    / PORTFOLIO_NAV
)

# =========================================================
# SAVE
# =========================================================

stress_results.to_csv(

    OUTPUT_DIR
    / "stress_results.csv",

    index=False,
)

summary.to_csv(

    OUTPUT_DIR
    / "stress_summary.csv",

    index=False,
)

dashboard.to_csv(

    OUTPUT_DIR
    / "stress_dashboard.csv",

    index=False,
)

dashboard.to_csv(

    REPORT_FILE,

    index=False,
)

# =========================================================
# REPORT
# =========================================================

worst = stress_results.iloc[0]

print("\n" + "=" * 70)

print(
    "🏁 STRESS TEST ENGINE COMPLETE"
)

print("=" * 70)

print(
    f"Worst Scenario      : "
    f"{worst['Scenario']}"
)

print(
    f"Worst Return        : "
    f"{worst['Portfolio_Return']:.2%}"
)

print(
    f"Worst Loss          : "
    f"₹{worst['Total_Loss']:,.0f}"
)

print(
    f"Average Stress Ret  : "
    f"{stress_results['Portfolio_Return'].mean():.2%}"
)

print(
    f"\nOutput Directory:\n"
    f"{OUTPUT_DIR}"
)

print("=" * 70)