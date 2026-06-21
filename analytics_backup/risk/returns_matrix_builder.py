"""
=========================================================
RETURNS MATRIX BUILDER
=========================================================

Institutional Quant Platform

Purpose
-------
Build institutional-grade return matrices
for risk modeling, covariance estimation,
factor models, portfolio optimization,
stress testing and risk attribution.

Input
-----
data/raw/security_price_history.parquet

Outputs
-------
returns_matrix.parquet
log_returns_matrix.parquet
monthly_returns.parquet
coverage_report.csv
returns_audit.csv

=========================================================
"""

from pathlib import Path
from datetime import datetime

import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# =========================================================
# CONFIGURATION
# =========================================================

ENGINE_NAME = "RETURNS_MATRIX_BUILDER"

ENGINE_VERSION = "2.0.0"

TRADING_DAYS = 252

MIN_HISTORY_DAYS = 252

MAX_MISSING_PCT = 0.10

RETURN_WINSOR_LOWER = 0.001

RETURN_WINSOR_UPPER = 0.999

ENABLE_WINSORIZATION = True

ENABLE_LOG_RETURNS = True

ENABLE_MONTHLY_RETURNS = True

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    ROOT
    / "data"
    / "raw"
    / "security_price_history.parquet"
)

OUTPUT_DIR = (
    ROOT
    / "data"
    / "risk"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)

RETURNS_MATRIX_FILE = (
    OUTPUT_DIR
    / "returns_matrix.parquet"
)

LOG_RETURNS_MATRIX_FILE = (
    OUTPUT_DIR
    / "log_returns_matrix.parquet"
)

MONTHLY_RETURNS_FILE = (
    OUTPUT_DIR
    / "monthly_returns.parquet"
)

COVERAGE_FILE = (
    OUTPUT_DIR
    / "coverage_report.csv"
)

AUDIT_FILE = (
    OUTPUT_DIR
    / "returns_audit.csv"
)

# =========================================================
# LOAD DATA
# =========================================================

print(
    "\n📥 Loading Security Price History..."
)

if not INPUT_FILE.exists():

    raise FileNotFoundError(
        f"Missing file: {INPUT_FILE}"
    )

prices = pd.read_parquet(
    INPUT_FILE
)

# =========================================================
# SCHEMA VALIDATION
# =========================================================

required_columns = [

    "Date",

    "Close",

    "Symbol"
]

missing_columns = [

    c

    for c in required_columns

    if c not in prices.columns
]

if missing_columns:

    raise ValueError(
        f"Missing columns: "
        f"{missing_columns}"
    )

# =========================================================
# DATA TYPE VALIDATION
# =========================================================

prices["Date"] = pd.to_datetime(
    prices["Date"],
    errors="coerce"
)

prices["Close"] = pd.to_numeric(
    prices["Close"],
    errors="coerce"
)

prices["Symbol"] = (
    prices["Symbol"]
    .astype(str)
    .str.strip()
)

prices = prices.dropna(
    subset=[
        "Date",
        "Close",
        "Symbol"
    ]
)

# =========================================================
# REMOVE DUPLICATES
# =========================================================

duplicate_count = (

    prices

    .duplicated(
        subset=[
            "Date",
            "Symbol"
        ]
    )

    .sum()
)

if duplicate_count > 0:

    print(
        f"Removing "
        f"{duplicate_count:,} duplicates"
    )

    prices = (

        prices

        .drop_duplicates(
            subset=[
                "Date",
                "Symbol"
            ],
            keep="last"
        )
    )

# =========================================================
# SORT DATA
# =========================================================

prices = (

    prices

    .sort_values(
        [
            "Symbol",
            "Date"
        ]
    )

    .reset_index(
        drop=True
    )
)

# =========================================================
# COVERAGE ANALYSIS
# =========================================================

print(
    "🔍 Building Coverage Statistics..."
)

coverage = (

    prices

    .groupby(
        "Symbol"
    )

    .agg({

        "Date": [
            "count",
            "min",
            "max"
        ]

    })

)

coverage.columns = [

    "Observations",

    "First_Date",

    "Last_Date"
]

coverage = (
    coverage
    .reset_index()
)

coverage[
    "Coverage_Years"
] = (

    coverage[
        "Observations"
    ]

    /

    TRADING_DAYS
)

coverage[
    "Eligible"
] = (

    coverage[
        "Observations"
    ]

    >=

    MIN_HISTORY_DAYS
)

# =========================================================
# ELIGIBLE UNIVERSE
# =========================================================

