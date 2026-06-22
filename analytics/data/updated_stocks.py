"""
=========================================================
UNIVERSE CONSTRUCTION ENGINE
=========================================================

Purpose:
Create investable universe for quantitative models

Input:
data/raw/symbol_metadata.csv
data/raw/prices/*.parquet

Output:
data/raw/updated_stocks.csv

=========================================================
"""

from pathlib import Path

import pandas as pd

# =========================================================
# CONFIG
# =========================================================

MIN_MARKET_CAP = 100e7      # ₹100 Cr
MIN_PRICE = 20
MIN_ADV = 1e7              # ₹1 Cr
MIN_HISTORY_DAYS = 252
MAX_MISSING_PCT = 0.10

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

METADATA_FILE = (
    ROOT
    / "data"
    / "raw"
    / "symbol_metadata.csv"
)

PRICE_DIR = (
    ROOT
    / "data"
    / "raw"
    / "prices"
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
# LOAD METADATA
# =========================================================

print("\n📥 Loading Symbol Metadata...")

metadata = pd.read_csv(
    METADATA_FILE
)

required_columns = [
    "Symbol",
    "Company_Name",
    "Sector",
    "Industry",
    "Market_Cap",
]

missing = [
    c
    for c in required_columns
    if c not in metadata.columns
]

if missing:

    raise ValueError(
        f"Missing columns in symbol_metadata.csv: {missing}"
    )

metadata["Symbol"] = (
    metadata["Symbol"]
    .astype(str)
    .str.upper()
    .str.strip()
)

metadata["Market_Cap"] = (
    pd.to_numeric(
        metadata["Market_Cap"],
        errors="coerce",
    )
    .fillna(0)
)

initial_count = len(metadata)

print(
    f"Initial Universe : {initial_count:,}"
)

# =========================================================
# BUILD PRICE STATISTICS
# =========================================================

print(
    "\n📊 Building Liquidity Metrics..."
)

stats = []

files = list(
    PRICE_DIR.glob("*.parquet")
)

for idx, file in enumerate(
    files,
    start=1,
):

    try:

        symbol = (
            file.stem.upper()
        )

        df = pd.read_parquet(
            file
        )

        if df.empty:
            continue

        close_col = (
            "Close"
            if "Close" in df.columns
            else "Adj Close"
        )

        close = pd.to_numeric(
            df[close_col],
            errors="coerce",
        )

        volume = pd.to_numeric(
            df["Volume"],
            errors="coerce",
        )

        if close.dropna().empty:
            continue

        last_close = (
            close.dropna()
            .iloc[-1]
        )

        avg_volume = (
            volume.mean()
        )

        stats.append(
            {
                "Symbol": symbol,
                "Last_Close": last_close,
                "Avg_Volume": avg_volume,
                "ADV": (
                    last_close
                    * avg_volume
                ),
                "History_Days": len(df),
                "Missing_Close": (
                    close.isna().mean()
                ),
            }
        )

        if idx % 100 == 0:

            print(
                f"{idx:,}/{len(files):,}"
            )

    except Exception:
        continue

stats = pd.DataFrame(
    stats
)

if stats.empty:

    raise ValueError(
        "No price statistics generated."
    )

print(
    f"Price Files Processed : {len(stats):,}"
)

# =========================================================
# MERGE
# =========================================================

universe = metadata.merge(
    stats,
    on="Symbol",
    how="left",
)

# =========================================================
# REMOVE SYMBOLS WITH NO PRICE DATA
# =========================================================

before = len(universe)

universe = universe.dropna(
    subset=[
        "Last_Close",
        "ADV",
        "History_Days",
    ]
)

no_price_removed = (
    before - len(universe)
)

# =========================================================
# FILTERS
# =========================================================

filter_report = {}

filter_report[
    "No Price Data Removed"
] = no_price_removed

before = len(universe)

universe = universe[
    universe["Market_Cap"]
    >= MIN_MARKET_CAP
]

filter_report[
    "MarketCap Removed"
] = before - len(universe)

before = len(universe)

universe = universe[
    universe["Last_Close"]
    >= MIN_PRICE
]

filter_report[
    "Penny Removed"
] = before - len(universe)

before = len(universe)

universe = universe[
    universe["ADV"]
    >= MIN_ADV
]

filter_report[
    "Liquidity Removed"
] = before - len(universe)

before = len(universe)

universe = universe[
    universe["History_Days"]
    >= MIN_HISTORY_DAYS
]

filter_report[
    "History Removed"
] = before - len(universe)

before = len(universe)

universe = universe[
    universe["Missing_Close"]
    <= MAX_MISSING_PCT
]

filter_report[
    "Data Quality Removed"
] = before - len(universe)

# =========================================================
# FINAL SORT
# =========================================================

universe = (
    universe
    .sort_values(
        [
            "Market_Cap",
            "ADV",
        ],
        ascending=False,
    )
    .reset_index(
        drop=True
    )
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
            *filter_report.keys(),
            "Final Universe",
        ],
        "Value": [
            initial_count,
            *filter_report.values(),
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
# CONSOLE REPORT
# =========================================================

print("\n" + "=" * 70)

print(
    "🏁 UNIVERSE CONSTRUCTION COMPLETE"
)

print("=" * 70)

print(
    f"Initial Universe : {initial_count:,}"
)

for metric, value in filter_report.items():

    print(
        f"{metric:<25}: {value:,}"
    )

print(
    f"Final Universe           : {len(universe):,}"
)

print(
    f"\nSaved:\n{OUTPUT_FILE}"
)

print("=" * 70)