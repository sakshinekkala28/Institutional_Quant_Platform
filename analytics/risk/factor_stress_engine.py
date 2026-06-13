"""
=========================================================
FACTOR STRESS ENGINE
=========================================================

Purpose:
Institutional Factor Stress Testing

Inputs:
data/portfolios/live_portfolio.csv
data/factors/factor_master.csv

Outputs:
data/risk/factor_stress_results.csv
data/risk/factor_stress_summary.csv
data/risk/factor_stress_dashboard.csv
data/risk/factor_position_impact.csv
data/risk/factor_sector_impact.csv

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
# FACTOR STRESS SCENARIOS
# =========================================================

FACTOR_SCENARIOS = {

    "MOMENTUM_CRASH": {

        "Description":
        "Momentum Factor Selloff",

        "Momentum_Shock":
        -0.15,
    },

    "LOWVOL_REVERSAL": {

        "Description":
        "Low Volatility Reversal",

        "LowVol_Shock":
        -0.10,
    },

    "SMALL_CAP_SELLOFF": {

        "Description":
        "Small Cap Underperformance",

        "Size_Shock":
        -0.20,
    },

    "LIQUIDITY_SHOCK": {

        "Description":
        "Liquidity Freeze",

        "Liquidity_Shock":
        -0.25,
    },

    "TREND_REVERSAL": {

        "Description":
        "Trend Breakdown",

        "Trend_Shock":
        -0.15,
    },

    "MULTI_FACTOR_CRISIS": {

        "Description":
        "Multi Factor Crisis",

        "Momentum_Shock":
        -0.15,

        "Liquidity_Shock":
        -0.20,

        "Trend_Shock":
        -0.15,
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
    / "risk"
)

REPORT_FILE = (
    ROOT
    / "data"
    / "logs"
    / "factor_stress_report.csv"
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

    "Momentum_1M",
    "Momentum_3M",
    "Momentum_6M",
    "Momentum_12M",

    "Volatility_20D",
    "Volatility_60D",

    "ATR_14",

    "Max_Drawdown_252D",

    "Distance_SMA50",
    "Distance_SMA200",
    "Distance_52W_High",

    "ADV_20D",
    "Dollar_Volume",

    "Log_Market_Cap",
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

stress_df = portfolio.merge(

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

    stress_df[
        "Log_Market_Cap"
    ]

    .notna()

    .mean()
)

if coverage < 0.90:

    raise ValueError(

        "Factor coverage too low: "

        f"{coverage:.2%}"
    )

print(
    f"Portfolio Holdings : "
    f"{len(portfolio)}"
)

print(
    f"Factor Coverage    : "
    f"{coverage:.2%}"
)

# =========================================================
# FACTOR CONSTRUCTION
# =========================================================

print(
    "\n📊 Building Factor Exposures..."
)

# ---------------------------------------------------------
# Momentum
# ---------------------------------------------------------

stress_df[
    "Momentum_Factor"
] = (

    stress_df[
        "Momentum_1M"
    ]

    +

    stress_df[
        "Momentum_3M"
    ]

    +

    stress_df[
        "Momentum_6M"
    ]

    +

    stress_df[
        "Momentum_12M"
    ]

) / 4

# ---------------------------------------------------------
# Low Vol
# ---------------------------------------------------------

stress_df[
    "LowVol_Factor"
] = -(

    stress_df[
        "Volatility_20D"
    ]

    +

    stress_df[
        "Volatility_60D"
    ]

    +

    stress_df[
        "ATR_14"
    ]

    +

    stress_df[
        "Max_Drawdown_252D"
    ].abs()

) / 4

# ---------------------------------------------------------
# Size
# ---------------------------------------------------------

stress_df[
    "Size_Factor"
] = -(

    stress_df[
        "Log_Market_Cap"
    ]
)

# ---------------------------------------------------------
# Liquidity
# ---------------------------------------------------------

stress_df[
    "Liquidity_Factor"
] = (

    np.log1p(
        stress_df[
            "ADV_20D"
        ]
    )

    +

    np.log1p(
        stress_df[
            "Dollar_Volume"
        ]
    )

) / 2

# ---------------------------------------------------------
# Trend
# ---------------------------------------------------------

stress_df[
    "Trend_Factor"
] = (

    stress_df[
        "Distance_SMA50"
    ]

    +

    stress_df[
        "Distance_SMA200"
    ]

    +

    stress_df[
        "Distance_52W_High"
    ]

) / 3

# =========================================================
# STANDARDIZATION
# =========================================================

factor_columns = [

    "Momentum_Factor",

    "LowVol_Factor",

    "Size_Factor",

    "Liquidity_Factor",

    "Trend_Factor",
]

for factor in factor_columns:

    std = stress_df[
        factor
    ].std()

    if pd.notna(std) and std > 0:

        stress_df[
            factor
        ] = (

            stress_df[
                factor
            ]

            -

            stress_df[
                factor
            ].mean()

        ) / std

# =========================================================
# STORAGE
# =========================================================

scenario_results = []

position_results = []

sector_results = []

print(
    f"Factor Scenarios Loaded : "
    f"{len(FACTOR_SCENARIOS)}"
)

for scenario in FACTOR_SCENARIOS:

    print(
        f"✓ {scenario}"
    )

# =========================================================
# PART 2 STARTS HERE
# =========================================================
#
# Next:
#
# Factor Shock Engine
# Position Impact
# Portfolio Loss
# Scenario Ranking
#
# =========================================================

# =========================================================
# FACTOR SHOCK ENGINE
# =========================================================

print(
    "\n📉 Running Factor Stress Scenarios..."
)

for scenario_name, scenario in FACTOR_SCENARIOS.items():

    print(
        f"\nRunning: {scenario_name}"
    )

    tmp = stress_df.copy()

    # =====================================================
    # INITIALIZE SHOCKS
    # =====================================================

    tmp["Momentum_Shock"] = 0.0
    tmp["LowVol_Shock"] = 0.0
    tmp["Size_Shock"] = 0.0
    tmp["Liquidity_Shock"] = 0.0
    tmp["Trend_Shock"] = 0.0

    # =====================================================
    # APPLY FACTOR SHOCKS
    # =====================================================

    if "Momentum_Shock" in scenario:

        tmp["Momentum_Shock"] = (

            tmp["Momentum_Factor"]

            *

            scenario[
                "Momentum_Shock"
            ]
        )

    if "LowVol_Shock" in scenario:

        tmp["LowVol_Shock"] = (

            tmp["LowVol_Factor"]

            *

            scenario[
                "LowVol_Shock"
            ]
        )

    if "Size_Shock" in scenario:

        tmp["Size_Shock"] = (

            tmp["Size_Factor"]

            *

            scenario[
                "Size_Shock"
            ]
        )

    if "Liquidity_Shock" in scenario:

        tmp["Liquidity_Shock"] = (

            tmp["Liquidity_Factor"]

            *

            scenario[
                "Liquidity_Shock"
            ]
        )

    if "Trend_Shock" in scenario:

        tmp["Trend_Shock"] = (

            tmp["Trend_Factor"]

            *

            scenario[
                "Trend_Shock"
            ]
        )

    # =====================================================
    # TOTAL STRESS RETURN
    # =====================================================

    tmp[
        "Factor_Stress_Return"
    ] = (

        tmp["Momentum_Shock"]

        +

        tmp["LowVol_Shock"]

        +

        tmp["Size_Shock"]

        +

        tmp["Liquidity_Shock"]

        +

        tmp["Trend_Shock"]
    )

    # =====================================================
    # POSITION IMPACT
    # =====================================================

    tmp[
        "Stress_PnL"
    ] = (

        tmp[
            "Position_Value"
        ]

        *

        tmp[
            "Factor_Stress_Return"
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

    # =====================================================
    # CONTRIBUTION
    # =====================================================

    tmp[
        "Contribution"
    ] = (

        tmp[
            "Stress_PnL"
        ]

        /

        PORTFOLIO_NAV
    )

    tmp[
        "Scenario"
    ] = scenario_name

    # =====================================================
    # FACTOR CONTRIBUTIONS
    # =====================================================

    tmp[
        "Momentum_PnL"
    ] = (

        tmp[
            "Position_Value"
        ]

        *

        tmp[
            "Momentum_Shock"
        ]
    )

    tmp[
        "LowVol_PnL"
    ] = (

        tmp[
            "Position_Value"
        ]

        *

        tmp[
            "LowVol_Shock"
        ]
    )

    tmp[
        "Size_PnL"
    ] = (

        tmp[
            "Position_Value"
        ]

        *

        tmp[
            "Size_Shock"
        ]
    )

    tmp[
        "Liquidity_PnL"
    ] = (

        tmp[
            "Position_Value"
        ]

        *

        tmp[
            "Liquidity_Shock"
        ]
    )

    tmp[
        "Trend_PnL"
    ] = (

        tmp[
            "Position_Value"
        ]

        *

        tmp[
            "Trend_Shock"
        ]
    )

    # =====================================================
    # STORE POSITION RESULTS
    # =====================================================

    position_results.append(

        tmp[[

            "Scenario",

            "Symbol",

            "Company_Name",

            "Sector",

            "Weight",

            "Position_Value",

            "Factor_Stress_Return",

            "Stress_PnL",

            "Stress_Value",

            "Contribution",

            "Momentum_PnL",

            "LowVol_PnL",

            "Size_PnL",

            "Liquidity_PnL",

            "Trend_PnL",
        ]]
    )

    # =====================================================
    # PORTFOLIO IMPACT
    # =====================================================

    portfolio_pnl = (

        tmp[
            "Stress_PnL"
        ].sum()
    )

    portfolio_return = (

        portfolio_pnl

        /

        PORTFOLIO_NAV
    )

    stress_nav = (

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
        stress_nav,

        "Portfolio_PnL":
        portfolio_pnl,

        "Portfolio_Return":
        portfolio_return,
    })

# =========================================================
# BUILD RESULTS
# =========================================================

factor_stress_results = pd.DataFrame(
    scenario_results
)

factor_position_impact = pd.concat(

    position_results,

    ignore_index=True
)

# =========================================================
# POSITION RANKING
# =========================================================

factor_position_impact[
    "Loss_Rank"
] = (

    factor_position_impact

    .groupby(
        "Scenario"
    )

    [
        "Stress_PnL"
    ]

    .rank(
        ascending=True,
        method="dense"
    )
)

# =========================================================
# WORST HOLDINGS
# =========================================================

worst_positions = (

    factor_position_impact

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
# BEST HOLDINGS
# =========================================================

best_positions = (

    factor_position_impact

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

factor_stress_results = (

    factor_stress_results

    .sort_values(
        "Portfolio_Return"
    )

    .reset_index(
        drop=True
    )
)

factor_stress_results[
    "Scenario_Rank"
] = (
    factor_stress_results.index + 1
)

worst_scenario = (
    factor_stress_results.iloc[0]
)

best_scenario = (
    factor_stress_results.iloc[-1]
)

# =========================================================
# DIAGNOSTICS
# =========================================================

print(
    f"\nWorst Scenario : "
    f"{worst_scenario['Scenario']}"
)

print(
    f"Return         : "
    f"{worst_scenario['Portfolio_Return']:.2%}"
)

print(
    f"\nBest Scenario  : "
    f"{best_scenario['Scenario']}"
)

print(
    f"Return         : "
    f"{best_scenario['Portfolio_Return']:.2%}"
)

# =========================================================
# PART 3 STARTS HERE
# =========================================================
#
# Next:
#
# Factor Attribution
# Sector Attribution
# Sector Damage Ranking
# Factor Dashboard
#
# =========================================================

# =========================================================
# FACTOR ATTRIBUTION
# =========================================================

print(
    "\n📊 Building Factor Attribution..."
)

factor_attribution = []

for scenario_name in (

    factor_position_impact[
        "Scenario"
    ].unique()

):

    tmp = factor_position_impact[

        factor_position_impact[
            "Scenario"
        ]

        ==

        scenario_name

    ]

    factor_attribution.append({

        "Scenario":
        scenario_name,

        "Momentum_PnL":
        tmp[
            "Momentum_PnL"
        ].sum(),

        "LowVol_PnL":
        tmp[
            "LowVol_PnL"
        ].sum(),

        "Size_PnL":
        tmp[
            "Size_PnL"
        ].sum(),

        "Liquidity_PnL":
        tmp[
            "Liquidity_PnL"
        ].sum(),

        "Trend_PnL":
        tmp[
            "Trend_PnL"
        ].sum(),

        "Total_PnL":
        tmp[
            "Stress_PnL"
        ].sum(),
    })

factor_attribution = pd.DataFrame(
    factor_attribution
)

# =========================================================
# FACTOR CONTRIBUTION %
# =========================================================

for factor in [

    "Momentum_PnL",

    "LowVol_PnL",

    "Size_PnL",

    "Liquidity_PnL",

    "Trend_PnL",
]:

    factor_attribution[
        factor.replace(
            "_PnL",
            "_Contribution"
        )
    ] = (

        factor_attribution[
            factor
        ]

        /

        factor_attribution[
            "Total_PnL"
        ].replace(
            0,
            np.nan
        )

    )

# =========================================================
# DOMINANT FACTOR
# =========================================================

factor_attribution[
    "Dominant_Factor"
] = (

    factor_attribution[[

        "Momentum_PnL",

        "LowVol_PnL",

        "Size_PnL",

        "Liquidity_PnL",

        "Trend_PnL",
    ]]

    .abs()

    .idxmax(axis=1)

    .str.replace(
        "_PnL",
        ""
    )
)

# =========================================================
# SECTOR ATTRIBUTION
# =========================================================

print(
    "\n🏭 Building Sector Attribution..."
)

factor_sector_impact = (

    factor_position_impact

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

factor_sector_impact[
    "Stress_Return"
] = (

    factor_sector_impact[
        "Stress_PnL"
    ]

    /

    factor_sector_impact[
        "Position_Value"
    ]
)

# =========================================================
# SECTOR CONTRIBUTION
# =========================================================

factor_sector_impact[
    "Contribution"
] = (

    factor_sector_impact[
        "Stress_PnL"
    ]

    /

    PORTFOLIO_NAV
)

# =========================================================
# DAMAGE RANK
# =========================================================

factor_sector_impact[
    "Damage_Rank"
] = (

    factor_sector_impact

    .groupby(
        "Scenario"
    )

    [
        "Stress_PnL"
    ]

    .rank(
        ascending=True,
        method="dense"
    )
)

# =========================================================
# WORST SECTORS
# =========================================================

worst_sectors = (

    factor_sector_impact

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
# BEST SECTORS
# =========================================================

best_sectors = (

    factor_sector_impact

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
# FACTOR DASHBOARD
# =========================================================

factor_stress_dashboard = (

    factor_stress_results[[

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

factor_stress_dashboard = (

    factor_stress_dashboard

    .merge(

        factor_attribution[

            [

                "Scenario",

                "Dominant_Factor",
            ]

        ],

        on="Scenario",

        how="left",
    )
)

# =========================================================
# TOP FACTOR DAMAGE
# =========================================================

worst_factor = (

    factor_attribution

    .assign(

        Worst_PnL=lambda x:

        x[[

            "Momentum_PnL",

            "LowVol_PnL",

            "Size_PnL",

            "Liquidity_PnL",

            "Trend_PnL",
        ]]

        .min(axis=1)

    )

    .sort_values(
        "Worst_PnL"
    )

    .iloc[0]
)

# =========================================================
# TOP SECTOR DAMAGE
# =========================================================

worst_sector = (

    factor_sector_impact

    .sort_values(
        "Stress_PnL"
    )

    .iloc[0]
)

best_sector = (

    factor_sector_impact

    .sort_values(
        "Stress_PnL",
        ascending=False
    )

    .iloc[0]
)

# =========================================================
# STRESS HEATMAP
# =========================================================

stress_heatmap = (

    factor_sector_impact

    .pivot_table(

        index="Sector",

        columns="Scenario",

        values="Stress_Return",

        aggfunc="mean"
    )
)

stress_heatmap.to_csv(

    OUTPUT_DIR
    / "factor_stress_heatmap.csv"
)

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
    f"PnL          : "
    f"{best_sector['Stress_PnL']:,.0f}"
)

print(
    f"\nWorst Factor Scenario : "
    f"{worst_factor['Scenario']}"
)

print(
    f"Dominant Factor       : "
    f"{worst_factor['Dominant_Factor']}"
)

# =========================================================
# PART 4 STARTS HERE
# =========================================================
#
# Next:
#
# Factor VaR
# Factor CVaR
# Risk Score
# Resilience Score
# Executive Summary
# Save Outputs
# Final Reporting
#
# =========================================================

# =========================================================
# FACTOR RISK METRICS
# =========================================================

print(
    "\n⚠ Calculating Factor Risk Metrics..."
)

stress_returns = (

    factor_stress_results[
        "Portfolio_Return"
    ]

    .values
)

# =========================================================
# FACTOR VAR 95
# =========================================================

factor_var_95 = np.percentile(

    stress_returns,

    5
)

# =========================================================
# FACTOR CVAR 95
# =========================================================

tail_returns = stress_returns[

    stress_returns
    <=
    factor_var_95
]

if len(
    tail_returns
) > 0:

    factor_cvar_95 = (
        tail_returns.mean()
    )

else:

    factor_cvar_95 = (
        factor_var_95
    )

# =========================================================
# WORST SCENARIO METRICS
# =========================================================

worst_return = (

    factor_stress_results[
        "Portfolio_Return"
    ]

    .min()
)

worst_loss = (

    factor_stress_results[
        "Portfolio_PnL"
    ]

    .min()
)

# =========================================================
# BEST SCENARIO METRICS
# =========================================================

best_return = (

    factor_stress_results[
        "Portfolio_Return"
    ]

    .max()
)

best_gain = (

    factor_stress_results[
        "Portfolio_PnL"
    ]

    .max()
)

# =========================================================
# SCENARIO DISPERSION
# =========================================================

scenario_dispersion = (

    factor_stress_results[
        "Portfolio_Return"
    ]

    .std()
)

# =========================================================
# FACTOR RISK SCORE
# =========================================================

risk_score = min(

    abs(
        worst_return
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
    risk_score
)

resilience_score = max(
    resilience_score,
    0
)

# =========================================================
# FACTOR DIVERSIFICATION
# =========================================================

dominant_factor_counts = (

    factor_attribution[
        "Dominant_Factor"
    ]

    .value_counts(
        normalize=True
    )
)

factor_hhi = (

    dominant_factor_counts

    ** 2

).sum()

effective_factors = (

    1

    /

    max(
        factor_hhi,
        1e-9
    )
)

diversification_score = (

    effective_factors

    /

    5

    * 100
)

diversification_score = min(
    diversification_score,
    100
)

# =========================================================
# RISK CLASSIFICATION
# =========================================================

if abs(
    worst_return
) < 0.05:

    risk_level = "LOW"

elif abs(
    worst_return
) < 0.10:

    risk_level = "MODERATE"

elif abs(
    worst_return
) < 0.20:

    risk_level = "HIGH"

else:

    risk_level = "SEVERE"

# =========================================================
# FACTOR CONTRIBUTION SUMMARY
# =========================================================

factor_summary = pd.DataFrame({

    "Factor": [

        "Momentum",

        "LowVol",

        "Size",

        "Liquidity",

        "Trend",
    ],

    "Average_PnL": [

        factor_attribution[
            "Momentum_PnL"
        ].mean(),

        factor_attribution[
            "LowVol_PnL"
        ].mean(),

        factor_attribution[
            "Size_PnL"
        ].mean(),

        factor_attribution[
            "Liquidity_PnL"
        ].mean(),

        factor_attribution[
            "Trend_PnL"
        ].mean(),
    ]
})

# =========================================================
# EXECUTIVE SUMMARY
# =========================================================

factor_stress_summary = pd.DataFrame({

    "Metric": [

        "Worst_Scenario",

        "Worst_Return",

        "Worst_Loss",

        "Best_Scenario",

        "Best_Return",

        "Best_Gain",

        "Factor_VaR_95",

        "Factor_CVaR_95",

        "Risk_Score",

        "Resilience_Score",

        "Diversification_Score",

        "Effective_Factors",

        "Scenario_Dispersion",

        "Risk_Level",

        "Run_Date",

        "Engine_Version",
    ],

    "Value": [

        worst_scenario[
            "Scenario"
        ],

        worst_return,

        worst_loss,

        best_scenario[
            "Scenario"
        ],

        best_return,

        best_gain,

        factor_var_95,

        factor_cvar_95,

        risk_score,

        resilience_score,

        diversification_score,

        effective_factors,

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

factor_stress_results.to_csv(

    OUTPUT_DIR
    / "factor_stress_results.csv",

    index=False,
)

factor_stress_dashboard.to_csv(

    OUTPUT_DIR
    / "factor_stress_dashboard.csv",

    index=False,
)

factor_stress_summary.to_csv(

    OUTPUT_DIR
    / "factor_stress_summary.csv",

    index=False,
)

factor_position_impact.to_csv(

    OUTPUT_DIR
    / "factor_position_impact.csv",

    index=False,
)

factor_sector_impact.to_csv(

    OUTPUT_DIR
    / "factor_sector_impact.csv",

    index=False,
)

factor_attribution.to_csv(

    OUTPUT_DIR
    / "factor_attribution.csv",

    index=False,
)

factor_summary.to_csv(

    OUTPUT_DIR
    / "factor_contribution_summary.csv",

    index=False,
)

worst_positions.to_csv(

    OUTPUT_DIR
    / "factor_worst_positions.csv",

    index=False,
)

best_positions.to_csv(

    OUTPUT_DIR
    / "factor_best_positions.csv",

    index=False,
)

worst_sectors.to_csv(

    OUTPUT_DIR
    / "factor_worst_sectors.csv",

    index=False,
)

best_sectors.to_csv(

    OUTPUT_DIR
    / "factor_best_sectors.csv",

    index=False,
)

factor_stress_summary.to_csv(

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
    "🏁 FACTOR STRESS ENGINE COMPLETE"
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
    f"{worst_return:.2%}"
)

print(
    f"Worst Loss          : "
    f"{worst_loss:,.0f}"
)

print(
    f"\nBest Scenario       : "
    f"{best_scenario['Scenario']}"
)

print(
    f"Best Return         : "
    f"{best_return:.2%}"
)

print(
    f"Best Gain           : "
    f"{best_gain:,.0f}"
)

print(
    f"\nFactor VaR (95%)    : "
    f"{factor_var_95:.2%}"
)

print(
    f"Factor CVaR (95%)   : "
    f"{factor_cvar_95:.2%}"
)

print(
    f"\nRisk Score          : "
    f"{risk_score:.2f}"
)

print(
    f"Resilience Score    : "
    f"{resilience_score:.2f}"
)

print(
    f"Diversification     : "
    f"{diversification_score:.2f}"
)

print(
    f"Effective Factors   : "
    f"{effective_factors:.2f}"
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
    f"Worst Sector Loss   : "
    f"{worst_sector['Stress_PnL']:,.0f}"
)

print(
    f"\nOutput Directory:\n"
    f"{OUTPUT_DIR}"
)

print(
    "=" * 70
)