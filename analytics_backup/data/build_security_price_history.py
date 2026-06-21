"""
=========================================================
SECURITY PRICE HISTORY BUILDER
=========================================================

Purpose:
Institutional Historical Price Database Builder

Features:
- Multi-Year Price History
- NSE Equity Universe Download
- Batch Processing
- Retry Logic
- Coverage Reporting
- Failure Tracking
- Data Quality Controls

Input:
data/raw/valid_stocks.xlsx

Output:
data/raw/security_price_history.csv

=========================================================
"""

from pathlib import Path
from datetime import datetime
import time

import numpy as np
import pandas as pd
import yfinance as yf

# =========================================================
# CONFIGURATION
# =========================================================

ENGINE_VERSION = "1.0.0"

START_DATE = "2020-01-01"

BATCH_SIZE = 50

MAX_RETRIES = 3

RETRY_SLEEP_SECONDS = 3

MIN_OBSERVATIONS = 252

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

UNIVERSE_FILE = (
    ROOT
    / "data"
    / "raw"
    / "security_master.csv"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "raw"
    / "security_price_history.csv"
)

COVERAGE_REPORT_FILE = (
    ROOT
    / "data"
    / "logs"
    / "security_price_coverage.csv"
)

FAILURE_REPORT_FILE = (
    ROOT
    / "data"
    / "logs"
    / "security_price_failures.csv"
)

AUDIT_REPORT_FILE = (
    ROOT
    / "data"
    / "logs"
    / "security_price_audit.csv"
)

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

COVERAGE_REPORT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

# =========================================================
# LOAD UNIVERSE
# =========================================================

print(
    "\n📥 Loading Security Universe..."
)

if not UNIVERSE_FILE.exists():

    raise FileNotFoundError(
        f"Missing file: {UNIVERSE_FILE}"
    )

universe = pd.read_csv(
    UNIVERSE_FILE
)

# =========================================================
# SCHEMA VALIDATION
# =========================================================

required_columns = [
    "Symbol"
]

missing_columns = [

    c

    for c in required_columns

    if c not in universe.columns
]

if missing_columns:

    raise ValueError(
        "Missing columns: "
        + ", ".join(missing_columns)
    )

# =========================================================
# CLEAN SYMBOLS
# =========================================================

universe["Symbol"] = (

    universe["Symbol"]

    .astype(str)

    .str.strip()

    .str.upper()
)

universe = universe.dropna(
    subset=["Symbol"]
)

universe = universe[
    universe["Symbol"] != ""
]

universe = universe.drop_duplicates(
    subset=["Symbol"]
)

symbols = sorted(
    universe["Symbol"].unique()
)

# =========================================================
# UNIVERSE SUMMARY
# =========================================================

print(
    f"Universe Size : "
    f"{len(symbols):,}"
)

# =========================================================
# DOWNLOAD HELPERS
# =========================================================

def download_symbol_history(
    symbol: str
) -> pd.DataFrame:

    for attempt in range(MAX_RETRIES):

        try:

            df = yf.download(
                symbol,
                start=START_DATE,
                auto_adjust=False,
                progress=False,
                threads=False
            )

            if df.empty:

                time.sleep(
                    RETRY_SLEEP_SECONDS
                )

                continue

            # Fix yfinance MultiIndex columns

            if isinstance(
                df.columns,
                pd.MultiIndex
            ):

                df.columns = (
                    df.columns
                    .get_level_values(0)
                )

            df = df.reset_index()

            df.columns = [
                str(c).strip()
                for c in df.columns
            ]

            df["Symbol"] = symbol

            return df

        except Exception as e:

            print(
                f"ERROR {symbol}: {e}"
            )

            time.sleep(
                RETRY_SLEEP_SECONDS
            )

    return pd.DataFrame()


def chunk_list(
    items,
    chunk_size
):

    for i in range(
        0,
        len(items),
        chunk_size
    ):

        yield items[
            i:i + chunk_size
        ]


