"""
=========================================================
FACTOR EXPOSURE MONITOR
=========================================================

Purpose
-------
Portfolio Factor Exposure Monitoring

Calculates:

• Factor Exposures
• Factor Concentration
• Factor HHI
• Effective Factors
• Dominant Factor

Not a covariance-based risk model.

=========================================================
"""

from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd

# =========================================================
# CONFIG
# =========================================================

ENGINE_VERSION = "1.0.0"

FACTOR_LIST = [

    "Momentum",
    "Quality",
    "Value",
    "Low_Vol",
    "Size",
]

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

PORTFOLIO_FILE = (
    ROOT
    / "data"
    / "portfolios"
    / "live_portfolio.csv"
)

FACTOR_DIR = (
    ROOT
    / "data"
    / "factors"
)

OUTPUT_DIR = (
    ROOT
    / "data"
    / "risk"
)

REPORT_FILE = (
    ROOT
    / "data"
    / "logs"
    / "factor_risk_report.csv"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

print(
    "\n📥 Loading Inputs..."
)

portfolio = pd.read_csv(
    PORTFOLIO_FILE
)

portfolio["Weight"] = (

    portfolio["Weight"]

    /

    portfolio["Weight"].sum()
)

factor_files = {

    "Momentum":
    "momentum_scores.csv",

    "Quality":
    "quality_scores.csv",

    "Value":
    "value_scores.csv",

    "Low_Vol":
    "low_vol_scores.csv",

    "Size":
    "size_scores.csv",
}

factor_data = []

for factor, file_name in factor_files.items():

    file = (
        FACTOR_DIR
        / file_name
    )

    if not file.exists():

        raise FileNotFoundError(
            file
        )

    df = pd.read_csv(
        file
    )

    score_col = [

        c

        for c in df.columns

        if "score"
        in c.lower()
    ][0]

    tmp = df[
        [
            "Symbol",
            score_col
        ]
    ].copy()

    tmp.columns = [

        "Symbol",

        factor
    ]

    factor_data.append(
        tmp
    )

factor_master = factor_data[0]

for df in factor_data[1:]:

    factor_master = factor_master.merge(

        df,

        on="Symbol",

        how="outer"
    )

portfolio_factor = portfolio.merge(

    factor_master,

    on="Symbol",

    how="left"
)

portfolio_factor = (
    portfolio_factor.fillna(0)
)

exposures = {}

for factor in FACTOR_LIST:

    exposures[factor] = (

        portfolio_factor[
            "Weight"
        ]

        *

        portfolio_factor[
            factor
        ]

    ).sum()

factor_exposure = pd.DataFrame({

    "Factor":
    list(
        exposures.keys()
    ),

    "Exposure":
    list(
        exposures.values()
    )
})
factor_exposure[
    "Abs_Exposure"
] = factor_exposure[
    "Exposure"
].abs()

total_abs = max(

    factor_exposure[
        "Abs_Exposure"
    ].sum(),

    1e-9
)

factor_exposure[
    "Contribution_Pct"
] = (

    factor_exposure[
        "Abs_Exposure"
    ]

    /

    total_abs

    * 100
)

factor_contributions = (
    factor_exposure.copy()
)

corr = factor_master[

    FACTOR_LIST

].corr()

corr.to_csv(

    OUTPUT_DIR
    / "factor_correlation.csv"
)

hhi = (

    factor_exposure[
        "Contribution_Pct"
    ]

    / 100

) ** 2

factor_hhi = hhi.sum()

effective_factors = (

    1

    /

    max(
        factor_hhi,
        1e-9
    )
)

risk_score = (

    factor_exposure[
        "Exposure"
    ]

    .abs()

    .mean()

    * 100
)

risk_score = min(
    risk_score,
    100
)

dominant_factor = (

    factor_exposure

    .sort_values(

        "Abs_Exposure",

        ascending=False,
    )

    .iloc[0]

    ["Factor"]
)

summary = pd.DataFrame({

    "Metric": [

        "Dominant_Factor",

        "Factor_Risk_Score",

        "Factor_HHI",

        "Effective_Factors",

        "Run_Date",

        "Engine_Version",
    ],

    "Value": [

        dominant_factor,

        risk_score,

        factor_hhi,

        effective_factors,

        datetime.now()
        .strftime(
            "%Y-%m-%d"
        ),

        ENGINE_VERSION,
    ]
})

factor_exposure.to_csv(

    OUTPUT_DIR
    / "factor_exposures.csv",

    index=False,
)

factor_contributions.to_csv(

    OUTPUT_DIR
    / "factor_contributions.csv",

    index=False,
)

summary.to_csv(

    OUTPUT_DIR
    / "factor_risk_summary.csv",

    index=False,
)

summary.to_csv(

    REPORT_FILE,

    index=False,
)

print("\n" + "=" * 70)

print(
    "🏁 FACTOR RISK MODEL COMPLETE"
)

print("=" * 70)

print(
    f"Dominant Factor : "
    f"{dominant_factor}"
)

print(
    f"Risk Score      : "
    f"{risk_score:.2f}"
)

print(
    f"Factor HHI      : "
    f"{factor_hhi:.4f}"
)

print(
    f"Effective Factors : "
    f"{effective_factors:.2f}"
)

print("=" * 70)