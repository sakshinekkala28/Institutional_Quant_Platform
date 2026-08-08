"""
====================================================================
Institutional Quant Platform

Factor Expected Returns Engine

Purpose
-------
Estimate forward expected returns from factor exposures and
historical factor premiums.

Inputs
------
data/risk/factor_exposure_matrix.parquet
data/risk/factor_returns.parquet

Output
------
data/risk/factor_expected_returns.parquet

Method
------
1. Calculate exponentially weighted factor premiums.
2. Calculate factor t-statistics.
3. Adjust factor premiums by statistical confidence.
4. Calculate cross-sectional factor alpha score.
5. Convert alpha score into annualized expected return.
6. Normalize expected returns using cross-sectional z-score.
7. Rank securities.

====================================================================
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

# =========================================================
# CONFIGURATION
# =========================================================

HALF_LIFE = 252

BASE_EXPECTED_RETURN = 0.08

EXPECTED_RETURN_SCALE = 0.06

MIN_EXPECTED_RETURN = -0.10

MAX_EXPECTED_RETURN = 0.25

FACTOR_COLS = [
    "Momentum",
    "Quality",
    "Value",
    "Growth",
    "Size",
    "Liquidity",
    "LowVol",
]


# =========================================================
# FACTOR WEIGHTS
# =========================================================

FACTOR_WEIGHTS = {
    "Momentum": 0.40,
    "Quality": 0.20,
    "Growth": 0.15,
    "Value": 0.10,
    "Liquidity": 0.05,
    "LowVol": -0.10,
}


# =========================================================
# PATHS
# =========================================================

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


# =========================================================
# VALIDATION
# =========================================================


def validate_inputs(
    exposure_df: pd.DataFrame,
    factor_returns: pd.DataFrame,
) -> None:
    """
    Validate factor exposure and factor return inputs.
    """

    required_exposure_columns = {
        "Symbol",
        *FACTOR_COLS,
    }

    missing_exposure = (
        required_exposure_columns
        - set(exposure_df.columns)
    )

    if missing_exposure:
        raise ValueError(
            "Missing factor exposure columns: "
            f"{sorted(missing_exposure)}"
        )

    missing_returns = (
        set(FACTOR_COLS)
        - set(factor_returns.columns)
    )

    if missing_returns:
        raise ValueError(
            "Missing factor return columns: "
            f"{sorted(missing_returns)}"
        )

    if exposure_df.empty:
        raise ValueError(
            "Factor exposure matrix is empty."
        )

    if factor_returns.empty:
        raise ValueError(
            "Factor returns dataset is empty."
        )


# =========================================================
# FACTOR PREMIUMS
# =========================================================


def calculate_factor_premiums(
    factor_returns: pd.DataFrame,
) -> pd.Series:
    """
    Calculate exponentially weighted factor premiums.
    """

    observations = len(
        factor_returns
    )

    if observations == 0:
        raise ValueError(
            "Cannot calculate factor premiums "
            "from an empty dataset."
        )

    weights = np.exp(
        np.log(0.5)
        * np.arange(observations)[::-1]
        / HALF_LIFE
    )

    weights = (
        weights
        / weights.sum()
    )

    return


# =========================================================
# FACTOR T-STATS
# =========================================================


def calculate_factor_tstats(
    factor_returns: pd.DataFrame,
) -> pd.Series:
    """
    Calculate factor return t-statistics.
    """

    observations = len(
        factor_returns
    )

    if observations < 2:
        raise ValueError(
            "At least two factor-return observations "
            "are required."
        )

    tstats = {}

    for factor in FACTOR_COLS:

        values = (
            factor_returns[factor]
            .dropna()
            .to_numpy(
                dtype=np.float64
            )
        )

        if len(values) < 2:
            tstats[factor] = 0.0
            continue

        standard_deviation = float(
            np.std(
                values,
                ddof=1,
            )
        )

        if standard_deviation == 0.0:

            tstats[factor] = 0.0

        else:

            tstats[factor] = float(
                np.mean(values)
                / (
                    standard_deviation
                    / np.sqrt(len(values))
                )
            )

    return pd.Series(
        tstats,
        dtype=np.float64,
    )


# =========================================================
# CONFIDENCE ADJUSTMENT
# =========================================================


def calculate_confidence_adjusted_premiums(
    factor_premiums: pd.Series,
    factor_tstats: pd.Series,
) -> pd.Series:
    """
    Adjust factor premiums using positive t-statistic confidence.
    """

    confidence = factor_tstats.clip(
        lower=0.0
    )

    maximum_confidence = float(
        confidence.max()
    )

    if maximum_confidence > 0.0:

        confidence = (
            confidence
            / maximum_confidence
        )

    else:

        confidence = confidence * 0.0

    return (
        factor_premiums
        * confidence
    )


# =========================================================
# ALPHA SCORE
# =========================================================


def calculate_alpha_score(
    exposure_df: pd.DataFrame,
) -> pd.Series:
    """
    Calculate cross-sectional factor alpha score.
    """

    alpha_score = pd.Series(
        0.0,
        index=exposure_df.index,
        dtype=np.float64,
    )

    for factor, weight in FACTOR_WEIGHTS.items():

        alpha_score = (
            alpha_score
            + weight
            * exposure_df[factor].astype(
                np.float64
            )
        )

    return alpha_score


# =========================================================
# FACTOR CONTRIBUTIONS
# =========================================================


def calculate_factor_contributions(
    exposure_df: pd.DataFrame,
    factor_premiums: pd.Series,
) -> pd.DataFrame:
    """
    Calculate per-security factor contribution.
    """

    contributions = pd.DataFrame(
        index=exposure_df.index
    )

    for factor in FACTOR_COLS:

        contributions[factor] = (
            exposure_df[factor]
            * factor_premiums[factor]
        )

    contributions["Symbol"] = (
        exposure_df["Symbol"]
    )

    return contributions


# =========================================================
# EXPECTED RETURN
# =========================================================


def calculate_expected_returns(
    exposure_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Calculate normalized annualized expected returns.
    """

    alpha_score = calculate_alpha_score(
        exposure_df
    )

    expected_returns = pd.DataFrame(
        {
            "Symbol": exposure_df[
                "Symbol"
            ].astype(str),
            "Alpha_Score": alpha_score,
        },
        index=exposure_df.index,
    )

    expected_returns[
        "Expected_Return_Raw"
    ] = (
        expected_returns["Alpha_Score"]
        * 0.15
    )

    raw_returns = expected_returns[
        "Expected_Return_Raw"
    ]

    mean = float(
        raw_returns.mean()
    )

    standard_deviation = float(
        raw_returns.std(
            ddof=1
        )
    )

    if standard_deviation > 0.0:

        expected_returns[
            "Expected_Return_Z"
        ] = (
            raw_returns - mean
        ) / standard_deviation

    else:

        expected_returns[
            "Expected_Return_Z"
        ] = 0.0

    expected_returns[
        "Expected_Return"
    ] = (
        BASE_EXPECTED_RETURN
        + EXPECTED_RETURN_SCALE
        * expected_returns[
            "Expected_Return_Z"
        ]
    )

    expected_returns[
        "Expected_Return"
    ] = expected_returns[
        "Expected_Return"
    ].clip(
        lower=MIN_EXPECTED_RETURN,
        upper=MAX_EXPECTED_RETURN,
    )

    expected_returns[
        "Expected_Return_Rank"
    ] = (
        expected_returns[
            "Expected_Return"
        ]
        .rank(
            ascending=False,
            method="min",
        )
    )

    return expected_returns.reset_index(
        drop=True
    )