eligible_symbols = set(

    coverage.loc[

        coverage[
            "Eligible"
        ],

        "Symbol"
    ]
)

prices = prices[

    prices[
        "Symbol"
    ]

    .isin(
        eligible_symbols
    )
]

coverage = coverage[

    coverage[
        "Eligible"
    ]
]

# =========================================================
# UNIVERSE SUMMARY
# =========================================================

print(
    f"Total Securities : "
    f"{coverage.shape[0]:,}"
)

print(
    f"Price Records    : "
    f"{len(prices):,}"
)

print(
    f"Average History  : "
    f"{coverage['Observations'].mean():,.0f}"
)

print(
    f"Min History      : "
    f"{coverage['Observations'].min():,.0f}"
)

# =========================================================
# RETURN SOURCE
# =========================================================

if "Daily_Return" in prices.columns:

    print(
        "✓ Using Existing Daily_Return"
    )

else:

    print(
        "📈 Calculating Daily Returns..."
    )

    prices[
        "Daily_Return"
    ] = (

        prices

        .groupby(
            "Symbol"
        )["Close"]

        .pct_change()
    )

# =========================================================
# REMOVE FIRST OBSERVATION
# =========================================================

prices = prices.dropna(
    subset=[
        "Daily_Return"
    ]
)

# =========================================================
# PART 2 STARTS HERE
# =========================================================

#
# Next:
#
# Returns Matrix Construction
# Log Return Matrix
# Monthly Returns
# Winsorization
# Outlier Controls
#
# =========================================================

# =========================================================
# RETURN MATRIX CONSTRUCTION
# =========================================================

print(
    "\n🏗 Building Return Matrices..."
)

# =========================================================
# RETURN DISTRIBUTION ANALYSIS
# =========================================================

raw_return_count = len(
    prices
)

raw_return_mean = (
    prices[
        "Daily_Return"
    ]
    .mean()
)

raw_return_std = (
    prices[
        "Daily_Return"
    ]
    .std()
)

# =========================================================
# WINSORIZATION
# =========================================================

if ENABLE_WINSORIZATION:

    print(
        "🛡 Applying Return Winsorization..."
    )

    lower_bound = (

        prices[
            "Daily_Return"
        ]

        .quantile(
            RETURN_WINSOR_LOWER
        )
    )

    upper_bound = (

        prices[
            "Daily_Return"
        ]

        .quantile(
            RETURN_WINSOR_UPPER
        )
    )

    prices[
        "Daily_Return"
    ] = (

        prices[
            "Daily_Return"
        ]

        .clip(
            lower=lower_bound,
            upper=upper_bound
        )
    )

else:

    lower_bound = np.nan
    upper_bound = np.nan

# =========================================================
# LOG RETURNS
# =========================================================

if ENABLE_LOG_RETURNS:

    print(
        "📈 Building Log Returns..."
    )

    prices[
        "Log_Return"
    ] = np.log(
        1 +
        prices[
            "Daily_Return"
        ]
    )

else:

    prices[
        "Log_Return"
    ] = np.nan

# =========================================================
# RETURN MATRIX
# =========================================================

print(
    "📊 Building Daily Return Matrix..."
)

returns_matrix = (

    prices

    .pivot_table(
        index="Date",
        columns="Symbol",
        values="Daily_Return",
        aggfunc="last"
    )

    .sort_index()
)

# =========================================================
# LOG RETURN MATRIX
# =========================================================

if ENABLE_LOG_RETURNS:

    print(
        "📊 Building Log Return Matrix..."
    )

    log_returns_matrix = (

        prices

        .pivot(
            index="Date",
            columns="Symbol",
            values="Log_Return",
        )

        .sort_index()
    )

else:

    log_returns_matrix = pd.DataFrame(
        index=returns_matrix.index
    )

# =========================================================
# MISSING DATA ANALYSIS
# =========================================================

print(
    "🔍 Evaluating Matrix Coverage..."
)

missing_stats = pd.DataFrame({

    "Symbol":
    returns_matrix.columns

})

coverage_stats = (
    returns_matrix
    .notna()
    .sum()
    .rename("Observations")
    .reset_index()
)

coverage_stats.columns = [
    "Symbol",
    "Observations"
]

missing_stats = missing_stats.merge(
    coverage_stats,
    on="Symbol",
    how="left"
)

missing_stats[
    "Missing_Pct"
] = (

    returns_matrix

    .isna()

    .mean()

    .values
)

