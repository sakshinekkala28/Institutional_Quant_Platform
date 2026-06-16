"""
=========================================================
EXECUTION QUALITY ENGINE
=========================================================

Purpose:
Institutional Execution Analytics

Measures:

1. Implementation Shortfall
2. Slippage
3. Market Impact
4. Execution Quality
5. Alpha Leakage

=========================================================
"""

from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd

# =========================================================
# CONFIGURATION
# =========================================================

ENGINE_VERSION = "1.0.0"

MAX_ALLOWED_SLIPPAGE = 0.02

HIGH_IMPACT_THRESHOLD = 0.10

MIN_EXECUTION_VALUE = 1_000

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

EXECUTION_DIR = (
    ROOT
    / "data"
    / "execution"
)

RAW_DIR = (
    ROOT
    / "data"
    / "raw"
)

LOG_DIR = (
    ROOT
    / "data"
    / "logs"
)

OUTPUT_DIR = (
    ROOT
    / "data"
    / "execution"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

LOG_DIR.mkdir(
    parents=True,
    exist_ok=True
)

# =========================================================
# INPUT FILES
# =========================================================

ORDERS_FILE = (
    EXECUTION_DIR
    / "orders.csv"
)

BLOTTER_FILE = (
    EXECUTION_DIR
    / "trade_blotter.csv"
)

PRICE_FILE = (
    RAW_DIR
    / "security_price_history.parquet"
)

# =========================================================
# OUTPUT FILES
# =========================================================

QUALITY_REPORT_FILE = (
    OUTPUT_DIR
    / "execution_quality_report.csv"
)

SLIPPAGE_FILE = (
    OUTPUT_DIR
    / "slippage_report.csv"
)

SHORTFALL_FILE = (
    OUTPUT_DIR
    / "implementation_shortfall.csv"
)

DASHBOARD_FILE = (
    OUTPUT_DIR
    / "execution_dashboard.csv"
)

AUDIT_FILE = (
    LOG_DIR
    / "execution_quality_audit.csv"
)

# =========================================================
# LOAD INPUTS
# =========================================================

print(
    "\n📥 Loading Execution Inputs..."
)

required_files = [

    ORDERS_FILE,
    BLOTTER_FILE,
    PRICE_FILE,
]

for file in required_files:

    if not file.exists():

        raise FileNotFoundError(
            file
        )

orders = pd.read_csv(
    ORDERS_FILE
)

trade_blotter = pd.read_csv(
    BLOTTER_FILE
)

prices = pd.read_parquet(
    PRICE_FILE
)

# =========================================================
# VALIDATION
# =========================================================

print(
    "✔ Validating Inputs..."
)

if orders.empty:

    raise ValueError(
        "orders.csv is empty"
    )

if trade_blotter.empty:

    raise ValueError(
        "trade_blotter.csv is empty"
    )

if prices.empty:

    raise ValueError(
        "security_price_history.csv is empty"
    )

# =========================================================
# REQUIRED COLUMNS
# =========================================================

required_trade_cols = [

    "Symbol",
    "Action",
    "Shares",
]

for col in required_trade_cols:

    if col not in orders.columns:

        raise ValueError(
            f"Missing orders column: {col}"
        )

required_blotter_cols = [

    "Symbol",
    "Action",
    "Trade_Value",
]

for col in required_blotter_cols:

    if col not in trade_blotter.columns:

        raise ValueError(
            f"Missing blotter column: {col}"
        )

# =========================================================
# STANDARDIZE SYMBOLS
# =========================================================

def normalize_symbol(symbol):

    if pd.isna(symbol):
        return ""

    symbol = str(symbol).upper().strip()

    symbol = symbol.replace(".NS", "")
    symbol = symbol.replace(".BO", "")

    return symbol


orders["Symbol"] = (
    orders["Symbol"]
    .apply(normalize_symbol)
)

trade_blotter["Symbol"] = (
    trade_blotter["Symbol"]
    .apply(normalize_symbol)
)

if "Symbol" not in prices.columns:
    raise ValueError(
        "Symbol column missing from price history."
    )

prices["Symbol"] = (
    prices["Symbol"]
    .apply(normalize_symbol)
)

latest_prices = (
    prices
    .sort_values("Date")
    .groupby("Symbol", as_index=False)
    .tail(1)
)

print(
    f"Latest Price Symbols : "
    f"{latest_prices['Symbol'].nunique():,}"
)

# =========================================================
# BUILD PRICE SNAPSHOT
# =========================================================

print(
    "📈 Building Price Snapshot..."
)

if "Date" not in prices.columns:

    raise ValueError(
        "Date column missing from price history."
    )

prices["Date"] = pd.to_datetime(
    prices["Date"]
)

latest_prices = (

    prices

    .sort_values(
        "Date"
    )

    .groupby(
        "Symbol",
        as_index=False
    )

    .tail(1)
)

close_column = None

for col in [

    "Close",
    "Adj_Close",
    "Adj Close",
]:

    if col in latest_prices.columns:

        close_column = col
        break

if close_column is None:

    raise ValueError(
        "No close price column found."
    )

latest_prices = latest_prices[
    [
        "Symbol",
        close_column
    ]
].copy()

latest_prices.columns = [

    "Symbol",
    "Arrival_Price"
]

# =========================================================
# MERGE EXECUTION DATA
# =========================================================

execution_data = trade_blotter.merge(

    latest_prices,

    on="Symbol",

    how="left"
)

matched = execution_data["Arrival_Price"].notna().sum()

print(
    f"Matched Prices : {matched:,}"
)

print(
    f"Missing Prices : "
    f"{len(execution_data) - matched:,}"
)

execution_data["Arrival_Price"] = (

    execution_data[
        "Arrival_Price"
    ].fillna(0)
)

# =========================================================
# INITIAL DIAGNOSTICS
# =========================================================

print(
    f"Orders Loaded : "
    f"{len(orders):,}"
)

print(
    f"Trades Loaded : "
    f"{len(trade_blotter):,}"
)

print(
    f"Securities    : "
    f"{execution_data['Symbol'].nunique():,}"
)

missing_prices = int(

    (
        execution_data[
            "Arrival_Price"
        ] == 0
    ).sum()
)

print(
    f"Missing Prices: "
    f"{missing_prices:,}"
)

# =========================================================
# AUDIT CONTAINER
# =========================================================

audit_metrics = {}

audit_metrics[
    "Orders"
] = len(
    orders
)

audit_metrics[
    "Trades"
] = len(
    trade_blotter
)

audit_metrics[
    "Missing_Prices"
] = missing_prices

audit_metrics[
    "Run_Date"
] = datetime.now().strftime(
    "%Y-%m-%d"
)

audit_metrics[
    "Engine_Version"
] = ENGINE_VERSION

# =========================================================
# PART 2 STARTS HERE
# =========================================================

#
# Implementation Shortfall
# Slippage Analytics
# Market Impact
#
# =========================================================

# =========================================================
# EXECUTION PRICE ESTIMATION
# =========================================================

print(
    "\n🏗 Building Execution Analytics..."
)

# =========================================================
# ESTIMATED EXECUTION PRICE
# =========================================================

#
# Until actual fills are available,
# use arrival price as baseline.
#


# TODO:
# Replace with broker fill prices
# when OMS/EMS integration is available.

execution_data["Execution_Price"] = (

    execution_data[
        "Arrival_Price"
    ]
)

# =========================================================
# SHARES
# =========================================================

if "Shares" not in execution_data.columns:

    execution_data = execution_data.merge(

        orders[
            [
                "Symbol",
                "Shares"
            ]
        ],

        on="Symbol",

        how="left"
    )

execution_data["Shares"] = (

    execution_data[
        "Shares"
    ]
    .fillna(0)
)

# =========================================================
# EXECUTION VALUE
# =========================================================

execution_data["Execution_Value"] = (

    execution_data[
        "Execution_Price"
    ]

    *

    execution_data[
        "Shares"
    ]
)

# =========================================================
# IMPLEMENTATION SHORTFALL
# =========================================================

print(
    "📉 Building Implementation Shortfall..."
)

execution_data["Implementation_Shortfall"] = (

    (
        execution_data[
            "Execution_Price"
        ]

        -

        execution_data[
            "Arrival_Price"
        ]
    )

    *

    execution_data[
        "Shares"
    ]
)

total_shortfall = (

    execution_data[
        "Implementation_Shortfall"
    ]
    .sum()
)

# =========================================================
# BPS SHORTFALL
# =========================================================

execution_data["Shortfall_Bps"] = np.where(

    execution_data[
        "Execution_Value"
    ] > 0,

    (
        execution_data[
            "Implementation_Shortfall"
        ]

        /

        execution_data[
            "Execution_Value"
        ]
    )

    * 10000,

    0
)

# =========================================================
# SLIPPAGE
# =========================================================

print(
    "📈 Building Slippage Analytics..."
)

execution_data["Slippage"] = (

    execution_data[
        "Execution_Price"
    ]

    -

    execution_data[
        "Arrival_Price"
    ]
)

execution_data["Slippage_Pct"] = np.where(

    execution_data[
        "Arrival_Price"
    ] > 0,

    execution_data[
        "Slippage"
    ]

    /

    execution_data[
        "Arrival_Price"
    ],

    0
)

average_slippage = (

    execution_data[
        "Slippage_Pct"
    ]
    .mean()
)

median_slippage = (

    execution_data[
        "Slippage_Pct"
    ]
    .median()
)

# =========================================================
# SLIPPAGE FLAG
# =========================================================

execution_data["Slippage_Flag"] = np.where(

    execution_data[
        "Slippage_Pct"
    ].abs()

    >

    MAX_ALLOWED_SLIPPAGE,

    "BREACH",

    "OK"
)

slippage_breaches = int(

    (
        execution_data[
            "Slippage_Flag"
        ]
        ==
        "BREACH"
    ).sum()
)

# =========================================================
# MARKET IMPACT
# =========================================================

print(
    "🏛 Building Market Impact..."
)

if "ADV_Pct" not in execution_data.columns:

    execution_data["ADV_Pct"] = 0

execution_data["Impact_Level"] = np.select(

    [

        execution_data[
            "ADV_Pct"
        ] < 0.02,

        execution_data[
            "ADV_Pct"
        ] < 0.05,

        execution_data[
            "ADV_Pct"
        ] < 0.10,
    ],

    [

        "LOW",

        "MEDIUM",

        "HIGH",
    ],

    default="EXTREME"
)

impact_distribution = (

    execution_data[
        "Impact_Level"
    ]
    .value_counts()
)

# =========================================================
# EXECUTION COST
# =========================================================

print(
    "💰 Building Execution Cost Analytics..."
)

execution_data["Estimated_Cost"] = (

    execution_data[
        "Execution_Value"
    ]
    .abs()

    * 0.0005
)

total_execution_cost = (

    execution_data[
        "Estimated_Cost"
    ]
    .sum()
)

# =========================================================
# QUALITY SCORE
# =========================================================

execution_quality_score = 100.0

execution_quality_score -= (

    slippage_breaches
    * 2
)

execution_quality_score -= min(

    total_execution_cost

    /

    max(
        execution_data[
            "Execution_Value"
        ]
        .abs()
        .sum(),

        1
    )

    * 100,

    20
)

execution_quality_score = max(

    execution_quality_score,

    0
)

# =========================================================
# DIAGNOSTICS
# =========================================================

print(
    f"Total Shortfall : "
    f"{total_shortfall:,.0f}"
)

print(
    f"Average Slippage : "
    f"{average_slippage:.4%}"
)

print(
    f"Median Slippage  : "
    f"{median_slippage:.4%}"
)

print(
    f"Cost Estimate    : "
    f"{total_execution_cost:,.0f}"
)

print(
    f"Slippage Breaches: "
    f"{slippage_breaches:,}"
)

print(
    f"Quality Score    : "
    f"{execution_quality_score:.2f}"
)

# =========================================================
# AUDIT METRICS
# =========================================================

audit_metrics[
    "Implementation_Shortfall"
] = total_shortfall

audit_metrics[
    "Average_Slippage"
] = average_slippage

audit_metrics[
    "Median_Slippage"
] = median_slippage

audit_metrics[
    "Execution_Cost"
] = total_execution_cost

audit_metrics[
    "Slippage_Breaches"
] = slippage_breaches

audit_metrics[
    "Execution_Quality_Score"
] = execution_quality_score

gross_execution_value = (
    execution_data["Execution_Value"]
    .abs()
    .sum()
)

portfolio_turnover = (
    gross_execution_value
    / 100_000_000
)

audit_metrics[
    "Gross_Execution_Value"
] = gross_execution_value

audit_metrics[
    "Portfolio_Turnover"
] = portfolio_turnover

# =========================================================
# PART 3 STARTS HERE
# =========================================================

#
# Execution Dashboard
# Reports
# Summary Statistics
# Export Layer
#
# =========================================================

# =========================================================
# SLIPPAGE REPORT
# =========================================================

print(
    "\n📊 Building Execution Reports..."
)

slippage_report = execution_data[

    [

        "Symbol",

        "Action",

        "Shares",

        "Arrival_Price",

        "Execution_Price",

        "Slippage",

        "Slippage_Pct",

        "Slippage_Flag",
    ]

].copy()

slippage_report = slippage_report.sort_values(

    "Slippage_Pct",

    ascending=False,
)

# =========================================================
# IMPLEMENTATION SHORTFALL REPORT
# =========================================================

shortfall_report = execution_data[

    [

        "Symbol",

        "Action",

        "Shares",

        "Execution_Value",

        "Implementation_Shortfall",

        "Shortfall_Bps",
    ]

].copy()

shortfall_report = shortfall_report.sort_values(

    "Implementation_Shortfall",

    ascending=False,
)

# =========================================================
# MARKET IMPACT REPORT
# =========================================================

impact_report = execution_data[

    [

        "Symbol",

        "Action",

        "Shares",

        "ADV_Pct",

        "Impact_Level",
    ]

].copy()

# =========================================================
# EXECUTION DASHBOARD
# =========================================================

execution_dashboard = pd.DataFrame({

    "Metric": [

        "Trades",

        "Total_Execution_Value",

        "Implementation_Shortfall",

        "Average_Slippage",

        "Median_Slippage",

        "Execution_Cost",

        "Slippage_Breaches",

        "Execution_Quality_Score",
    ],

    "Value": [

        len(
            execution_data
        ),

        execution_data[
            "Execution_Value"
        ].abs().sum(),

        total_shortfall,

        average_slippage,

        median_slippage,

        total_execution_cost,

        slippage_breaches,

        execution_quality_score,
    ]
})

# =========================================================
# IMPACT SUMMARY
# =========================================================

impact_summary = pd.DataFrame({

    "Impact_Level":
    impact_distribution.index,

    "Count":
    impact_distribution.values
})

IMPACT_SUMMARY_FILE = (
    OUTPUT_DIR
    / "impact_summary.csv"
)

impact_summary.to_csv(
    IMPACT_SUMMARY_FILE,
    index=False
)

# =========================================================
# EXECUTION SUMMARY
# =========================================================

execution_summary = pd.DataFrame({

    "Metric": [

        "Total_Trades",

        "Unique_Securities",

        "Execution_Value",

        "Implementation_Shortfall",

        "Execution_Cost",

        "Average_Slippage",

        "Quality_Score",

        "Run_Date",

        "Engine_Version",
    ],

    "Value": [

        len(
            execution_data
        ),

        execution_data[
            "Symbol"
        ].nunique(),

        execution_data[
            "Execution_Value"
        ].abs().sum(),

        total_shortfall,

        total_execution_cost,

        average_slippage,

        execution_quality_score,

        datetime.now().strftime(
            "%Y-%m-%d"
        ),

        ENGINE_VERSION,
    ]
})

# =========================================================
# OUTPUT FILES
# =========================================================

IMPACT_FILE = (

    OUTPUT_DIR
    / "market_impact_report.csv"
)

SUMMARY_FILE = (

    OUTPUT_DIR
    / "execution_summary.csv"
)

# =========================================================
# SAVE OUTPUTS
# =========================================================

print(
    "💾 Saving Outputs..."
)

slippage_report.to_csv(

    SLIPPAGE_FILE,

    index=False
)

shortfall_report.to_csv(

    SHORTFALL_FILE,

    index=False
)

impact_report.to_csv(

    IMPACT_FILE,

    index=False
)

execution_dashboard.to_csv(

    DASHBOARD_FILE,

    index=False
)

execution_summary.to_csv(

    SUMMARY_FILE,

    index=False
)

# =========================================================
# AUDIT REPORT
# =========================================================

audit_report = pd.DataFrame({

    "Metric":
    list(
        audit_metrics.keys()
    ),

    "Value":
    list(
        audit_metrics.values()
    )
})

audit_report.to_csv(

    AUDIT_FILE,

    index=False
)

# =========================================================
# VALIDATION
# =========================================================

print(
    "✔ Running Validation..."
)

required_outputs = [

    SLIPPAGE_FILE,

    SHORTFALL_FILE,

    IMPACT_FILE,

    IMPACT_SUMMARY_FILE,

    DASHBOARD_FILE,

    SUMMARY_FILE,

    AUDIT_FILE,
]

for file in required_outputs:

    if not file.exists():

        raise FileNotFoundError(
            file
        )

# =========================================================
# PART 4 STARTS HERE
# =========================================================

#
# Governance
# Execution Grading
# Exception Management
# Final Reporting
#
# =========================================================

# =========================================================
# EXECUTION EXCEPTIONS
# =========================================================

print(
    "\n🛡 Building Governance Controls..."
)

exceptions = []

if slippage_breaches > 0:

    exceptions.append(
        f"{slippage_breaches} slippage breaches detected"
    )

high_impact_count = int(

    (
        execution_data[
            "Impact_Level"
        ]
        == "EXTREME"
    ).sum()
)

if high_impact_count > 0:

    exceptions.append(
        f"{high_impact_count} extreme impact trades"
    )

if execution_quality_score < 70:

    exceptions.append(
        "Execution quality below threshold"
    )

if total_execution_cost > (
    execution_data[
        "Execution_Value"
    ].abs().sum()
    * 0.01
):

    exceptions.append(
        "Execution costs exceed 1% of traded value"
    )

has_exception = len(exceptions) > 0

if not has_exception:
    exceptions = [
        "No execution exceptions detected"
    ]

print(
    f"Exceptions             : "
    f"{0 if not has_exception else len(exceptions):,}"
)

# =========================================================
# EXECUTION GRADE
# =========================================================

if execution_quality_score >= 95:

    execution_grade = "A"

elif execution_quality_score >= 85:

    execution_grade = "B"

elif execution_quality_score >= 75:

    execution_grade = "C"

elif execution_quality_score >= 65:

    execution_grade = "D"

else:

    execution_grade = "F"

# =========================================================
# EXECUTION READINESS
# =========================================================

execution_ready = (

    execution_quality_score >= 75

    and

    high_impact_count == 0
)

# =========================================================
# EXCEPTION REPORT
# =========================================================

exception_report = pd.DataFrame({

    "Exception":
    exceptions
})

EXCEPTION_FILE = (

    OUTPUT_DIR
    / "execution_exceptions.csv"
)

exception_report.to_csv(

    EXCEPTION_FILE,

    index=False
)

# =========================================================
# GOVERNANCE REPORT
# =========================================================

governance_report = pd.DataFrame({

    "Metric": [

        "Execution_Quality_Score",

        "Execution_Grade",

        "Execution_Ready",

        "Slippage_Breaches",

        "Extreme_Impact_Trades",

        "Implementation_Shortfall",

        "Execution_Cost",

        "Run_Date",

        "Engine_Version",
    ],

    "Value": [

        execution_quality_score,

        execution_grade,

        execution_ready,

        slippage_breaches,

        high_impact_count,

        total_shortfall,

        total_execution_cost,

        datetime.now().strftime(
            "%Y-%m-%d"
        ),

        ENGINE_VERSION,
    ]
})

GOVERNANCE_FILE = (

    OUTPUT_DIR
    / "execution_governance_report.csv"
)

governance_report.to_csv(

    GOVERNANCE_FILE,

    index=False
)

# =========================================================
# UPDATE AUDIT
# =========================================================

audit_metrics[
    "Execution_Grade"
] = execution_grade

audit_metrics[
    "Execution_Ready"
] = execution_ready

audit_metrics[
    "Extreme_Impact_Trades"
] = high_impact_count

# overwrite final audit with governance metrics
pd.DataFrame({

    "Metric":
    list(
        audit_metrics.keys()
    ),

    "Value":
    list(
        audit_metrics.values()
    )

}).to_csv(

    AUDIT_FILE,

    index=False
)

# =========================================================
# FINAL VALIDATION
# =========================================================

print(
    "✔ Running Governance Validation..."
)

governance_files = [

    EXCEPTION_FILE,

    GOVERNANCE_FILE,
]

for file in governance_files:

    if not file.exists():

        raise FileNotFoundError(
            file
        )

# =========================================================
# COMPLETION REPORT
# =========================================================

print("\n" + "=" * 60)

print(
    "🏁 EXECUTION QUALITY ENGINE COMPLETE"
)

print("=" * 60)

print(
    f"Trades                 : "
    f"{len(execution_data):,}"
)

print(
    f"Gross Execution Value  : "
    f"{gross_execution_value:,.0f}"
)

print(
    f"Implementation Shortfall: "
    f"{total_shortfall:,.0f}"
)

print(
    f"Execution Cost         : "
    f"{total_execution_cost:,.0f}"
)

print(
    f"Average Slippage       : "
    f"{average_slippage:.4%}"
)

print(
    f"Quality Score          : "
    f"{execution_quality_score:.2f}"
)

print(
    f"Execution Grade        : "
    f"{execution_grade}"
)

print(
    f"Execution Ready        : "
    f"{execution_ready}"
)

print(
    f"Exceptions             : "
    f"{len(exception_report):,}"
)

print("\nOutput Directory:")

print(
    OUTPUT_DIR
)

print("=" * 60)