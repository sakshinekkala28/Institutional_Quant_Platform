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

FACTOR_RETURNS_FILE = (
    ROOT
    / "data"
    / "risk"
    / "factor_returns.parquet"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "risk"
    / "factor_expected_returns.parquet"
)

print(
    "\nLoading Inputs..."
)

B_df = pd.read_parquet(
    EXPOSURE_FILE
)

factor_returns = pd.read_parquet(
    FACTOR_RETURNS_FILE
)

factor_cols = [

    "Momentum",
    "Quality",
    "Value",
    "Growth",
    "Size",
    "Liquidity",
    "LowVol"

]

# ====================================================
# FACTOR PREMIUMS
# ====================================================

HALF_LIFE = 252

weights = np.exp(
    np.log(0.5)
    *
    np.arange(
        len(factor_returns)
    )[::-1]
    /
    HALF_LIFE
)

weights = (
    weights
    /
    weights.sum()
)

factor_premium = pd.Series({

    col:

    np.average(
        factor_returns[col],
        weights=weights
    )

    for col in factor_cols

})

print(
    "\nFactor Premiums:"
)

print(
    factor_premium
)

factor_tstats = pd.Series({

    col:

    factor_returns[col].mean()

    /

    (
        factor_returns[col].std()
        /
        np.sqrt(
            len(factor_returns)
        )
    )

    for col in factor_cols

})

print(
    "\nFactor T-Stats:"
)

print(
    factor_tstats
    .sort_values(
        ascending=False
    )
)

# ====================================================
# FACTOR EXPOSURES
# ====================================================

B = B_df[
    factor_cols
]

# ====================================================
# EXPECTED RETURNS
# ====================================================

confidence_factor = (

    factor_tstats

    .clip(
        lower=0
    )

)

confidence_factor = (

    confidence_factor

    /

    confidence_factor.max()

)

adjusted_premium = (

    factor_premium

    *

    confidence_factor

)

expected_return = (

      0.40 * B_df["Momentum"]

    + 0.20 * B_df["Quality"]

    + 0.15 * B_df["Growth"]

    + 0.10 * B_df["Value"]

    + 0.05 * B_df["Liquidity"]

    - 0.10 * B_df["LowVol"]

)

expected_return_df = pd.DataFrame({

    "Symbol":
        B_df["Symbol"],

    "Alpha_Score":
        expected_return

})

expected_return_df["Expected_Return"] = (

    expected_return_df["Alpha_Score"]

    *

    0.15

)

factor_contribution = pd.DataFrame()

for factor in factor_cols:

    factor_contribution[factor] = (

        B_df[factor]

        *

        factor_premium[factor]

    )

factor_contribution["Symbol"] = (
    B_df["Symbol"]
)

print("\nTOP STOCK FACTOR BREAKDOWN")

top = (
    expected_return_df
    .sort_values(
        "Expected_Return",
        ascending=False
    )
    .head(10)
)

for symbol in top["Symbol"]:

    print("\n", symbol)

    print(

        factor_contribution[
            factor_contribution["Symbol"]
            == symbol
        ]

        .drop(
            columns="Symbol"
        )

        .T

        .sort_values(
            by=factor_contribution[
                factor_contribution["Symbol"]
                == symbol
            ]
            .index[0],
            ascending=False
        )

    )

# ====================================================
# Z-SCORE NORMALIZATION
# ====================================================

mu = (
    expected_return_df
    ["Expected_Return"]
)

expected_return_df[
    "Expected_Return_Z"
] = (

    (
        mu
        -
        mu.mean()
    )

    /

    mu.std()

)

# ==========================================
# CONVERT SCORE TO ANNUALIZED ALPHA
# ==========================================

expected_return_df["Expected_Return"] = (

    0.08

    +

    0.06

    *

    expected_return_df[
        "Expected_Return_Z"
    ]

)

expected_return_df["Expected_Return"] = (

    expected_return_df[
        "Expected_Return"
    ]

    .clip(
        lower=-0.10,
        upper=0.25
    )

)

# ====================================================
# RANK
# ====================================================

expected_return_df[
    "Expected_Return_Rank"
] = (

    expected_return_df[
        "Expected_Return"
    ]

    .rank(
        ascending=False
    )

)

# ====================================================
# SAVE
# ====================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

expected_return_df.to_parquet(
    OUTPUT_FILE,
    index=False
)

print(
    "\nExpected Return Shape:",
    expected_return_df.shape
)

print(
    expected_return_df
    .sort_values(
        "Expected_Return",
        ascending=False
    )
    .head(20)
)