MIN_RISK_HISTORY_DAYS = 504

valid_symbols = missing_stats.loc[
    (
        missing_stats["Missing_Pct"]
        <= MAX_MISSING_PCT
    )
    |
    (
        missing_stats["Observations"]
        >= MIN_RISK_HISTORY_DAYS
    ),
    "Symbol"
]

coverage_rejections = (

    missing_stats[

        missing_stats[
            "Missing_Pct"
        ]

        >

        MAX_MISSING_PCT
    ]

    .sort_values(
        "Missing_Pct",
        ascending=False
    )
)

print(
    f"Coverage Filter Removed: "
    f"{len(coverage_rejections):,}"
)

coverage_rejections.to_csv(
    OUTPUT_DIR / "coverage_rejections.csv",
    index=False
)

returns_matrix = (

    returns_matrix[
        sorted(
            valid_symbols
        )
    ]
)

if ENABLE_LOG_RETURNS:

    log_returns_matrix = (

        log_returns_matrix[
            sorted(
                valid_symbols
            )
        ]
    )

# =========================================================
# LIMITED FORWARD FILL
# =========================================================

returns_matrix = (

    returns_matrix

    .ffill(
        limit=3
    )
)

if ENABLE_LOG_RETURNS:

    log_returns_matrix = (

        log_returns_matrix

        .ffill(
            limit=3
        )
    )

# =========================================================
# REMOVE EMPTY ROWS
# =========================================================

returns_matrix = (

    returns_matrix

    .dropna(
        how="all"
    )
)

if ENABLE_LOG_RETURNS:

    log_returns_matrix = (

        log_returns_matrix

        .dropna(
            how="all"
        )
    )

# =========================================================
# MONTHLY RETURNS
# =========================================================

if ENABLE_MONTHLY_RETURNS:

    print(
        "📅 Building Monthly Returns..."
    )

    monthly_returns = (

        returns_matrix

        .resample(
            "ME"
        )

        .apply(

            lambda x:

            (
                1 + x
            )

            .prod()

            - 1
        )
    )

else:

    monthly_returns = pd.DataFrame()

# =========================================================
# MATRIX STATISTICS
# =========================================================

print(
    "📈 Building Return Statistics..."
)

security_statistics = pd.DataFrame({

    "Symbol":
    returns_matrix.columns

})

security_statistics[
    "Mean_Return"
] = (

    returns_matrix

    .mean()

    .values
)

security_statistics[
    "Annualized_Return"
] = (

    returns_matrix

    .mean()

    * TRADING_DAYS

).values

security_statistics[
    "Volatility"
] = (

    returns_matrix

    .std()

    .values
)

security_statistics[
    "Annualized_Volatility"
] = (

    returns_matrix

    .std()

    * np.sqrt(
        TRADING_DAYS
    )

).values

security_statistics[
    "Sharpe"
] = (

    security_statistics[
        "Annualized_Return"
    ]

    /

    security_statistics[
        "Annualized_Volatility"
    ]

    .replace(
        0,
        np.nan
    )
)

security_statistics[
    "Observations"
] = (

    returns_matrix

    .count()

    .values
)

# =========================================================
# MATRIX DIMENSIONS
# =========================================================

matrix_rows = (
    returns_matrix.shape[0]
)

matrix_columns = (
    returns_matrix.shape[1]
)

print(
    f"Trading Days     : "
    f"{matrix_rows:,}"
)

print(
    f"Securities       : "
    f"{matrix_columns:,}"
)

print(
    f"Return Records   : "
    f"{matrix_rows * matrix_columns:,}"
)

print(
    f"Average Vol      : "
    f"{security_statistics['Annualized_Volatility'].mean():.2%}"
)

print(
    "\nAnnualized Return Distribution:"
)

print(

    security_statistics[
        "Annualized_Return"
    ]

    .describe()
)

# =========================================================
# RETURN QUALITY METRICS
# =========================================================

return_quality = pd.DataFrame({

    "Metric": [

        "Raw_Return_Count",

        "Return_Mean",

        "Return_Std",

        "Winsor_Lower",

        "Winsor_Upper",

        "Trading_Days",

        "Securities"
    ],

    "Value": [

        raw_return_count,

        raw_return_mean,

        raw_return_std,

        lower_bound,

        upper_bound,

        matrix_rows,

        matrix_columns
    ]
})

# =========================================================
# PART 3 STARTS HERE
# =========================================================
#
# Next:
#
# Coverage Analytics
# Missing Data Diagnostics
# Distribution Analysis
# Market Statistics
# Quality Scoring
#
# =========================================================

