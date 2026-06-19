# =========================================================
# BUILD BETA MASTER V2.0
# =========================================================

from pathlib import Path

import numpy as np
import pandas as pd
import yfinance as yf

# =========================================================
# PATHS
# =========================================================

ROOT_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    ROOT_DIR
    / "data"
    / "raw"
    / "security_master.csv"
)

OUTPUT_FILE = (
    ROOT_DIR
    / "data"
    / "risk"
    / "beta_master.csv"
)

# =========================================================
# SETTINGS
# =========================================================

LOOKBACK_PERIOD = "3y"

MIN_OBSERVATIONS = 252

DEFAULT_BETA = 1.0

BETA_FLOOR = 0.25

BETA_CAP = 3.00

BENCHMARK = "^NSEI"

SHRINKAGE_WEIGHT = 0.33

# =========================================================
# LOAD UNIVERSE
# =========================================================

print("\n📥 Loading Security Master...")

universe = pd.read_csv(
    INPUT_FILE
)

required_cols = [

    "Symbol",

    "Yahoo_Symbol"

]

for col in required_cols:

    if col not in universe.columns:

        raise ValueError(
            f"Missing column: {col}"
        )

symbols_df = (

    universe[
        ["Symbol", "Yahoo_Symbol"]
    ]

    .dropna()

    .drop_duplicates()

)

symbol_map = dict(

    zip(

        symbols_df["Yahoo_Symbol"],

        symbols_df["Symbol"]

    )

)

symbols = (

    symbols_df[
        "Yahoo_Symbol"
    ]

    .tolist()

)

print(
    f"Universe Size: {len(symbols)}"
)

# =========================================================
# DOWNLOAD BENCHMARK
# =========================================================

print(
    "\n📈 Downloading Benchmark..."
)

benchmark = yf.download(

    BENCHMARK,

    period=LOOKBACK_PERIOD,

    auto_adjust=True,

    progress=False

)

if benchmark.empty:

    raise ValueError(
        "Benchmark download failed."
    )

benchmark_close = (

    benchmark["Close"]

    .squeeze()

)

benchmark_returns = (

    benchmark_close

    .pct_change()

    .dropna()

)

print(
    f"Benchmark Observations: {len(benchmark_returns)}"
)

# =========================================================
# DOWNLOAD STOCK UNIVERSE
# =========================================================

print(
    "\n📈 Downloading Stock Universe..."
)

price_data = yf.download(

    symbols,

    period=LOOKBACK_PERIOD,

    auto_adjust=True,

    threads=True,

    group_by="ticker",

    progress=False

)

print(
    "✓ Stock Universe Downloaded"
)

# =========================================================
# BETA CALCULATOR
# =========================================================

def calculate_beta(

    stock_returns,

    benchmark_returns

):

    merged = pd.concat(

        [

            stock_returns,

            benchmark_returns

        ],

        axis=1,

        join="inner"

    ).dropna()

    if len(merged) < MIN_OBSERVATIONS:

        return DEFAULT_BETA

    stock = merged.iloc[:, 0]

    bench = merged.iloc[:, 1]

    bench_var = bench.var()

    if bench_var <= 0:

        return DEFAULT_BETA

    beta = (

        stock.cov(bench)

        /

        bench_var

    )

    if pd.isna(beta):

        return DEFAULT_BETA

    return float(beta)

# =========================================================
# BUILD BETA MASTER
# =========================================================

print(
    "\n⚙ Building Betas..."
)

results = []

failed_symbols = []

for i, symbol in enumerate(symbols, start=1):

    try:

        close = (

            price_data

            [symbol]

            ["Close"]

        )

        returns = (

            close

            .pct_change()

            .dropna()

        )

        raw_beta = calculate_beta(

            returns,

            benchmark_returns

        )

        # =====================================
        # BAYESIAN SHRINKAGE
        # =====================================

        beta = (

            (1 - SHRINKAGE_WEIGHT)

            * raw_beta

            +

            SHRINKAGE_WEIGHT

            * 1.0

        )

        results.append({

            "Symbol":
            symbol_map.get(
                symbol,
                symbol
            ),

            "Yahoo_Symbol":
            symbol,

            "Raw_Beta":
            round(
                raw_beta,
                4
            ),

            "Beta":
            round(
                beta,
                4
            ),

            "Observation_Count":
            len(
                returns
            )

        })

        if i % 100 == 0:

            print(
                f"Processed {i}/{len(symbols)}"
            )

    except Exception as e:

        failed_symbols.append(
            symbol
        )

        print(
            f"Failed: {symbol}"
        )

        print(e)

        results.append({

            "Symbol":
            symbol_map.get(
                symbol,
                symbol
            ),

            "Yahoo_Symbol":
            symbol,

            "Raw_Beta":
            DEFAULT_BETA,

            "Beta":
            DEFAULT_BETA,

            "Observation_Count":
            0

        })

# =========================================================
# DATAFRAME
# =========================================================

beta_df = pd.DataFrame(
    results
)

# =========================================================
# CLEANING
# =========================================================

beta_df["Beta"] = (

    beta_df["Beta"]

    .replace(
        [np.inf, -np.inf],
        np.nan
    )

    .fillna(
        DEFAULT_BETA
    )

)

beta_df["Beta"] = (

    beta_df["Beta"]

    .clip(

        lower=BETA_FLOOR,

        upper=BETA_CAP

    )

)

# =========================================================
# QUALITY CONTROL
# =========================================================

print(
    "\n📊 BETA QC"
)

print(

    beta_df["Beta"]

    .describe()

)

print(
    "\n🔺 TOP BETAS"
)

print(

    beta_df

    .sort_values(

        "Beta",

        ascending=False

    )

    .head(10)

)

print(
    "\n🔻 LOWEST BETAS"
)

print(

    beta_df

    .sort_values(

        "Beta"

    )

    .head(10)

)

print(
    "\nFailed Symbols:",
    len(failed_symbols)
)

if failed_symbols:

    pd.DataFrame({

        "Yahoo_Symbol":
        failed_symbols

    }).to_csv(

        ROOT_DIR
        / "data"
        / "risk"
        / "beta_failures.csv",

        index=False

    )
# =========================================================
# SAVE
# =========================================================

OUTPUT_FILE.parent.mkdir(

    parents=True,

    exist_ok=True

)

beta_df.to_csv(

    OUTPUT_FILE,

    index=False

)

print(
    f"\n✓ Saved: {OUTPUT_FILE}"
)

print(
    f"Total Stocks: {len(beta_df)}"
)

print(
    "\n🏁 Beta Master Build Complete"
)