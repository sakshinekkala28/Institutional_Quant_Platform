"""
=========================================================
FACTOR ATTRIBUTION ENGINE
=========================================================

Purpose:
Institutional Factor Performance Attribution

Inputs:
data/factors/factor_snapshot_master.csv
data/portfolios/live_portfolio.csv

Outputs:
factor_exposures.csv
factor_contributions.csv
factor_attribution_summary.csv
factor_attribution_rankings.csv

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

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

FACTOR_FILE = (
    ROOT
    / "data"
    / "factors"
    / "factor_snapshot_master.csv"
)

PORTFOLIO_FILE = (
    ROOT
    / "data"
    / "portfolios"
    / "live_portfolio.csv"
)

OUTPUT_DIR = (
    ROOT
    / "data"
    / "research"
)

REPORT_FILE = (
    ROOT
    / "data"
    / "logs"
    / "factor_attribution_report.csv"
)

HISTORY_FILE = (
    OUTPUT_DIR
    / "factor_history.csv"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

for file in [

    FACTOR_FILE,
    PORTFOLIO_FILE,

]:

    if not file.exists():

        raise FileNotFoundError(
            file
        )
    
# =========================================================
# LOAD
# =========================================================

print(
    "\n📥 Loading Data..."
)

factors = pd.read_csv(
    FACTOR_FILE
)

portfolio = pd.read_csv(
    PORTFOLIO_FILE
)

if factors.empty:

    raise ValueError(
        "Factor snapshot file empty"
    )

if portfolio.empty:

    raise ValueError(
        "Portfolio file empty"
    )

# =========================================================
# LATEST SNAPSHOT
# =========================================================

if "Snapshot_Date" not in factors.columns:

    raise ValueError(
        "Missing Snapshot_Date"
    )

factors["Snapshot_Date"] = pd.to_datetime(
    factors["Snapshot_Date"]
)

latest_date = (
    factors["Snapshot_Date"]
    .max()
)

factors = factors[
    factors["Snapshot_Date"]
    == latest_date
].copy()

# =========================================================
# MERGE
# =========================================================

required_portfolio_cols = [
    "Symbol",
    "Weight",
]

for col in required_portfolio_cols:

    if col not in portfolio.columns:

        raise ValueError(
            f"Missing Portfolio Column: {col}"
        )

merged = portfolio.merge(
    factors,
    on="Symbol",
    how="inner"
)

if len(merged) < MIN_SECURITIES:

    raise ValueError(
        "Insufficient merged securities"
    )

coverage = (

    len(merged)

    /

    max(
        len(portfolio),
        1
    )
)

if "Expected_Return" in merged.columns:

    realized_return = (
        merged[
            "Expected_Return"
        ]
    )

elif "Alpha_Adjusted" in merged.columns:

    realized_return = (
        merged[
            "Alpha_Adjusted"
        ]
    )

else:

    raise ValueError(
        "No return field available."
    )

# =========================================================
# FACTORS
# =========================================================

candidate_factors = [

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

    "Market_Cap",

    "Last_Close",
]

factor_columns = [

    c

    for c in candidate_factors

    if c in merged.columns
]

if not factor_columns:

    raise ValueError(
        "No factor columns available"
    )

# =========================================================
# FORWARD RETURNS
# =========================================================

if "Last_Close" not in merged.columns:

    if "Last_Close_x" in merged.columns:

        merged["Last_Close"] = (
            merged["Last_Close_x"]
        )

    elif "Last_Close_y" in merged.columns:

        merged["Last_Close"] = (
            merged["Last_Close_y"]
        )

    else:

        raise ValueError(
            f"Last_Close missing. Columns: "
            f"{merged.columns.tolist()}"
        )
    
# Approximate next-period return
# (replace with actual realized returns
# if available later)

# =========================================================
# EXPOSURES
# =========================================================

exposure_records = []

contribution_records = []

for factor in factor_columns:

    values = pd.to_numeric(

        merged[factor],

        errors="coerce"
    )

    values = values.fillna(
        values.median()
    )

    zscore = (

        values
        - values.mean()

    ) / max(
        values.std(),
        1e-9,
    )

    exposure = (

        zscore

        * merged[
            "Weight"
        ]

    ).sum()

    factor_return = np.corrcoef(
        zscore,
        realized_return
    )[0, 1]

    contribution = (
        exposure
        * factor_return
    )

    exposure_records.append({

        "Factor":
        factor,

        "Exposure":
        exposure,
    })

    contribution_records.append({

        "Factor":
        factor,

        "Contribution":
        contribution,
    })

# =========================================================
# DATAFRAMES
# =========================================================

exposures = pd.DataFrame(
    exposure_records
)

contributions = pd.DataFrame(
    contribution_records
)

summary = exposures.merge(
    contributions,
    on="Factor",
    how="inner",
)

summary["Abs_Contribution"] = (
    summary[
        "Contribution"
    ].abs()
)

# =========================================================
# NORMALIZED %
# =========================================================

total_abs = max(

    summary[
        "Abs_Contribution"
    ].sum(),

    1e-9,
)

summary[
    "Contribution_%"
] = (

    summary[
        "Abs_Contribution"
    ]

    / total_abs

    * 100
)

# =========================================================
# RANKING
# =========================================================

rankings = (

    summary

    .sort_values(
        "Contribution_%",
        ascending=False,
    )

    .reset_index(
        drop=True
    )
)

rankings["Rank"] = (
    rankings.index + 1
)

rankings["Exposure_Rank"] = (
    rankings["Exposure"]
    .rank(
        ascending=False,
        pct=True
    )
    * 100
)

positive_factors = (
    rankings[
        rankings["Contribution"] > 0
    ]
)

negative_factors = (
    rankings[
        rankings["Contribution"] < 0
    ]
)

positive_share = (
    positive_factors["Contribution_%"]
    .sum()
)

negative_share = (
    negative_factors["Contribution_%"]
    .sum()
)

top_factor_share = (

    rankings.head(1)[
        "Contribution_%"
    ]

    .sum()
)

top3_share = (

    rankings.head(3)[
        "Contribution_%"
    ]

    .sum()
)

top5_share = (

    rankings.head(5)[
        "Contribution_%"
    ]

    .sum()
)

hhi = (

    (
        rankings[
            "Contribution_%"
        ]
        / 100
    ) ** 2

).sum()

factor_div_score = (

    1

    /

    (
        (
            rankings[
                "Contribution_%"
            ]
            / 100
        ) ** 2
    ).sum()
)

quality_score = max(

    0,

    100

    -

    abs(

        rankings[
            "Contribution_%"
        ].sum()

        - 100

    )
)

breadth_score = (

    len(positive_factors)

    /

    max(
        len(rankings),
        1
    )
)

if breadth_score >= 0.70:
    breadth_grade = "Excellent"

elif breadth_score >= 0.50:
    breadth_grade = "Healthy"

elif breadth_score >= 0.30:
    breadth_grade = "Narrow"

else:
    breadth_grade = "Highly Concentrated"

crowding_score = (

    top3_share

    /

    max(
        factor_div_score,
        1
    )
)

if crowding_score > 10:
    crowding = "High"

elif crowding_score > 5:
    crowding = "Moderate"

else:
    crowding = "Low"


health_score = (

    coverage * 30

    +

    min(
        factor_div_score,
        10
    ) * 3

    +

    (1 - hhi) * 20

    +

    breadth_score * 20
)

health_score = min(
    health_score,
    100
)

# =========================================================
# FACTOR TYPE
# =========================================================

def classify_factor(
    factor,
):

    if "Momentum" in factor:
        return "Momentum"

    if "Volatility" in factor:
        return "Risk"

    if "Drawdown" in factor:
        return "Risk"

    if "ADV" in factor:
        return "Liquidity"

    if "Volume" in factor:
        return "Liquidity"

    if "Cap" in factor:
        return "Size"

    return "Technical"

rankings[
    "Factor_Group"
] = rankings[
    "Factor"
].apply(
    classify_factor
)

group_summary = (

    rankings

    .groupby(
        "Factor_Group"
    )

    [
        "Contribution_%"
    ]

    .sum()

    .reset_index()
)

group_summary["Rank"] = (
    group_summary[
        "Contribution_%"
    ]
    .rank(
        ascending=False
    )
)

top_group = (

    group_summary

    .sort_values(
        "Contribution_%",
        ascending=False
    )

    .iloc[0]
)

if top_group["Factor_Group"] == "Momentum":

    regime = "Trending Market"

elif top_group["Factor_Group"] == "Risk":

    regime = "Defensive Market"

elif top_group["Factor_Group"] == "Liquidity":

    regime = "Institutional Accumulation"

else:

    regime = "Mixed Market"

warnings = []

if top_factor_share > 40:

    warnings.append(
        "Factor concentration risk"
    )

if coverage < 0.95:

    warnings.append(
        "Low factor coverage"
    )

if factor_div_score < 5:

    warnings.append(
        "Low factor diversification"
    )

if warnings:

    for warning in warnings:

        print(
            f"⚠ {warning}"
        )

if factor_div_score >= 8:

    diversification = "Excellent"

elif factor_div_score >= 6:

    diversification = "Good"

elif factor_div_score >= 4:

    diversification = "Moderate"

else:

    diversification = "Concentrated"


factor_risk_score = (

    hhi * 40

    +

    (1 - breadth_score) * 30

    +

    (top_factor_share / 100) * 30
)

if factor_risk_score < 20:
    risk_rating = "Low"

elif factor_risk_score < 40:
    risk_rating = "Moderate"

else:
    risk_rating = "High"

top_positive = (
    positive_factors
    .sort_values(
        "Contribution",
        ascending=False
    )
    .iloc[0]
)

top_negative = (
    negative_factors
    .sort_values(
        "Contribution"
    )
    .iloc[0]
)

dashboard = pd.DataFrame({

    "Metric": [

        "Coverage",
        "Factors_Analyzed",
        "Top_Factor_Share",
        "Top3_Share",
        "Top5_Share",
        "Effective_Factors",
        "Factor_HHI",
        "Positive_Factors",
        "Negative_Factors",
        "Quality_Score",
    ],

    "Value": [

        coverage,
        len(rankings),
        top_factor_share,
        top3_share,
        top5_share,
        factor_div_score,
        hhi,
        len(positive_factors),
        len(negative_factors),
        quality_score,
    ]
})


# =========================================================
# SAVE
# =========================================================

exposures.to_csv(

    OUTPUT_DIR
    / "factor_exposures.csv",

    index=False,
)

contributions.to_csv(

    OUTPUT_DIR
    / "factor_contributions.csv",

    index=False,
)

summary.to_csv(

    OUTPUT_DIR
    / "factor_attribution_summary.csv",

    index=False,
)

rankings.to_csv(

    OUTPUT_DIR
    / "factor_attribution_rankings.csv",

    index=False,
)

group_summary.to_csv(

    OUTPUT_DIR
    / "factor_group_summary.csv",

    index=False,
)

warnings_df = pd.DataFrame({

    "Warning": warnings

    if warnings

    else ["None"]
})

warnings_df.to_csv(

    OUTPUT_DIR
    / "factor_warnings.csv",

    index=False,
)

dashboard.to_csv(

    OUTPUT_DIR
    / "factor_dashboard.csv",

    index=False,
)

# =========================================================
# REPORT
# =========================================================

best = rankings.iloc[0]

report = pd.DataFrame({

    "Metric": [

        "Coverage",
        "Top_Group",
        "Top_Group_Share",
        "Effective_Factors",
        "Factor_HHI",
        "Positive_Factors",
        "Negative_Factors",
        "Diversification",
        "Warnings",
        "Run_Date",
        "Engine_Version",

    ],

    "Value": [

        coverage,
        top_group["Factor_Group"],
        top_group["Contribution_%"],
        factor_div_score,
        hhi,
        len(positive_factors),
        len(negative_factors),
        diversification,
        len(warnings),
        datetime.now()
        .strftime(
            "%Y-%m-%d"
        ),
        ENGINE_VERSION,

    ]
})

report.to_csv(
    REPORT_FILE,
    index=False,
)

history_row = pd.DataFrame({

    "Run_Date": [
        datetime.now().strftime(
            "%Y-%m-%d"
        )
    ],

    "Top_Factor": [
        best["Factor"]
    ],

    "Top_Group": [
        top_group["Factor_Group"]
    ],

    "Top_Factor_Share": [
        top_factor_share
    ],

    "Top_Group_Share": [
        top_group["Contribution_%"]
    ],

    "Effective_Factors": [
        factor_div_score
    ],

    "Factor_HHI": [
        hhi
    ],

    "Breadth_Score": [
        breadth_score
    ],

    "Health_Score": [
        health_score
    ],

    "Warnings": [
        len(warnings)
    ]
})

if HISTORY_FILE.exists():

    history = pd.read_csv(
        HISTORY_FILE
    )

    history = pd.concat(
        [
            history,
            history_row
        ],
        ignore_index=True
    )

else:

    history = history_row.copy()

history.to_csv(
    HISTORY_FILE,
    index=False
)

required_outputs = [

    OUTPUT_DIR
    / "factor_exposures.csv",

    OUTPUT_DIR
    / "factor_contributions.csv",

    OUTPUT_DIR
    / "factor_attribution_summary.csv",

    OUTPUT_DIR
    / "factor_attribution_rankings.csv",

    OUTPUT_DIR
    / "factor_warnings.csv",

    OUTPUT_DIR
    / "factor_group_summary.csv",

    OUTPUT_DIR
    / "factor_dashboard.csv",

    REPORT_FILE,

    HISTORY_FILE,
]

for file in required_outputs:

    if not file.exists():

        raise FileNotFoundError(
            file
        )

# =========================================================
# REPORT
# =========================================================

print("\n" + "=" * 70)

print(
    "🏁 FACTOR ATTRIBUTION ENGINE COMPLETE"
)

print("=" * 70)

# ---------------------------------------------------------
# EXECUTIVE SUMMARY
# ---------------------------------------------------------

print(
    f"Factors Analyzed : "
    f"{len(rankings)}"
)

print(
    f"Coverage         : "
    f"{coverage:.2%}"
)

print(
    f"Health Score     : "
    f"{health_score:.2f}"
)

print(
    f"Quality Score    : "
    f"{quality_score:.2f}"
)

# ---------------------------------------------------------
# DIVERSIFICATION & RISK
# ---------------------------------------------------------

print(
    f"Effective Factors: "
    f"{factor_div_score:.2f}"
)

print(
    f"Factor HHI       : "
    f"{hhi:.3f}"
)

print(
    f"Diversification  : "
    f"{diversification}"
)

print(
    f"Crowding Score   : "
    f"{crowding_score:.2f}"
)

print(
    f"Crowding Risk    : "
    f"{crowding}"
)

# ---------------------------------------------------------
# BREADTH
# ---------------------------------------------------------

print(
    f"Breadth Score    : "
    f"{breadth_score:.2%}"
)

print(
    f"Breadth Grade    : "
    f"{breadth_grade}"
)

print(
    f"Positive Factors : "
    f"{len(positive_factors)}"
)

print(
    f"Positive Share   : "
    f"{positive_share:.2f}%"
)

print(
    f"Negative Factors : "
    f"{len(negative_factors)}"
)

print(
    f"Negative Share   : "
    f"{negative_share:.2f}%"
)

# ---------------------------------------------------------
# FACTOR LEADERSHIP
# ---------------------------------------------------------

print(
    f"Top Factor       : "
    f"{best['Factor']}"
)

print(
    f"Contribution     : "
    f"{best['Contribution_%']:.2f}%"
)

print(
    f"Top Positive     : "
    f"{top_positive['Factor']}"
)

print(
    f"Top Negative     : "
    f"{top_negative['Factor']}"
)

print(
    f"Top Factor Share : "
    f"{top_factor_share:.2f}%"
)

print(
    f"Top 3 Share      : "
    f"{top3_share:.2f}%"
)

print(
    f"Top 5 Share      : "
    f"{top5_share:.2f}%"
)

# ---------------------------------------------------------
# FACTOR REGIME
# ---------------------------------------------------------

print(
    f"Top Group        : "
    f"{top_group['Factor_Group']}"
)

print(
    f"Group Share      : "
    f"{top_group['Contribution_%']:.2f}%"
)

print(
    f"Factor Regime    : "
    f"{regime}"
)

# ---------------------------------------------------------
# GOVERNANCE
# ---------------------------------------------------------

print(
    f"Warnings         : "
    f"{len(warnings)}"
)

if warnings:

    for warning in warnings:

        print(
            f"⚠ {warning}"
        )

print(
    f"\nOutput Directory:\n"
    f"{OUTPUT_DIR}"
)

print("=" * 70)