# =========================================================
# BUILD FACTOR EXPOSURE MATRIX
# Institutional Quant Platform V4
# =========================================================

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
    / "factors"
    / "factor_master.csv"
)

FUNDAMENTAL_FILE = (
    ROOT
    / "data"
    / "factors"
    / "fundamental_factor_master.csv"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "risk"
    / "factor_exposure_matrix.parquet"
)

# =========================================================
# LOAD DATA
# =========================================================

print("\nLoading Factor Data...")

factor_df = pd.read_csv(
    FACTOR_FILE
)

fund_df = pd.read_csv(
    FUNDAMENTAL_FILE
)

# =========================================================
# MERGE
# =========================================================

df = factor_df.merge(
    fund_df,
    on="Symbol",
    how="outer",
    suffixes=("", "_fund")
)

print(
    "Universe:",
    len(df)
)

# =========================================================
# HELPER
# =========================================================

def pct_rank(series):

    return (
        series
        .rank(
            pct=True,
            method="average"
        )
        .fillna(0.50)
    )

# =========================================================
# MOMENTUM
# =========================================================

momentum_cols = [

    "Momentum_1M",
    "Momentum_3M",
    "Momentum_6M",
    "Momentum_12M"

]

for col in momentum_cols:

    if col not in df.columns:

        df[col] = np.nan

df["Momentum"] = (

      0.10 * pct_rank(df["Momentum_1M"])

    + 0.20 * pct_rank(df["Momentum_3M"])

    + 0.30 * pct_rank(df["Momentum_6M"])

    + 0.40 * pct_rank(df["Momentum_12M"])

)

# =========================================================
# QUALITY
# =========================================================

quality_cols = [

    "ROE",
    "ROCE",
    "Operating_Margin"

]

for col in quality_cols:

    if col not in df.columns:

        df[col] = np.nan

quality_matrix = pd.concat(
    [
        pct_rank(df[c])
        for c in quality_cols
    ],
    axis=1
)

df["Quality"] = (
    quality_matrix.mean(axis=1)
)

# =========================================================
# VALUE
# =========================================================

if "PE" not in df.columns:

    df["PE"] = np.nan

pe = df["PE"].where(
    df["PE"] > 0
)

inverse_pe = (
    1 / pe
)

df["Value"] = pct_rank(
    inverse_pe
)

# =========================================================
# GROWTH
# =========================================================

growth_cols = [

    "Revenue_Growth",
    "EPS_Growth",
    "Profit_Growth"

]

for col in growth_cols:

    if col not in df.columns:

        df[col] = np.nan

growth_matrix = pd.concat(
    [
        pct_rank(df[c])
        for c in growth_cols
    ],
    axis=1
)

df["Growth"] = (
    growth_matrix.mean(axis=1)
)

# =========================================================
# SIZE
# =========================================================

if "Log_Market_Cap" in df.columns:

    size_raw = (
        -df["Log_Market_Cap"]
    )

else:

    market_cap = (
        df["Market_Cap"]
        .clip(lower=1)
    )

    size_raw = (
        -np.log(
            market_cap
        )
    )

df["Size"] = pct_rank(
    size_raw
)

# =========================================================
# LIQUIDITY
# =========================================================

if "ADV_20D" not in df.columns:

    df["ADV_20D"] = np.nan

df["Liquidity"] = pct_rank(
    df["ADV_20D"]
)

# =========================================================
# LOW VOL
# =========================================================

vol_col = None

for candidate in [

    "Volatility_252D",
    "Volatility_60D",
    "Volatility_20D"

]:

    if candidate in df.columns:

        vol_col = candidate

        break

if vol_col is None:

    df["LowVol"] = 0.50

else:

    df["LowVol"] = (

        1
        -
        pct_rank(
            df[vol_col]
        )

    )

# =========================================================
# BETA
# =========================================================

if "Beta" not in df.columns:

    df["Beta"] = 1.0

df["Beta"] = (
    df["Beta"]
    .fillna(1.0)
)

# =========================================================
# FINAL MATRIX
# =========================================================

factor_matrix = df[[
    "Symbol",
    "Momentum",
    "Quality",
    "Value",
    "Growth",
    "Size",
    "Liquidity",
    "LowVol",
    "Beta"
]].copy()

# =========================================================
# CLEAN
# =========================================================

factor_cols = [

    "Momentum",
    "Quality",
    "Value",
    "Growth",
    "Size",
    "Liquidity",
    "LowVol"

]

for col in factor_cols:

    factor_matrix[col] = (
        factor_matrix[col]
        .fillna(0.50)
        .clip(0, 1)
    )

factor_matrix = factor_matrix.drop_duplicates(
    subset=["Symbol"]
)

# =========================================================
# SAVE
# =========================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

factor_matrix.to_parquet(
    OUTPUT_FILE,
    index=False
)

print(
    "\nFactor Matrix Shape:",
    factor_matrix.shape
)

print(
    "\nFactor Matrix Head:"
)

print(
    factor_matrix.head()
)

print(
    "\nFactor Summary:"
)

print(
    factor_matrix.describe()
)

print(
    "\nSaved:"
)

print(
    OUTPUT_FILE
)