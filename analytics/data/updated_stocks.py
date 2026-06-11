"""
=========================================================
UNIVERSE CONSTRUCTION ENGINE
=========================================================

Purpose:
Create investable universe from valid_stocks.xlsx

Input:
data/raw/valid_stocks.xlsx
data/raw/symbol_metadata.csv
data/raw/price_history.parquet

Output:
data/raw/updated_stocks.csv

=========================================================
"""

from pathlib import Path

import pandas as pd

# =========================================================
# CONFIG
# =========================================================

MIN_MARKET_CAP = 500e7      # ₹500 Cr

MIN_PRICE = 30

MIN_ADV = 1e7              # ₹1 Cr

MIN_HISTORY_DAYS = 252

MAX_MISSING_PCT = 0.10

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

VALID_STOCKS_FILE = (
    ROOT
    / "data"
    / "raw"
    / "valid_stocks.xlsx"
)

METADATA_FILE = (
    ROOT
    / "data"
    / "raw"
    / "symbol_metadata.csv"
)

PRICE_FILE = (
    ROOT
    / "data"
    / "raw"
    / "price_history.parquet"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "raw"
    / "updated_stocks.csv"
)

REPORT_FILE = (
    ROOT
    / "data"
    / "logs"
    / "universe_report.csv"
)

# =========================================================
# LOAD UNIVERSE
# =========================================================

print("\n📥 Loading Valid Stocks...")

universe = pd.read_excel(
    VALID_STOCKS_FILE
)

# =========================================================
# IDENTIFY SYMBOL COLUMN
# =========================================================

possible_cols = [
    "Symbol",
    "SYMBOL",
    "symbol",
    "Stock",
]

symbol_col = None

for col in possible_cols:

    if col in universe.columns:

        symbol_col = col

        break

if symbol_col is None:

    raise ValueError(
        "Symbol column not found."
    )

universe["Symbol"] = (
    universe[symbol_col]
    .astype(str)
    .str.upper()
    .str.strip()
    .str.replace(".NS", "", regex=False)
)

universe = (
    universe[["Symbol"]]
    .drop_duplicates()
)

initial_count = len(universe)

print(
    f"Initial Universe: {initial_count:,}"
)
# =========================================================
# LOAD METADATA
# =========================================================

print("\n📥 Loading Metadata...")

metadata = pd.read_csv(
    METADATA_FILE
)

metadata["Symbol"] = (
    metadata["Symbol"]
    .astype(str)
    .str.upper()
    .str.strip()
)

metadata["Market_Cap"] = pd.to_numeric(
    metadata["Market_Cap"],
    errors="coerce",
).fillna(0)

# =========================================================
# MERGE METADATA
# =========================================================

universe = universe.merge(
    metadata[
        [
            "Symbol",
            "Company_Name",
            "Sector",
            "Industry",
            "Market_Cap",
        ]
    ],
    on="Symbol",
    how="left",
)

PRICE_DIR = (
    ROOT
    / "data"
    / "raw"
    / "prices"
)

# =========================================================
# BUILD PRICE STATISTICS
# =========================================================

PRICE_DIR = (
    ROOT
    / "data"
    / "raw"
    / "prices"
)

files = list(
    PRICE_DIR.glob("*.parquet")
)

print("\n📊 Building Liquidity Metrics...")

stats = []

files = list(
    PRICE_DIR.glob("*.parquet")
)

for idx, file in enumerate(files, start=1):

    try:

        symbol = file.stem.upper()

        df = pd.read_parquet(file)

        if df.empty:
            continue

        close_col = (
            "Close"
            if "Close" in df.columns
            else "Adj Close"
        )

        volume_col = "Volume"

        df[close_col] = pd.to_numeric(
            df[close_col],
            errors="coerce",
        )

        df[volume_col] = pd.to_numeric(
            df[volume_col],
            errors="coerce",
        )

        last_close = (
            df[close_col]
            .dropna()
            .iloc[-1]
        )

        avg_volume = (
            df[volume_col]
            .mean()
        )

        history_days = len(df)

        missing_close = (
            df[close_col]
            .isna()
            .mean()
        )

        adv = (
            last_close
            * avg_volume
        )

        stats.append(
            {
                "Symbol": symbol,
                "Last_Close": last_close,
                "Avg_Volume": avg_volume,
                "ADV": adv,
                "History_Days": history_days,
                "Missing_Close": missing_close,
            }
        )

        if idx % 100 == 0:

            print(
                f"{idx:,}/{len(files):,}"
            )

    except Exception:
        continue

stats = pd.DataFrame(stats)

# =========================================================
# MERGE
# =========================================================

universe = universe.merge(
    stats,
    on="Symbol",
    how="left",
)

# =========================================================
# FILTER 1
# MARKET CAP
# =========================================================

before = len(universe)

universe = universe[
    universe["Market_Cap"]
    >= MIN_MARKET_CAP
]

marketcap_removed = (
    before - len(universe)
)

# =========================================================
# FILTER 2
# PENNY STOCK
# =========================================================

before = len(universe)

universe = universe[
    universe["Last_Close"]
    >= MIN_PRICE
]

penny_removed = (
    before - len(universe)
)

# =========================================================
# FILTER 3
# LIQUIDITY
# =========================================================

before = len(universe)

universe = universe[
    universe["ADV"]
    >= MIN_ADV
]

liquidity_removed = (
    before - len(universe)
)

# =========================================================
# FILTER 4
# HISTORY
# =========================================================

before = len(universe)

universe = universe[
    universe["History_Days"]
    >= MIN_HISTORY_DAYS
]

history_removed = (
    before - len(universe)
)

# =========================================================
# FILTER 5
# DATA QUALITY
# =========================================================

before = len(universe)

universe = universe[
    universe["Missing_Close"]
    <= MAX_MISSING_PCT
]

quality_removed = (
    before - len(universe)
)

# =========================================================
# FINAL SORT
# =========================================================

universe = (
    universe
    .sort_values(
        "Market_Cap",
        ascending=False,
    )
    .reset_index(drop=True)
)

# =========================================================
# SAVE UNIVERSE
# =========================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

universe.to_csv(
    OUTPUT_FILE,
    index=False,
)

# =========================================================
# REPORT
# =========================================================

report = pd.DataFrame(
    {
        "Metric": [
            "Initial Universe",
            "MarketCap Removed",
            "Penny Removed",
            "Liquidity Removed",
            "History Removed",
            "Data Quality Removed",
            "Final Universe",
        ],
        "Value": [
            initial_count,
            marketcap_removed,
            penny_removed,
            liquidity_removed,
            history_removed,
            quality_removed,
            len(universe),
        ],
    }
)

REPORT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

report.to_csv(
    REPORT_FILE,
    index=False,
)

# =========================================================
# REPORT
# =========================================================

print("\n" + "=" * 70)

print(
    "🏁 UNIVERSE CONSTRUCTION COMPLETE"
)

print("=" * 70)

print(
    f"Initial Universe : {initial_count:,}"
)

print(
    f"Final Universe   : {len(universe):,}"
)

print(
    f"MarketCap Filter : {marketcap_removed:,}"
)

print(
    f"Penny Filter     : {penny_removed:,}"
)

print(
    f"Liquidity Filter : {liquidity_removed:,}"
)

print(
    f"History Filter   : {history_removed:,}"
)

print(
    f"Quality Filter   : {quality_removed:,}"
)

print(
    f"\nSaved:\n{OUTPUT_FILE}"
)

print("=" * 70)