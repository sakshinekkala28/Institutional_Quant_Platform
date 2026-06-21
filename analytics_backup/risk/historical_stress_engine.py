"""
=========================================================
HISTORICAL STRESS ENGINE
=========================================================

Purpose:
Replay Historical Market Crises Against
Current Portfolio Holdings

Inputs:
data/portfolios/live_portfolio.csv
data/raw/prices/*.parquet

Outputs:
data/stress_tests/historical_stress_results.csv
data/stress_tests/historical_stress_dashboard.csv
data/stress_tests/historical_stress_summary.csv
data/stress_tests/historical_sector_impact.csv
data/stress_tests/historical_position_impact.csv

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

MIN_HISTORY_DAYS = 30

MIN_PORTFOLIO_SIZE = 20

# =========================================================
# HISTORICAL CRISIS LIBRARY
# =========================================================

CRISES = {

    "COVID_CRASH": {

        "Start_Date":
        "2020-02-20",

        "End_Date":
        "2020-03-23",

        "Description":
        "COVID Market Crash",
    },

    "RUSSIA_UKRAINE": {

        "Start_Date":
        "2022-02-01",

        "End_Date":
        "2022-03-31",

        "Description":
        "Russia Ukraine Conflict",
    },

    "RATE_SHOCK_2022": {

        "Start_Date":
        "2022-01-01",

        "End_Date":
        "2022-10-31",

        "Description":
        "Global Rate Shock",
    },

    "SVB_CRISIS": {

        "Start_Date":
        "2023-03-01",

        "End_Date":
        "2023-03-31",

        "Description":
        "Silicon Valley Bank Crisis",
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

PRICE_DIR = (
    ROOT
    / "data"
    / "raw"
    / "prices"
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
    / "historical_stress_report.csv"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

# =========================================================
# LOAD PORTFOLIO
# =========================================================

print(
    "\n📥 Loading Portfolio..."
)

portfolio = pd.read_csv(
    PORTFOLIO_FILE
)

# =========================================================
# VALIDATION
# =========================================================

required_columns = [

    "Symbol",
    "Weight",
    "Sector",
]

for col in required_columns:

    if col not in portfolio.columns:

        raise ValueError(
            f"Missing Column: {col}"
        )

if len(portfolio) < MIN_PORTFOLIO_SIZE:

    raise ValueError(
        f"Portfolio too small: "
        f"{len(portfolio)}"
    )

# =========================================================
# CLEAN WEIGHTS
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
# POSITION VALUES
# =========================================================

portfolio[
    "Position_Value"
] = (

    portfolio[
        "Weight"
    ]

    * PORTFOLIO_NAV
)

# =========================================================
# PRICE FILE COVERAGE
# =========================================================

available_prices = 0
missing_prices = 0

for symbol in portfolio["Symbol"]:

    file = (
        PRICE_DIR
        / f"{symbol}.parquet"
    )

    if file.exists():

        available_prices += 1

    else:

        missing_prices += 1

coverage = (

    available_prices

    /

    max(
        len(portfolio),
        1
    )
)

if coverage < 0.90:

    raise ValueError(

        "Price coverage too low: "

        f"{coverage:.2%}"
    )

# =========================================================
# DIAGNOSTICS
# =========================================================

print(
    f"Portfolio Holdings : "
    f"{len(portfolio)}"
)

print(
    f"Price Coverage     : "
    f"{coverage:.2%}"
)

print(
    f"Crisis Scenarios   : "
    f"{len(CRISES)}"
)

for crisis in CRISES:

    print(
        f"✓ {crisis}"
    )

# =========================================================
# STORAGE CONTAINERS
# =========================================================

crisis_results = []

position_results = []

sector_results = []

# =========================================================
# PART 2 STARTS HERE
# =========================================================
#
# Next:
#
# Historical Return Construction
# Crisis Window Returns
# Position-Level Crisis Impact
# Portfolio Crisis Returns
#
# =========================================================

# =========================================================
# HISTORICAL CRISIS REPLAY
# =========================================================

print(
    "\n📉 Running Historical Stress Replay..."
)

for crisis_name, crisis in CRISES.items():

    print(
        f"\nRunning: {crisis_name}"
    )

    crisis_start = pd.to_datetime(
        crisis["Start_Date"]
    )

    crisis_end = pd.to_datetime(
        crisis["End_Date"]
    )

    portfolio_return = 0.0
    portfolio_pnl = 0.0

    crisis_positions = []

    # =====================================================
    # POSITION REPLAY
    # =====================================================

    for _, position in portfolio.iterrows():

        symbol = position["Symbol"]

        weight = position["Weight"]

        sector = position["Sector"]

        position_value = position[
            "Position_Value"
        ]

        file = (
            PRICE_DIR
            / f"{symbol}.parquet"
        )

        if not file.exists():
            continue

        try:

            prices = pd.read_parquet(
                file
            )

            if (
                "Date"
                not in prices.columns
                or
                "Close"
                not in prices.columns
            ):
                continue

            prices["Date"] = pd.to_datetime(
                prices["Date"]
            )

            prices = prices.sort_values(
                "Date"
            )

            crisis_window = prices[

                (
                    prices["Date"]
                    >= crisis_start
                )

                &

                (
                    prices["Date"]
                    <= crisis_end
                )

            ].copy()

            if len(
                crisis_window
            ) < MIN_HISTORY_DAYS:

                continue

            start_price = float(

                crisis_window[
                    "Close"
                ].iloc[0]

            )

            end_price = float(

                crisis_window[
                    "Close"
                ].iloc[-1]

            )

            if start_price <= 0:
                continue

            crisis_return = (

                end_price
                /
                start_price

                - 1
            )

            pnl = (

                position_value
                *
                crisis_return
            )

            stressed_value = (

                position_value
                +
                pnl
            )

            contribution = (

                pnl
                /
                PORTFOLIO_NAV
            )

            portfolio_return += (

                weight
                *
                crisis_return
            )

            portfolio_pnl += pnl

            crisis_positions.append({

                "Crisis":
                crisis_name,

                "Symbol":
                symbol,

                "Sector":
                sector,

                "Weight":
                weight,

                "Position_Value":
                position_value,

                "Start_Date":
                crisis_start,

                "End_Date":
                crisis_end,

                "Historical_Return":
                crisis_return,

                "Stress_PnL":
                pnl,

                "Stress_Value":
                stressed_value,

                "Contribution":
                contribution,
            })

        except Exception:

            continue

    # =====================================================
    # POSITION DATAFRAME
    # =====================================================

    if len(
        crisis_positions
    ) == 0:

        continue

    crisis_positions = pd.DataFrame(
        crisis_positions
    )

    position_results.append(
        crisis_positions
    )

    # =====================================================
    # PORTFOLIO RESULT
    # =====================================================

    stress_nav = (

        PORTFOLIO_NAV
        +
        portfolio_pnl
    )

    crisis_results.append({

        "Crisis":
        crisis_name,

        "Description":
        crisis[
            "Description"
        ],

        "Start_Date":
        crisis_start,

        "End_Date":
        crisis_end,

        "Portfolio_NAV":
        PORTFOLIO_NAV,

        "Stress_NAV":
        stress_nav,

        "Portfolio_Return":
        portfolio_return,

        "Portfolio_PnL":
        portfolio_pnl,
    })

# =========================================================
# BUILD RESULTS
# =========================================================

if len(
    crisis_results
) == 0:

    raise ValueError(
        "No crisis results generated"
    )

historical_results = pd.DataFrame(
    crisis_results
)

historical_positions = pd.concat(

    position_results,

    ignore_index=True
)

# =========================================================
# POSITION RANKING
# =========================================================

historical_positions[
    "Loss_Rank"
] = (

    historical_positions

    .groupby(
        "Crisis"
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

    historical_positions

    .sort_values(
        "Stress_PnL"
    )

    .groupby(
        "Crisis"
    )

    .head(10)

    .copy()
)

# =========================================================
# BEST HOLDINGS
# =========================================================

best_positions = (

    historical_positions

    .sort_values(

        "Stress_PnL",

        ascending=False

    )

    .groupby(
        "Crisis"
    )

    .head(10)

    .copy()
)

# =========================================================
# CRISIS RANKING
# =========================================================

historical_results = (

    historical_results

    .sort_values(
        "Portfolio_Return"
    )

    .reset_index(
        drop=True
    )
)

historical_results[
    "Crisis_Rank"
] = (
    historical_results.index + 1
)

worst_crisis = (

    historical_results

    .iloc[0]
)

best_crisis = (

    historical_results

    .iloc[-1]
)

# =========================================================
# DIAGNOSTICS
# =========================================================

print(
    f"\nWorst Crisis : "
    f"{worst_crisis['Crisis']}"
)

print(
    f"Return       : "
    f"{worst_crisis['Portfolio_Return']:.2%}"
)

print(
    f"\nBest Crisis  : "
    f"{best_crisis['Crisis']}"
)

print(
    f"Return       : "
    f"{best_crisis['Portfolio_Return']:.2%}"
)

# =========================================================
# PART 3 STARTS HERE
# =========================================================
#
# Next:
#
# Sector Attribution
# Sector Damage Analysis
# Crisis Dashboard
# Heatmap Dataset
#
# =========================================================

# =========================================================
# SECTOR ATTRIBUTION
# =========================================================

print(
    "\n🏭 Building Historical Sector Attribution..."
)

historical_sector_impact = (

    historical_positions

    .groupby(

        [
            "Crisis",
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

historical_sector_impact[
    "Sector_Return"
] = (

    historical_sector_impact[
        "Stress_PnL"
    ]

    /

    historical_sector_impact[
        "Position_Value"
    ]
)

# =========================================================
# PORTFOLIO CONTRIBUTION
# =========================================================

historical_sector_impact[
    "Contribution"
] = (

    historical_sector_impact[
        "Stress_PnL"
    ]

    /

    PORTFOLIO_NAV
)

# =========================================================
# DAMAGE RANKING
# =========================================================

historical_sector_impact[
    "Damage_Rank"
] = (

    historical_sector_impact

    .groupby(
        "Crisis"
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

    historical_sector_impact

    .sort_values(
        "Stress_PnL"
    )

    .groupby(
        "Crisis"
    )

    .head(10)

    .copy()
)

# =========================================================
# BEST SECTORS
# =========================================================

best_sectors = (

    historical_sector_impact

    .sort_values(
        "Stress_PnL",
        ascending=False
    )

    .groupby(
        "Crisis"
    )

    .head(10)

    .copy()
)

# =========================================================
# TOP / BOTTOM SECTOR
# =========================================================

worst_sector = (

    historical_sector_impact

    .sort_values(
        "Stress_PnL"
    )

    .iloc[0]
)

best_sector = (

    historical_sector_impact

    .sort_values(
        "Stress_PnL",
        ascending=False
    )

    .iloc[0]
)

# =========================================================
# CRISIS DASHBOARD
# =========================================================

historical_dashboard = (

    historical_results[[

        "Crisis",

        "Description",

        "Start_Date",

        "End_Date",

        "Portfolio_NAV",

        "Stress_NAV",

        "Portfolio_Return",

        "Portfolio_PnL",

        "Crisis_Rank",
    ]]

    .copy()
)

# =========================================================
# SECTOR HEATMAP
# =========================================================

sector_heatmap = (

    historical_sector_impact

    .pivot_table(

        index="Sector",

        columns="Crisis",

        values="Sector_Return",

        aggfunc="mean"
    )
)

sector_heatmap.to_csv(

    OUTPUT_DIR
    / "historical_sector_heatmap.csv"
)

# =========================================================
# CRISIS STATISTICS
# =========================================================

average_crisis_return = (

    historical_results[
        "Portfolio_Return"
    ]

    .mean()
)

worst_crisis_return = (

    historical_results[
        "Portfolio_Return"
    ]

    .min()
)

best_crisis_return = (

    historical_results[
        "Portfolio_Return"
    ]

    .max()
)

crisis_volatility = (

    historical_results[
        "Portfolio_Return"
    ]

    .std()
)

# =========================================================
# DAMAGE SUMMARY
# =========================================================

damage_summary = pd.DataFrame({

    "Metric": [

        "Average_Crisis_Return",

        "Worst_Crisis_Return",

        "Best_Crisis_Return",

        "Crisis_Volatility",

        "Worst_Sector",

        "Best_Sector",
    ],

    "Value": [

        average_crisis_return,

        worst_crisis_return,

        best_crisis_return,

        crisis_volatility,

        worst_sector[
            "Sector"
        ],

        best_sector[
            "Sector"
        ],
    ]
})

# =========================================================
# SECTOR CONCENTRATION
# =========================================================

sector_concentration = (

    historical_sector_impact

    .groupby(
        "Crisis"
    )

    .apply(

        lambda x:

        pd.Series({

            "Sector_Count":

                len(x),

            "Largest_Loss":

                x[
                    "Stress_PnL"
                ].min(),

            "Largest_Gain":

                x[
                    "Stress_PnL"
                ].max(),
        })

    )

    .reset_index()
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
    f"\nAverage Crisis Return : "
    f"{average_crisis_return:.2%}"
)

# =========================================================
# PART 4 STARTS HERE
# =========================================================
#
# Next:
#
# Historical VaR
# Historical CVaR
# Crisis Risk Score
# Resilience Score
# Executive Summary
# Save Outputs
# Final Reporting
#
# =========================================================

# =========================================================
# SECTOR ATTRIBUTION
# =========================================================

print(
    "\n🏭 Building Historical Sector Attribution..."
)

historical_sector_impact = (

    historical_positions

    .groupby(

        [
            "Crisis",
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

historical_sector_impact[
    "Sector_Return"
] = (

    historical_sector_impact[
        "Stress_PnL"
    ]

    /

    historical_sector_impact[
        "Position_Value"
    ]
)

# =========================================================
# PORTFOLIO CONTRIBUTION
# =========================================================

historical_sector_impact[
    "Contribution"
] = (

    historical_sector_impact[
        "Stress_PnL"
    ]

    /

    PORTFOLIO_NAV
)

# =========================================================
# DAMAGE RANKING
# =========================================================

historical_sector_impact[
    "Damage_Rank"
] = (

    historical_sector_impact

    .groupby(
        "Crisis"
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

    historical_sector_impact

    .sort_values(
        "Stress_PnL"
    )

    .groupby(
        "Crisis"
    )

    .head(10)

    .copy()
)

# =========================================================
# BEST SECTORS
# =========================================================

best_sectors = (

    historical_sector_impact

    .sort_values(
        "Stress_PnL",
        ascending=False
    )

    .groupby(
        "Crisis"
    )

    .head(10)

    .copy()
)

# =========================================================
# TOP / BOTTOM SECTOR
# =========================================================

worst_sector = (

    historical_sector_impact

    .sort_values(
        "Stress_PnL"
    )

    .iloc[0]
)

best_sector = (

    historical_sector_impact

    .sort_values(
        "Stress_PnL",
        ascending=False
    )

    .iloc[0]
)

# =========================================================
# CRISIS DASHBOARD
# =========================================================

historical_dashboard = (

    historical_results[[

        "Crisis",

        "Description",

        "Start_Date",

        "End_Date",

        "Portfolio_NAV",

        "Stress_NAV",

        "Portfolio_Return",

        "Portfolio_PnL",

        "Crisis_Rank",
    ]]

    .copy()
)

# =========================================================
# SECTOR HEATMAP
# =========================================================

sector_heatmap = (

    historical_sector_impact

    .pivot_table(

        index="Sector",

        columns="Crisis",

        values="Sector_Return",

        aggfunc="mean"
    )
)

sector_heatmap.to_csv(

    OUTPUT_DIR
    / "historical_sector_heatmap.csv"
)

# =========================================================
# CRISIS STATISTICS
# =========================================================

average_crisis_return = (

    historical_results[
        "Portfolio_Return"
    ]

    .mean()
)

worst_crisis_return = (

    historical_results[
        "Portfolio_Return"
    ]

    .min()
)

best_crisis_return = (

    historical_results[
        "Portfolio_Return"
    ]

    .max()
)

crisis_volatility = (

    historical_results[
        "Portfolio_Return"
    ]

    .std()
)

# =========================================================
# DAMAGE SUMMARY
# =========================================================

damage_summary = pd.DataFrame({

    "Metric": [

        "Average_Crisis_Return",

        "Worst_Crisis_Return",

        "Best_Crisis_Return",

        "Crisis_Volatility",

        "Worst_Sector",

        "Best_Sector",
    ],

    "Value": [

        average_crisis_return,

        worst_crisis_return,

        best_crisis_return,

        crisis_volatility,

        worst_sector[
            "Sector"
        ],

        best_sector[
            "Sector"
        ],
    ]
})

# =========================================================
# SECTOR CONCENTRATION
# =========================================================

sector_concentration = (

    historical_sector_impact

    .groupby(
        "Crisis"
    )

    .apply(

        lambda x:

        pd.Series({

            "Sector_Count":

                len(x),

            "Largest_Loss":

                x[
                    "Stress_PnL"
                ].min(),

            "Largest_Gain":

                x[
                    "Stress_PnL"
                ].max(),
        })

    )

    .reset_index()
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
    f"\nAverage Crisis Return : "
    f"{average_crisis_return:.2%}"
)

# =========================================================
# PART 4 STARTS HERE
# =========================================================
#
# Next:
#
# Historical VaR
# Historical CVaR
# Crisis Risk Score
# Resilience Score
# Executive Summary
# Save Outputs
# Final Reporting
#
# =========================================================

# =========================================================
# HISTORICAL RISK METRICS
# =========================================================

print(
    "\n⚠ Calculating Historical Risk Metrics..."
)

historical_returns = (

    historical_results[
        "Portfolio_Return"
    ]

    .values
)

# =========================================================
# HISTORICAL VAR 95
# =========================================================

historical_var_95 = np.percentile(

    historical_returns,

    5
)

# =========================================================
# HISTORICAL CVAR 95
# =========================================================

tail_returns = historical_returns[

    historical_returns
    <=
    historical_var_95
]

if len(
    tail_returns
) > 0:

    historical_cvar_95 = (
        tail_returns.mean()
    )

else:

    historical_cvar_95 = (
        historical_var_95
    )

# =========================================================
# WORST CRISIS
# =========================================================

worst_crisis_return = (

    historical_results[
        "Portfolio_Return"
    ]

    .min()
)

worst_crisis_loss = (

    historical_results[
        "Portfolio_PnL"
    ]

    .min()
)

# =========================================================
# BEST CRISIS
# =========================================================

best_crisis_return = (

    historical_results[
        "Portfolio_Return"
    ]

    .max()
)

best_crisis_gain = (

    historical_results[
        "Portfolio_PnL"
    ]

    .max()
)

# =========================================================
# RISK SCORE
# =========================================================

risk_score = min(

    abs(
        worst_crisis_return
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
# RECOVERY SCORE
# =========================================================

recovery_score = (

    (
        best_crisis_return

        -

        worst_crisis_return
    )

    * 100
)

recovery_score = max(
    recovery_score,
    0
)

# =========================================================
# CRISIS DISPERSION
# =========================================================

crisis_dispersion = (

    historical_results[
        "Portfolio_Return"
    ]

    .std()
)

# =========================================================
# RISK CLASSIFICATION
# =========================================================

if abs(
    worst_crisis_return
) < 0.10:

    risk_level = (
        "LOW"
    )

elif abs(
    worst_crisis_return
) < 0.20:

    risk_level = (
        "MODERATE"
    )

elif abs(
    worst_crisis_return
) < 0.30:

    risk_level = (
        "HIGH"
    )

else:

    risk_level = (
        "SEVERE"
    )

# =========================================================
# CRISIS SURVIVAL SCORE
# =========================================================

survival_score = (

    100

    *

    (

        historical_results[
            "Portfolio_Return"
        ]

        >

        -0.20

    ).mean()
)

# =========================================================
# EXECUTIVE SUMMARY
# =========================================================

historical_summary = pd.DataFrame({

    "Metric": [

        "Worst_Crisis",

        "Worst_Crisis_Return",

        "Worst_Crisis_Loss",

        "Best_Crisis",

        "Best_Crisis_Return",

        "Best_Crisis_Gain",

        "Historical_VaR_95",

        "Historical_CVaR_95",

        "Risk_Score",

        "Resilience_Score",

        "Recovery_Score",

        "Survival_Score",

        "Crisis_Dispersion",

        "Risk_Level",

        "Run_Date",

        "Engine_Version",
    ],

    "Value": [

        worst_crisis[
            "Crisis"
        ],

        worst_crisis_return,

        worst_crisis_loss,

        best_crisis[
            "Crisis"
        ],

        best_crisis_return,

        best_crisis_gain,

        historical_var_95,

        historical_cvar_95,

        risk_score,

        resilience_score,

        recovery_score,

        survival_score,

        crisis_dispersion,

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

historical_results.to_csv(

    OUTPUT_DIR
    / "historical_stress_results.csv",

    index=False,
)

historical_dashboard.to_csv(

    OUTPUT_DIR
    / "historical_stress_dashboard.csv",

    index=False,
)

historical_summary.to_csv(

    OUTPUT_DIR
    / "historical_stress_summary.csv",

    index=False,
)

historical_sector_impact.to_csv(

    OUTPUT_DIR
    / "historical_sector_impact.csv",

    index=False,
)

historical_positions.to_csv(

    OUTPUT_DIR
    / "historical_position_impact.csv",

    index=False,
)

worst_positions.to_csv(

    OUTPUT_DIR
    / "historical_worst_positions.csv",

    index=False,
)

best_positions.to_csv(

    OUTPUT_DIR
    / "historical_best_positions.csv",

    index=False,
)

worst_sectors.to_csv(

    OUTPUT_DIR
    / "historical_worst_sectors.csv",

    index=False,
)

best_sectors.to_csv(

    OUTPUT_DIR
    / "historical_best_sectors.csv",

    index=False,
)

historical_summary.to_csv(

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
    "🏁 HISTORICAL STRESS ENGINE COMPLETE"
)

print(
    "=" * 70
)

print(
    f"Worst Crisis        : "
    f"{worst_crisis['Crisis']}"
)

print(
    f"Worst Return        : "
    f"{worst_crisis_return:.2%}"
)

print(
    f"Worst Loss          : "
    f"{worst_crisis_loss:,.0f}"
)

print(
    f"\nBest Crisis         : "
    f"{best_crisis['Crisis']}"
)

print(
    f"Best Return         : "
    f"{best_crisis_return:.2%}"
)

print(
    f"Best Gain           : "
    f"{best_crisis_gain:,.0f}"
)

print(
    f"\nHistorical VaR 95   : "
    f"{historical_var_95:.2%}"
)

print(
    f"Historical CVaR 95  : "
    f"{historical_cvar_95:.2%}"
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
    f"Recovery Score      : "
    f"{recovery_score:.2f}"
)

print(
    f"Survival Score      : "
    f"{survival_score:.2f}"
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