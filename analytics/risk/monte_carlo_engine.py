"""
=========================================================
FACTOR RISK MODEL
=========================================================

Purpose:
Institutional Multi-Factor Risk Analytics

Inputs:
data/portfolios/live_portfolio.csv
data/factors/factor_master.csv

Outputs:
data/risk/factor_exposures.csv
data/risk/factor_sector_exposure.csv
data/risk/factor_concentration.csv
data/risk/factor_risk_summary.csv
data/risk/factor_dashboard.csv

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

MIN_SECURITIES = 20

FACTOR_COLUMNS = [

    "Momentum_1M",
    "Momentum_3M",
    "Momentum_6M",
    "Momentum_12M",

    "Volatility_20D",
    "Volatility_60D",

    "ATR_14",

    "Max_Drawdown_252D",

    "Distance_SMA50",
    "Distance_SMA200",
    "Distance_52W_High",

    "ADV_20D",
    "Dollar_Volume",

    "Log_Market_Cap",
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

FACTOR_FILE = (
    ROOT
    / "data"
    / "factors"
    / "factor_master.csv"
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

# =========================================================
# LOAD DATA
# =========================================================

print(
    "\n📥 Loading Inputs..."
)

portfolio = pd.read_csv(
    PORTFOLIO_FILE
)

factor_master = pd.read_csv(
    FACTOR_FILE
)

# =========================================================
# VALIDATION
# =========================================================

if portfolio.empty:

    raise ValueError(
        "Portfolio file empty"
    )

if factor_master.empty:

    raise ValueError(
        "Factor master file empty"
    )

required_portfolio = [

    "Symbol",
    "Weight",
    "Sector",
]

required_factor = [

    "Symbol",

    "Sector",

    "Log_Market_Cap",

    "Momentum_1M",
    "Momentum_3M",
    "Momentum_6M",
    "Momentum_12M",

    "Volatility_20D",
    "Volatility_60D",

    "ATR_14",

    "Max_Drawdown_252D",

    "Distance_SMA50",
    "Distance_SMA200",
    "Distance_52W_High",

    "ADV_20D",
    "Dollar_Volume",
]

for col in required_portfolio:

    if col not in portfolio.columns:

        raise ValueError(
            f"Missing Portfolio Column: {col}"
        )

for col in required_factor:

    if col not in factor_master.columns:

        raise ValueError(
            f"Missing Factor Column: {col}"
        )

if len(portfolio) < MIN_SECURITIES:

    raise ValueError(
        f"Portfolio contains "
        f"{len(portfolio)} securities. "
        f"Minimum required: "
        f"{MIN_SECURITIES}"
    )

# =========================================================
# CLEAN PORTFOLIO
# =========================================================

portfolio["Weight"] = pd.to_numeric(

    portfolio["Weight"],

    errors="coerce"
)

portfolio = portfolio.dropna(
    subset=["Weight"]
)

portfolio["Weight"] = (

    portfolio["Weight"]

    /

    portfolio["Weight"].sum()
)

# =========================================================
# CLEAN FACTOR DATA
# =========================================================

for col in FACTOR_COLUMNS:

    factor_master[col] = pd.to_numeric(

        factor_master[col],

        errors="coerce"
    )

factor_master = factor_master.replace(

    [
        np.inf,
        -np.inf,
    ],

    np.nan
)

# =========================================================
# MERGE PORTFOLIO + FACTORS
# =========================================================

portfolio_factor = portfolio.merge(

    factor_master,

    on="Symbol",

    how="left",

    suffixes=(
        "",
        "_factor"
    )
)

# =========================================================
# COVERAGE CHECK
# =========================================================

coverage = (

    portfolio_factor[
        "Log_Market_Cap"
    ]

    .notna()

    .mean()
)

if coverage < 0.90:

    raise ValueError(

        "Factor coverage too low: "

        f"{coverage:.2%}"
    )

print(
    f"Factor Coverage : "
    f"{coverage:.2%}"
)

# =========================================================
# DIAGNOSTICS
# =========================================================

print(
    f"Portfolio Holdings : "
    f"{len(portfolio)}"
)

print(
    f"Factor Universe    : "
    f"{len(factor_master)}"
)

print(
    f"Merged Holdings    : "
    f"{len(portfolio_factor)}"
)

# =========================================================
# PART 2 STARTS HERE
# =========================================================
#
# Next:
#
# Momentum Factor
# Low Vol Factor
# Size Factor
# Liquidity Factor
# Trend Factor
#
# Factor Standardization
#
# =========================================================

# =========================================================
# FACTOR CONSTRUCTION
# =========================================================

print(
    "\n📊 Building Factor Model..."
)

# =========================================================
# WINSORIZATION FUNCTION
# =========================================================

def winsorize_series(
    series,
    lower=0.01,
    upper=0.99,
):

    if series.notna().sum() == 0:

        return series

    low = series.quantile(
        lower
    )

    high = series.quantile(
        upper
    )

    return series.clip(
        lower=low,
        upper=high
    )

# =========================================================
# Z-SCORE FUNCTION
# =========================================================

def zscore(
    series
):

    std = series.std()

    if (
        pd.isna(std)
        or std == 0
    ):

        return pd.Series(
            0,
            index=series.index
        )

    return (

        series
        -
        series.mean()

    ) / std

# =========================================================
# WINSORIZE RAW FACTORS
# =========================================================

for col in FACTOR_COLUMNS:

    portfolio_factor[col] = (
        winsorize_series(
            portfolio_factor[col]
        )
    )

# =========================================================
# MOMENTUM FACTOR
# =========================================================

portfolio_factor[
    "Momentum_Factor"
] = (

    portfolio_factor[
        "Momentum_1M"
    ]

    +

    portfolio_factor[
        "Momentum_3M"
    ]

    +

    portfolio_factor[
        "Momentum_6M"
    ]

    +

    portfolio_factor[
        "Momentum_12M"
    ]

) / 4

# =========================================================
# LOW VOL FACTOR
# =========================================================

portfolio_factor[
    "LowVol_Factor"
] = -(

    portfolio_factor[
        "Volatility_20D"
    ]

    +

    portfolio_factor[
        "Volatility_60D"
    ]

    +

    portfolio_factor[
        "ATR_14"
    ]

    +

    portfolio_factor[
        "Max_Drawdown_252D"
    ].abs()

) / 4

# =========================================================
# SIZE FACTOR
# =========================================================

portfolio_factor[
    "Size_Factor"
] = -(

    portfolio_factor[
        "Log_Market_Cap"
    ]
)

# =========================================================
# LIQUIDITY FACTOR
# =========================================================

portfolio_factor[
    "Liquidity_Factor"
] = (

    np.log1p(

        portfolio_factor[
            "ADV_20D"
        ]

    )

    +

    np.log1p(

        portfolio_factor[
            "Dollar_Volume"
        ]

    )

) / 2

# =========================================================
# TREND FACTOR
# =========================================================

portfolio_factor[
    "Trend_Factor"
] = (

    portfolio_factor[
        "Distance_SMA50"
    ]

    +

    portfolio_factor[
        "Distance_SMA200"
    ]

    +

    portfolio_factor[
        "Distance_52W_High"
    ]

) / 3

# =========================================================
# STANDARDIZE FACTORS
# =========================================================

factor_names = [

    "Momentum_Factor",

    "LowVol_Factor",

    "Size_Factor",

    "Liquidity_Factor",

    "Trend_Factor",
]

for factor in factor_names:

    portfolio_factor[
        factor
    ] = zscore(

        portfolio_factor[
            factor
        ]
    )

# =========================================================
# FACTOR MATRIX
# =========================================================

factor_matrix = portfolio_factor[[

    "Symbol",

    "Sector",

    "Weight",

    "Momentum_Factor",

    "LowVol_Factor",

    "Size_Factor",

    "Liquidity_Factor",

    "Trend_Factor",
]].copy()

# =========================================================
# FACTOR CORRELATION
# =========================================================

factor_correlation = (

    factor_matrix[

        [

            "Momentum_Factor",

            "LowVol_Factor",

            "Size_Factor",

            "Liquidity_Factor",

            "Trend_Factor",
        ]

    ]

    .corr()
)

factor_correlation.to_csv(

    OUTPUT_DIR
    / "factor_correlation.csv"
)

# =========================================================
# DIAGNOSTICS
# =========================================================

print(
    "\nFactors Built:"
)

for factor in factor_names:

    print(
        f"✓ {factor}"
    )

print(
    "\nCorrelation Matrix Saved"
)

# =========================================================
# PART 3 STARTS HERE
# =========================================================
#
# Next:
#
# Portfolio Factor Exposure
# Sector Factor Exposure
# Factor Contribution
# Factor Crowding
#
# =========================================================
# =========================================================
# PORTFOLIO FACTOR EXPOSURES
# =========================================================

print(
    "\n📈 Calculating Factor Exposures..."
)

factor_columns = [

    "Momentum_Factor",

    "LowVol_Factor",

    "Size_Factor",

    "Liquidity_Factor",

    "Trend_Factor",
]

exposures = []

for factor in factor_columns:

    exposure = (

        portfolio_factor[
            "Weight"
        ]

        *

        portfolio_factor[
            factor
        ]

    ).sum()

    exposures.append({

        "Factor":
        factor.replace(
            "_Factor",
            ""
        ),

        "Exposure":
        exposure,
    })

factor_exposures = pd.DataFrame(
    exposures
)

# =========================================================
# ABS EXPOSURES
# =========================================================

factor_exposures[
    "Abs_Exposure"
] = (

    factor_exposures[
        "Exposure"
    ].abs()
)

total_abs_exposure = max(

    factor_exposures[
        "Abs_Exposure"
    ].sum(),

    1e-9,
)

factor_exposures[
    "Contribution_Pct"
] = (

    factor_exposures[
        "Abs_Exposure"
    ]

    /

    total_abs_exposure

    * 100
)

# =========================================================
# RANK FACTORS
# =========================================================

factor_exposures = (

    factor_exposures

    .sort_values(

        "Abs_Exposure",

        ascending=False,
    )

    .reset_index(
        drop=True
    )
)

factor_exposures[
    "Factor_Rank"
] = (
    factor_exposures.index + 1
)

# =========================================================
# DOMINANT FACTOR
# =========================================================

dominant_factor = (

    factor_exposures

    .iloc[0]

    ["Factor"]
)

dominant_exposure = (

    factor_exposures

    .iloc[0]

    ["Exposure"]
)

# =========================================================
# SECTOR FACTOR EXPOSURE
# =========================================================

print(
    "\n🏭 Building Sector Exposures..."
)

sector_exposure = (

    portfolio_factor

    .groupby(
        "Sector"
    )

    .apply(

        lambda x: pd.Series({

            "Portfolio_Weight":

                x[
                    "Weight"
                ].sum(),

            "Momentum_Exposure":

                (
                    x["Weight"]

                    *

                    x[
                        "Momentum_Factor"
                    ]
                ).sum(),

            "LowVol_Exposure":

                (
                    x["Weight"]

                    *

                    x[
                        "LowVol_Factor"
                    ]
                ).sum(),

            "Size_Exposure":

                (
                    x["Weight"]

                    *

                    x[
                        "Size_Factor"
                    ]
                ).sum(),

            "Liquidity_Exposure":

                (
                    x["Weight"]

                    *

                    x[
                        "Liquidity_Factor"
                    ]
                ).sum(),

            "Trend_Exposure":

                (
                    x["Weight"]

                    *

                    x[
                        "Trend_Factor"
                    ]
                ).sum(),
        })

    )

    .reset_index()
)

# =========================================================
# SECTOR CROWDING SCORE
# =========================================================

sector_exposure[
    "Crowding_Score"
] = (

    sector_exposure[

        [

            "Momentum_Exposure",

            "LowVol_Exposure",

            "Size_Exposure",

            "Liquidity_Exposure",

            "Trend_Exposure",
        ]

    ]

    .abs()

    .sum(axis=1)
)

sector_exposure = (

    sector_exposure

    .sort_values(

        "Crowding_Score",

        ascending=False,
    )

    .reset_index(
        drop=True
    )
)

sector_exposure[
    "Crowding_Rank"
] = (
    sector_exposure.index + 1
)

# =========================================================
# MOST CROWDED SECTOR
# =========================================================

most_crowded_sector = (

    sector_exposure

    .iloc[0]

    ["Sector"]
)

# =========================================================
# FACTOR CONTRIBUTION TABLE
# =========================================================

factor_contributions = factor_exposures[[

    "Factor",

    "Exposure",

    "Abs_Exposure",

    "Contribution_Pct",

    "Factor_Rank",
]].copy()

# =========================================================
# FACTOR DASHBOARD
# =========================================================

factor_dashboard = factor_exposures[[

    "Factor_Rank",

    "Factor",

    "Exposure",

    "Contribution_Pct",
]].copy()

# =========================================================
# TOP FACTORS
# =========================================================

top_factor = (
    factor_exposures.iloc[0]
)

bottom_factor = (
    factor_exposures.iloc[-1]
)

# =========================================================
# DIAGNOSTICS
# =========================================================

print(
    f"\nDominant Factor : "
    f"{dominant_factor}"
)

print(
    f"Exposure        : "
    f"{dominant_exposure:.4f}"
)

print(
    f"\nMost Crowded Sector : "
    f"{most_crowded_sector}"
)

print(
    f"Top Factor          : "
    f"{top_factor['Factor']}"
)

print(
    f"Bottom Factor       : "
    f"{bottom_factor['Factor']}"
)

# =========================================================
# PART 4 STARTS HERE
# =========================================================
#
# Next:
#
# HHI
# Effective Factors
# Diversification Score
# Factor Risk Score
# Executive Summary
# Save Outputs
#
# =========================================================

# =========================================================
# FACTOR CONCENTRATION
# =========================================================

print(
    "\n⚠ Calculating Concentration Risk..."
)

factor_concentration = (
    factor_exposures.copy()
)

factor_concentration[
    "Exposure_Pct"
] = (

    factor_concentration[
        "Abs_Exposure"
    ]

    /

    max(
        factor_concentration[
            "Abs_Exposure"
        ].sum(),
        1e-9
    )
)

# =========================================================
# HHI
# =========================================================

factor_hhi = (

    factor_concentration[
        "Exposure_Pct"
    ]

    ** 2

).sum()

# =========================================================
# EFFECTIVE FACTORS
# =========================================================

effective_factors = (

    1

    /

    max(
        factor_hhi,
        1e-9
    )
)

# =========================================================
# DIVERSIFICATION SCORE
# =========================================================

max_factors = len(
    factor_columns
)

diversification_score = (

    effective_factors

    /

    max_factors

    * 100
)

diversification_score = min(
    diversification_score,
    100
)

# =========================================================
# FACTOR RISK SCORE
# =========================================================

factor_risk_score = (

    factor_exposures[
        "Abs_Exposure"
    ]

    .mean()

    * 100
)

factor_risk_score = min(
    factor_risk_score,
    100
)

# =========================================================
# CONCENTRATION CLASSIFICATION
# =========================================================

if factor_hhi < 0.15:

    concentration_level = (
        "LOW"
    )

elif factor_hhi < 0.25:

    concentration_level = (
        "MODERATE"
    )

else:

    concentration_level = (
        "HIGH"
    )

# =========================================================
# FACTOR BALANCE SCORE
# =========================================================

factor_std = (

    factor_exposures[
        "Contribution_Pct"
    ]

    .std()
)

balance_score = (

    100

    /

    (
        1
        +
        factor_std
    )
)

# =========================================================
# EXECUTIVE SUMMARY
# =========================================================

summary = pd.DataFrame({

    "Metric": [

        "Dominant_Factor",

        "Dominant_Exposure",

        "Most_Crowded_Sector",

        "Factor_HHI",

        "Effective_Factors",

        "Diversification_Score",

        "Factor_Risk_Score",

        "Balance_Score",

        "Concentration_Level",

        "Total_Securities",

        "Run_Date",

        "Engine_Version",
    ],

    "Value": [

        dominant_factor,

        dominant_exposure,

        most_crowded_sector,

        factor_hhi,

        effective_factors,

        diversification_score,

        factor_risk_score,

        balance_score,

        concentration_level,

        len(
            portfolio
        ),

        datetime.now()
        .strftime(
            "%Y-%m-%d"
        ),

        ENGINE_VERSION,
    ]
})

# =========================================================
# CONCENTRATION REPORT
# =========================================================

concentration_report = pd.DataFrame({

    "Metric": [

        "Factor_HHI",

        "Effective_Factors",

        "Diversification_Score",

        "Concentration_Level",
    ],

    "Value": [

        factor_hhi,

        effective_factors,

        diversification_score,

        concentration_level,
    ]
})

# =========================================================
# SAVE OUTPUTS
# =========================================================

factor_exposures.to_csv(

    OUTPUT_DIR
    / "factor_exposures.csv",

    index=False,
)

sector_exposure.to_csv(

    OUTPUT_DIR
    / "factor_sector_exposure.csv",

    index=False,
)

factor_contributions.to_csv(

    OUTPUT_DIR
    / "factor_contributions.csv",

    index=False,
)

factor_concentration.to_csv(

    OUTPUT_DIR
    / "factor_concentration.csv",

    index=False,
)

factor_dashboard.to_csv(

    OUTPUT_DIR
    / "factor_dashboard.csv",

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

# =========================================================
# FINAL REPORT
# =========================================================

print(
    "\n"
    + "=" * 70
)

print(
    "🏁 FACTOR RISK MODEL COMPLETE"
)

print(
    "=" * 70
)

print(
    f"Dominant Factor      : "
    f"{dominant_factor}"
)

print(
    f"Dominant Exposure    : "
    f"{dominant_exposure:.4f}"
)

print(
    f"Most Crowded Sector  : "
    f"{most_crowded_sector}"
)

print(
    f"Factor HHI           : "
    f"{factor_hhi:.4f}"
)

print(
    f"Effective Factors    : "
    f"{effective_factors:.2f}"
)

print(
    f"Diversification      : "
    f"{diversification_score:.2f}"
)

print(
    f"Risk Score           : "
    f"{factor_risk_score:.2f}"
)

print(
    f"Balance Score        : "
    f"{balance_score:.2f}"
)

print(
    f"Concentration Level  : "
    f"{concentration_level}"
)

print(
    f"\nOutput Directory:\n"
    f"{OUTPUT_DIR}"
)

print(
    "=" * 70
)