# =========================================================
# DOWNLOAD TRACKERS
# =========================================================

all_prices = []

coverage_records = []

failure_records = []

download_start = datetime.now()

# =========================================================
# BATCH SUMMARY
# =========================================================

total_batches = (

    len(symbols)

    // BATCH_SIZE
)

if len(symbols) % BATCH_SIZE:

    total_batches += 1

print(
    f"Download Batches : "
    f"{total_batches}"
)

# =========================================================
# PART 2 STARTS HERE
# =========================================================
#
# Next:
#
# Batch Downloads
# Coverage Tracking
# Failure Tracking
# Historical Dataset Build
#
# =========================================================

# =========================================================
# BATCH DOWNLOAD ENGINE
# =========================================================

print(
    "\n⬇ Downloading Historical Prices..."
)

batch_number = 0

for batch in chunk_list(
    symbols,
    BATCH_SIZE
):

    batch_number += 1

    print(
        f"\nBatch "
        f"{batch_number:,}"
        f"/"
        f"{total_batches:,}"
    )

    batch_success = 0

    batch_failures = 0

    for symbol in batch:

        try:

            history = (
                download_symbol_history(
                    symbol
                )
            )

            # ----------------------------------
            # FAILED DOWNLOAD
            # ----------------------------------

            if history.empty:

                failure_records.append({

                    "Symbol":
                    symbol,

                    "Failure_Type":
                    "No_Data",

                    "Timestamp":
                    datetime.now()
                })

                batch_failures += 1

                continue

            # ----------------------------------
            # COLUMN STANDARDIZATION
            # ----------------------------------

            rename_map = {}

            for col in history.columns:

                col_str = str(col)

                if "Date" in col_str:
                    rename_map[col] = "Date"

                elif "Open" in col_str:
                    rename_map[col] = "Open"

                elif "High" in col_str:
                    rename_map[col] = "High"

                elif "Low" in col_str:
                    rename_map[col] = "Low"

                elif col_str == "Close":
                    rename_map[col] = "Close"

                elif col_str == "Adj Close":
                    rename_map[col] = "Adj_Close"

                elif "Volume" in col_str:
                    rename_map[col] = "Volume"

            history = history.rename(
                columns=rename_map
            )

            history = history.loc[
                :,
                ~history.columns.duplicated()
            ]

            required_price_cols = [

                "Date",

                "Open",

                "High",

                "Low",

                "Close",

                "Volume",

                "Symbol"
            ]

            missing_cols = [

                c

                for c in required_price_cols

                if c not in history.columns
            ]

            if missing_cols:

                failure_records.append({

                    "Symbol":
                    symbol,

                    "Failure_Type":
                    f"Missing_Columns_{missing_cols}",

                    "Timestamp":
                    datetime.now()
                })

                batch_failures += 1

                continue

            # ----------------------------------
            # DATA CLEANING
            # ----------------------------------

            history["Date"] = pd.to_datetime(
                history["Date"],
                errors="coerce"
            )

            history["Close"] = pd.to_numeric(
                history["Close"],
                errors="coerce"
            )

            history["Volume"] = pd.to_numeric(
                history["Volume"],
                errors="coerce"
            )

            history = history.dropna(
                subset=[
                    "Date",
                    "Close"
                ]
            )

            history = history[
                history["Close"] > 0
            ]

            if history.empty:

                batch_failures += 1

                failure_records.append({

                    "Symbol":
                    symbol,

                    "Failure_Type":
                    "Invalid_Price_Data",

                    "Timestamp":
                    datetime.now()
                })

                continue

            # ----------------------------------
            # COVERAGE TRACKING
            # ----------------------------------

            observation_count = len(
                history
            )

            if observation_count < MIN_OBSERVATIONS:

                batch_failures += 1

                continue

            start_date = (
                history["Date"]
                .min()
            )

            end_date = (
                history["Date"]
                .max()
            )

            coverage_records.append({

                "Symbol":
                symbol,

                "Start_Date":
                start_date,

                "End_Date":
                end_date,

                "Observations":
                observation_count,

                "Coverage_Years":
                observation_count
                / 252,

                "Pass_Min_History":
                observation_count
                >=
                MIN_OBSERVATIONS
            })

            try:

                all_prices.append(
                    history[
                        required_price_cols
                    ]
                )

                batch_success += 1

                if len(all_prices) % 500 == 0:

                    print(
                        f"Loaded {len(all_prices):,} securities..."
                    )

            except Exception as e:

                print(
                    f"APPEND ERROR: {symbol}"
                )

                print(e)

                raise

        except Exception as e:

            print(
                f"\nFAILED SYMBOL: {symbol}"
            )

            print(
                f"ERROR: {e}"
            )

            batch_failures += 1

            failure_records.append({

                "Symbol": symbol,

               "Failure_Type": str(e),

                "Timestamp": datetime.now()
            })

    print(
        f"Batch Success : {batch_success:,}"
    )

    print(
        f"Batch Failed  : {batch_failures:,}"
    )

    print(
        f"Total Loaded  : {len(all_prices):,}"
    )

