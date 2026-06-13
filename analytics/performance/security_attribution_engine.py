"""
=========================================================
SECURITY ATTRIBUTION ENGINE
=========================================================

Purpose:
Institutional Security-Level Attribution

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

LOOKBACK_DAYS = 252

TOP_N = 20

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
    / "security_attribution_report.csv"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

# =========================================================
# LOAD
# =========================================================

print(
    "\n📥 Loading Data..."
)

portfolio = pd.read_csv(
    PORTFOLIO_FILE
)

benchmark = pd.read_csv(
    BENCHMARK_FILE
)

required_portfolio = [
    "Symbol",
    "Weight",
]

required_benchmark = [
    "Symbol",
    "Weight",
]

for col in required_portfolio:

    if col not in portfolio.columns:

        raise ValueError(
            f"Missing Portfolio Column: {col}"
        )

for col in required_benchmark:

    if col not in benchmark.columns:

        raise ValueError(
            f"Missing Benchmark Column: {col}"
        )

portfolio["Weight"] = (
    portfolio["Weight"]
    / portfolio["Weight"].sum()
)

benchmark["Weight"] = (
    benchmark["Weight"]
    / benchmark["Weight"].sum()
)

print(
    "\n📊 Building Security Returns..."
)

returns = {}

symbols = sorted(

    set(portfolio["Symbol"])

    |

    set(benchmark["Symbol"])
)

for symbol in symbols:

    file = (
        PRICE_DIR
        / f"{symbol}.parquet"
    )

    if not file.exists():
        continue

    try:

        df = pd.read_parquet(
            file
        )

        close = pd.to_numeric(
            df["Close"],
            errors="coerce"
        ).dropna()

        if len(close) < LOOKBACK_DAYS:
            continue

        ret = (

            close.iloc[-1]

            /

            close.iloc[-LOOKBACK_DAYS]

            - 1
        )

        returns[symbol] = ret

    except Exception:

        continue

returns_df = pd.DataFrame({

    "Symbol":
    list(
        returns.keys()
    ),

    "Security_Return":
    list(
        returns.values()
    )
})

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

security = (

    portfolio

    .merge(

        benchmark[
            [
                "Symbol",
                "Weight"
            ]
        ],

        on="Symbol",

        how="outer",

        suffixes=(
            "_Portfolio",
            "_Benchmark"
        )
    )

)

security = (
    security.fillna(0)
)

security[
    "Security_Return"
] = security[
    "Security_Return"
].replace(
    0,
    np.nan
)

security = security.dropna(
    subset=[
        "Security_Return"
    ]
)

security[
    "Portfolio_Contribution"
] = (

    security[
        "Weight_Portfolio"
    ]

    *

    security[
        "Security_Return"
    ]
)

security[
    "Benchmark_Contribution"
] = (

    security[
        "Weight_Benchmark"
    ]

    *

    security[
        "Security_Return"
    ]
)

security[
    "Active_Weight"
] = (

    security[
        "Weight_Portfolio"
    ]

    -

    security[
        "Weight_Benchmark"
    ]
)

security[
    "Active_Contribution"
] = (

    security[
        "Portfolio_Contribution"
    ]

    -

    security[
        "Benchmark_Contribution"
    ]
)

security = security.sort_values(

    "Active_Contribution",

    ascending=False,
)

security["Rank"] = (
    range(
        1,
        len(security) + 1
    )
)

top_contributors = (
    security.head(TOP_N)
)

bottom_contributors = (
    security.tail(TOP_N)
)

portfolio_return = (
    security[
        "Portfolio_Contribution"
    ]
    .sum()
)

benchmark_return = (
    security[
        "Benchmark_Contribution"
    ]
    .sum()
)

active_return = (
    portfolio_return
    -
    benchmark_return
)

dashboard = security[[

    "Rank",

    "Symbol",

    "Company_Name",
    
    "Sector",

    "Security_Return",

    "Weight_Portfolio",

    "Weight_Benchmark",

    "Active_Weight",

    "Portfolio_Contribution",

    "Benchmark_Contribution",

    "Active_Contribution",
]]

summary = pd.DataFrame({

    "Metric": [

        "Portfolio_Return",

        "Benchmark_Return",

        "Active_Return",

        "Securities",

        "Run_Date",

        "Engine_Version",
    ],

    "Value": [

        portfolio_return,

        benchmark_return,

        active_return,

        len(security),

        datetime.now()
        .strftime(
            "%Y-%m-%d"
        ),

        ENGINE_VERSION,
    ]
})

security.to_csv(

    OUTPUT_DIR
    / "security_attribution.csv",

    index=False,
)

top_contributors.to_csv(

    OUTPUT_DIR
    / "top_contributors.csv",

    index=False,
)

bottom_contributors.to_csv(

    OUTPUT_DIR
    / "bottom_contributors.csv",

    index=False,
)

dashboard.to_csv(

    OUTPUT_DIR
    / "security_dashboard.csv",

    index=False,
)

summary.to_csv(

    OUTPUT_DIR
    / "security_alpha.csv",

    index=False,
)

summary.to_csv(

    REPORT_FILE,

    index=False,
)

print("\n" + "=" * 70)

print(
    "🏁 SECURITY ATTRIBUTION COMPLETE"
)

print("=" * 70)

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
    f"\nTop Contributor  : "
    f"{top_contributors.iloc[0]['Symbol']}"
)

print(
    f"Contribution     : "
    f"{top_contributors.iloc[0]['Active_Contribution']:.2%}"
)

print(
    f"\nOutput Directory:\n"
    f"{OUTPUT_DIR}"
)

print("=" * 70)