# =========================================================
# COVERAGE ANALYTICS
# =========================================================

print(
    "\n🔍 Building Coverage Analytics..."
)

coverage_analysis = pd.DataFrame({

    "Symbol":
    returns_matrix.columns

})

coverage_analysis[
    "Observations"
] = (

    returns_matrix

    .count()

    .values
)

coverage_analysis[
    "Missing_Count"
] = (

    returns_matrix

    .isna()

    .sum()

    .values
)

coverage_analysis[
    "Missing_Pct"
] = (

    returns_matrix

    .isna()

    .mean()

    .values
)

coverage_analysis[
    "Coverage_Pct"
] = (

    1
    -
    coverage_analysis[
        "Missing_Pct"
    ]

) * 100

coverage_analysis[
    "Eligible"
] = (

    coverage_analysis[
        "Coverage_Pct"
    ]

    >=

    (
        100
        *
        (
            1
            -
            MAX_MISSING_PCT
        )
    )
)

# =========================================================
# DATE COVERAGE ANALYSIS
# =========================================================

date_coverage = pd.DataFrame({

    "Coverage":

    returns_matrix

    .notna()

    .sum(
        axis=1
    )

}, index=returns_matrix.index)

date_coverage[
    "Coverage_Pct"
] = (

    date_coverage[
        "Coverage"
    ]

    /

    len(
        returns_matrix.columns
    )

) * 100

# =========================================================
# MARKET RETURN SERIES
# =========================================================

print(
    "📈 Building Market Statistics..."
)

market_return = (

    returns_matrix

    .clip(
        lower=-0.20,
        upper=0.20
    )

    .mean(
        axis=1,
        skipna=True
    )
)

market_statistics = {

    "Average_Daily_Return":

    market_return.mean(),

    "Annualized_Return":

    market_return.mean()

    * TRADING_DAYS,

    "Daily_Volatility":

    market_return.std(),

    "Annualized_Volatility":

    market_return.std()

    * np.sqrt(
        TRADING_DAYS
    ),

    "Best_Day":

    market_return.max(),

    "Worst_Day":

    market_return.min(),

    "Positive_Days":

    (
        market_return > 0
    ).sum(),

    "Negative_Days":

    (
        market_return < 0
    ).sum()
}

# =========================================================
# DISTRIBUTION ANALYSIS
# =========================================================

print(
    "📊 Building Distribution Analytics..."
)

distribution_analysis = pd.DataFrame({

    "Metric": [

        "Mean",

        "Median",

        "Std",

        "Min",

        "Max",

        "1%",

        "5%",

        "95%",

        "99%"
    ],

    "Value": [

        market_return.mean(),

        market_return.median(),

        market_return.std(),

        market_return.min(),

        market_return.max(),

        market_return.quantile(
            0.01
        ),

        market_return.quantile(
            0.05
        ),

        market_return.quantile(
            0.95
        ),

        market_return.quantile(
            0.99
        )
    ]
})

# =========================================================
# SKEWNESS & KURTOSIS
# =========================================================

market_skew = (
    market_return.skew()
)

market_kurtosis = (
    market_return.kurtosis()
)

distribution_analysis.loc[
    len(
        distribution_analysis
    )
] = [

    "Skewness",

    market_skew
]

distribution_analysis.loc[
    len(
        distribution_analysis
    )
] = [

    "Kurtosis",

    market_kurtosis
]

# =========================================================
# RISK METRICS
# =========================================================

print(
    "⚠ Building Risk Metrics..."
)

var_95 = (
    market_return.quantile(
        0.05
    )
)

cvar_95 = (

    market_return[
        market_return
        <=
        var_95
    ]

    .mean()
)

risk_metrics = pd.DataFrame({

    "Metric": [

        "VaR_95",

        "CVaR_95",

        "Max_Drawdown",

        "Worst_Day",

        "Best_Day"
    ],

    "Value": [

        var_95,

        cvar_95,

        (
            (
                (
                    1
                    +
                    market_return
                )
                .cumprod()
            )
            /
            (
                (
                    1
                    +
                    market_return
                )
                .cumprod()
                .cummax()
            )
            -
            1
        ).min(),

        market_return.min(),

        market_return.max()
    ]
})

# =========================================================
# SECURITY QUALITY SCORING
# =========================================================

print(
    "🏛 Building Security Quality Scores..."
)

quality_scores = coverage_analysis.copy()

