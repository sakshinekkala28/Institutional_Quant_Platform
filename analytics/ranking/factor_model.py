"""
=========================================================
FACTOR MODEL ENGINE
=========================================================

Institutional Multi-Factor Alpha Model

Output:
data/processed/factor_model_rankings.csv
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

LIQUIDITY_FILE = (
    ROOT
    / "data"
    / "processed"
    / "liquidity_scores.csv"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "processed"
    / "factor_model_rankings.csv"
)

# =========================================================
# LOAD
# =========================================================

print("\n📥 Loading Factor Data...")

prices = pd.read_csv(
    PRICE_FILE
)

metadata = pd.read_csv(
    METADATA_FILE
)

liquidity = pd.read_csv(
    LIQUIDITY_FILE
)

# =========================================================
# DATE CLEAN
# =========================================================

prices["Date"] = pd.to_datetime(
    prices["Date"]
)

prices = prices.sort_values(
    ["Symbol", "Date"]
)

# =========================================================
# MOMENTUM CALCULATIONS
# =========================================================

def compute_momentum(group):

    group = group.sort_values(
        "Date"
    )

    latest = group["Close"].iloc[-1]

    result = {}

    # 252 Trading Days

    if len(group) >= 252:

        past_12m = group[
            "Close"
        ].iloc[-252]

        result["MOM_12M"] = (
            (latest / past_12m) - 1
        ) * 100

    else:

        result["MOM_12M"] = 0

    # 126 Trading Days

    if len(group) >= 126:

        past_6m = group[
            "Close"
        ].iloc[-126]

        result["MOM_6M"] = (
            (latest / past_6m) - 1
        ) * 100

    else:

        result["MOM_6M"] = 0

    return pd.Series(result)


factor_df = (
    prices.groupby("Symbol")
    .apply(
        compute_momentum
    )
    .reset_index()
)

# =========================================================
# RELATIVE STRENGTH
# =========================================================

factor_df[
    "RELATIVE_STRENGTH"
] = (
    factor_df["MOM_12M"] * 0.6
    +
    factor_df["MOM_6M"] * 0.4
)

# =========================================================
# MARKET CAP
# =========================================================

factor_df = factor_df.merge(
    metadata[
        [
            "Symbol",
            "Market_Cap",
        ]
    ],
    on="Symbol",
    how="left",
)

factor_df["Market_Cap"] = (
    pd.to_numeric(
        factor_df["Market_Cap"],
        errors="coerce",
    )
    .fillna(0)
)

# =========================================================
# LIQUIDITY
# =========================================================

factor_df = factor_df.merge(
    liquidity[
        [
            "Symbol",
            "LIQUIDITY_SCORE",
        ]
    ],
    on="Symbol",
    how="left",
)

factor_df[
    "LIQUIDITY_SCORE"
] = (
    factor_df[
        "LIQUIDITY_SCORE"
    ]
    .fillna(0)
)

# =========================================================
# RANKS
# =========================================================

factor_df["MOM12_RANK"] = (
    factor_df["MOM_12M"]
    .rank(pct=True)
)

factor_df["MOM6_RANK"] = (
    factor_df["MOM_6M"]
    .rank(pct=True)
)

factor_df["RS_RANK"] = (
    factor_df[
        "RELATIVE_STRENGTH"
    ]
    .rank(pct=True)
)

factor_df["LIQ_RANK"] = (
    factor_df[
        "LIQUIDITY_SCORE"
    ]
    .rank(pct=True)
)

factor_df["MCAP_RANK"] = (
    factor_df[
        "Market_Cap"
    ]
    .rank(pct=True)
)

# =========================================================
# MULTI FACTOR SCORE
# =========================================================

factor_df[
    "MULTI_FACTOR_SCORE"
] = (
    factor_df["MOM12_RANK"] * 30
    +
    factor_df["MOM6_RANK"] * 25
    +
    factor_df["RS_RANK"] * 20
    +
    factor_df["LIQ_RANK"] * 15
    +
    factor_df["MCAP_RANK"] * 10
)

# =========================================================
# SORT
# =========================================================

factor_df = factor_df.sort_values(
    "MULTI_FACTOR_SCORE",
    ascending=False,
)

factor_df[
    "FACTOR_RANK"
] = range(
    1,
    len(factor_df) + 1,
)

# =========================================================
# ROUND
# =========================================================

round_cols = [
    "MOM_12M",
    "MOM_6M",
    "RELATIVE_STRENGTH",
    "MULTI_FACTOR_SCORE",
]

for col in round_cols:

    factor_df[col] = (
        factor_df[col]
        .round(2)
    )

# =========================================================
# SAVE
# =========================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

factor_df.to_csv(
    OUTPUT_FILE,
    index=False,
)

# =========================================================
# REPORT
# =========================================================

print("\n" + "=" * 70)

print(
    "🏁 FACTOR MODEL COMPLETE"
)

print("=" * 70)

print(
    f"Stocks Ranked : {len(factor_df):,}"
)

print(
    f"\nSaved:\n{OUTPUT_FILE}"
)

print("=" * 70)