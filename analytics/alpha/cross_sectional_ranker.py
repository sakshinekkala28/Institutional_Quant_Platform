"""
=========================================================
CROSS SECTIONAL RANKER
=========================================================

Institutional Relative Ranking Engine

Output:
data/processed/cross_sectional_rankings.csv
=========================================================
"""

from pathlib import Path

import numpy as np
import pandas as pd

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

FACTOR_FILE = (
    ROOT
    / "data"
    / "processed"
    / "factor_model_rankings.csv"
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
    / "cross_sectional_rankings.csv"
)

# =========================================================
# LOAD
# =========================================================

print("\n📥 Loading Factor Rankings...")

factors = pd.read_csv(
    FACTOR_FILE
)

metadata = pd.read_csv(
    METADATA_FILE
)

# =========================================================
# MERGE
# =========================================================

df = factors.merge(
    metadata[
        [
            "Symbol",
            "Sector",
            "Industry",
        ]
    ],
    on="Symbol",
    how="left",
)

df["Sector"] = (
    df["Sector"]
    .fillna("Unknown")
)

df["Industry"] = (
    df["Industry"]
    .fillna("Unknown")
)

# =========================================================
# GLOBAL PERCENTILE
# =========================================================

df[
    "GLOBAL_PERCENTILE"
] = (
    df[
        "MULTI_FACTOR_SCORE"
    ]
    .rank(
        pct=True
    )
    * 100
)

# =========================================================
# SECTOR PERCENTILE
# =========================================================

df[
    "SECTOR_PERCENTILE"
] = (
    df.groupby(
        "Sector"
    )[
        "MULTI_FACTOR_SCORE"
    ]
    .rank(
        pct=True
    )
    * 100
)

# =========================================================
# INDUSTRY PERCENTILE
# =========================================================

df[
    "INDUSTRY_PERCENTILE"
] = (
    df.groupby(
        "Industry"
    )[
        "MULTI_FACTOR_SCORE"
    ]
    .rank(
        pct=True
    )
    * 100
)

# =========================================================
# Z SCORE
# =========================================================

mean_score = (
    df[
        "MULTI_FACTOR_SCORE"
    ]
    .mean()
)

std_score = (
    df[
        "MULTI_FACTOR_SCORE"
    ]
    .std()
)

if std_score == 0:
    std_score = 1

df["Z_SCORE"] = (
    (
        df[
            "MULTI_FACTOR_SCORE"
        ]
        - mean_score
    )
    / std_score
)

# =========================================================
# ALPHA SCORE
# =========================================================

df["ALPHA_SCORE"] = (
    df["GLOBAL_PERCENTILE"] * 0.50
    +
    df["SECTOR_PERCENTILE"] * 0.30
    +
    df["INDUSTRY_PERCENTILE"] * 0.20
)

# =========================================================
# ALPHA RANK
# =========================================================

df = df.sort_values(
    "ALPHA_SCORE",
    ascending=False,
)

df["ALPHA_RANK"] = range(
    1,
    len(df) + 1,
)

# =========================================================
# ROUND
# =========================================================

round_cols = [
    "GLOBAL_PERCENTILE",
    "SECTOR_PERCENTILE",
    "INDUSTRY_PERCENTILE",
    "Z_SCORE",
    "ALPHA_SCORE",
]

for col in round_cols:

    df[col] = (
        df[col]
        .round(2)
    )

# =========================================================
# SAVE
# =========================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

df.to_csv(
    OUTPUT_FILE,
    index=False,
)

# =========================================================
# REPORT
# =========================================================

print("\n" + "=" * 70)

print(
    "🏁 CROSS SECTIONAL RANKER COMPLETE"
)

print("=" * 70)

print(
    f"Stocks Ranked : {len(df):,}"
)

print(
    f"\nSaved:\n{OUTPUT_FILE}"
)

print("=" * 70)