# =========================================================
# ENGINE
# =========================================================


def main() -> dict:
    """
    Execute the factor expected returns engine.
    """

    print(
        "\nLoading Factor Expected Return Inputs..."
    )

    if not EXPOSURE_FILE.exists():

        raise FileNotFoundError(
            "Factor exposure file not found: "
            f"{EXPOSURE_FILE}"
        )

    if not FACTOR_RETURNS_FILE.exists():

        raise FileNotFoundError(
            "Factor returns file not found: "
            f"{FACTOR_RETURNS_FILE}"
        )

    exposure_df = pd.read_parquet(
        EXPOSURE_FILE
    )

    factor_returns = pd.read_parquet(
        FACTOR_RETURNS_FILE
    )

    validate_inputs(
        exposure_df,
        factor_returns,
    )

    print(
        f"Exposure Universe : "
        f"{len(exposure_df):,}"
    )

    print(
        f"Factor Observations : "
        f"{len(factor_returns):,}"
    )

    # -----------------------------------------------------
    # FACTOR PREMIUMS
    # -----------------------------------------------------

    factor_premiums = (
        calculate_factor_premiums(
            factor_returns
        )
    )

    print(
        "\nFactor Premiums:"
    )

    print(
        factor_premiums
    )

    # -----------------------------------------------------
    # T-STATS
    # -----------------------------------------------------

    factor_tstats = (
        calculate_factor_tstats(
            factor_returns
        )
    )

    print(
        "\nFactor T-Stats:"
    )

    print(
        factor_tstats.sort_values(
            ascending=False
        )
    )

    # -----------------------------------------------------
    # CONFIDENCE-ADJUSTED PREMIUMS
    # -----------------------------------------------------

    adjusted_premiums = (
        calculate_confidence_adjusted_premiums(
            factor_premiums,
            factor_tstats,
        )
    )

    print(
        "\nConfidence Adjusted Premiums:"
    )

    print(
        adjusted_premiums
    )

    # -----------------------------------------------------
    # EXPECTED RETURNS
    # -----------------------------------------------------

    expected_returns = (
        calculate_expected_returns(
            exposure_df
        )
    )

    # -----------------------------------------------------
    # FACTOR CONTRIBUTIONS
    # -----------------------------------------------------

    factor_contributions = (
        calculate_factor_contributions(
            exposure_df,
            adjusted_premiums,
        )
    )

    # -----------------------------------------------------
    # TOP STOCK BREAKDOWN
    # -----------------------------------------------------

    print(
        "\nTOP STOCK FACTOR BREAKDOWN"
    )

    top = (
        expected_returns
        .sort_values(
            "Expected_Return",
            ascending=False,
        )
        .head(10)
    )

    for symbol in top["Symbol"]:

        print(
            f"\n{symbol}"
        )

        stock_contribution = (
            factor_contributions[
                factor_contributions[
                    "Symbol"
                ]
                == symbol
            ]
            .drop(
                columns="Symbol"
            )
            .T
        )

        print(
            stock_contribution.sort_values(
                by=stock_contribution.columns[0],
                ascending=False,
            )
        )

    # -----------------------------------------------------
    # SAVE
    # -----------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    expected_returns.to_parquet(
        OUTPUT_FILE,
        index=False,
    )

    # -----------------------------------------------------
    # REPORT
    # -----------------------------------------------------

    print(
        "\nExpected Return Shape:",
        expected_returns.shape,
    )

    print(
        expected_returns
        .sort_values(
            "Expected_Return",
            ascending=False,
        )
        .head(20)
    )

    print(
        "\nExpected Return Output:"
    )

    print(
        OUTPUT_FILE
    )

    return {
        "engine": (
            "Factor Expected Returns"
        ),
        "universe_size": len(
            expected_returns
        ),
        "factor_observations": len(
            factor_returns
        ),
        "output_file": str(
            OUTPUT_FILE
        ),
    }


# =========================================================
# CLI
# =========================================================

if __name__ == "__main__":

    main()