quality_scores[
    "Quality_Score"
] = (

    quality_scores[
        "Coverage_Pct"
    ]

    * 0.60

)

quality_scores[
    "Quality_Score"
] += (

    np.minimum(

        quality_scores[
            "Observations"
        ]

        /

        (
            5
            *
            TRADING_DAYS
        ),

        1
    )

    * 40
)

quality_scores[
    "Quality_Score"
] = (

    quality_scores[
        "Quality_Score"
    ]

    .clip(
        lower=0,
        upper=100
    )
)

# =========================================================
# TOP / BOTTOM SECURITIES
# =========================================================

top_quality = (

    quality_scores

    .sort_values(
        "Quality_Score",
        ascending=False
    )

    .head(25)
)

bottom_quality = (

    quality_scores

    .sort_values(
        "Quality_Score",
        ascending=True
    )

    .head(25)
)

# =========================================================
# MATRIX HEALTH SCORE
# =========================================================

matrix_health_score = (

    quality_scores[
        "Quality_Score"
    ]

    .mean()
)

# =========================================================
# DIAGNOSTIC SUMMARY
# =========================================================

print(
    f"Average Coverage : "
    f"{coverage_analysis['Coverage_Pct'].mean():.2f}%"
)

print(
    f"Matrix Health    : "
    f"{matrix_health_score:.2f}"
)

print(
    f"Market Return    : "
    f"{market_statistics['Annualized_Return']:.2%}"
)

print(
    f"Market Vol       : "
    f"{market_statistics['Annualized_Volatility']:.2%}"
)

print(
    f"VaR 95%          : "
    f"{var_95:.2%}"
)

# =========================================================
# AUDIT DATASET
# =========================================================

audit_summary = pd.DataFrame({

    "Metric": [

        "Engine_Version",

        "Run_Time",

        "Trading_Days",

        "Eligible_Securities",

        "Average_Coverage",

        "Matrix_Health",

        "Market_Return",

        "Market_Volatility",

        "VaR_95",

        "CVaR_95"
    ],

    "Value": [

        ENGINE_VERSION,

        datetime.now(),

        matrix_rows,

        matrix_columns,

        coverage_analysis[
            "Coverage_Pct"
        ].mean(),

        matrix_health_score,

        market_statistics[
            "Annualized_Return"
        ],

        market_statistics[
            "Annualized_Volatility"
        ],

        var_95,

        cvar_95
    ]
})

# =========================================================
# PART 4 STARTS HERE
# =========================================================
#
# Next:
#
# Parquet Exports
# CSV Reports
# Validation Layer
# Audit Reports
# Production Completion
#
# =========================================================

# =========================================================
# OUTPUT FILES
# =========================================================

print(
    "\n💾 Saving Outputs..."
)

QUALITY_FILE = (
    OUTPUT_DIR
    / "quality_scores.csv"
)

TOP_QUALITY_FILE = (
    OUTPUT_DIR
    / "top_quality_securities.csv"
)

BOTTOM_QUALITY_FILE = (
    OUTPUT_DIR
    / "bottom_quality_securities.csv"
)

MARKET_STATS_FILE = (
    OUTPUT_DIR
    / "market_statistics.csv"
)

RISK_METRICS_FILE = (
    OUTPUT_DIR
    / "risk_metrics.csv"
)

DISTRIBUTION_FILE = (
    OUTPUT_DIR
    / "distribution_analysis.csv"
)

# =========================================================
# FINAL VALIDATION
# =========================================================

print(
    "✔ Running Final Validation..."
)

if returns_matrix.empty:

    raise ValueError(
        "Returns matrix is empty."
    )

if matrix_columns < 100:

    raise ValueError(
        "Too few securities."
    )

if matrix_rows < 252:

    raise ValueError(
        "Insufficient trading history."
    )

if returns_matrix.isna().all().all():

    raise ValueError(
        "Returns matrix contains only NaN values."
    )

# =========================================================
# CORRELATION HEALTH CHECK
# =========================================================

print(
    "🔗 Building Correlation Diagnostics..."
)

sample_cols = list(
    returns_matrix.columns[:200]
)

correlation_sample = (

    returns_matrix[
        sample_cols
    ]

    .corr()
)

corr_values = (

    correlation_sample

    .values
)

corr_values = corr_values[
    ~np.eye(
        corr_values.shape[0],
        dtype=bool
    )
]

average_correlation = np.nanmean(
    corr_values
)

median_correlation = np.nanmedian(
    corr_values
)

