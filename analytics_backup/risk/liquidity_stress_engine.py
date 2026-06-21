"""
=========================================================
LIQUIDITY STRESS ENGINE
=========================================================

Purpose:
Institutional Liquidity Risk & Capacity Analysis

Inputs:
data/portfolios/live_portfolio.csv
data/factors/factor_master.csv

Outputs:
data/liquidity/liquidity_stress_results.csv
data/liquidity/liquidity_stress_summary.csv
data/liquidity/liquidity_stress_dashboard.csv
data/liquidity/position_liquidity_risk.csv
data/liquidity/capacity_analysis.csv
data/liquidity/liquidation_schedule.csv

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

# Institutional Participation Rate
PARTICIPATION_RATE = 0.20

# Capacity Participation
CAPACITY_PARTICIPATION = 0.10

# Market Impact Multiplier
IMPACT_MULTIPLIER = 0.10

# =========================================================
# LIQUIDITY STRESS SCENARIOS
# =========================================================

LIQUIDITY_SCENARIOS = {

    "NORMAL_MARKET": {

        "ADV_Shock": 0.00,

        "Description":
        "Normal Market Liquidity",
    },

    "MODERATE_STRESS": {

        "ADV_Shock": -0.30,

        "Description":
        "Moderate Liquidity Contraction",
    },

    "SEVERE_STRESS": {

        "ADV_Shock": -0.50,

        "Description":
        "Severe Liquidity Stress",
    },

    "CRISIS": {

        "ADV_Shock": -0.80,

        "Description":
        "Crisis Liquidity Environment",
    },

    "MARKET_FREEZE": {

        "ADV_Shock": -0.95,

        "Description":
        "Market Freeze Event",
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
    / "liquidity"
)

REPORT_FILE = (
    ROOT
    / "data"
    / "logs"
    / "liquidity_stress_report.csv"
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
]

required_factor = [

    "Symbol",

    "Sector",

    "Market_Cap",

    "ADV_20D",

    "Dollar_Volume",

    "Volatility_20D",

    "Volatility_60D",
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
        f"Portfolio too small: {len(portfolio)}"
    )

# =========================================================
# CLEAN PORTFOLIO
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

portfolio[
    "Position_Value"
] = (

    portfolio["Weight"]

    * PORTFOLIO_NAV
)

# =========================================================
# MERGE FACTORS
# =========================================================

liquidity_df = portfolio.merge(

    factor_master,

    on="Symbol",

    how="left",

    suffixes=(
        "",
        "_factor"
    )
)

# =========================================================
# COVERAGE CHECK
# =========================================================

coverage = (

    liquidity_df[
        "ADV_20D"
    ]

    .notna()

    .mean()
)

if coverage < 0.90:

    raise ValueError(

        "Liquidity coverage too low: "

        f"{coverage:.2%}"
    )

# =========================================================
# LIQUIDITY FACTORS
# =========================================================

print(
    "\n💧 Building Liquidity Factors..."
)

# ---------------------------------------------------------
# ADV Score
# ---------------------------------------------------------

liquidity_df[
    "ADV_Score"
] = np.log1p(

    liquidity_df[
        "ADV_20D"
    ]
)

# ---------------------------------------------------------
# Dollar Volume Score
# ---------------------------------------------------------

liquidity_df[
    "Dollar_Volume_Score"
] = np.log1p(

    liquidity_df[
        "Dollar_Volume"
    ]
)

# ---------------------------------------------------------
# Market Cap Score
# ---------------------------------------------------------

liquidity_df[
    "Market_Cap_Score"
] = np.log1p(

    liquidity_df[
        "Market_Cap"
    ]
)

# ---------------------------------------------------------
# Volatility Score
# ---------------------------------------------------------

liquidity_df[
    "Volatility_Score"
] = -(

    liquidity_df[
        "Volatility_20D"
    ]

    +

    liquidity_df[
        "Volatility_60D"
    ]

) / 2

# =========================================================
# STANDARDIZATION
# =========================================================

factor_cols = [

    "ADV_Score",

    "Dollar_Volume_Score",

    "Market_Cap_Score",

    "Volatility_Score",
]

for col in factor_cols:

    std = liquidity_df[
        col
    ].std()

    if pd.notna(std) and std > 0:

        liquidity_df[
            col
        ] = (

            liquidity_df[
                col
            ]

            -

            liquidity_df[
                col
            ].mean()

        ) / std

# =========================================================
# COMPOSITE LIQUIDITY SCORE
# =========================================================

liquidity_df[
    "Liquidity_Score"
] = (

    liquidity_df[
        "ADV_Score"
    ]

    +

    liquidity_df[
        "Dollar_Volume_Score"
    ]

    +

    liquidity_df[
        "Market_Cap_Score"
    ]

    +

    liquidity_df[
        "Volatility_Score"
    ]

) / 4

# =========================================================
# STORAGE
# =========================================================

scenario_results = []

position_results = []

capacity_results = []

print(
    f"Portfolio Holdings : "
    f"{len(portfolio)}"
)

print(
    f"Liquidity Coverage : "
    f"{coverage:.2%}"
)

print(
    f"Stress Scenarios   : "
    f"{len(LIQUIDITY_SCENARIOS)}"
)

for scenario in LIQUIDITY_SCENARIOS:

    print(
        f"✓ {scenario}"
    )

# =========================================================
# PART 2 STARTS HERE
# =========================================================
#
# Next:
#
# Days To Liquidate
# Position Liquidity Risk
# Liquidation Schedule
# Portfolio Liquidity Metrics
#
# =========================================================

# =========================================================
# POSITION LIQUIDITY ANALYSIS
# =========================================================

print(
    "\n💧 Building Position Liquidity Analysis..."
)

# =========================================================
# TRADEABLE DAILY LIQUIDITY
# =========================================================

liquidity_df[
    "Tradeable_ADV"
] = (

    liquidity_df[
        "ADV_20D"
    ]

    *

    PARTICIPATION_RATE
)

liquidity_df[
    "Capacity_ADV"
] = (

    liquidity_df[
        "ADV_20D"
    ]

    *

    CAPACITY_PARTICIPATION
)

# =========================================================
# DAYS TO LIQUIDATE
# =========================================================

liquidity_df[
    "Days_To_Liquidate"
] = (

    liquidity_df[
        "Position_Value"
    ]

    /

    liquidity_df[
        "Tradeable_ADV"
    ].replace(
        0,
        np.nan
    )
)

liquidity_df[
    "Days_To_Liquidate"
] = (

    liquidity_df[
        "Days_To_Liquidate"
    ]

    .replace(
        [np.inf, -np.inf],
        np.nan
    )

    .fillna(999)
)

# =========================================================
# DAYS TO BUILD POSITION
# =========================================================

liquidity_df[
    "Days_To_Build"
] = (

    liquidity_df[
        "Position_Value"
    ]

    /

    liquidity_df[
        "Capacity_ADV"
    ].replace(
        0,
        np.nan
    )
)

liquidity_df[
    "Days_To_Build"
] = (

    liquidity_df[
        "Days_To_Build"
    ]

    .replace(
        [np.inf, -np.inf],
        np.nan
    )

    .fillna(999)
)

# =========================================================
# MARKET IMPACT MODEL
# =========================================================

liquidity_df[
    "Participation_Ratio"
] = (

    liquidity_df[
        "Position_Value"
    ]

    /

    liquidity_df[
        "ADV_20D"
    ].replace(
        0,
        np.nan
    )
)

liquidity_df[
    "Participation_Ratio"
] = (

    liquidity_df[
        "Participation_Ratio"
    ]

    .fillna(0)
)

liquidity_df[
    "Market_Impact"
] = (

    liquidity_df[
        "Participation_Ratio"
    ]

    *

    liquidity_df[
        "Volatility_20D"
    ]

    *

    IMPACT_MULTIPLIER
)

# =========================================================
# FORCED SALE COST
# =========================================================

liquidity_df[
    "Forced_Sale_Cost"
] = (

    liquidity_df[
        "Position_Value"
    ]

    *

    liquidity_df[
        "Market_Impact"
    ]
)

# =========================================================
# LIQUIDITY BUCKETS
# =========================================================

conditions = [

    liquidity_df[
        "Days_To_Liquidate"
    ] <= 1,

    liquidity_df[
        "Days_To_Liquidate"
    ].between(1, 3),

    liquidity_df[
        "Days_To_Liquidate"
    ].between(3, 5),

    liquidity_df[
        "Days_To_Liquidate"
    ].between(5, 10),

    liquidity_df[
        "Days_To_Liquidate"
    ] > 10,
]

labels = [

    "VERY_LIQUID",

    "LIQUID",

    "MODERATE",

    "ILLIQUID",

    "CRITICAL",
]

liquidity_df[
    "Liquidity_Bucket"
] = np.select(

    conditions,

    labels,

    default="UNKNOWN"
)

# =========================================================
# POSITION RISK SCORE
# =========================================================

max_days = max(

    liquidity_df[
        "Days_To_Liquidate"
    ].max(),

    1
)

liquidity_df[
    "Liquidity_Risk_Score"
] = (

    liquidity_df[
        "Days_To_Liquidate"
    ]

    /

    max_days

    * 100
)

# =========================================================
# POSITION OUTPUT
# =========================================================

position_liquidity_risk = (

    liquidity_df[[

        "Symbol",

        "Company_Name",

        "Sector",

        "Weight",

        "Position_Value",

        "ADV_20D",

        "Tradeable_ADV",

        "Dollar_Volume",

        "Liquidity_Score",

        "Days_To_Liquidate",

        "Days_To_Build",

        "Market_Impact",

        "Forced_Sale_Cost",

        "Liquidity_Risk_Score",

        "Liquidity_Bucket",
    ]]

    .copy()
)

# =========================================================
# LIQUIDATION SCHEDULE
# =========================================================

liquidation_schedule = (

    position_liquidity_risk[[

        "Symbol",

        "Position_Value",

        "Tradeable_ADV"
        if "Tradeable_ADV"
        in liquidity_df.columns
        else "ADV_20D",

        "Days_To_Liquidate",
    ]]

    .copy()
)

# safer version
liquidation_schedule = liquidity_df[[

    "Symbol",

    "Position_Value",

    "Tradeable_ADV",

    "Days_To_Liquidate",
]].copy()

liquidation_schedule[
    "Daily_Exit_Value"
] = liquidation_schedule[
    "Tradeable_ADV"
]

liquidation_schedule[
    "Completion_Date_Days"
] = np.ceil(

    liquidation_schedule[
        "Days_To_Liquidate"
    ]
)

# =========================================================
# PORTFOLIO LIQUIDITY METRICS
# =========================================================

portfolio_days_to_exit = (

    liquidity_df[
        "Days_To_Liquidate"
    ]

    .mean()
)

max_days_to_exit = (

    liquidity_df[
        "Days_To_Liquidate"
    ]

    .max()
)

portfolio_market_impact = (

    liquidity_df[
        "Market_Impact"
    ]

    .mean()
)

portfolio_forced_sale_cost = (

    liquidity_df[
        "Forced_Sale_Cost"
    ]

    .sum()
)

portfolio_liquidity_score = (

    liquidity_df[
        "Liquidity_Score"
    ]

    .mean()
)

# =========================================================
# BUCKET SUMMARY
# =========================================================

bucket_summary = (

    liquidity_df

    .groupby(
        "Liquidity_Bucket"
    )

    .agg({

        "Symbol":
        "count",

        "Position_Value":
        "sum",
    })

    .reset_index()

    .rename(columns={

        "Symbol":
        "Position_Count"
    })
)

# =========================================================
# DIAGNOSTICS
# =========================================================

print(
    f"Avg Days To Exit : "
    f"{portfolio_days_to_exit:.2f}"
)

print(
    f"Max Days To Exit : "
    f"{max_days_to_exit:.2f}"
)

print(
    f"Liquidity Score  : "
    f"{portfolio_liquidity_score:.2f}"
)

print(
    f"Forced Sale Cost : "
    f"{portfolio_forced_sale_cost:,.0f}"
)

# =========================================================
# PART 3 STARTS HERE
# =========================================================
#
# Next:
#
# Liquidity Stress Scenarios
# Capacity Analysis
# Crisis Liquidity
# Market Impact Stress
#
# =========================================================

# =========================================================
# LIQUIDITY STRESS TESTING
# =========================================================

print(
    "\n⚠ Running Liquidity Stress Scenarios..."
)

for scenario_name, scenario in LIQUIDITY_SCENARIOS.items():

    print(
        f"Running: {scenario_name}"
    )

    tmp = liquidity_df.copy()

    adv_shock = scenario[
        "ADV_Shock"
    ]

    # =====================================================
    # SHOCKED ADV
    # =====================================================

    tmp[
        "Stressed_ADV"
    ] = (

        tmp[
            "ADV_20D"
        ]

        *

        (
            1
            +
            adv_shock
        )
    )

    tmp[
        "Stressed_ADV"
    ] = (

        tmp[
            "Stressed_ADV"
        ]

        .clip(
            lower=1
        )
    )

    # =====================================================
    # STRESSED DAYS TO EXIT
    # =====================================================

    tmp[
        "Stress_Days_To_Liquidate"
    ] = (

        tmp[
            "Position_Value"
        ]

        /

        (

            tmp[
                "Stressed_ADV"
            ]

            *

            PARTICIPATION_RATE

        )
    )

    # =====================================================
    # STRESSED MARKET IMPACT
    # =====================================================

    tmp[
        "Stress_Impact"
    ] = (

        tmp[
            "Position_Value"
        ]

        /

        tmp[
            "Stressed_ADV"
        ]

        *

        tmp[
            "Volatility_20D"
        ]

        *

        IMPACT_MULTIPLIER
    )

    # =====================================================
    # STRESSED SALE COST
    # =====================================================

    tmp[
        "Stress_Sale_Cost"
    ] = (

        tmp[
            "Position_Value"
        ]

        *

        tmp[
            "Stress_Impact"
        ]
    )

    # =====================================================
    # SCENARIO SUMMARY
    # =====================================================

    avg_days = (

        tmp[
            "Stress_Days_To_Liquidate"
        ]

        .mean()
    )

    max_days = (

        tmp[
            "Stress_Days_To_Liquidate"
        ]

        .max()
    )

    total_cost = (

        tmp[
            "Stress_Sale_Cost"
        ]

        .sum()
    )

    avg_impact = (

        tmp[
            "Stress_Impact"
        ]

        .mean()
    )

    scenario_results.append({

        "Scenario":
        scenario_name,

        "Description":
        scenario[
            "Description"
        ],

        "ADV_Shock":
        adv_shock,

        "Average_Days_To_Exit":
        avg_days,

        "Maximum_Days_To_Exit":
        max_days,

        "Average_Impact":
        avg_impact,

        "Forced_Sale_Cost":
        total_cost,
    })

    # =====================================================
    # STORE POSITION RESULTS
    # =====================================================

    tmp[
        "Scenario"
    ] = scenario_name

    position_results.append(

        tmp[[

            "Scenario",

            "Symbol",

            "Sector",

            "Position_Value",

            "ADV_20D",

            "Stressed_ADV",

            "Stress_Days_To_Liquidate",

            "Stress_Impact",

            "Stress_Sale_Cost",
        ]]
    )

# =========================================================
# SCENARIO RESULTS
# =========================================================

liquidity_stress_results = pd.DataFrame(
    scenario_results
)

if len(position_results) == 0:

    raise ValueError(
        "No liquidity stress results generated."
    )

stress_positions = pd.concat(

    position_results,

    ignore_index=True
)

# =========================================================
# CAPACITY ANALYSIS
# =========================================================

print(
    "\n📊 Building Capacity Analysis..."
)

capacity_df = liquidity_df.copy()

capacity_df[
    "Maximum_Position"
] = (

    capacity_df[
        "ADV_20D"
    ]

    *

    CAPACITY_PARTICIPATION
)

capacity_df[
    "Capacity_Multiple"
] = (

    capacity_df[
        "Maximum_Position"
    ]

    /

    capacity_df[
        "Position_Value"
    ]
)

capacity_df[
    "Capacity_NAV"
] = (

    PORTFOLIO_NAV

    *

    capacity_df[
        "Capacity_Multiple"
    ]
)

# =========================================================
# PORTFOLIO CAPACITY
# =========================================================

portfolio_capacity = (

    capacity_df[
        "Capacity_NAV"
    ]

    .median()
)

capacity_utilization = (

    PORTFOLIO_NAV

    /

    portfolio_capacity

)

# =========================================================
# CROWDING RISK
# =========================================================

capacity_df[
    "Crowding_Risk"
] = np.where(

    capacity_df[
        "Capacity_Multiple"
    ] < 2,

    "HIGH",

    np.where(

        capacity_df[
            "Capacity_Multiple"
        ] < 5,

        "MEDIUM",

        "LOW"
    )
)

# =========================================================
# CAPACITY OUTPUT
# =========================================================

capacity_analysis = (

    capacity_df[[

        "Symbol",

        "Sector",

        "Position_Value",

        "ADV_20D",

        "Maximum_Position",

        "Capacity_Multiple",

        "Capacity_NAV",

        "Crowding_Risk",
    ]]

    .copy()
)

# =========================================================
# CRISIS LIQUIDITY
# =========================================================

crisis_scenario = (

    liquidity_stress_results[

        liquidity_stress_results[
            "Scenario"
        ]

        ==

        "MARKET_FREEZE"

    ]
)

if not crisis_scenario.empty:

    crisis_days = float(

        crisis_scenario[
            "Average_Days_To_Exit"
        ].iloc[0]
    )

    crisis_cost = float(

        crisis_scenario[
            "Forced_Sale_Cost"
        ].iloc[0]
    )

else:

    crisis_days = np.nan

    crisis_cost = np.nan

# =========================================================
# WORST POSITIONS
# =========================================================

worst_positions = (

    stress_positions

    .sort_values(
        "Stress_Sale_Cost",
        ascending=False
    )

    .head(20)
)

# =========================================================
# HEATMAP DATASET
# =========================================================

liquidity_heatmap = (

    stress_positions

    .pivot_table(

        index="Symbol",

        columns="Scenario",

        values="Stress_Days_To_Liquidate",

        aggfunc="mean"
    )
)

liquidity_heatmap.to_csv(

    OUTPUT_DIR
    / "liquidity_heatmap.csv"
)

# =========================================================
# DASHBOARD
# =========================================================

liquidity_stress_dashboard = pd.DataFrame({

    "Metric": [

        "Portfolio_NAV",

        "Portfolio_Capacity",

        "Capacity_Utilization",

        "Average_Days_To_Exit",

        "Maximum_Days_To_Exit",

        "Forced_Sale_Cost",

        "Crisis_Days_To_Exit",

        "Crisis_Sale_Cost",
    ],

    "Value": [

        PORTFOLIO_NAV,

        portfolio_capacity,

        capacity_utilization,

        portfolio_days_to_exit,

        max_days_to_exit,

        portfolio_forced_sale_cost,

        crisis_days,

        crisis_cost,
    ]
})

# =========================================================
# DIAGNOSTICS
# =========================================================

print(
    f"Portfolio Capacity : "
    f"{portfolio_capacity:,.0f}"
)

print(
    f"Capacity Utilization : "
    f"{capacity_utilization:.2f}x"
)

print(
    f"Crisis Exit Days : "
    f"{crisis_days:.2f}"
)

# =========================================================
# PART 4 STARTS HERE
# =========================================================
#
# Next:
#
# Liquidity VaR
# Liquidity CVaR
# Liquidity Risk Score
# Executive Summary
# Save Outputs
# Final Reporting
#
# =========================================================

# =========================================================
# LIQUIDITY RISK METRICS
# =========================================================

print(
    "\n⚠ Calculating Liquidity Risk Metrics..."
)

stress_days = (

    liquidity_stress_results[
        "Average_Days_To_Exit"
    ]

    .values
)

stress_costs = (

    liquidity_stress_results[
        "Forced_Sale_Cost"
    ]

    .values
)

# =========================================================
# LIQUIDITY VAR
# =========================================================

liquidity_var_95 = np.percentile(

    stress_costs,

    95
)

# =========================================================
# LIQUIDITY CVAR
# =========================================================

tail_costs = stress_costs[

    stress_costs
    >=
    liquidity_var_95
]

if len(
    tail_costs
) > 0:

    liquidity_cvar_95 = (
        tail_costs.mean()
    )

else:

    liquidity_cvar_95 = (
        liquidity_var_95
    )

# =========================================================
# WORST SCENARIO
# =========================================================

worst_scenario = (

    liquidity_stress_results

    .sort_values(
        "Forced_Sale_Cost",
        ascending=False
    )

    .iloc[0]
)

# =========================================================
# BEST SCENARIO
# =========================================================

best_scenario = (

    liquidity_stress_results

    .sort_values(
        "Forced_Sale_Cost"
    )

    .iloc[0]
)

# =========================================================
# PORTFOLIO LIQUIDITY SCORE
# =========================================================

portfolio_liquidity_score = (

    liquidity_df[
        "Liquidity_Score"
    ]

    .mean()
)

portfolio_liquidity_score = (

    (
        portfolio_liquidity_score
        + 3
    )

    / 6

    * 100
)

portfolio_liquidity_score = np.clip(

    portfolio_liquidity_score,

    0,

    100
)

# =========================================================
# LIQUIDITY RISK SCORE
# =========================================================

risk_score = min(

    worst_scenario[
        "Forced_Sale_Cost"
    ]

    /

    PORTFOLIO_NAV

    * 100,

    100
)

# =========================================================
# RESILIENCE SCORE
# =========================================================

resilience_score = (

    100

    -

    risk_score
)

resilience_score = max(
    resilience_score,
    0
)

# =========================================================
# LIQUIDITY CLASSIFICATION
# =========================================================

if portfolio_days_to_exit <= 2:

    liquidity_rating = (
        "EXCELLENT"
    )

elif portfolio_days_to_exit <= 5:

    liquidity_rating = (
        "GOOD"
    )

elif portfolio_days_to_exit <= 10:

    liquidity_rating = (
        "MODERATE"
    )

elif portfolio_days_to_exit <= 20:

    liquidity_rating = (
        "WEAK"
    )

else:

    liquidity_rating = (
        "CRITICAL"
    )

# =========================================================
# CROWDING SUMMARY
# =========================================================

crowding_summary = (

    capacity_analysis

    .groupby(
        "Crowding_Risk"
    )

    .size()

    .reset_index(
        name="Count"
    )
)

high_crowding_count = (

    (
        capacity_analysis[
            "Crowding_Risk"
        ]

        ==

        "HIGH"
    )

    .sum()
)

# =========================================================
# LIQUIDITY SUMMARY
# =========================================================

liquidity_stress_summary = pd.DataFrame({

    "Metric": [

        "Portfolio_NAV",

        "Portfolio_Capacity",

        "Capacity_Utilization",

        "Portfolio_Liquidity_Score",

        "Liquidity_Risk_Score",

        "Liquidity_VaR_95",

        "Liquidity_CVaR_95",

        "Average_Days_To_Exit",

        "Maximum_Days_To_Exit",

        "Forced_Sale_Cost",

        "High_Crowding_Positions",

        "Liquidity_Rating",

        "Risk_Score",

        "Resilience_Score",

        "Run_Date",

        "Engine_Version",
    ],

    "Value": [

        PORTFOLIO_NAV,

        portfolio_capacity,

        capacity_utilization,

        portfolio_liquidity_score,

        risk_score,

        liquidity_var_95,

        liquidity_cvar_95,

        portfolio_days_to_exit,

        max_days_to_exit,

        portfolio_forced_sale_cost,

        high_crowding_count,

        liquidity_rating,

        risk_score,

        resilience_score,

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

liquidity_stress_results.to_csv(

    OUTPUT_DIR
    / "liquidity_stress_results.csv",

    index=False,
)

liquidity_stress_summary.to_csv(

    OUTPUT_DIR
    / "liquidity_stress_summary.csv",

    index=False,
)

liquidity_stress_dashboard.to_csv(

    OUTPUT_DIR
    / "liquidity_stress_dashboard.csv",

    index=False,
)

position_liquidity_risk.to_csv(

    OUTPUT_DIR
    / "position_liquidity_risk.csv",

    index=False,
)

capacity_analysis.to_csv(

    OUTPUT_DIR
    / "capacity_analysis.csv",

    index=False,
)

liquidation_schedule.to_csv(

    OUTPUT_DIR
    / "liquidation_schedule.csv",

    index=False,
)

crowding_summary.to_csv(

    OUTPUT_DIR
    / "crowding_summary.csv",

    index=False,
)

worst_positions.to_csv(

    OUTPUT_DIR
    / "worst_liquidity_positions.csv",

    index=False,
)

liquidity_stress_summary.to_csv(

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
    "🏁 LIQUIDITY STRESS ENGINE COMPLETE"
)

print(
    "=" * 70
)

print(
    f"Portfolio Capacity    : "
    f"{portfolio_capacity:,.0f}"
)

print(
    f"Capacity Utilization  : "
    f"{capacity_utilization:.2f}x"
)

print(
    f"Liquidity Score       : "
    f"{portfolio_liquidity_score:.2f}"
)

print(
    f"Liquidity Rating      : "
    f"{liquidity_rating}"
)

print(
    f"\nAvg Days To Exit      : "
    f"{portfolio_days_to_exit:.2f}"
)

print(
    f"Max Days To Exit      : "
    f"{max_days_to_exit:.2f}"
)

print(
    f"\nLiquidity VaR 95      : "
    f"{liquidity_var_95:,.0f}"
)

print(
    f"Liquidity CVaR 95     : "
    f"{liquidity_cvar_95:,.0f}"
)

print(
    f"\nWorst Scenario        : "
    f"{worst_scenario['Scenario']}"
)

print(
    f"Worst Sale Cost       : "
    f"{worst_scenario['Forced_Sale_Cost']:,.0f}"
)

print(
    f"\nHigh Crowding Names   : "
    f"{high_crowding_count}"
)

print(
    f"Risk Score            : "
    f"{risk_score:.2f}"
)

print(
    f"Resilience Score      : "
    f"{resilience_score:.2f}"
)

print(
    f"\nOutput Directory:\n"
    f"{OUTPUT_DIR}"
)

print(
    "=" * 70
)