# =========================================================
# DOWNLOAD COMPLETION CHECK
# =========================================================

if len(all_prices) == 0:

    raise ValueError(
        "No price history downloaded."
    )

# =========================================================
# BUILD MASTER DATASET
# =========================================================

print(
    "\n🏗 Building Master Price Database..."
)

security_prices = pd.concat(

    all_prices,

    ignore_index=True
)

# =========================================================
# DUPLICATE REMOVAL
# =========================================================

duplicate_count = (

    security_prices

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

    security_prices = (

        security_prices

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

security_prices = (

    security_prices

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
# COVERAGE DATAFRAME
# =========================================================

coverage_report = pd.DataFrame(
    coverage_records
)

failure_report = pd.DataFrame(
    failure_records
)

# =========================================================
# ELIGIBLE UNIVERSE
# =========================================================

eligible_symbols = set(

    coverage_report.loc[

        coverage_report[
            "Pass_Min_History"
        ],

        "Symbol"
    ]
)

security_prices = security_prices[

    security_prices[
        "Symbol"
    ]

    .isin(
        eligible_symbols
    )
]

# =========================================================
# SUMMARY
# =========================================================

print(
    f"Downloaded Symbols : "
    f"{coverage_report.shape[0]:,}"
)

print(
    f"Eligible Symbols   : "
    f"{len(eligible_symbols):,}"
)

print(
    f"Price Records      : "
    f"{len(security_prices):,}"
)

print(
    f"Failures           : "
    f"{len(failure_report):,}"
)

# =========================================================
# PART 3 STARTS HERE
# =========================================================
#
# Next:
#
# Data Quality Controls
# Missing Data Analysis
# Price Diagnostics
# Coverage Analytics
# Institutional Validation
#
# =========================================================

# =========================================================
# DATA QUALITY CONTROLS
# =========================================================

print(
    "\n🔍 Running Data Quality Controls..."
)

# =========================================================
# PRICE INTEGRITY CHECKS
# =========================================================

security_prices["Price_Error"] = False

invalid_prices = (

    (security_prices["Open"] <= 0)

    |

    (security_prices["High"] <= 0)

    |

    (security_prices["Low"] <= 0)

    |

    (security_prices["Close"] <= 0)

)

security_prices.loc[
    invalid_prices,
    "Price_Error"
] = True

price_error_count = int(
    invalid_prices.sum()
)

# =========================================================
# OHLC CONSISTENCY CHECK
# =========================================================

security_prices[
    "OHLC_Error"
] = False

ohlc_errors = (

    (security_prices["High"]
     < security_prices["Low"])

    |

    (security_prices["High"]
     < security_prices["Open"])

    |

    (security_prices["High"]
     < security_prices["Close"])

    |

    (security_prices["Low"]
     > security_prices["Open"])

    |

    (security_prices["Low"]
     > security_prices["Close"])

)

security_prices.loc[
    ohlc_errors,
    "OHLC_Error"
] = True

ohlc_error_count = int(
    ohlc_errors.sum()
)

# =========================================================
# VOLUME QUALITY CHECK
# =========================================================

security_prices[
    "Volume_Error"
] = False

volume_errors = (

    security_prices["Volume"]
    < 0

)

security_prices.loc[
    volume_errors,
    "Volume_Error"
] = True

volume_error_count = int(
    volume_errors.sum()
)

# =========================================================
# DAILY RETURN ANALYSIS
# =========================================================

print(
    "📈 Building Return Diagnostics..."
)

security_prices[
    "Daily_Return"
] = (

    security_prices

    .groupby("Symbol")["Close"]

    .pct_change()
)

# =========================================================
# EXTREME RETURN CHECK
# =========================================================

EXTREME_RETURN_LIMIT = 0.50

security_prices[
    "Extreme_Return"
] = (

    security_prices[
        "Daily_Return"
    ]

    .abs()

    >

    EXTREME_RETURN_LIMIT
)

extreme_return_count = int(

    security_prices[
        "Extreme_Return"
    ]

    .sum()
)

# =========================================================
# MISSING DATA ANALYSIS
# =========================================================

print(
    "📊 Building Missing Data Report..."
)

missing_report = (

    security_prices

    .groupby("Symbol")

    .agg({

        "Open":
        lambda x:
        x.isna().sum(),

        "High":
        lambda x:
        x.isna().sum(),

        "Low":
        lambda x:
        x.isna().sum(),

        "Close":
        lambda x:
        x.isna().sum(),

        "Volume":
        lambda x:
        x.isna().sum()

    })

)

missing_report.columns = [

    "Missing_Open",

    "Missing_High",

    "Missing_Low",

    "Missing_Close",

    "Missing_Volume"

]

missing_report = (
    missing_report
    .reset_index()
)

missing_report[
    "Total_Missing"
] = (

    missing_report[
        [
            "Missing_Open",

            "Missing_High",

            "Missing_Low",

            "Missing_Close",

            "Missing_Volume"
        ]
    ]

    .sum(axis=1)
)

# =========================================================
# SECURITY QUALITY METRICS
# =========================================================

print(
    "🏛 Building Security Quality Metrics..."
)

security_quality = (

    security_prices

    .groupby("Symbol")

    .agg({

        "Date":
        "count",

        "Close":
        [
            "mean",
            "std",
            "min",
            "max"
        ],

        "Volume":
        [
            "mean",
            "median"
        ]
    })

)

security_quality.columns = [

    "Observations",

    "Average_Close",

    "Close_Volatility",

    "Min_Close",

    "Max_Close",

    "Average_Volume",

    "Median_Volume"
]

security_quality = (
    security_quality
    .reset_index()
)

# =========================================================
# COVERAGE ANALYTICS
# =========================================================

coverage_report[
    "Coverage_Score"
] = np.where(

    coverage_report[
        "Observations"
    ]

    >=

    5 * 252,

    100,

    (

        coverage_report[
            "Observations"
        ]

        /

        (5 * 252)

    )

    * 100
)

# =========================================================
# QUALITY SCORING
# =========================================================

quality_flags = (

    security_prices

    .groupby("Symbol")

    .agg({

        "Price_Error":
        "sum",

        "OHLC_Error":
        "sum",

        "Volume_Error":
        "sum",

        "Extreme_Return":
        "sum"
    })

)

quality_flags = (
    quality_flags
    .reset_index()
)

quality_flags["Quality_Score"] = (

    100

    - np.minimum(
        quality_flags["Price_Error"],
        5
    ) * 10

    - np.minimum(
        quality_flags["OHLC_Error"],
        5
    ) * 5

    - np.minimum(
        quality_flags["Volume_Error"],
        5
    ) * 2
)

quality_flags[
    "Quality_Score"
] = (

    quality_flags[
        "Quality_Score"
    ]

    .clip(
        lower=0,
        upper=100
    )
)

# =========================================================
# MERGE QUALITY DATA
# =========================================================

security_quality = (

    security_quality

    .merge(

        quality_flags[
            [
                "Symbol",

                "Quality_Score"
            ]
        ],

        on="Symbol",

        how="left"
    )
)

# =========================================================
# DATA QUALITY DASHBOARD
# =========================================================

quality_dashboard = pd.DataFrame({

    "Metric": [

        "Total_Securities",

        "Eligible_Securities",

        "Total_Records",

        "Price_Errors",

        "OHLC_Errors",

        "Volume_Errors",

        "Extreme_Returns",

        "Average_Quality_Score"
    ],

    "Value": [

        coverage_report.shape[0],

        len(
            eligible_symbols
        ),

        len(
            security_prices
        ),

        price_error_count,

        ohlc_error_count,

        volume_error_count,

        extreme_return_count,

        quality_flags[
            "Quality_Score"
        ].mean()
    ]
})

# =========================================================
# VALIDATION
# =========================================================

print(
    "✔ Running Institutional Validation..."
)

if security_prices.empty:

    raise ValueError(
        "Security price database is empty."
    )

if len(
    eligible_symbols
) < 100:

    print(
        "⚠ Universe size appears small."
    )

if quality_flags[
    "Quality_Score"
].mean() < 80:

    print(
        "⚠ Low average quality score."
    )

# =========================================================
# SUMMARY
# =========================================================

print(
    f"Price Errors      : "
    f"{price_error_count:,}"
)

print(
    f"OHLC Errors       : "
    f"{ohlc_error_count:,}"
)

print(
    f"Volume Errors     : "
    f"{volume_error_count:,}"
)

print(
    f"Extreme Returns   : "
    f"{extreme_return_count:,}"
)

print(
    f"Quality Score     : "
    f"{quality_flags['Quality_Score'].mean():.2f}"
)

# =========================================================
# PART 4 STARTS HERE
# =========================================================
#
# Next:
#
# CSV Exports
# Coverage Reports
# Audit Reports
# Dashboard Files
# Production Reporting
#
# =========================================================

# =========================================================
# OUTPUT FILES
# =========================================================

print(
    "\n💾 Saving Outputs..."
)

QUALITY_REPORT_FILE = (
    ROOT
    / "data"
    / "logs"
    / "security_quality_report.csv"
)

QUALITY_DASHBOARD_FILE = (
    ROOT
    / "data"
    / "logs"
    / "quality_dashboard.csv"
)

# =========================================================
# SAVE MASTER DATABASE
# =========================================================

security_prices = (
    security_prices
    .drop(
        columns=[
            "Price_Error",
            "OHLC_Error",
            "Volume_Error",
            "Extreme_Return"
        ],
        errors="ignore"
    )
)

security_prices.to_parquet(
    ROOT / "data/raw/security_price_history.parquet",
    index=False
)

# =========================================================
# SAVE REPORTS
# =========================================================

coverage_report.to_csv(
    COVERAGE_REPORT_FILE,
    index=False
)

failure_report.to_csv(
    FAILURE_REPORT_FILE,
    index=False
)

security_quality.to_csv(
    QUALITY_REPORT_FILE,
    index=False
)

quality_dashboard.to_csv(
    QUALITY_DASHBOARD_FILE,
    index=False
)

# =========================================================
# BUILD AUDIT REPORT
# =========================================================

print(
    "🧾 Building Audit Report..."
)

audit_report = pd.DataFrame({

    "Metric": [

        "Engine_Version",

        "Run_Timestamp",

        "Universe_Size",

        "Downloaded_Securities",

        "Eligible_Securities",

        "Failed_Securities",

        "Total_Records",

        "Price_Errors",

        "OHLC_Errors",

        "Volume_Errors",

        "Extreme_Returns",

        "Average_Quality_Score",

        "Coverage_Score",

        "Database_Start_Date",

        "Database_End_Date"
    ],

    "Value": [

        ENGINE_VERSION,

        datetime.now(),

        len(symbols),

        coverage_report.shape[0],

        len(eligible_symbols),

        len(failure_report),

        len(security_prices),

        price_error_count,

        ohlc_error_count,

        volume_error_count,

        extreme_return_count,

        round(
            quality_flags[
                "Quality_Score"
            ].mean(),
            2
        ),

        round(
            coverage_report[
                "Coverage_Score"
            ].mean(),
            2
        ),

        security_prices[
            "Date"
        ].min(),

        security_prices[
            "Date"
        ].max()
    ]
})

audit_report.to_csv(
    AUDIT_REPORT_FILE,
    index=False
)

# =========================================================
# TOP QUALITY SECURITIES
# =========================================================

top_quality = (

    security_quality

    .sort_values(
        "Quality_Score",
        ascending=False
    )

    .head(25)
)

top_quality.to_csv(

    ROOT
    / "data"
    / "logs"
    / "top_quality_securities.csv",

    index=False
)

# =========================================================
# COVERAGE LEADERS
# =========================================================

coverage_leaders = (

    coverage_report

    .sort_values(
        "Observations",
        ascending=False
    )

    .head(25)
)

coverage_leaders.to_csv(

    ROOT
    / "data"
    / "logs"
    / "coverage_leaders.csv",

    index=False
)

# =========================================================
# FINAL VALIDATION
# =========================================================

print(
    "✔ Running Final Validation..."
)

if security_prices.empty:

    raise ValueError(
        "Security price history is empty."
    )

if len(
    eligible_symbols
) == 0:

    raise ValueError(
        "No eligible securities found."
    )

if (
    security_prices[
        "Close"
    ].isna().all()
):

    raise ValueError(
        "Close prices are empty."
    )

if len(
    security_prices
) < 10000:

    print(
        "⚠ Low record count detected."
    )

# =========================================================
# DOWNLOAD STATISTICS
# =========================================================

runtime_seconds = (

    datetime.now()

    -

    download_start

).total_seconds()

success_rate = (

    len(eligible_symbols)

    /

    max(
        len(symbols),
        1
    )

    * 100
)

# =========================================================
# FINAL REPORTING
# =========================================================

print(
    "\n====================================================="
)

print(
    "🏁 SECURITY PRICE HISTORY BUILDER COMPLETE"
)

print(
    "====================================================="
)

print(
    f"Universe Size       : "
    f"{len(symbols):,}"
)

print(
    f"Downloaded          : "
    f"{coverage_report.shape[0]:,}"
)

print(
    f"Eligible            : "
    f"{len(eligible_symbols):,}"
)

print(
    f"Failures            : "
    f"{len(failure_report):,}"
)

print(
    f"Success Rate        : "
    f"{success_rate:.2f}%"
)

print(
    f"Price Records       : "
    f"{len(security_prices):,}"
)

print(
    f"Price Errors        : "
    f"{price_error_count:,}"
)

print(
    f"OHLC Errors         : "
    f"{ohlc_error_count:,}"
)

print(
    f"Extreme Returns     : "
    f"{extreme_return_count:,}"
)

print(
    f"Avg Quality Score   : "
    f"{quality_flags['Quality_Score'].mean():.2f}"
)

print(
    f"Coverage Score      : "
    f"{coverage_report['Coverage_Score'].mean():.2f}"
)

print(
    f"Runtime (seconds)   : "
    f"{runtime_seconds:,.1f}"
)

print(
    "\nOutput File:"
)

print(
    OUTPUT_FILE
)

print(
    "====================================================="
)

# =========================================================
# END OF FILE
# =========================================================