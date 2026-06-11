"""
=========================================================
LIQUIDITY ENGINE
=========================================================

Institutional Liquidity Ranking

Output:
data/processed/liquidity_scores.csv
=========================================================
"""

from pathlib import Path

import numpy as np
import pandas as pd

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

PRICE_FILE = (
    ROOT
    / "data"
    / "raw"
    / "price_history.csv"
)

METADATA_FILE = (
    ROOT
    / "data"
    / "raw"
    / "stock_metadata.csv"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "processed"
    / "liquidity_scores.csv"
)

# =========================================================
# LOAD
# =========================================================

print("\n📥 Loading Liquidity Data...")

prices = pd.read_csv(
    PRICE_FILE
)

metadata = pd.read_csv(
    METADATA_FILE
)

# =========================================================
# CLEAN
# =========================================================

prices["Date"] = pd.to_datetime(
    prices["Date"]
)

prices = prices.sort_values(
    ["Symbol", "Date"]
)

# =========================================================
# LAST 63 DAYS
# =========================================================

latest_date = prices["Date"].max()

cutoff = latest_date - pd.Timedelta(
    days=90
)

prices = prices[
    prices["Date"] >= cutoff
]

# =========================================================
# ADTV
# =========================================================

prices["TRADED_VALUE"] = (
    prices["Close"]
    * prices["Volume"]
)

# =========================================================
# AGGREGATE
# =========================================================

liquidity = (
    prices.groupby("Symbol")
    .agg(
        AVG_VOLUME=(
            "Volume",
            "mean",
        ),
        VOLUME_STD=(
            "Volume",
            "std",
        ),
        ADTV=(
            "TRADED_VALUE",
            "mean",
        ),
    )
    .reset_index()
)

# =========================================================
# STABILITY
# =========================================================

liquidity["VOLUME_STABILITY"] = (
    liquidity["AVG_VOLUME"]
    /
    liquidity["VOLUME_STD"]
    .replace(
        0,
        np.nan,
    )
)

liquidity[
    "VOLUME_STABILITY"
] = liquidity[
    "VOLUME_STABILITY"
].fillna(0)

# =========================================================
# MARKET CAP
# =========================================================

metadata = metadata[
    [
        "Symbol",
        "Market_Cap",
    ]
]

liquidity = liquidity.merge(
    metadata,
    on="Symbol",
    how="left",
)

liquidity["Market_Cap"] = (
    pd.to_numeric(
        liquidity["Market_Cap"],
        errors="coerce",
    )
    .fillna(0)
)

# =========================================================
# RANKS
# =========================================================

liquidity["ADTV_RANK"] = (
    liquidity["ADTV"]
    .rank(
        pct=True
    )
)

liquidity["MCAP_RANK"] = (
    liquidity["Market_Cap"]
    .rank(
        pct=True
    )
)

liquidity["STABILITY_RANK"] = (
    liquidity["VOLUME_STABILITY"]
    .rank(
        pct=True
    )
)

liquidity["VOLUME_RANK"] = (
    liquidity["AVG_VOLUME"]
    .rank(
        pct=True
    )
)

# =========================================================
# FINAL SCORE
# =========================================================

liquidity["LIQUIDITY_SCORE"] = (
    liquidity["ADTV_RANK"] * 40
    + liquidity["MCAP_RANK"] * 30
    + liquidity["STABILITY_RANK"] * 20
    + liquidity["VOLUME_RANK"] * 10
)

# =========================================================
# SORT
# =========================================================

liquidity = liquidity.sort_values(
    "LIQUIDITY_SCORE",
    ascending=False,
)

liquidity[
    "LIQUIDITY_RANK"
] = range(
    1,
    len(liquidity) + 1,
)

# =========================================================
# ROUND
# =========================================================

numeric_cols = [
    "ADTV",
    "AVG_VOLUME",
    "VOLUME_STABILITY",
    "LIQUIDITY_SCORE",
]

for col in numeric_cols:
    liquidity[col] = (
        liquidity[col]
        .round(2)
    )

# =========================================================
# SAVE
# =========================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

liquidity.to_csv(
    OUTPUT_FILE,
    index=False,
)

# =========================================================
# REPORT
# =========================================================

print("\n" + "=" * 70)

print(
    "🏁 LIQUIDITY ENGINE COMPLETE"
)

print("=" * 70)

print(
    f"Stocks Ranked : {len(liquidity):,}"
)

print(
    f"\nSaved:\n{OUTPUT_FILE}"
)

print("=" * 70)