from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[2]

EXPOSURE_FILE = (
    ROOT
    / "data"
    / "risk"
    / "factor_exposure_matrix.parquet"
)

RETURNS_FILE = (
    ROOT
    / "data"
    / "risk"
    / "daily_returns.parquet"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "risk"
    / "factor_returns.parquet"
)

FACTORS = [

    "Momentum",
    "Quality",
    "Value",
    "Growth",
    "Size",
    "Liquidity",
    "LowVol"

]

print("Loading Data...")

factor_exp = pd.read_parquet(
    EXPOSURE_FILE
)

returns_df = pd.read_parquet(
    RETURNS_FILE
)

print(
    "Exposures:",
    factor_exp.shape
)

print(
    "Returns:",
    returns_df.shape
)

# ====================================================
# SYMBOL STANDARDIZATION
# ====================================================

returns_df["Symbol"] = (
    returns_df["Symbol"]
    .astype(str)
    .str.upper()
    .str.strip()
    .str.replace(
        ".NS",
        "",
        regex=False
    )
)

factor_exp["Symbol"] = (
    factor_exp["Symbol"]
    .astype(str)
    .str.upper()
    .str.strip()
)

common_symbols = set(
    returns_df["Symbol"]
).intersection(
    set(factor_exp["Symbol"])
)

print(
    "\nCommon Symbols:",
    len(common_symbols)
)

print(
    "Returns Symbols:",
    returns_df["Symbol"].nunique()
)

print(
    "Exposure Symbols:",
    factor_exp["Symbol"].nunique()
)

factor_return_rows = []

dates = sorted(
    returns_df["Date"].unique()
)

for dt in dates:

    daily_returns = (
        returns_df[
            returns_df["Date"] == dt
        ]
    )

    merged = daily_returns.merge(
        factor_exp,
        on="Symbol",
        how="inner"
    )

    if len(merged) < 50:
        continue

    row = {
        "Date": dt
    }

    for factor in FACTORS:

        q80 = (
            merged[factor]
            .quantile(0.80)
        )

        q20 = (
            merged[factor]
            .quantile(0.20)
        )

        long_leg = merged[
            merged[factor] >= q80
        ]

        short_leg = merged[
            merged[factor] <= q20
        ]

        long_return = (
            long_leg["Return"]
            .mean()
        )

        short_return = (
            short_leg["Return"]
            .mean()
        )

        factor_return = (
            long_return
            -
            short_return
        )

        row[factor] = factor_return

    factor_return_rows.append(
        row
    )

factor_returns = pd.DataFrame(
    factor_return_rows
)

if factor_returns.empty:

    raise ValueError(
        "\nNo factor returns generated.\n"
        "Likely Symbol mismatch between\n"
        "daily_returns and factor_exposure_matrix."
    )

factor_returns = (
    factor_returns
    .sort_values("Date")
)

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

factor_returns.to_parquet(
    OUTPUT_FILE,
    index=False
)

print(
    "\nFactor Returns Shape:",
    factor_returns.shape
)

print(
    factor_returns.head()
)

print(
    factor_returns.describe()
)