# =========================================================
# DATASET METADATA
# =========================================================

metadata = pd.DataFrame({

    "Metric": [

        "Engine_Name",

        "Engine_Version",

        "Build_Time",

        "Trading_Days",

        "Securities",

        "Average_Coverage",

        "Average_Correlation",

        "Median_Correlation",

        "Matrix_Health",

        "Average_Volatility"
    ],

    "Value": [

        ENGINE_NAME,

        ENGINE_VERSION,

        datetime.now(),

        matrix_rows,

        matrix_columns,

        coverage_analysis[
            "Coverage_Pct"
        ].mean(),

        average_correlation,

        median_correlation,

        matrix_health_score,

        security_statistics[
            "Annualized_Volatility"
        ].mean()
    ]
})

# =========================================================
# MEMORY OPTIMIZATION
# =========================================================

returns_matrix = returns_matrix.astype(
    np.float32
)

if ENABLE_LOG_RETURNS:

    log_returns_matrix = (
        log_returns_matrix
        .astype(np.float32)
    )

# =========================================================
# EXPORT MATRICES
# =========================================================

print(
    "📊 Saving Return Matrices..."
)

returns_matrix.to_parquet(
    RETURNS_MATRIX_FILE,
    index=True
)

if ENABLE_LOG_RETURNS:

    log_returns_matrix.to_parquet(
        LOG_RETURNS_MATRIX_FILE,
        index=True
    )

if ENABLE_MONTHLY_RETURNS:

    monthly_returns.to_parquet(
        MONTHLY_RETURNS_FILE,
        index=True
    )

# =========================================================
# EXPORT REPORTS
# =========================================================

coverage_analysis.to_csv(
    COVERAGE_FILE,
    index=False
)

audit_summary.to_csv(
    AUDIT_FILE,
    index=False
)

quality_scores.to_csv(
    QUALITY_FILE,
    index=False
)

top_quality.to_csv(
    TOP_QUALITY_FILE,
    index=False
)

bottom_quality.to_csv(
    BOTTOM_QUALITY_FILE,
    index=False
)

pd.DataFrame(
    [market_statistics]
).to_csv(
    MARKET_STATS_FILE,
    index=False
)

risk_metrics.to_csv(
    RISK_METRICS_FILE,
    index=False
)

distribution_analysis.to_csv(
    DISTRIBUTION_FILE,
    index=False
)

metadata.to_csv(
    OUTPUT_DIR
    / "returns_metadata.csv",
    index=False
)

security_statistics.to_csv(
    OUTPUT_DIR
    / "security_statistics.csv",
    index=False
)

security_statistics[
    "Annualized_Return"
].describe().to_csv(

    OUTPUT_DIR
    / "return_distribution.csv"
)

# =========================================================
# FINAL SUMMARY
# =========================================================

print(
    "\n=========================================================="
)

print(
    "🏁 RETURNS MATRIX BUILDER COMPLETE"
)

print(
    "=========================================================="
)

print(
    f"Trading Days         : "
    f"{matrix_rows:,}"
)

print(
    f"Securities           : "
    f"{matrix_columns:,}"
)

print(
    f"Return Matrix Shape  : "
    f"{returns_matrix.shape}"
)

if ENABLE_LOG_RETURNS:

    print(
        f"Log Matrix Shape     : "
        f"{log_returns_matrix.shape}"
    )

if ENABLE_MONTHLY_RETURNS:

    print(
        f"Monthly Matrix Shape : "
        f"{monthly_returns.shape}"
    )

print(
    f"Average Coverage     : "
    f"{coverage_analysis['Coverage_Pct'].mean():.2f}%"
)

print(
    f"Matrix Health Score  : "
    f"{matrix_health_score:.2f}"
)

print(
    f"Market Return        : "
    f"{market_statistics['Annualized_Return']:.2%}"
)

print(
    f"Market Volatility    : "
    f"{market_statistics['Annualized_Volatility']:.2%}"
)

print(
    f"VaR (95%)            : "
    f"{var_95:.2%}"
)

print(
    f"CVaR (95%)           : "
    f"{cvar_95:.2%}"
)

print(
    f"Average Correlation  : "
    f"{average_correlation:.4f}"
)

print(
    f"Median Correlation   : "
    f"{median_correlation:.4f}"
)

print(
    "\nOutput Directory:"
)

print(
    OUTPUT_DIR
)

print(
    "=========================================================="
)

# =========================================================
# END OF FILE
# =========================================================