"""
=========================================================
CAPACITY ENGINE
=========================================================

Purpose:
Institutional Strategy Capacity Analysis

Inputs:
data/portfolios/live_portfolio.csv

Outputs:
data/capacity/capacity_master.csv
data/capacity/capacity_summary.csv
data/logs/capacity_report.csv

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

MAX_ADV_PARTICIPATION = 0.10

PORTFOLIO_NAV = 100_000_000

TARGET_EXIT_DAYS = 3

TARGET_POSITION_SIZE = 0.05

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

OUTPUT_DIR = (
    ROOT
    / "data"
    / "capacity"
)

REPORT_FILE = (
    ROOT
    / "data"
    / "logs"
    / "capacity_report.csv"
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

if portfolio.empty:

    raise ValueError(
        "Portfolio is empty"
    )

# =========================================================
# VALIDATION
# =========================================================

required_columns = [

    "Symbol",

    "Weight",

    "ADV_20D",

    "Market_Cap",
]

missing = [

    c

    for c in required_columns

    if c not in portfolio.columns
]

if missing:

    raise ValueError(
        f"Missing Columns: {missing}"
    )

# =========================================================
# CLEAN
# =========================================================

portfolio["ADV_20D"] = pd.to_numeric(
    portfolio["ADV_20D"],
    errors="coerce",
)

portfolio["Market_Cap"] = pd.to_numeric(
    portfolio["Market_Cap"],
    errors="coerce",
)

portfolio = portfolio.dropna(
    subset=[
        "ADV_20D",
        "Market_Cap",
    ]
)

# =========================================================
# POSITION CAPACITY
# =========================================================

portfolio["Max_Daily_Trade"] = (

    portfolio["ADV_20D"]

    * MAX_ADV_PARTICIPATION
)

portfolio["Position_Capacity"] = (

    portfolio["Max_Daily_Trade"]

    * TARGET_EXIT_DAYS
)

# =========================================================
# IMPLIED FUND SIZE
# =========================================================

portfolio["Implied_Fund_Capacity"] = (

    portfolio["Position_Capacity"]

    / np.maximum(
        portfolio["Weight"],
        0.0001,
    )
)

# =========================================================
# MARKET CAP CONSTRAINT
# =========================================================

portfolio["MarketCap_Limit"] = (

    portfolio["Market_Cap"]

    * 0.01
)

portfolio["Effective_Capacity"] = np.minimum(

    portfolio["Implied_Fund_Capacity"],

    portfolio["MarketCap_Limit"],
)

# =========================================================
# DAYS TO EXIT
# =========================================================

portfolio["Days_To_Exit"] = (

    portfolio["Weight"]

    * portfolio[
        "Effective_Capacity"
    ]

) / np.maximum(

    portfolio["Max_Daily_Trade"],

    1,
)

# =========================================================
# PARTICIPATION RATE
# =========================================================

portfolio["Participation_Rate"] = (

    (
        portfolio["Weight"]

        * portfolio[
            "Effective_Capacity"
        ]
    )

    /

    np.maximum(
        portfolio["ADV_20D"],
        1,
    )
)

# =========================================================
# CAPACITY SCORE
# =========================================================

adv_rank = (

    portfolio["ADV_20D"]

    .rank(
        pct=True
    )
)

mcap_rank = (

    portfolio["Market_Cap"]

    .rank(
        pct=True
    )
)

exit_rank = (

    1

    -

    portfolio[
        "Days_To_Exit"
    ]

    .rank(
        pct=True
    )
)

portfolio["Capacity_Score"] = (

      0.40
    * adv_rank

    + 0.40
    * mcap_rank

    + 0.20
    * exit_rank

) * 100

# =========================================================
# CAPACITY CLASSIFICATION
# =========================================================

conditions = [

    portfolio[
        "Capacity_Score"
    ] >= 80,

    portfolio[
        "Capacity_Score"
    ] >= 60,

    portfolio[
        "Capacity_Score"
    ] >= 40,
]

choices = [

    "INSTITUTIONAL",

    "SCALABLE",

    "LIMITED",
]

portfolio["Capacity_Class"] = np.select(

    conditions,

    choices,

    default="CONSTRAINED",
)

# =========================================================
# STRATEGY CAPACITY
# =========================================================

strategy_capacity = (

    portfolio[
        "Effective_Capacity"
    ]

    .min()
)

constraint = (

    portfolio

    .sort_values(
        "Effective_Capacity"
    )

    .iloc[0]
)

constraint_symbol = constraint["Symbol"]

constraint_capacity = (
    constraint["Effective_Capacity"]
)

constraints = (

    portfolio

    .nsmallest(
        20,
        "Effective_Capacity"
    )
)

top5_capacity_share = (

    portfolio

    .nlargest(
        5,
        "Effective_Capacity"
    )

    [
        "Effective_Capacity"
    ]

    .sum()

    /

    portfolio[
        "Effective_Capacity"
    ].sum()
)

portfolio["Liquidity_Breach"] = (

    portfolio[
        "Days_To_Exit"
    ]

    > TARGET_EXIT_DAYS
)

breaches = (

    portfolio[
        "Liquidity_Breach"
    ]

    .sum()
)

weighted_capacity = (

    portfolio[
        "Effective_Capacity"
    ]

    .median()
)

avg_days_exit = (

    portfolio[
        "Days_To_Exit"
    ]

    .mean()
)

avg_score = (

    portfolio[
        "Capacity_Score"
    ]

    .mean()
)

capacity_utilization = (

    PORTFOLIO_NAV

    /

    max(
        strategy_capacity,
        1
    )
)

if capacity_utilization < 0.25:

    capacity_grade = "A"

elif capacity_utilization < 0.50:

    capacity_grade = "B"

elif capacity_utilization < 0.75:

    capacity_grade = "C"

else:

    capacity_grade = "D"


institutional_positions = (

    portfolio[
        "Capacity_Class"
    ]

    == "INSTITUTIONAL"

).sum()

institutional_share = (

    institutional_positions

    /

    len(portfolio)
)

scalable_positions = (

    portfolio[
        "Capacity_Class"
    ]

    == "SCALABLE"

).sum()

limited_positions = (

    portfolio[
        "Capacity_Class"
    ]

    == "LIMITED"

).sum()

constrained_positions = (

    portfolio[
        "Capacity_Class"
    ]

    == "CONSTRAINED"

).sum()

capacity_distribution = (

    portfolio[
        "Capacity_Class"
    ]

    .value_counts(
        normalize=True
    )

    * 100
)

institutional_scalable_share = (

    institutional_positions

    + scalable_positions

) / len(portfolio)

if institutional_scalable_share >= 0.70:

    capacity_risk = "LOW"

elif institutional_scalable_share >= 0.50:

    capacity_risk = "MODERATE"

else:

    capacity_risk = "HIGH"

capacity_health = (

      min(
          avg_score,
          100
      ) * 0.4

    + (1 - min(
          capacity_utilization,
          1
      )) * 30

    + (1 - top5_capacity_share) * 30
)



# =========================================================
# SUMMARY
# =========================================================

summary = pd.DataFrame({

    "Metric": [

        "Strategy_Capacity",

        "Median_Position_Capacity",

        "Average_Days_To_Exit",

        "Average_Capacity_Score",

        "Capacity_Utilization",

        "Capacity_Grade",

        "Capacity_Health",

        "Largest_Constraint",

        "Constraint_Capacity",

        "Top5_Capacity_Share",

        "Liquidity_Breaches",

        "Total_Positions",

        "Institutional_Positions",

        "Run_Date",

        "Engine_Version",
    ],

    "Value": [

        strategy_capacity,

        weighted_capacity,

        avg_days_exit,

        avg_score,

        capacity_utilization,

        capacity_grade,

        capacity_health,

        constraint_symbol,

        constraint_capacity,

        top5_capacity_share,

        breaches,

        len(portfolio),

        institutional_positions,

        datetime.now()
        .strftime(
            "%Y-%m-%d"
        ),

        ENGINE_VERSION,
    ]
})

# =========================================================
# SAVE
# =========================================================

portfolio.to_csv(

    OUTPUT_DIR
    / "capacity_master.csv",

    index=False,
)

summary.to_csv(

    OUTPUT_DIR
    / "capacity_summary.csv",

    index=False,
)

summary.to_csv(

    REPORT_FILE,

    index=False,
)

constraints.to_csv(
    OUTPUT_DIR
    / "capacity_constraints.csv",
    index=False
)

# =========================================================
# REPORT
# =========================================================

print("\n" + "=" * 70)

print(
    "🏁 CAPACITY ENGINE COMPLETE"
)

print("=" * 70)

print(
    f"Portfolio Positions    : "
    f"{len(portfolio):,}"
)

print()

print(
    f"Strategy Capacity      : "
    f"₹{strategy_capacity:,.0f}"
)

print(
    f"Capacity Utilization   : "
    f"{capacity_utilization:.2%}"
)

print(
    f"Capacity Grade         : "
    f"{capacity_grade}"
)

print()

print(
    f"Average Capacity Score : "
    f"{avg_score:.2f}"
)

print(
    f"Capacity Health        : "
    f"{capacity_health:.2f}"
)

print()

print(
    f"Largest Constraint     : "
    f"{constraint_symbol}"
)

print(
    f"Constraint Capacity    : "
    f"₹{constraint_capacity:,.0f}"
)

print()

print(
    f"Median Capacity        : "
    f"₹{weighted_capacity:,.0f}"
)

print(
    f"Average Days To Exit   : "
    f"{avg_days_exit:.2f}"
)

print(
    f"Top 5 Capacity Share   : "
    f"{top5_capacity_share:.2%}"
)

print(
    f"Institutional Positions : "
    f"{institutional_positions}"
)

print(
    f"Institutional Share     : "
    f"{institutional_share:.2%}"
)

print(
    f"Scalable Positions      : "
    f"{scalable_positions}"
)

print(
    f"Limited Positions       : "
    f"{limited_positions}"
)

print(
    f"Constrained Positions   : "
    f"{constrained_positions}"
)

print("\nCapacity Distribution")

print(
    capacity_distribution
)

print(
    f"Institutional+Scalable : "
    f"{institutional_scalable_share:.2%}"
)

print(
    f"Capacity Risk          : "
    f"{capacity_risk}"
)

print(
    f"Liquidity Breaches     : "
    f"{breaches:,}"
)

print(
    f"\nOutput Directory:\n"
    f"{OUTPUT_DIR}"
)

print("=" * 70)