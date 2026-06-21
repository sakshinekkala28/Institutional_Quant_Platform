"""
=========================================================
PORTFOLIO HISTORY ENGINE
=========================================================

Purpose:
Institutional Portfolio Snapshot Archive

Inputs:
data/portfolios/live_portfolio.csv

Outputs:
data/portfolios/portfolio_history.csv

=========================================================
"""

from pathlib import Path
from datetime import datetime

import pandas as pd

# =========================================================
# CONFIG
# =========================================================

ENGINE_VERSION = "1.0.0"

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

HISTORY_FILE = (
    ROOT
    / "data"
    / "portfolios"
    / "portfolio_history.csv"
)

REPORT_FILE = (
    ROOT
    / "data"
    / "logs"
    / "portfolio_history_report.csv"
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

if portfolio.empty:

    raise ValueError(
        "Portfolio is empty"
    )

required_cols = [

    "Symbol",
    "Weight",
]

for col in required_cols:

    if col not in portfolio.columns:

        raise ValueError(
            f"Missing column: {col}"
        )

# =========================================================
# SNAPSHOT DATE
# =========================================================

if "Portfolio_Date" in portfolio.columns:

    snapshot_date = pd.to_datetime(
        portfolio[
            "Portfolio_Date"
        ]
    ).max()

else:

    snapshot_date = pd.Timestamp.today().normalize()

# =========================================================
# BUILD SNAPSHOT
# =========================================================

snapshot = portfolio.copy()

snapshot[
    "Portfolio_Date"
] = snapshot_date

# Optional columns if available

desired_cols = [

    "Portfolio_Date",

    "Symbol",

    "Company_Name",

    "Sector",

    "Weight",

    "Rank",

    "Alpha_Adjusted",

    "Last_Close",
]

existing_cols = [

    c

    for c in desired_cols

    if c in snapshot.columns
]

snapshot = snapshot[
    existing_cols
].copy()

snapshot[
    "Engine_Version"
] = ENGINE_VERSION

snapshot[
    "Created_Timestamp"
] = datetime.now()

# =========================================================
# LOAD HISTORY
# =========================================================

if HISTORY_FILE.exists():

    history = pd.read_csv(
        HISTORY_FILE
    )

    history[
        "Portfolio_Date"
    ] = pd.to_datetime(
        history[
            "Portfolio_Date"
        ]
    )

    snapshot_date_norm = (
        pd.Timestamp(
            snapshot_date
        )
        .normalize()
    )

    history = history[

        history[
            "Portfolio_Date"
        ].dt.normalize()

        !=

        snapshot_date_norm

    ]

else:

    history = pd.DataFrame()
    
# =========================================================
# APPEND
# =========================================================

history = pd.concat(

    [
        history,
        snapshot,
    ],

    ignore_index=True,
)

history = history.sort_values(

    [
        "Portfolio_Date",
        "Weight",
    ],

    ascending=[
        True,
        False,
    ],
)

# =========================================================
# SAVE
# =========================================================

history.to_csv(
    HISTORY_FILE,
    index=False,
)

report = pd.DataFrame({

    "Metric": [

        "Snapshot_Date",

        "Positions",

        "History_Records",

        "Unique_Snapshots",

        "Engine_Version",
    ],

    "Value": [

        str(
            snapshot_date.date()
        ),

        len(
            snapshot
        ),

        len(
            history
        ),

        history[
            "Portfolio_Date"
        ].nunique(),

        ENGINE_VERSION,
    ]
})

report.to_csv(
    REPORT_FILE,
    index=False,
)

# =========================================================
# REPORT
# =========================================================

print(
    "\n"
    + "=" * 70
)

print(
    "🏁 PORTFOLIO HISTORY ENGINE COMPLETE"
)

print(
    "=" * 70
)

print(
    f"Snapshot Date     : "
    f"{snapshot_date.date()}"
)

print(
    f"Positions         : "
    f"{len(snapshot)}"
)

print(
    f"History Records   : "
    f"{len(history)}"
)

print(
    f"Unique Snapshots  : "
    f"{history['Portfolio_Date'].nunique()}"
)

print(
    f"\nSaved:\n"
    f"{HISTORY_FILE}"
)

print(
    "=" * 70
)