"""
=========================================================
ENSEMBLE ENGINE
=========================================================

Purpose:
Institutional Multi-Strategy Portfolio Builder

=========================================================
"""

from pathlib import Path
from datetime import datetime

import pandas as pd

ENGINE_VERSION = "1.0.0"

ROOT = Path(__file__).resolve().parents[2]

ALLOCATION_FILE = (
    ROOT
    / "data"
    / "research"
    / "meta_strategy_allocation.csv"
)

STRATEGY_DIR = (
    ROOT
    / "data"
    / "strategies"
)

OUTPUT_DIR = (
    ROOT
    / "data"
    / "research"
)

PORTFOLIO_DIR = (
    ROOT
    / "data"
    / "portfolios"
)

REPORT_FILE = (
    ROOT
    / "data"
    / "logs"
    / "ensemble_report.csv"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

PORTFOLIO_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

print(
    "\n📥 Loading Strategy Allocations..."
)

allocation = pd.read_csv(
    ALLOCATION_FILE
)

required = [
    "Strategy",
    "Weight",
]

for col in required:

    if col not in allocation.columns:

        raise ValueError(
            f"Missing Column: {col}"
        )

ensemble_positions = []

for _, row in allocation.iterrows():

    strategy = str(
        row["Strategy"]
    ).strip()

    meta_weight = float(
        row["Weight"]
    )

    file = (
        STRATEGY_DIR
        / f"{strategy}.csv"
    )

    if not file.exists():

        print(
            f"Skipping {strategy}"
        )

        continue

    try:

        portfolio = pd.read_csv(
            file
        )

        if (
            "Symbol"
            not in portfolio.columns
            or
            "Weight"
            not in portfolio.columns
        ):
            continue

        portfolio = portfolio[
            [
                "Symbol",
                "Weight",
            ]
        ].copy()

        portfolio[
            "Strategy"
        ] = strategy

        portfolio[
            "Meta_Weight"
        ] = meta_weight

        portfolio[
            "Effective_Weight"
        ] = (

            portfolio["Weight"]

            * meta_weight
        )

        ensemble_positions.append(
            portfolio
        )

    except Exception:

        continue

if not ensemble_positions:

    raise ValueError(
        "No strategy portfolios loaded"
    )

combined = pd.concat(
    ensemble_positions,
    ignore_index=True,
)

ensemble = (

    combined

    .groupby("Symbol")

    ["Effective_Weight"]

    .sum()

    .reset_index()

)

ensemble.columns = [

    "Symbol",

    "Weight",
]

ensemble["Weight"] = (

    ensemble["Weight"]

    / ensemble["Weight"].sum()
)

ensemble = (

    ensemble

    .sort_values(
        "Weight",
        ascending=False,
    )

    .reset_index(
        drop=True
    )
)

ensemble["Rank"] = (
    ensemble.index + 1
)

ensemble = ensemble[

    [
        "Rank",
        "Symbol",
        "Weight",
    ]
]

# Save

ensemble.to_csv(

    PORTFOLIO_DIR
    / "ensemble_portfolio.csv",

    index=False,
)

combined.to_csv(

    OUTPUT_DIR
    / "ensemble_weights.csv",

    index=False,
)

summary = pd.DataFrame({

    "Metric": [

        "Strategies",

        "Securities",

        "Run_Date",

        "Engine_Version",
    ],

    "Value": [

        allocation[
            "Strategy"
        ].nunique(),

        ensemble[
            "Symbol"
        ].nunique(),

        datetime.now()
        .strftime(
            "%Y-%m-%d"
        ),

        ENGINE_VERSION,
    ]
})

summary.to_csv(

    OUTPUT_DIR
    / "ensemble_summary.csv",

    index=False,
)

summary.to_csv(
    REPORT_FILE,
    index=False,
)

print("\n" + "=" * 70)
print(
    "🏁 ENSEMBLE ENGINE COMPLETE"
)
print("=" * 70)
print(
    f"Strategies : "
    f"{allocation['Strategy'].nunique()}"
)
print(
    f"Securities : "
    f"{ensemble['Symbol'].nunique()}"
)
print(
    f"\nPortfolio:\n"
    f"{PORTFOLIO_DIR / 'ensemble_portfolio.csv'}"
)
print("=" * 70)