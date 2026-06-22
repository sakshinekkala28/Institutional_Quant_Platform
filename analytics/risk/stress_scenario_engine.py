"""
=========================================================
STRESS SCENARIO ENGINE
=========================================================

Purpose:
Institutional Portfolio Stress Testing

Inputs:
data/portfolios/live_portfolio.csv
data/factors/factor_master.csv

Outputs:
data/stress_tests/stress_results.csv
data/stress_tests/stress_dashboard.csv
data/stress_tests/stress_summary.csv
data/stress_tests/stress_sector_impact.csv
data/stress_tests/stress_position_impact.csv

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

MIN_PORTFOLIO_SIZE = 20

# =========================================================
# SCENARIO LIBRARY
# =========================================================

SCENARIOS = {

    "MARKET_CRASH": {

        "Description":
        "Broad Market Selloff",

        "Default_Shock":
        -0.30,
    },

    "FINANCIAL_CRISIS": {

        "Description":
        "Banking System Stress",

        "Sector_Shocks": {

            "Financial Services":
            -0.25,

            "Banks":
            -0.25,

            "Insurance":
            -0.20,
        },

        "Default_Shock":
        -0.15,
    },

    "RATE_SHOCK": {

        "Description":
        "Interest Rate Spike",

        "Sector_Shocks": {

            "Utilities":
            -0.20,

            "Real Estate":
            -0.20,

            "Financial Services":
             0.10,
        },

        "Default_Shock":
        -0.05,
    },

    "COMMODITY_SHOCK": {

        "Description":
        "Commodity Price Surge",

        "Sector_Shocks": {

            "Energy":
             0.15,

            "Industrials":
            -0.10,

            "Consumer Cyclical":
            -0.08,
        },

        "Default_Shock":
        -0.05,
    },

    "COVID_EVENT": {

        "Description":
        "Pandemic Shock",

        "Sector_Shocks": {

            "Healthcare":
             0.10,

            "Technology":
             0.05,

            "Financial Services":
            -0.25,

            "Travel":
            -0.40,
        },

        "Default_Shock":
        -0.10,
    },
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

FACTOR_FILE = (
    ROOT
    / "data"
    / "factors"
    / "factor_master.csv"
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
# LOAD DATA
# =========================================================

print(
    "\n📥 Loading Inputs..."
)

portfolio = pd.read_csv(
    PORTFOLIO_FILE
)

factor_master = pd.read_csv(
    FACTOR_FILE
)

# =========================================================
# VALIDATION
# =========================================================

required_portfolio = [

    "Symbol",
    "Weight",
    "Sector",
]

required_factor = [

    "Symbol",
    "Sector",
    "Market_Cap",
]

for col in required_portfolio:

    if col not in portfolio.columns:

        raise ValueError(
            f"Missing Portfolio Column: {col}"
        )

for col in required_factor:

    if col not in factor_master.columns:

        raise ValueError(
            f"Missing Factor Column: {col}"
        )

if len(portfolio) < MIN_PORTFOLIO_SIZE:

    raise ValueError(
        f"Portfolio too small: "
        f"{len(portfolio)}"
    )

# =========================================================
# NORMALIZE WEIGHTS
# =========================================================

portfolio["Weight"] = pd.to_numeric(

    portfolio["Weight"],

    errors="coerce"
)

portfolio = portfolio.dropna(
    subset=["Weight"]
)

portfolio["Weight"] = (

    portfolio["Weight"]

    /

    portfolio["Weight"].sum()
)

# =========================================================
# MERGE FACTOR DATA
# =========================================================

stress_df = portfolio.merge(

    factor_master[[
        "Symbol",
        "Sector",
        "Market_Cap",
    ]],

    on="Symbol",

    how="left",

    suffixes=(
        "",
        "_factor"
    )
)

coverage = (

    stress_df[
        "Market_Cap"
    ]

    .notna()

    .mean()
)

if coverage < 0.90:

    raise ValueError(

        "Factor coverage too low: "

        f"{coverage:.2%}"
    )

# =========================================================
# POSITION VALUES
# =========================================================

stress_df[
    "Position_Value"
] = (

    stress_df[
        "Weight"
    ]

    * PORTFOLIO_NAV
)

# =========================================================
# DIAGNOSTICS
# =========================================================

print(
    f"Portfolio Holdings : "
    f"{len(portfolio)}"
)

print(
    f"Factor Coverage    : "
    f"{coverage:.2%}"
)

print(
    f"Scenarios Loaded   : "
    f"{len(SCENARIOS)}"
)

for scenario in SCENARIOS:

    print(
        f"✓ {scenario}"
    )

# =========================================================
# PART 2 STARTS HERE
# =========================================================
#
# Next:
#
# Scenario Shock Engine
# Position-Level Stress
# Loss Calculations
# Scenario Impact
#
# =========================================================

# =========================================================
# SCENARIO ENGINE
# =========================================================

print(
    "\n📉 Running Stress Scenarios..."
)

scenario_results = []

position_results = []

# =========================================================
# PROCESS SCENARIOS
# =========================================================

for scenario_name, scenario in SCENARIOS.items():

    print(
        f"\nRunning: {scenario_name}"
    )

    tmp = stress_df.copy()

    # =====================================================
    # SHOCK ASSIGNMENT
    # =====================================================

    default_shock = scenario.get(
        "Default_Shock",
        -0.10
    )

    tmp["Shock"] = default_shock

    if "Sector_Shocks" in scenario:

        sector_shocks = scenario[
            "Sector_Shocks"
        ]

        for sector, shock in sector_shocks.items():

            tmp.loc[

                tmp["Sector"]
                .astype(str)
                .str.upper()

                ==

                sector.upper(),

                "Shock"

            ] = shock

    # =====================================================
    # POSITION IMPACT
    # =====================================================

    tmp[
        "Stress_Return"
    ] = tmp[
        "Shock"
    ]

    tmp[
        "Stress_PnL"
    ] = (

        tmp[
            "Position_Value"
        ]

        *

        tmp[
            "Stress_Return"
        ]
    )

    tmp[
        "Stress_Value"
    ] = (

        tmp[
            "Position_Value"
        ]

        +

        tmp[
            "Stress_PnL"
        ]
    )

    tmp[
        "Scenario"
    ] = scenario_name

    # =====================================================
    # CONTRIBUTION
    # =====================================================

    tmp[
        "Loss_Contribution"
    ] = (

        tmp[
            "Stress_PnL"
        ]

        /

        PORTFOLIO_NAV
    )

    # =====================================================
    # POSITION STORAGE
    # =====================================================

    position_results.append(

        tmp[[

            "Scenario",

            "Symbol",

            "Company_Name",

            "Sector",

            "Weight",

            "Position_Value",

            "Shock",

            "Stress_Return",

            "Stress_PnL",

            "Stress_Value",

            "Loss_Contribution",
        ]]
    )

    # =====================================================
    # PORTFOLIO SUMMARY
    # =====================================================

    portfolio_pnl = (

        tmp[
            "Stress_PnL"
        ].sum()
    )

    portfolio_loss_pct = (

        portfolio_pnl

        /

        PORTFOLIO_NAV
    )

    stressed_nav = (

        PORTFOLIO_NAV

        +

        portfolio_pnl
    )

    scenario_results.append({

        "Scenario":
        scenario_name,

        "Description":
        scenario[
            "Description"
        ],

        "Portfolio_NAV":
        PORTFOLIO_NAV,

        "Stress_NAV":
        stressed_nav,

        "Portfolio_PnL":
        portfolio_pnl,

        "Portfolio_Return":
        portfolio_loss_pct,
    })

# =========================================================
# RESULTS DATAFRAMES
# =========================================================

scenario_results = pd.DataFrame(
    scenario_results
)

position_impact = pd.concat(

    position_results,

    ignore_index=True
)

# =========================================================
# RANK POSITIONS
# =========================================================

position_impact[
    "Loss_Rank"
] = (

    position_impact

    .groupby(
        "Scenario"
    )

    [
        "Stress_PnL"
    ]

    .rank(
        method="first"
    )
)

# =========================================================
# TOP LOSERS
# =========================================================

worst_positions = (

    position_impact

    .sort_values(
        "Stress_PnL"
    )

    .groupby(
        "Scenario"
    )

    .head(10)

    .copy()
)

# =========================================================
# TOP WINNERS
# =========================================================

best_positions = (

    position_impact

    .sort_values(
        "Stress_PnL",
        ascending=False
    )

    .groupby(
        "Scenario"
    )

    .head(10)

    .copy()
)

# =========================================================
# SCENARIO RANKING
# =========================================================

scenario_results = (

    scenario_results

    .sort_values(

        "Portfolio_Return"

    )

    .reset_index(
        drop=True
    )
)

scenario_results[
    "Scenario_Rank"
] = (
    scenario_results.index + 1
)

# =========================================================
# WORST SCENARIO
# =========================================================

worst_scenario = (

    scenario_results

    .iloc[0]
)

best_scenario = (

    scenario_results

    .iloc[-1]
)

# =========================================================
# DIAGNOSTICS
# =========================================================

print(
    f"\nWorst Scenario : "
    f"{worst_scenario['Scenario']}"
)

print(
    f"Portfolio Loss : "
    f"{worst_scenario['Portfolio_Return']:.2%}"
)

print(
    f"\nBest Scenario  : "
    f"{best_scenario['Scenario']}"
)

print(
    f"Portfolio Loss : "
    f"{best_scenario['Portfolio_Return']:.2%}"
)

# =========================================================
# PART 3 STARTS HERE
# =========================================================
#
# Next:
#
# Sector Stress Attribution
# Sector Damage Ranking
# Sector Concentration Impact
# Scenario Dashboard
#
# =========================================================

# =========================================================
# SECTOR STRESS ATTRIBUTION
# =========================================================

print(
    "\n🏭 Building Sector Stress Attribution..."
)

sector_impact = (

    position_impact

    .groupby(

        [
            "Scenario",
            "Sector"
        ]

    )

    .agg({

        "Position_Value":
        "sum",

        "Stress_PnL":
        "sum",

        "Stress_Value":
        "sum",
    })

    .reset_index()
)

# =========================================================
# SECTOR RETURN
# =========================================================

sector_impact[
    "Stress_Return"
] = (

    sector_impact[
        "Stress_PnL"
    ]

    /

    sector_impact[
        "Position_Value"
    ]
)

# =========================================================
# SECTOR CONTRIBUTION
# =========================================================

sector_impact[
    "Loss_Contribution"
] = (

    sector_impact[
        "Stress_PnL"
    ]

    /

    PORTFOLIO_NAV
)

# =========================================================
# DAMAGE RANK
# =========================================================

sector_impact[
    "Damage_Rank"
] = (

    sector_impact

    .groupby(
        "Scenario"
    )

    [
        "Stress_PnL"
    ]

    .rank(
        method="dense"
    )
)

# =========================================================
# MOST DAMAGED SECTOR
# =========================================================

worst_sector = (

    sector_impact

    .sort_values(
        "Stress_PnL"
    )

    .iloc[0]
)

# =========================================================
# LEAST DAMAGED SECTOR
# =========================================================

best_sector = (

    sector_impact

    .sort_values(
        "Stress_PnL",
        ascending=False
    )

    .iloc[0]
)

# =========================================================
# SCENARIO DASHBOARD
# =========================================================

stress_dashboard = (

    scenario_results[[

        "Scenario",

        "Description",

        "Portfolio_NAV",

        "Stress_NAV",

        "Portfolio_PnL",

        "Portfolio_Return",

        "Scenario_Rank",
    ]]

    .copy()
)

# =========================================================
# SECTOR HEATMAP DATASET
# =========================================================

stress_heatmap = (

    sector_impact

    .pivot_table(

        index="Sector",

        columns="Scenario",

        values="Stress_Return",

        aggfunc="mean"
    )
)

stress_heatmap.to_csv(

    OUTPUT_DIR
    / "stress_heatmap.csv"
)

# =========================================================
# TOP 10 SECTOR LOSERS
# =========================================================

top_sector_losers = (

    sector_impact

    .sort_values(
        "Stress_PnL"
    )

    .groupby(
        "Scenario"
    )

    .head(10)

    .copy()
)

# =========================================================
# TOP 10 SECTOR WINNERS
# =========================================================

top_sector_winners = (

    sector_impact

    .sort_values(
        "Stress_PnL",
        ascending=False
    )

    .groupby(
        "Scenario"
    )

    .head(10)

    .copy()
)

# =========================================================
# SCENARIO STATISTICS
# =========================================================

average_loss = (

    scenario_results[
        "Portfolio_Return"
    ]

    .mean()
)

worst_loss = (

    scenario_results[
        "Portfolio_Return"
    ]

    .min()
)

best_loss = (

    scenario_results[
        "Portfolio_Return"
    ]

    .max()
)

# =========================================================
# DAMAGE SUMMARY
# =========================================================

damage_summary = pd.DataFrame({

    "Metric": [

        "Average_Stress_Return",

        "Worst_Stress_Return",

        "Best_Stress_Return",

        "Worst_Sector",

        "Best_Sector",
    ],

    "Value": [

        average_loss,

        worst_loss,

        best_loss,

        worst_sector[
            "Sector"
        ],

        best_sector[
            "Sector"
        ],
    ]
})

# =========================================================
# DIAGNOSTICS
# =========================================================

print(
    f"\nWorst Sector : "
    f"{worst_sector['Sector']}"
)

print(
    f"Loss         : "
    f"{worst_sector['Stress_PnL']:,.0f}"
)

print(
    f"\nBest Sector  : "
    f"{best_sector['Sector']}"
)

print(
    f"Loss         : "
    f"{best_sector['Stress_PnL']:,.0f}"
)

# =========================================================
# PART 4 STARTS HERE
# =========================================================
#
# Next:
#
# Stress VaR
# Expected Shortfall
# Scenario Risk Score
# Executive Summary
# Save Outputs
# Final Reporting
#
# =========================================================

# =========================================================
# STRESS VAR
# =========================================================

print(
    "\n⚠ Calculating Stress Risk Metrics..."
)

stress_returns = (

    scenario_results[
        "Portfolio_Return"
    ]

    .values
)

# =========================================================
# VAR 95
# =========================================================

stress_var_95 = np.percentile(
    stress_returns,
    5
)

# =========================================================
# CVAR 95
# =========================================================

tail_returns = stress_returns[

    stress_returns
    <=
    stress_var_95
]

if len(tail_returns) > 0:

    stress_cvar_95 = (
        tail_returns.mean()
    )

else:

    stress_cvar_95 = (
        stress_var_95
    )

# =========================================================
# WORST CASE LOSS
# =========================================================

worst_case_loss = (

    scenario_results[
        "Portfolio_PnL"
    ]

    .min()
)

worst_case_return = (

    scenario_results[
        "Portfolio_Return"
    ]

    .min()
)

# =========================================================
# BEST CASE LOSS
# =========================================================

best_case_loss = (

    scenario_results[
        "Portfolio_PnL"
    ]

    .max()
)

best_case_return = (

    scenario_results[
        "Portfolio_Return"
    ]

    .max()
)

# =========================================================
# SCENARIO RISK SCORE
# =========================================================

scenario_risk_score = min(

    abs(
        worst_case_return
    )

    * 100,

    100
)

# =========================================================
# RESILIENCE SCORE
# =========================================================

resilience_score = (

    100

    -

    scenario_risk_score
)

resilience_score = max(
    resilience_score,
    0
)

# =========================================================
# SCENARIO DISPERSION
# =========================================================

scenario_dispersion = (

    scenario_results[
        "Portfolio_Return"
    ]

    .std()
)

# =========================================================
# STRESS CLASSIFICATION
# =========================================================

if abs(
    worst_case_return
) < 0.10:

    risk_level = "LOW"

elif abs(
    worst_case_return
) < 0.20:

    risk_level = "MODERATE"

elif abs(
    worst_case_return
) < 0.30:

    risk_level = "HIGH"

else:

    risk_level = "SEVERE"

# =========================================================
# EXECUTIVE SUMMARY
# =========================================================

stress_summary = pd.DataFrame({

    "Metric": [

        "Worst_Scenario",

        "Worst_Return",

        "Worst_Loss",

        "Best_Scenario",

        "Best_Return",

        "Best_Loss",

        "Stress_VaR_95",

        "Stress_CVaR_95",

        "Scenario_Risk_Score",

        "Resilience_Score",

        "Scenario_Dispersion",

        "Risk_Level",

        "Run_Date",

        "Engine_Version",
    ],

    "Value": [

        worst_scenario[
            "Scenario"
        ],

        worst_case_return,

        worst_case_loss,

        best_scenario[
            "Scenario"
        ],

        best_case_return,

        best_case_loss,

        stress_var_95,

        stress_cvar_95,

        scenario_risk_score,

        resilience_score,

        scenario_dispersion,

        risk_level,

        datetime.now()
        .strftime(
            "%Y-%m-%d"
        ),

        ENGINE_VERSION,
    ]
})

# =========================================================
# SAVE OUTPUTS
# =========================================================

scenario_results.to_csv(

    OUTPUT_DIR
    / "stress_results.csv",

    index=False,
)

stress_dashboard.to_csv(

    OUTPUT_DIR
    / "stress_dashboard.csv",

    index=False,
)

stress_summary.to_csv(

    OUTPUT_DIR
    / "stress_summary.csv",

    index=False,
)

sector_impact.to_csv(

    OUTPUT_DIR
    / "stress_sector_impact.csv",

    index=False,
)

position_impact.to_csv(

    OUTPUT_DIR
    / "stress_position_impact.csv",

    index=False,
)

top_sector_losers.to_csv(

    OUTPUT_DIR
    / "top_sector_losers.csv",

    index=False,
)

top_sector_winners.to_csv(

    OUTPUT_DIR
    / "top_sector_winners.csv",

    index=False,
)

worst_positions.to_csv(

    OUTPUT_DIR
    / "worst_positions.csv",

    index=False,
)

best_positions.to_csv(

    OUTPUT_DIR
    / "best_positions.csv",

    index=False,
)

stress_summary.to_csv(

    REPORT_FILE,

    index=False,
)

# =========================================================
# FINAL REPORT
# =========================================================

print(
    "\n"
    + "=" * 70
)

print(
    "🏁 STRESS SCENARIO ENGINE COMPLETE"
)

print(
    "=" * 70
)

print(
    f"Worst Scenario      : "
    f"{worst_scenario['Scenario']}"
)

print(
    f"Worst Return        : "
    f"{worst_case_return:.2%}"
)

print(
    f"Worst Loss          : "
    f"{worst_case_loss:,.0f}"
)

print(
    f"\nBest Scenario       : "
    f"{best_scenario['Scenario']}"
)

print(
    f"Best Return         : "
    f"{best_case_return:.2%}"
)

print(
    f"\nStress VaR (95%)    : "
    f"{stress_var_95:.2%}"
)

print(
    f"Stress CVaR (95%)   : "
    f"{stress_cvar_95:.2%}"
)

print(
    f"\nRisk Score          : "
    f"{scenario_risk_score:.2f}"
)

print(
    f"Resilience Score    : "
    f"{resilience_score:.2f}"
)

print(
    f"Risk Level          : "
    f"{risk_level}"
)

print(
    f"\nWorst Sector        : "
    f"{worst_sector['Sector']}"
)

print(
    f"Most Crowded Loss   : "
    f"{worst_sector['Stress_PnL']:,.0f}"
)

print(
    f"\nOutput Directory:\n"
    f"{OUTPUT_DIR}"
)

print(
    "=" * 70
)