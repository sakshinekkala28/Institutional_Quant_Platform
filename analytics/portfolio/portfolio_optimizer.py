"""
=========================================================
PORTFOLIO OPTIMIZER
=========================================================

Purpose:
Institutional Portfolio Optimization Engine

Input:
data/portfolios/live_portfolio.csv

Output:
data/portfolios/optimized_portfolio.csv
data/portfolios/weight_changes.csv
data/logs/optimizer_report.csv

=========================================================
"""

from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd

from scipy.optimize import minimize

# =========================================================
# CONFIG
# =========================================================

ENGINE_VERSION = "1.0.0"

MAX_POSITION_WEIGHT = 0.05

MAX_SECTOR_WEIGHT = 0.25

MAX_ADV_PARTICIPATION = 0.10

PORTFOLIO_NAV = 100_000_000

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    ROOT
    / "data"
    / "portfolios"
    / "live_portfolio.csv"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "portfolios"
    / "optimized_portfolio.csv"
)

WEIGHT_CHANGE_FILE = (
    ROOT
    / "data"
    / "portfolios"
    / "weight_changes.csv"
)

REPORT_FILE = (
    ROOT
    / "data"
    / "logs"
    / "optimizer_report.csv"
)

# =========================================================
# LOAD
# =========================================================

print("\n📥 Loading Portfolio...")

df = pd.read_csv(INPUT_FILE)

if df.empty:

    raise ValueError(
        "Portfolio is empty."
    )

required_columns = [

    "Symbol",
    "Sector",

    "Weight",

    "Alpha_Adjusted",

    "ADV_20D",
]

missing = [

    c

    for c in required_columns

    if c not in df.columns
]

if missing:

    raise ValueError(
        f"Missing Columns: {missing}"
    )

# =========================================================
# DATA
# =========================================================

alphas = (
    df["Alpha_Adjusted"]
    .fillna(0)
    .values
)

current_weights = (
    df["Weight"]
    .fillna(0)
    .values
)

n_assets = len(df)

# =========================================================
# OBJECTIVE
# =========================================================

def objective(weights):

    return -np.dot(
        weights,
        alphas
    )

# =========================================================
# FULLY INVESTED
# =========================================================

constraints = [

    {
        "type": "eq",

        "fun":
        lambda w:
        np.sum(w) - 1
    }
]

# =========================================================
# SECTOR CONSTRAINTS
# =========================================================

for sector in df["Sector"].dropna().unique():

    sector_idx = np.where(
        df["Sector"] == sector
    )[0]

    constraints.append(

        {

            "type": "ineq",

            "fun":
            lambda w,
            idx=sector_idx:

            MAX_SECTOR_WEIGHT

            - np.sum(
                w[idx]
            )
        }
    )

# =========================================================
# LIQUIDITY CONSTRAINTS
# =========================================================

for i in range(n_assets):

    adv = df.iloc[i]["ADV_20D"]

    max_weight = min(

        MAX_POSITION_WEIGHT,

        (
            adv
            * MAX_ADV_PARTICIPATION
        )
        / PORTFOLIO_NAV
    )

    constraints.append(

        {

            "type": "ineq",

            "fun":
            lambda w,
            i=i,
            limit=max_weight:

            limit - w[i]
        }
    )

# =========================================================
# BOUNDS
# =========================================================

bounds = [

    (
        0,
        MAX_POSITION_WEIGHT
    )

    for _ in range(
        n_assets
    )
]

# =========================================================
# INITIAL GUESS
# =========================================================

x0 = current_weights.copy()

if x0.sum() <= 0:

    x0 = np.repeat(
        1 / n_assets,
        n_assets
    )

# =========================================================
# OPTIMIZE
# =========================================================

print(
    "\n⚙️ Running Optimizer..."
)

result = minimize(

    objective,

    x0,

    method="SLSQP",

    bounds=bounds,

    constraints=constraints,

    options={

        "maxiter": 500,

        "disp": False,
    }
)

if not result.success:

    raise RuntimeError(
        result.message
    )

optimized_weights = (
    result.x
)

# =========================================================
# OUTPUT
# =========================================================

optimized = df.copy()

optimized[
    "Current_Weight"
] = current_weights

optimized[
    "Optimized_Weight"
] = optimized_weights

optimized[
    "Weight_Change"
] = (

    optimized[
        "Optimized_Weight"
    ]

    -

    optimized[
        "Current_Weight"
    ]
)

optimized[
    "Portfolio_Date"
] = datetime.now().strftime(
    "%Y-%m-%d"
)

optimized[
    "Engine_Version"
] = ENGINE_VERSION

optimized = optimized.sort_values(

    "Optimized_Weight",

    ascending=False
)

# =========================================================
# SAVE
# =========================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

optimized.to_csv(
    OUTPUT_FILE,
    index=False
)

weight_changes = optimized[
    [

        "Symbol",

        "Current_Weight",

        "Optimized_Weight",

        "Weight_Change",
    ]
]

weight_changes.to_csv(

    WEIGHT_CHANGE_FILE,

    index=False
)

# =========================================================
# REPORT
# =========================================================

top_weight = (
    optimized[
        "Optimized_Weight"
    ].max()
)

largest_sector = (

    optimized

    .groupby("Sector")

    ["Optimized_Weight"]

    .sum()

    .max()
)

turnover = (

    optimized[
        "Weight_Change"
    ]

    .abs()

    .sum()
)

report = pd.DataFrame(

    {

        "Metric": [

            "Portfolio_Size",

            "Top_Position",

            "Largest_Sector",

            "Turnover",

            "Average_Alpha",

            "Run_Date",

            "Engine_Version",
        ],

        "Value": [

            len(optimized),

            top_weight,

            largest_sector,

            turnover,

            optimized[
                "Alpha_Adjusted"
            ].mean(),

            datetime.now().strftime(
                "%Y-%m-%d"
            ),

            ENGINE_VERSION,
        ]
    }
)

REPORT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

report.to_csv(
    REPORT_FILE,
    index=False
)

# =========================================================
# REPORT
# =========================================================

print("\n" + "=" * 70)

print(
    "🏁 PORTFOLIO OPTIMIZER COMPLETE"
)

print("=" * 70)

print(
    f"Portfolio Size : "
    f"{len(optimized):,}"
)

print(
    f"Top Position   : "
    f"{top_weight:.2%}"
)

print(
    f"Turnover       : "
    f"{turnover:.2%}"
)

print(
    f"\nOutput:\n"
    f"{OUTPUT_FILE}"
)

print("=" * 70)