"""
=========================================================
MONTE CARLO ENGINE
=========================================================

Purpose:
Institutional Forward-Looking Risk Simulation

Method:
Historical Bootstrap Monte Carlo

Input:
data/backtests/walk_forward_equity_curve.csv

Outputs:
data/monte_carlo/monte_carlo_paths.csv
data/monte_carlo/monte_carlo_summary.csv
data/monte_carlo/risk_distribution.csv

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

SIMULATIONS = 10000

FORECAST_YEARS = 5

MONTHS = FORECAST_YEARS * 12

INITIAL_CAPITAL = 1_000_000

SEED = 42

np.random.seed(SEED)

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    ROOT
    / "data"
    / "backtests"
    / "walk_forward_equity_curve.csv"
)

OUTPUT_DIR = (
    ROOT
    / "data"
    / "monte_carlo"
)

REPORT_FILE = (
    ROOT
    / "data"
    / "logs"
    / "monte_carlo_report.csv"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

# =========================================================
# LOAD
# =========================================================

print(
    "\n📥 Loading Walk Forward Results..."
)

equity = pd.read_csv(
    INPUT_FILE
)

required_cols = [
    "Date",
    "Portfolio_Value",
]

missing = [
    c
    for c in required_cols
    if c not in equity.columns
]

if missing:

    raise ValueError(
        f"Missing Columns: {missing}"
    )

# =========================================================
# RETURNS
# =========================================================

returns = (

    equity[
        "Portfolio_Value"
    ]

    .pct_change()

    .dropna()

    .values
)

if len(returns) < 24:

    raise ValueError(
        "Insufficient return history"
    )

# =========================================================
# MONTE CARLO
# =========================================================

print(
    "\n🎲 Running Monte Carlo..."
)

terminal_values = []

max_drawdowns = []

paths = np.zeros(
    (
        MONTHS + 1,
        SIMULATIONS
    )
)

for sim in range(
    SIMULATIONS
):

    sampled_returns = np.random.choice(

        returns,

        size=MONTHS,

        replace=True,
    )

    portfolio = np.empty(
        MONTHS + 1
    )

    portfolio[0] = (
        INITIAL_CAPITAL
    )

    for t in range(
        MONTHS
    ):

        portfolio[
            t + 1
        ] = (

            portfolio[t]

            * (

                1
                + sampled_returns[t]

            )
        )

    paths[:, sim] = portfolio

    terminal_values.append(
        portfolio[-1]
    )

    running_max = np.maximum.accumulate(
        portfolio
    )

    drawdown = (
        portfolio
        / running_max
    ) - 1

    max_drawdowns.append(
        drawdown.min()
    )

# =========================================================
# PATH OUTPUT
# =========================================================

paths_df = pd.DataFrame(
    paths
)

paths_df.to_csv(

    OUTPUT_DIR
    / "monte_carlo_paths.csv",

    index=False,
)

# =========================================================
# STATISTICS
# =========================================================

terminal_values = np.array(
    terminal_values
)

max_drawdowns = np.array(
    max_drawdowns
)

cagrs = (

    (
        terminal_values
        / INITIAL_CAPITAL
    )

    ** (

        1
        / FORECAST_YEARS

    )

    - 1
)

# =========================================================
# VAR
# =========================================================

portfolio_returns = (

    terminal_values

    / INITIAL_CAPITAL

    - 1
)

var95 = np.percentile(

    portfolio_returns,

    5,
)

var99 = np.percentile(

    portfolio_returns,

    1,
)

# =========================================================
# PROBABILITIES
# =========================================================

prob_loss = (

    terminal_values
    < INITIAL_CAPITAL

).mean()

prob_dd20 = (

    max_drawdowns
    <= -0.20

).mean()

prob_dd40 = (

    max_drawdowns
    <= -0.40

).mean()

# =========================================================
# SUMMARY
# =========================================================

summary = pd.DataFrame({

    "Metric": [

        "Median_CAGR",

        "CAGR_5th",

        "CAGR_95th",

        "Median_Terminal_Value",

        "Worst_5pct_Terminal",

        "Best_95pct_Terminal",

        "Probability_Loss",

        "Probability_DD20",

        "Probability_DD40",

        "VaR_95",

        "VaR_99",

        "Median_Max_Drawdown",

        "Run_Date",

        "Engine_Version",
    ],

    "Value": [

        np.median(
            cagrs
        ),

        np.percentile(
            cagrs,
            5,
        ),

        np.percentile(
            cagrs,
            95,
        ),

        np.median(
            terminal_values
        ),

        np.percentile(
            terminal_values,
            5,
        ),

        np.percentile(
            terminal_values,
            95,
        ),

        prob_loss,

        prob_dd20,

        prob_dd40,

        var95,

        var99,

        np.median(
            max_drawdowns
        ),

        datetime.now()
        .strftime(
            "%Y-%m-%d"
        ),

        ENGINE_VERSION,
    ]
})

# =========================================================
# RISK DISTRIBUTION
# =========================================================

distribution = pd.DataFrame({

    "Terminal_Value":
    terminal_values,

    "CAGR":
    cagrs,

    "Max_Drawdown":
    max_drawdowns,
})

# =========================================================
# SAVE
# =========================================================

summary.to_csv(

    OUTPUT_DIR
    / "monte_carlo_summary.csv",

    index=False,
)

distribution.to_csv(

    OUTPUT_DIR
    / "risk_distribution.csv",

    index=False,
)

summary.to_csv(

    REPORT_FILE,

    index=False,
)

# =========================================================
# REPORT
# =========================================================

print("\n" + "=" * 70)

print(
    "🏁 MONTE CARLO COMPLETE"
)

print("=" * 70)

print(
    f"Simulations          : "
    f"{SIMULATIONS:,}"
)

print(
    f"Forecast Horizon     : "
    f"{FORECAST_YEARS} Years"
)

print(
    f"Median CAGR          : "
    f"{np.median(cagrs):.2%}"
)

print(
    f"5th Percentile CAGR  : "
    f"{np.percentile(cagrs,5):.2%}"
)

print(
    f"95th Percentile CAGR : "
    f"{np.percentile(cagrs,95):.2%}"
)

print(
    f"Probability Loss     : "
    f"{prob_loss:.2%}"
)

print(
    f"Probability DD >20%  : "
    f"{prob_dd20:.2%}"
)

print(
    f"Probability DD >40%  : "
    f"{prob_dd40:.2%}"
)

print(
    f"VaR 95               : "
    f"{var95:.2%}"
)

print(
    f"VaR 99               : "
    f"{var99:.2%}"
)

print(
    f"\nOutput Directory:\n"
    f"{OUTPUT_DIR}"
)

print("=" * 70)