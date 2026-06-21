"""
=========================================================
BRINSON ATTRIBUTION ENGINE
=========================================================

Purpose:
Institutional Brinson-Fachler Performance Attribution

Methodology:
Allocation Effect
Selection Effect
Interaction Effect

Inputs:
data/portfolios/live_portfolio.csv
data/benchmark/benchmark_constituents.csv
data/raw/prices/*.parquet

Outputs:
data/performance/*.csv

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

RETURN_LOOKBACK_DAYS = 252

MIN_SECURITIES = 20

MIN_SECTOR_COVERAGE = 0.90

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

BENCHMARK_FILE = (
    ROOT
    / "data"
    / "benchmark"
    / "benchmark_constituents.csv"
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
    / "performance"
)

REPORT_FILE = (
    ROOT
    / "data"
    / "logs"
    / "brinson_report.csv"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

for file in [
    PORTFOLIO_FILE,
    BENCHMARK_FILE,
]:
    if not file.exists():
        raise FileNotFoundError(file)
    
# =========================================================
# LOAD DATA
# =========================================================

print(
    "\n📥 Loading Inputs..."
)

portfolio = pd.read_csv(
    PORTFOLIO_FILE
)

benchmark = pd.read_csv(
    BENCHMARK_FILE
)

# =========================================================
# VALIDATION
# =========================================================

if portfolio.empty:

    raise ValueError(
        "Portfolio file empty"
    )

if benchmark.empty:

    raise ValueError(
        "Benchmark file empty"
    )

required_portfolio = [

    "Symbol",
    "Weight",
    "Sector",
]

required_benchmark = [

    "Symbol",
    "Weight",
    "Sector",
]

for col in required_portfolio:

    if col not in portfolio.columns:

        raise ValueError(
            f"Portfolio Missing: {col}"
        )

for col in required_benchmark:

    if col not in benchmark.columns:

        raise ValueError(
            f"Benchmark Missing: {col}"
        )

if len(portfolio) < MIN_SECURITIES:

    raise ValueError(
        "Portfolio size too small"
    )

# =========================================================
# CLEAN WEIGHTS
# =========================================================

portfolio["Weight"] = pd.to_numeric(

    portfolio["Weight"],

    errors="coerce"
)

benchmark["Weight"] = pd.to_numeric(

    benchmark["Weight"],

    errors="coerce"
)

portfolio = portfolio.dropna(
    subset=["Weight"]
)

benchmark = benchmark.dropna(
    subset=["Weight"]
)

portfolio["Weight"] = (

    portfolio["Weight"]

    / portfolio["Weight"].sum()
)

benchmark["Weight"] = (

    benchmark["Weight"]

    / benchmark["Weight"].sum()
)

# =========================================================
# RETURN CONSTRUCTION
# =========================================================

print(
    "\n📊 Building Security Returns..."
)

# Dictionary:
# Symbol -> Return

security_returns = {}

# Diagnostics

processed = 0
missing_files = 0
insufficient_history = 0

symbols = sorted(

    set(
        portfolio["Symbol"]
    )

    |

    set(
        benchmark["Symbol"]
    )
)

for symbol in symbols:

    file = (
        PRICE_DIR
        / f"{symbol}.parquet"
    )

    if not file.exists():

        missing_files += 1
        continue

    try:

        df = pd.read_parquet(
            file,
            columns=[
                "Date",
                "Close",
            ]
        )

        if len(df) < RETURN_LOOKBACK_DAYS:

            insufficient_history += 1
            continue

        close = pd.to_numeric(

            df["Close"],

            errors="coerce"
        )

        close = close.dropna()

        if len(close) < RETURN_LOOKBACK_DAYS:

            insufficient_history += 1
            continue

        start_price = (
            close.iloc[
                -RETURN_LOOKBACK_DAYS
            ]
        )

        end_price = (
            close.iloc[-1]
        )

        total_return = (

            end_price
            / start_price

            - 1
        )

        security_returns[
            symbol
        ] = total_return

        processed += 1

    except Exception:

        continue

# =========================================================
# RETURN DATAFRAME
# =========================================================

returns_df = pd.DataFrame({

    "Symbol":
    list(
        security_returns.keys()
    ),

    "Security_Return":
    list(
        security_returns.values()
    )
})

if returns_df.empty:

    raise ValueError(
        "No security returns built"
    )

# =========================================================
# MERGE RETURNS
# =========================================================

portfolio = portfolio.merge(

    returns_df,

    on="Symbol",

    how="left"
)

benchmark = benchmark.merge(

    returns_df,

    on="Symbol",

    how="left"
)

# =========================================================
# COVERAGE CHECK
# =========================================================

portfolio_coverage = (

    portfolio[
        "Security_Return"
    ]

    .notna()

    .mean()
)

benchmark_coverage = (

    benchmark[
        "Security_Return"
    ]

    .notna()

    .mean()
)

print(
    f"Portfolio Coverage : "
    f"{portfolio_coverage:.2%}"
)

print(
    f"Benchmark Coverage : "
    f"{benchmark_coverage:.2%}"
)

if (

    portfolio_coverage
    <
    MIN_SECTOR_COVERAGE
):

    raise ValueError(

        "Portfolio return coverage "
        f"too low: "
        f"{portfolio_coverage:.2%}"
    )

if (

    benchmark_coverage
    <
    MIN_SECTOR_COVERAGE
):

    raise ValueError(

        "Benchmark return coverage "
        f"too low: "
        f"{benchmark_coverage:.2%}"
    )

portfolio = portfolio.dropna(
    subset=[
        "Security_Return"
    ]
)

benchmark = benchmark.dropna(
    subset=[
        "Security_Return"
    ]
)

# =========================================================
# PORTFOLIO RETURN
# =========================================================

portfolio_return = (

    portfolio["Weight"]

    * portfolio[
        "Security_Return"
    ]

).sum()

benchmark_return = (

    benchmark["Weight"]

    * benchmark[
        "Security_Return"
    ]

).sum()

active_return = (

    portfolio_return

    - benchmark_return
)

# =========================================================
# DIAGNOSTICS
# =========================================================

print(
    f"\nPortfolio Return : "
    f"{portfolio_return:.2%}"
)

print(
    f"Benchmark Return : "
    f"{benchmark_return:.2%}"
)

print(
    f"Active Return    : "
    f"{active_return:.2%}"
)

print(
    f"\nReturns Built    : "
    f"{processed}"
)

print(
    f"Missing Files    : "
    f"{missing_files}"
)

print(
    f"Insufficient Hist: "
    f"{insufficient_history}"
)

# =========================================================
# PART 2 STARTS HERE
# =========================================================
#
# Next:
#
# Sector Aggregation
# Portfolio Sector Returns
# Benchmark Sector Returns
# Active Weights
# Active Returns
#
# =========================================================

# =========================================================
# SECTOR AGGREGATION
# =========================================================

print(
    "\n🏭 Building Sector Aggregation..."
)

# =========================================================
# PORTFOLIO SECTOR METRICS
# =========================================================

portfolio_sector = (

    portfolio

    .groupby(
        "Sector",
        as_index=False
    )

    .apply(

        lambda x: pd.Series({

            "Portfolio_Weight":

                x[
                    "Weight"
                ].sum(),

            "Portfolio_Return":

                np.average(

                    x[
                        "Security_Return"
                    ],

                    weights=
                    x[
                        "Weight"
                    ]
                ),

            "Portfolio_Securities":

                len(x),
        })

    )

    .reset_index(
        drop=True
    )
)

# =========================================================
# BENCHMARK SECTOR METRICS
# =========================================================

benchmark_sector = (

    benchmark

    .groupby(
        "Sector",
        as_index=False
    )

    .apply(

        lambda x: pd.Series({

            "Benchmark_Weight":

                x[
                    "Weight"
                ].sum(),

            "Benchmark_Return":

                np.average(

                    x[
                        "Security_Return"
                    ],

                    weights=
                    x[
                        "Weight"
                    ]
                ),

            "Benchmark_Securities":

                len(x),
        })

    )

    .reset_index(
        drop=True
    )
)

# =========================================================
# MERGE SECTOR TABLES
# =========================================================

sector_table = (

    portfolio_sector

    .merge(

        benchmark_sector,

        on="Sector",

        how="outer"
    )

)

sector_table = (
    sector_table.fillna(0)
)

# =========================================================
# ACTIVE WEIGHTS
# =========================================================

sector_table[
    "Active_Weight"
] = (

    sector_table[
        "Portfolio_Weight"
    ]

    -

    sector_table[
        "Benchmark_Weight"
    ]
)

# =========================================================
# ACTIVE RETURNS
# =========================================================

sector_table[
    "Active_Return"
] = (

    sector_table[
        "Portfolio_Return"
    ]

    -

    sector_table[
        "Benchmark_Return"
    ]
)

# =========================================================
# CONTRIBUTIONS
# =========================================================

sector_table[
    "Portfolio_Contribution"
] = (

    sector_table[
        "Portfolio_Weight"
    ]

    *

    sector_table[
        "Portfolio_Return"
    ]
)

sector_table[
    "Benchmark_Contribution"
] = (

    sector_table[
        "Benchmark_Weight"
    ]

    *

    sector_table[
        "Benchmark_Return"
    ]
)

sector_table[
    "Contribution_Difference"
] = (

    sector_table[
        "Portfolio_Contribution"
    ]

    -

    sector_table[
        "Benchmark_Contribution"
    ]
)

# =========================================================
# SECTOR RANKING
# =========================================================

sector_table = (

    sector_table

    .sort_values(

        "Contribution_Difference",

        ascending=False,
    )

    .reset_index(
        drop=True
    )
)

sector_table[
    "Sector_Rank"
] = (
    sector_table.index + 1
)

# =========================================================
# DIAGNOSTICS
# =========================================================

portfolio_sector_weight = (

    sector_table[
        "Portfolio_Weight"
    ].sum()
)

benchmark_sector_weight = (

    sector_table[
        "Benchmark_Weight"
    ].sum()
)

if not np.isclose(
    portfolio_sector_weight,
    1.0,
    atol=0.01
):

    raise ValueError(
        "Portfolio sector weights "
        "do not sum to 100%"
    )

if not np.isclose(
    benchmark_sector_weight,
    1.0,
    atol=0.01
):

    raise ValueError(
        "Benchmark sector weights "
        "do not sum to 100%"
    )

# =========================================================
# TOP / BOTTOM SECTORS
# =========================================================

best_sector = (
    sector_table.iloc[0]
)

worst_sector = (
    sector_table.iloc[-1]
)

print(
    f"\nTop Sector    : "
    f"{best_sector['Sector']}"
)

print(
    f"Contribution  : "
    f"{best_sector['Contribution_Difference']:.2%}"
)

print(
    f"\nWorst Sector  : "
    f"{worst_sector['Sector']}"
)

print(
    f"Contribution  : "
    f"{worst_sector['Contribution_Difference']:.2%}"
)

# =========================================================
# ATTRIBUTION BASE TABLE
# =========================================================

attribution_base = sector_table[[

    "Sector",

    "Portfolio_Weight",
    "Benchmark_Weight",

    "Active_Weight",

    "Portfolio_Return",
    "Benchmark_Return",

    "Active_Return",

    "Portfolio_Contribution",
    "Benchmark_Contribution",

    "Contribution_Difference",

    "Portfolio_Securities",
    "Benchmark_Securities",

    "Sector_Rank",
]].copy()

# =========================================================
# PART 3 STARTS HERE
# =========================================================
#
# Next:
#
# Brinson-Fachler Attribution
# Allocation Effect
# Selection Effect
# Interaction Effect
# Active Return Reconciliation
#
# =========================================================

# =========================================================
# BRINSON-FACHLER ATTRIBUTION
# =========================================================

print(
    "\n📊 Running Brinson Attribution..."
)

# =========================================================
# BENCHMARK TOTAL RETURN
# =========================================================

benchmark_total_return = (
    benchmark_return
)

# =========================================================
# ALLOCATION EFFECT
# =========================================================

attribution_base[
    "Allocation_Effect"
] = (

    (

        attribution_base[
            "Portfolio_Weight"
        ]

        -

        attribution_base[
            "Benchmark_Weight"
        ]

    )

    *

    (

        attribution_base[
            "Benchmark_Return"
        ]

        -

        benchmark_total_return

    )
)

# =========================================================
# SELECTION EFFECT
# =========================================================

attribution_base[
    "Selection_Effect"
] = (

    attribution_base[
        "Benchmark_Weight"
    ]

    *

    (

        attribution_base[
            "Portfolio_Return"
        ]

        -

        attribution_base[
            "Benchmark_Return"
        ]

    )
)

# =========================================================
# INTERACTION EFFECT
# =========================================================

attribution_base[
    "Interaction_Effect"
] = (

    (

        attribution_base[
            "Portfolio_Weight"
        ]

        -

        attribution_base[
            "Benchmark_Weight"
        ]

    )

    *

    (

        attribution_base[
            "Portfolio_Return"
        ]

        -

        attribution_base[
            "Benchmark_Return"
        ]

    )
)

# =========================================================
# TOTAL EFFECT
# =========================================================

attribution_base[
    "Total_Effect"
] = (

    attribution_base[
        "Allocation_Effect"
    ]

    +

    attribution_base[
        "Selection_Effect"
    ]

    +

    attribution_base[
        "Interaction_Effect"
    ]
)

# =========================================================
# CONTRIBUTION %
# =========================================================

total_abs = max(

    attribution_base[
        "Total_Effect"
    ]
    .abs()
    .sum(),

    1e-9
)

attribution_base[
    "Contribution_Pct"
] = (

    attribution_base[
        "Total_Effect"
    ]
    .abs()

    / total_abs

    * 100
)

# =========================================================
# RECONCILIATION
# =========================================================

allocation_total = (

    attribution_base[
        "Allocation_Effect"
    ]
    .sum()
)

selection_total = (

    attribution_base[
        "Selection_Effect"
    ]
    .sum()
)

interaction_total = (

    attribution_base[
        "Interaction_Effect"
    ]
    .sum()
)

total_attribution = (

    allocation_total

    +

    selection_total

    +

    interaction_total
)

allocation_share = (

    allocation_total

    / max(
        abs(active_return),
        1e-9
    )
)

selection_share = (

    selection_total

    / max(
        abs(active_return),
        1e-9
    )
)

interaction_share = (

    interaction_total

    / max(
        abs(active_return),
        1e-9
    )
)

print(
    f"Allocation Share : "
    f"{allocation_share:.2%}"
)

print(
    f"Selection Share  : "
    f"{selection_share:.2%}"
)

print(
    f"Interaction Share: "
    f"{interaction_share:.2%}"
)

residual = (

    active_return

    -

    total_attribution
)

quality_score = max(

    0,

    100
    -
    abs(residual) * 10000
)

print(
    f"Quality Score   : "
    f"{quality_score:.2f}"
)

# =========================================================
# RECONCILIATION CHECK
# =========================================================

reconciliation_error = abs(
    residual
)

if reconciliation_error > 0.01:

    print(
        "\n⚠ WARNING:"
        " Attribution residual "
        f"{residual:.4%}"
    )

# =========================================================
# RANKINGS
# =========================================================

attribution_base = (

    attribution_base

    .sort_values(

        "Total_Effect",

        ascending=False,
    )

    .reset_index(
        drop=True
    )
)

attribution_base[
    "Attribution_Rank"
] = (
    attribution_base.index + 1
)

# =========================================================
# TOP POSITIVE
# =========================================================

top_positive = (
    attribution_base.iloc[0]
)

# =========================================================
# TOP NEGATIVE
# =========================================================

top_negative = (
    attribution_base.iloc[-1]
)

# =========================================================
# EFFECT TABLES
# =========================================================

allocation_effect = attribution_base[[

    "Sector",

    "Portfolio_Weight",
    "Benchmark_Weight",

    "Allocation_Effect",

    "Attribution_Rank",
]].copy()

selection_effect = attribution_base[[

    "Sector",

    "Portfolio_Return",
    "Benchmark_Return",

    "Selection_Effect",

    "Attribution_Rank",
]].copy()

interaction_effect = attribution_base[[

    "Sector",

    "Active_Weight",
    "Active_Return",

    "Interaction_Effect",

    "Attribution_Rank",
]].copy()

# =========================================================
# SUMMARY
# =========================================================

summary = pd.DataFrame({

    "Metric": [

        "Portfolio_Return",

        "Benchmark_Return",

        "Active_Return",

        "Allocation_Share",

        "Selection_Share",
        
        "Interaction_Share",

        "Allocation_Total",

        "Selection_Total",

        "Interaction_Total",

        "Total_Attribution",

        "Quality_Score",

        "Coverage_Portfolio",

        "Coverage_Benchmark",

        "Residual",

        "Top_Positive_Sector",

        "Top_Negative_Sector",

        "Run_Date",

        "Engine_Version",
    ],

    "Value": [

        portfolio_return,

        benchmark_return,

        active_return,

        allocation_total,

        selection_total,

        interaction_total,

        total_attribution,

        quality_score,

        portfolio_coverage,

        benchmark_coverage,

        residual,

        top_positive[
            "Sector"
        ],

        top_negative[
            "Sector"
        ],

        datetime.now()
        .strftime(
            "%Y-%m-%d"
        ),

        ENGINE_VERSION,
    ]
})

# =========================================================
# DIAGNOSTICS
# =========================================================

print(
    f"\nPortfolio Return : "
    f"{portfolio_return:.2%}"
)

print(
    f"Benchmark Return : "
    f"{benchmark_return:.2%}"
)

print(
    f"Active Return    : "
    f"{active_return:.2%}"
)

print(
    f"\nAllocation       : "
    f"{allocation_total:.2%}"
)

print(
    f"Selection        : "
    f"{selection_total:.2%}"
)

print(
    f"Interaction      : "
    f"{interaction_total:.2%}"
)

print(
    f"Residual         : "
    f"{residual:.4%}"
)

print(
    f"\nTop Positive     : "
    f"{top_positive['Sector']}"
)

print(
    f"Effect           : "
    f"{top_positive['Total_Effect']:.2%}"
)

print(
    f"\nTop Negative     : "
    f"{top_negative['Sector']}"
)

print(
    f"Effect           : "
    f"{top_negative['Total_Effect']:.2%}"
)

# =========================================================
# PART 4 STARTS HERE
# =========================================================
#
# Next:
#
# Save Outputs
# Attribution Rankings
# Reports
# Institutional Logging
# Final Dashboard
#
# =========================================================

# =========================================================
# ATTRIBUTION DASHBOARD
# =========================================================

dashboard = attribution_base[[

    "Attribution_Rank",

    "Sector",

    "Portfolio_Weight",
    "Benchmark_Weight",

    "Active_Weight",

    "Portfolio_Return",
    "Benchmark_Return",

    "Active_Return",

    "Allocation_Effect",
    "Selection_Effect",
    "Interaction_Effect",

    "Total_Effect",

    "Contribution_Pct",
]].copy()

# =========================================================
# POSITIVE CONTRIBUTORS
# =========================================================

positive_contributors = (

    attribution_base[

        attribution_base[
            "Total_Effect"
        ] > 0

    ]

    .copy()

    .sort_values(
        "Total_Effect",
        ascending=False,
    )
)

# =========================================================
# NEGATIVE CONTRIBUTORS
# =========================================================

negative_contributors = (

    attribution_base[

        attribution_base[
            "Total_Effect"
        ] < 0

    ]

    .copy()

    .sort_values(
        "Total_Effect",
        ascending=True,
    )
)

# =========================================================
# ATTRIBUTION STATISTICS
# =========================================================

positive_effect = (

    attribution_base[
        attribution_base[
            "Total_Effect"
        ] > 0
    ]

    [
        "Total_Effect"
    ]

    .sum()
)

negative_effect = (

    attribution_base[
        attribution_base[
            "Total_Effect"
        ] < 0
    ]

    [
        "Total_Effect"
    ]

    .sum()
)

winning_sectors = (

    attribution_base[
        "Total_Effect"
    ] > 0

).sum()

losing_sectors = (

    attribution_base[
        "Total_Effect"
    ] < 0

).sum()

# =========================================================
# RECONCILIATION REPORT
# =========================================================

reconciliation = pd.DataFrame({

    "Metric": [

        "Portfolio_Return",

        "Benchmark_Return",

        "Active_Return",

        "Allocation_Effect",

        "Selection_Effect",

        "Interaction_Effect",

        "Total_Attribution",

        "Residual",
    ],

    "Value": [

        portfolio_return,

        benchmark_return,

        active_return,

        allocation_total,

        selection_total,

        interaction_total,

        total_attribution,

        residual,
    ]
})

# =========================================================
# EXECUTIVE SUMMARY
# =========================================================

executive_summary = pd.DataFrame({

    "Metric": [

        "Top_Positive_Sector",

        "Top_Positive_Effect",

        "Top_Negative_Sector",

        "Top_Negative_Effect",

        "Winning_Sectors",

        "Losing_Sectors",

        "Positive_Effect",

        "Negative_Effect",

        "Attribution_Residual",

        "Run_Date",

        "Engine_Version",
    ],

    "Value": [

        top_positive[
            "Sector"
        ],

        top_positive[
            "Total_Effect"
        ],

        top_negative[
            "Sector"
        ],

        top_negative[
            "Total_Effect"
        ],

        winning_sectors,

        losing_sectors,

        positive_effect,

        negative_effect,

        residual,

        datetime.now()
        .strftime(
            "%Y-%m-%d"
        ),

        ENGINE_VERSION,
    ]
})

# =========================================================
# SAVE FILES
# =========================================================

attribution_base.to_csv(

    OUTPUT_DIR
    / "brinson_sector_attribution.csv",

    index=False,
)

allocation_effect.to_csv(

    OUTPUT_DIR
    / "allocation_effect.csv",

    index=False,
)

selection_effect.to_csv(

    OUTPUT_DIR
    / "selection_effect.csv",

    index=False,
)

interaction_effect.to_csv(

    OUTPUT_DIR
    / "interaction_effect.csv",

    index=False,
)

dashboard.to_csv(

    OUTPUT_DIR
    / "brinson_dashboard.csv",

    index=False,
)

summary.to_csv(

    OUTPUT_DIR
    / "brinson_summary.csv",

    index=False,
)

reconciliation.to_csv(

    OUTPUT_DIR
    / "brinson_reconciliation.csv",

    index=False,
)

positive_contributors.to_csv(

    OUTPUT_DIR
    / "positive_contributors.csv",

    index=False,
)

negative_contributors.to_csv(

    OUTPUT_DIR
    / "negative_contributors.csv",

    index=False,
)

executive_summary.to_csv(

    REPORT_FILE,

    index=False,
)

# =========================================================
# QUALITY CHECKS
# =========================================================

if abs(
    portfolio_return
    -
    benchmark_return
    -
    active_return
) > 1e-6:

    print(
        "\n⚠ Active return "
        "reconciliation warning"
    )

if abs(
    residual
) > 0.02:

    print(
        "\n⚠ High attribution "
        f"residual: {residual:.2%}"
    )

print(
    "\n✔ Running Output Validation..."
)

required_outputs = [

    OUTPUT_DIR / "brinson_sector_attribution.csv",
    OUTPUT_DIR / "allocation_effect.csv",
    OUTPUT_DIR / "selection_effect.csv",
    OUTPUT_DIR / "interaction_effect.csv",
    OUTPUT_DIR / "brinson_dashboard.csv",
    OUTPUT_DIR / "brinson_summary.csv",
    OUTPUT_DIR / "brinson_reconciliation.csv",
    REPORT_FILE,
]

for file in required_outputs:

    if not file.exists():

        raise FileNotFoundError(
            file
        )
    
# =========================================================
# FINAL REPORT
# =========================================================

print(
    "\n"
    + "=" * 70
)

print(
    "🏁 BRINSON ATTRIBUTION COMPLETE"
)

print(
    "=" * 70
)

print(
    f"Portfolio Return : "
    f"{portfolio_return:.2%}"
)

print(
    f"Benchmark Return : "
    f"{benchmark_return:.2%}"
)

print(
    f"Active Return    : "
    f"{active_return:.2%}"
)

print(
    f"\nAllocation       : "
    f"{allocation_total:.2%}"
)

print(
    f"Selection        : "
    f"{selection_total:.2%}"
)

print(
    f"Interaction      : "
    f"{interaction_total:.2%}"
)

print(
    f"Residual         : "
    f"{residual:.4%}"
)

print(
    f"\nWinning Sectors  : "
    f"{winning_sectors}"
)

print(
    f"Losing Sectors   : "
    f"{losing_sectors}"
)

print(
    f"\nTop Positive     : "
    f"{top_positive['Sector']}"
)

print(
    f"Effect           : "
    f"{top_positive['Total_Effect']:.2%}"
)

print(
    f"\nTop Negative     : "
    f"{top_negative['Sector']}"
)

print(
    f"Effect           : "
    f"{top_negative['Total_Effect']:.2%}"
)

print(
    f"\nOutput Directory:\n"
    f"{OUTPUT_DIR}"
)

print(
    "=" * 70
)