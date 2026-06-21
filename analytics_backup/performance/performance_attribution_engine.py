"""
=========================================================
PERFORMANCE ATTRIBUTION ENGINE
=========================================================

Purpose:
Institutional Portfolio Performance Attribution

Inputs:
data/backtests/equity_curve.csv
data/portfolios/live_portfolio.csv
data/factors/factor_snapshot_master.csv

Outputs:
data/performance/performance_attribution.csv
data/performance/factor_attribution.csv
data/performance/sector_attribution.csv
data/performance/performance_dashboard.csv

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

TRADING_DAYS = 252

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

EQUITY_FILE = (
    ROOT
    / "data"
    / "backtests"
    / "equity_curve.csv"
)

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
    / "factor_snapshot_master.csv"
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
    / "performance_attribution_report.csv"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

required_files = [

    EQUITY_FILE,
    PORTFOLIO_FILE,
    FACTOR_FILE,
]

for file in required_files:

    if not file.exists():

        raise FileNotFoundError(
            file
        )
    
# =========================================================
# LOAD
# =========================================================

print(
    "\n📥 Loading Data..."
)

equity = pd.read_csv(
    EQUITY_FILE
)

portfolio = pd.read_csv(
    PORTFOLIO_FILE
)

if "Weight" not in portfolio.columns:

    raise ValueError(
        "Weight column missing."
    )

weight_sum = portfolio["Weight"].sum()

if abs(weight_sum - 1.0) > 0.01:

    print(
        f"⚠ Normalizing weights "
        f"(sum={weight_sum:.4f})"
    )

    portfolio["Weight"] = (

        portfolio["Weight"]

        / weight_sum
    )

factors = pd.read_csv(
    FACTOR_FILE
)

# =========================================================
# VALIDATION
# =========================================================

required_equity = [
    "Portfolio_Return",
]

for col in required_equity:

    if col not in equity.columns:

        raise ValueError(
            f"Missing Column: {col}"
        )

required_portfolio = [

    "Symbol",
    "Weight",
]

for col in required_portfolio:

    if col not in portfolio.columns:

        raise ValueError(
            f"Missing Column: {col}"
        )

# =========================================================
# CLEAN
# =========================================================
equity["Portfolio_Return"] = pd.to_numeric(
    equity["Portfolio_Return"],
    errors="coerce"
)

if "Benchmark_Return" in equity.columns:

    equity["Benchmark_Return"] = pd.to_numeric(
        equity["Benchmark_Return"],
        errors="coerce"
    )

if "Active_Return" in equity.columns:

    equity["Active_Return"] = pd.to_numeric(
        equity["Active_Return"],
        errors="coerce"
    )

equity = equity.dropna(
    subset=["Portfolio_Return"]
)

# =========================================================
# PERFORMANCE STATISTICS
# =========================================================

portfolio_returns = equity[
    "Portfolio_Return"
]

if "Benchmark_Return" in equity.columns:

    benchmark_returns = (

        equity[
            "Benchmark_Return"
        ]
        .dropna()
    )

    benchmark_coverage = (

        len(benchmark_returns)

        /

        len(equity)
    )

    print(
        f"Benchmark Coverage : "
        f"{benchmark_coverage:.2%}"
    )

    if benchmark_coverage < 0.95:

        print(
            "⚠ Benchmark coverage below 95%"
        )

    benchmark_total_return = (

        (1 + benchmark_returns)
        .prod()

        - 1
    )

else:

    benchmark_returns = None

    benchmark_coverage = 0

    benchmark_total_return = np.nan

if "Active_Return" in equity.columns:

    active_returns = equity[
        "Active_Return"
    ]

else:

    active_returns = None

portfolio_total_return = (

    (1 + portfolio_returns)

    .prod()

    - 1
)

if pd.notna(
    benchmark_total_return
):

    excess_return = (
        portfolio_total_return
        - benchmark_total_return
    )

else:

    excess_return = 0.0
annual_return = (

    (1 + portfolio_returns.mean())

    ** TRADING_DAYS

    - 1
)

annual_volatility = (

    portfolio_returns.std()

    * np.sqrt(
        TRADING_DAYS
    )
)

if active_returns is not None:

    tracking_error = (
        active_returns.std()
        * np.sqrt(TRADING_DAYS)
    )

    information_ratio = (
        active_returns.mean()
        * TRADING_DAYS
    ) / max(
        tracking_error,
        1e-9
    )

    hit_ratio = (
        (active_returns > 0)
        .mean()
    )

else:

    tracking_error = np.nan
    information_ratio = np.nan
    hit_ratio = np.nan

# =========================================================
# SHARPE
# =========================================================

sharpe_ratio = (

    annual_return

    / max(
        annual_volatility,
        1e-9
    )
)

# =========================================================
# ALPHA / BETA
# =========================================================

if benchmark_returns is not None:

    aligned = pd.concat(

        [

            portfolio_returns,

            benchmark_returns,

        ],

        axis=1,

    ).dropna()

    aligned.columns = [

        "Portfolio",
        "Benchmark",
    ]

    covariance = np.cov(

        aligned["Portfolio"],
        aligned["Benchmark"]
    )

    beta = (

        covariance[0, 1]

        /

        max(
            covariance[1, 1],
            1e-9
        )
    )

    alpha = (

        aligned["Portfolio"].mean()

        -

        beta

        * aligned[
            "Benchmark"
        ].mean()
    ) * TRADING_DAYS

    correlation = np.corrcoef(

        aligned["Portfolio"],
        aligned["Benchmark"]
    )[0, 1]

    r_squared = (

        correlation ** 2
    )

else:

    alpha = np.nan

    beta = np.nan

    r_squared = np.nan

# =========================================================
# DRAWDOWN
# =========================================================

if "Drawdown" in equity.columns:

    max_drawdown = (
        equity["Drawdown"]
        .min()
    )

else:

    max_drawdown = np.nan

# =========================================================
# PERFORMANCE ATTRIBUTION
# =========================================================

performance_attribution = pd.DataFrame({

    "Metric": [

        "Portfolio_Return",
        "Benchmark_Return",
        "Excess_Return",

        "Annual_Return",
        "Annual_Volatility",

        "Sharpe_Ratio",

        "Tracking_Error",

        "Information_Ratio",

        "Hit_Ratio",

        "Max_Drawdown",
    ],

    "Value": [

        portfolio_total_return,

        benchmark_total_return,

        excess_return,

        annual_return,

        annual_volatility,

        sharpe_ratio,

        tracking_error,

        information_ratio,

        hit_ratio,

        max_drawdown,
    ]
})

# =========================================================
# FACTOR ATTRIBUTION
# =========================================================

print(
    "\n📊 Factor Attribution..."
)

factors["Snapshot_Date"] = pd.to_datetime(
    factors["Snapshot_Date"]
)

latest_date = (
    factors["Snapshot_Date"]
    .max()
)

factors = factors[
    factors["Snapshot_Date"]
    == latest_date
]

merged = portfolio.merge(

    factors,

    on="Symbol",

    how="inner"
)

factor_groups = {

    "Momentum": [

        "Momentum_1M",
        "Momentum_3M",
        "Momentum_6M",
        "Momentum_12M",
    ],

    "Volatility": [

        "Volatility_20D",
        "Volatility_60D",
        "ATR_14",
        "Max_Drawdown_252D",
    ],

    "Trend": [

        "Distance_SMA50",
        "Distance_SMA200",
        "Distance_52W_High",
    ],

    "Liquidity": [

        "ADV_20D",
        "Dollar_Volume",
    ],

    "Size": [

        "Market_Cap",
    ]
}

factor_records = []

for group, cols in factor_groups.items():

    available = [

        c

        for c in cols

        if c in merged.columns
    ]

    if not available:
        continue

    exposure = 0

    for factor in available:

        values = pd.to_numeric(

            merged[factor],

            errors="coerce"
        )

        values = values.fillna(
            values.median()
        )

        zscore = (

            values
            - values.mean()

        ) / max(
            values.std(),
            1e-9,
        )

        exposure += (

            zscore

            * merged[
                "Weight"
            ]

        ).sum()

    factor_records.append({

        "Factor_Group":
        group,

        "Exposure":
        exposure,

        "Contribution":
        exposure * excess_return,
    })

factor_attribution = pd.DataFrame(
    factor_records
)

if not factor_attribution.empty:

    total = max(

        factor_attribution[
            "Contribution"
        ].abs().sum(),

        1e-9,
    )

    factor_attribution[
        "Contribution_%"
    ] = (

        factor_attribution[
            "Contribution"
        ]

        .abs()

        / total

        * 100
    )

# =========================================================
# SECTOR ATTRIBUTION
# =========================================================

print(
    "🏭 Sector Attribution..."
)

if "Sector" not in merged.columns:

    sector_attribution = pd.DataFrame({

        "Sector": ["UNKNOWN"],

        "Portfolio_Weight": [
            merged["Weight"].sum()
        ],

        "Sector_Score": [0],

        "Contribution": [0],
    })

else:

    if "Alpha_Adjusted" in merged.columns:

        sector_attribution = (

            merged

            .groupby("Sector")

            .agg(

                Portfolio_Weight=(
                    "Weight",
                    "sum"
                ),

                Sector_Score=(
                    "Alpha_Adjusted",
                    "mean"
                ),
            )

            .reset_index()
        )

    else:

        sector_attribution = (

            merged

            .groupby("Sector")

            .agg(

                Portfolio_Weight=(
                    "Weight",
                    "sum"
                ),

                Sector_Score=(
                    "Weight",
                    "count"
                ),
            )

            .reset_index()
        )

    sector_attribution[
        "Contribution"
    ] = (

        sector_attribution[
            "Portfolio_Weight"
        ]

        * sector_attribution[
            "Sector_Score"
        ]
    )

# =========================================================
# ATTRIBUTION AUDIT
# =========================================================

audit_metrics = {

    "Portfolio_Return":
    portfolio_total_return,

    "Benchmark_Return":
    benchmark_total_return,

    "Excess_Return":
    excess_return,

    "Annual_Return":
    annual_return,

    "Annual_Volatility":
    annual_volatility,

    "Sharpe_Ratio":
    sharpe_ratio,

    "Tracking_Error":
    tracking_error,

    "Information_Ratio":
    information_ratio,

    "Hit_Ratio":
    hit_ratio,

    "Max_Drawdown":
    max_drawdown,

    "Alpha":
    alpha,

    "Beta":
    beta,

    "R_Squared":
    r_squared,

    "Run_Date":
    datetime.now().strftime(
        "%Y-%m-%d"
    ),

    "Engine_Version":
    ENGINE_VERSION,
}

AUDIT_FILE = (

    OUTPUT_DIR
    / "performance_audit.csv"
)

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
# DASHBOARD
# =========================================================

dashboard = pd.DataFrame({

    "Metric": [

        "Portfolio_Return",

        "Benchmark_Return",

        "Excess_Return",

        "Sharpe_Ratio",

        "Information_Ratio",

        "Hit_Ratio",

        "Max_Drawdown",

        "Alpha",

        "Beta",

        "R_Squared",

        "Factors",

        "Sectors",

        "Engine_Version",
    ],

    "Value": [

        portfolio_total_return,

        benchmark_total_return,

        excess_return,

        sharpe_ratio,

        information_ratio,

        hit_ratio,

        max_drawdown,

        alpha,

        beta,

        r_squared,

        len(
            factor_attribution
        ),

        len(
            sector_attribution
        ),

        ENGINE_VERSION,
    ]
})

# =========================================================
# SAVE
# =========================================================

performance_attribution.to_csv(

    OUTPUT_DIR
    / "performance_attribution.csv",

    index=False,
)

factor_attribution.to_csv(

    OUTPUT_DIR
    / "factor_attribution.csv",

    index=False,
)

sector_attribution.to_csv(

    OUTPUT_DIR
    / "sector_attribution.csv",

    index=False,
)

dashboard.to_csv(

    OUTPUT_DIR
    / "performance_dashboard.csv",

    index=False,
)

dashboard.to_csv(
    REPORT_FILE,
    index=False,
)

# =========================================================
# OUTPUT VALIDATION
# =========================================================

print(
    "✔ Running Output Validation..."
)

required_outputs = [

    OUTPUT_DIR / "performance_attribution.csv",

    OUTPUT_DIR / "factor_attribution.csv",

    OUTPUT_DIR / "sector_attribution.csv",

    OUTPUT_DIR / "performance_dashboard.csv",

    AUDIT_FILE,
]

for file in required_outputs:

    if not file.exists():

        raise FileNotFoundError(
            file
        )


benchmark_display = (

    f"{benchmark_total_return:.2%}"

    if pd.notna(
        benchmark_total_return
    )

    else "N/A"
)

# =========================================================
# REPORT
# =========================================================

print(
    "\n"
    + "=" * 70
)

print(
    "🏁 PERFORMANCE ATTRIBUTION COMPLETE"
)

print(
    "=" * 70
)

print(
    f"Alpha               : "
    f"{alpha:.2%}"
)

print(
    f"Beta                : "
    f"{beta:.2f}"
)

print(
    f"R-Squared           : "
    f"{r_squared:.2%}"
)

print(
    f"Portfolio Return : "
    f"{portfolio_total_return:.2%}"
)

print(
    f"Benchmark Return : "
    f"{benchmark_total_return:.2%}"
)

print(
    f"excess_return            : "
    f"{excess_return:.2%}"
)

print(
    f"Sharpe Ratio     : "
    f"{sharpe_ratio:.2f}"
)

print(
    f"Information Ratio: "
    f"{information_ratio:.2f}"
)

print(
    f"Hit Ratio        : "
    f"{hit_ratio:.2%}"
)

print(
    f"Max Drawdown     : "
    f"{max_drawdown:.2%}"
)

print(
    f"\nOutput Directory:\n"
    f"{OUTPUT_DIR}"
)

print(
    "=" * 70
)