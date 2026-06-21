"""
=========================================================
ENTERPRISE RISK DASHBOARD ENGINE
=========================================================

Purpose:
Aggregate All Risk Engines Into A Single
Institutional Risk Dashboard

Inputs:
data/backtests/backtest_results.csv
data/stress_tests/stress_summary.csv
data/stress_tests/historical_stress_summary.csv
data/risk/factor_stress_summary.csv
data/liquidity/liquidity_stress_summary.csv
data/risk/risk_report.csv

Outputs:
data/risk/enterprise_risk_dashboard.csv
data/risk/enterprise_risk_summary.csv
data/risk/enterprise_risk_scorecard.csv

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

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

BACKTEST_FILE = (
    ROOT
    / "data"
    / "backtests"
    / "backtest_results.csv"
)

RISK_REPORT_FILE = (
    ROOT
    / "data"
    / "risk"
    / "risk_report.csv"
)

FACTOR_STRESS_FILE = (
    ROOT
    / "data"
    / "risk"
    / "factor_stress_summary.csv"
)

LIQUIDITY_FILE = (
    ROOT
    / "data"
    / "liquidity"
    / "liquidity_stress_summary.csv"
)

SCENARIO_STRESS_FILE = (
    ROOT
    / "data"
    / "stress_tests"
    / "stress_summary.csv"
)

HISTORICAL_STRESS_FILE = (
    ROOT
    / "data"
    / "stress_tests"
    / "historical_stress_summary.csv"
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
    / "enterprise_risk_report.csv"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

# =========================================================
# HELPERS
# =========================================================

def load_metric_file(path):

    if not path.exists():

        print(
            f"⚠ Missing: {path.name}"
        )

        return pd.DataFrame()

    try:

        return pd.read_csv(path)

    except Exception as e:

        print(
            f"⚠ Failed: {path.name}"
        )

        print(e)

        return pd.DataFrame()


def metric_lookup(
    df,
    metric_name,
    default=np.nan
):

    try:

        value = df.loc[
            df["Metric"] == metric_name,
            "Value"
        ]

        if len(value):

            return float(
                value.iloc[0]
            )

        return default

    except Exception:

        return default


# =========================================================
# LOAD DATA
# =========================================================

print(
    "\n📥 Loading Risk Sources..."
)

backtest_df = load_metric_file(
    BACKTEST_FILE
)

risk_report_df = load_metric_file(
    RISK_REPORT_FILE
)

factor_stress_df = load_metric_file(
    FACTOR_STRESS_FILE
)

liquidity_df = load_metric_file(
    LIQUIDITY_FILE
)

scenario_stress_df = load_metric_file(
    SCENARIO_STRESS_FILE
)

historical_stress_df = load_metric_file(
    HISTORICAL_STRESS_FILE
)

# =========================================================
# FILE HEALTH CHECK
# =========================================================

source_health = pd.DataFrame({

    "Source": [

        "Backtest",

        "Risk_Report",

        "Factor_Stress",

        "Liquidity",

        "Scenario_Stress",

        "Historical_Stress",
    ],

    "Loaded": [

        not backtest_df.empty,

        not risk_report_df.empty,

        not factor_stress_df.empty,

        not liquidity_df.empty,

        not scenario_stress_df.empty,

        not historical_stress_df.empty,
    ]
})

healthy_sources = int(
    source_health["Loaded"].sum()
)

total_sources = len(
    source_health
)

coverage = (

    healthy_sources
    /
    total_sources
)

print(
    f"Risk Sources Loaded : "
    f"{healthy_sources}"
    f"/{total_sources}"
)

print(
    f"Coverage            : "
    f"{coverage:.2%}"
)

if coverage < 0.50:

    raise ValueError(
        "Insufficient risk source coverage."
    )

# =========================================================
# EXTRACT BACKTEST METRICS
# =========================================================

print(
    "\n📊 Extracting Risk Metrics..."
)

cagr = metric_lookup(
    backtest_df,
    "CAGR"
)

sharpe = metric_lookup(
    backtest_df,
    "Sharpe_Ratio"
)

sortino = metric_lookup(
    backtest_df,
    "Sortino_Ratio"
)

max_drawdown = metric_lookup(
    backtest_df,
    "Max_Drawdown"
)

calmar = metric_lookup(
    backtest_df,
    "Calmar_Ratio"
)

profit_factor = metric_lookup(
    backtest_df,
    "Profit_Factor"
)

# =========================================================
# SCENARIO STRESS METRICS
# =========================================================

stress_var = metric_lookup(
    scenario_stress_df,
    "Stress_VaR_95"
)

stress_cvar = metric_lookup(
    scenario_stress_df,
    "Stress_CVaR_95"
)

stress_risk_score = metric_lookup(
    scenario_stress_df,
    "Scenario_Risk_Score"
)

# =========================================================
# HISTORICAL STRESS
# =========================================================

historical_var = metric_lookup(
    historical_stress_df,
    "Historical_VaR_95"
)

historical_cvar = metric_lookup(
    historical_stress_df,
    "Historical_CVaR_95"
)

historical_risk_score = metric_lookup(
    historical_stress_df,
    "Risk_Score"
)

# =========================================================
# FACTOR STRESS
# =========================================================

factor_var = metric_lookup(
    factor_stress_df,
    "Factor_VaR_95"
)

factor_cvar = metric_lookup(
    factor_stress_df,
    "Factor_CVaR_95"
)

factor_risk_score = metric_lookup(
    factor_stress_df,
    "Risk_Score"
)

effective_factors = metric_lookup(
    factor_stress_df,
    "Effective_Factors"
)

# =========================================================
# LIQUIDITY METRICS
# =========================================================

liquidity_score = metric_lookup(
    liquidity_df,
    "Portfolio_Liquidity_Score"
)

capacity_utilization = metric_lookup(
    liquidity_df,
    "Capacity_Utilization"
)

liquidity_risk_score = metric_lookup(
    liquidity_df,
    "Liquidity_Risk_Score"
)

# =========================================================
# STORAGE
# =========================================================

dashboard_rows = []

summary_rows = []

print(
    "\n✓ Metrics Extraction Complete"
)

# =========================================================
# PART 2 STARTS HERE
# =========================================================
#
# Next:
#
# Enterprise Dashboard
# Aggregate Risk View
# Risk Normalization
# Dashboard Construction
#
# =========================================================

# =========================================================
# RISK NORMALIZATION HELPERS
# =========================================================

print(
    "\n📊 Building Enterprise Dashboard..."
)

def normalize_score(
    value,
    low,
    high,
    reverse=False
):

    if pd.isna(value):

        return np.nan

    score = (

        (value - low)

        /

        max(
            high - low,
            1e-9
        )

    )

    score = np.clip(
        score,
        0,
        1
    )

    if reverse:

        score = (
            1
            -
            score
        )

    return (
        score
        * 100
    )


# =========================================================
# MARKET RISK
# =========================================================

market_risk_metrics = {

    "CAGR":
    cagr,

    "Sharpe":
    sharpe,

    "Sortino":
    sortino,

    "Calmar":
    calmar,

    "Max_Drawdown":
    max_drawdown,
}

market_risk_score = np.nanmean([

    normalize_score(
        sharpe,
        0,
        3
    ),

    normalize_score(
        sortino,
        0,
        4
    ),

    normalize_score(
        calmar,
        0,
        5
    ),

    normalize_score(
        abs(max_drawdown),
        0,
        0.50,
        reverse=True
    ),
])

# =========================================================
# STRESS RISK
# =========================================================

stress_risk_score_final = np.nanmean([

    normalize_score(
        abs(stress_var),
        0,
        0.50,
        reverse=True
    ),

    normalize_score(
        abs(stress_cvar),
        0,
        0.75,
        reverse=True
    ),

    normalize_score(
        stress_risk_score,
        0,
        100,
        reverse=True
    ),
])

# =========================================================
# HISTORICAL STRESS RISK
# =========================================================

historical_score_final = np.nanmean([

    normalize_score(
        abs(historical_var),
        0,
        0.50,
        reverse=True
    ),

    normalize_score(
        abs(historical_cvar),
        0,
        0.75,
        reverse=True
    ),

    normalize_score(
        historical_risk_score,
        0,
        100,
        reverse=True
    ),
])

# =========================================================
# FACTOR RISK
# =========================================================

factor_score_final = np.nanmean([

    normalize_score(
        abs(factor_var),
        0,
        0.50,
        reverse=True
    ),

    normalize_score(
        abs(factor_cvar),
        0,
        0.75,
        reverse=True
    ),

    normalize_score(
        factor_risk_score,
        0,
        100,
        reverse=True
    ),

    normalize_score(
        effective_factors,
        1,
        10
    ),
])

# =========================================================
# LIQUIDITY RISK
# =========================================================

liquidity_score_final = np.nanmean([

    normalize_score(
        liquidity_score,
        0,
        100
    ),

    normalize_score(
        capacity_utilization,
        0,
        5,
        reverse=True
    ),

    normalize_score(
        liquidity_risk_score,
        0,
        100,
        reverse=True
    ),
])

# =========================================================
# RISK PILLARS
# =========================================================

risk_pillars = pd.DataFrame({

    "Risk_Pillar": [

        "Market_Risk",

        "Stress_Risk",

        "Historical_Risk",

        "Factor_Risk",

        "Liquidity_Risk",
    ],

    "Score": [

        market_risk_score,

        stress_risk_score_final,

        historical_score_final,

        factor_score_final,

        liquidity_score_final,
    ]
})

# =========================================================
# DASHBOARD DATASET
# =========================================================

enterprise_dashboard = pd.DataFrame({

    "Metric": [

        "CAGR",

        "Sharpe_Ratio",

        "Sortino_Ratio",

        "Calmar_Ratio",

        "Max_Drawdown",

        "Stress_VaR_95",

        "Stress_CVaR_95",

        "Historical_VaR_95",

        "Historical_CVaR_95",

        "Factor_VaR_95",

        "Factor_CVaR_95",

        "Effective_Factors",

        "Liquidity_Score",

        "Capacity_Utilization",
    ],

    "Value": [

        cagr,

        sharpe,

        sortino,

        calmar,

        max_drawdown,

        stress_var,

        stress_cvar,

        historical_var,

        historical_cvar,

        factor_var,

        factor_cvar,

        effective_factors,

        liquidity_score,

        capacity_utilization,
    ]
})

# =========================================================
# EXECUTIVE DASHBOARD
# =========================================================

executive_dashboard = pd.DataFrame({

    "Category": [

        "Market",

        "Stress",

        "Historical",

        "Factor",

        "Liquidity",
    ],

    "Score": [

        market_risk_score,

        stress_risk_score_final,

        historical_score_final,

        factor_score_final,

        liquidity_score_final,
    ]
})

# =========================================================
# RISK HEALTH CHECK
# =========================================================

risk_health = pd.DataFrame({

    "Metric": [

        "Market_Risk",

        "Stress_Risk",

        "Historical_Risk",

        "Factor_Risk",

        "Liquidity_Risk",
    ],

    "Healthy": [

        market_risk_score >= 60,

        stress_risk_score_final >= 60,

        historical_score_final >= 60,

        factor_score_final >= 60,

        liquidity_score_final >= 60,
    ]
})

healthy_count = int(
    risk_health[
        "Healthy"
    ].sum()
)

print(
    f"Healthy Pillars : "
    f"{healthy_count}/5"
)

print(
    f"Market Score    : "
    f"{market_risk_score:.2f}"
)

print(
    f"Stress Score    : "
    f"{stress_risk_score_final:.2f}"
)

print(
    f"Factor Score    : "
    f"{factor_score_final:.2f}"
)

print(
    f"Liquidity Score : "
    f"{liquidity_score_final:.2f}"
)

# =========================================================
# PART 3 STARTS HERE
# =========================================================
#
# Next:
#
# Enterprise Risk Score
# Enterprise Grade
# Risk Ranking
# Scorecard
#
# =========================================================

# =========================================================
# ENTERPRISE RISK SCORE
# =========================================================

print(
    "\n🏦 Calculating Enterprise Risk Score..."
)

# ---------------------------------------------------------
# INSTITUTIONAL WEIGHTS
# ---------------------------------------------------------

MARKET_WEIGHT = 0.30

STRESS_WEIGHT = 0.25

FACTOR_WEIGHT = 0.20

LIQUIDITY_WEIGHT = 0.15

HISTORICAL_WEIGHT = 0.10

# =========================================================
# ENTERPRISE SCORE
# =========================================================

enterprise_risk_score = (

    market_risk_score
    * MARKET_WEIGHT

    +

    stress_risk_score_final
    * STRESS_WEIGHT

    +

    factor_score_final
    * FACTOR_WEIGHT

    +

    liquidity_score_final
    * LIQUIDITY_WEIGHT

    +

    historical_score_final
    * HISTORICAL_WEIGHT
)

enterprise_risk_score = float(
    np.clip(
        enterprise_risk_score,
        0,
        100
    )
)

# =========================================================
# ENTERPRISE GRADE
# =========================================================

if enterprise_risk_score >= 90:

    enterprise_grade = (
        "EXCELLENT"
    )

elif enterprise_risk_score >= 75:

    enterprise_grade = (
        "GOOD"
    )

elif enterprise_risk_score >= 60:

    enterprise_grade = (
        "MODERATE"
    )

elif enterprise_risk_score >= 40:

    enterprise_grade = (
        "HIGH_RISK"
    )

else:

    enterprise_grade = (
        "CRITICAL"
    )

# =========================================================
# RISK RANKING
# =========================================================

risk_pillars = risk_pillars.sort_values(

    "Score",

    ascending=False

).reset_index(
    drop=True
)

risk_pillars[
    "Rank"
] = (
    risk_pillars.index + 1
)

# =========================================================
# STRONGEST PILLAR
# =========================================================

best_pillar = (

    risk_pillars

    .iloc[0]
)

# =========================================================
# WEAKEST PILLAR
# =========================================================

worst_pillar = (

    risk_pillars

    .iloc[-1]
)

# =========================================================
# PILLAR CONTRIBUTIONS
# =========================================================

pillar_contributions = pd.DataFrame({

    "Risk_Pillar": [

        "Market_Risk",

        "Stress_Risk",

        "Factor_Risk",

        "Liquidity_Risk",

        "Historical_Risk",
    ],

    "Weight": [

        MARKET_WEIGHT,

        STRESS_WEIGHT,

        FACTOR_WEIGHT,

        LIQUIDITY_WEIGHT,

        HISTORICAL_WEIGHT,
    ],

    "Score": [

        market_risk_score,

        stress_risk_score_final,

        factor_score_final,

        liquidity_score_final,

        historical_score_final,
    ]
})

pillar_contributions[
    "Weighted_Contribution"
] = (

    pillar_contributions[
        "Weight"
    ]

    *

    pillar_contributions[
        "Score"
    ]
)

# =========================================================
# RISK CONCENTRATION
# =========================================================

total_score = (

    pillar_contributions[
        "Weighted_Contribution"
    ]

    .sum()
)

pillar_contributions[
    "Contribution_Pct"
] = (

    pillar_contributions[
        "Weighted_Contribution"
    ]

    /

    max(
        total_score,
        1e-9
    )

    * 100
)

# =========================================================
# RISK BALANCE SCORE
# =========================================================

risk_balance_score = (

    100

    -

    risk_pillars[
        "Score"
    ]

    .std()
)

risk_balance_score = max(
    risk_balance_score,
    0
)

# =========================================================
# SCORECARD
# =========================================================

enterprise_scorecard = pd.DataFrame({

    "Metric": [

        "Enterprise_Risk_Score",

        "Enterprise_Grade",

        "Risk_Balance_Score",

        "Best_Pillar",

        "Best_Pillar_Score",

        "Worst_Pillar",

        "Worst_Pillar_Score",

        "Healthy_Pillars",
    ],

    "Value": [

        enterprise_risk_score,

        enterprise_grade,

        risk_balance_score,

        best_pillar[
            "Risk_Pillar"
        ],

        best_pillar[
            "Score"
        ],

        worst_pillar[
            "Risk_Pillar"
        ],

        worst_pillar[
            "Score"
        ],

        healthy_count,
    ]
})

# =========================================================
# ENTERPRISE SUMMARY
# =========================================================

enterprise_summary = pd.DataFrame({

    "Metric": [

        "Enterprise_Risk_Score",

        "Enterprise_Grade",

        "Risk_Balance_Score",

        "Healthy_Pillars",

        "Best_Pillar",

        "Worst_Pillar",

        "Run_Date",

        "Engine_Version",
    ],

    "Value": [

        enterprise_risk_score,

        enterprise_grade,

        risk_balance_score,

        healthy_count,

        best_pillar[
            "Risk_Pillar"
        ],

        worst_pillar[
            "Risk_Pillar"
        ],

        datetime.now()
        .strftime(
            "%Y-%m-%d"
        ),

        ENGINE_VERSION,
    ]
})

# =========================================================
# DIAGNOSTICS
# =========================================================

print(
    f"Enterprise Score : "
    f"{enterprise_risk_score:.2f}"
)

print(
    f"Risk Grade       : "
    f"{enterprise_grade}"
)

print(
    f"Best Pillar      : "
    f"{best_pillar['Risk_Pillar']}"
)

print(
    f"Worst Pillar     : "
    f"{worst_pillar['Risk_Pillar']}"
)

print(
    f"Risk Balance     : "
    f"{risk_balance_score:.2f}"
)

# =========================================================
# PART 4 STARTS HERE
# =========================================================
#
# Next:
#
# Save Outputs
# Enterprise Dashboard Export
# Reporting Layer
# Final CIO Report
#
# =========================================================

# =========================================================
# ENTERPRISE DASHBOARD ENHANCEMENT
# =========================================================

enterprise_dashboard = enterprise_dashboard.copy()

enterprise_dashboard["Engine_Version"] = (
    ENGINE_VERSION
)

enterprise_dashboard["Run_Date"] = (
    datetime.now()
    .strftime("%Y-%m-%d")
)

# =========================================================
# EXECUTIVE CIO DASHBOARD
# =========================================================

cio_dashboard = pd.DataFrame({

    "Category": [

        "Market Risk",

        "Stress Risk",

        "Historical Risk",

        "Factor Risk",

        "Liquidity Risk",

        "Enterprise Risk",
    ],

    "Score": [

        market_risk_score,

        stress_risk_score_final,

        historical_score_final,

        factor_score_final,

        liquidity_score_final,

        enterprise_risk_score,
    ]
})

# =========================================================
# ENTERPRISE RISK MATRIX
# =========================================================

enterprise_risk_matrix = pd.DataFrame({

    "Risk_Pillar":

    risk_pillars[
        "Risk_Pillar"
    ],

    "Score":

    risk_pillars[
        "Score"
    ],

    "Rank":

    risk_pillars[
        "Rank"
    ],
})

# =========================================================
# ENTERPRISE HEALTH STATUS
# =========================================================

enterprise_risk_matrix[
    "Status"
] = np.where(

    enterprise_risk_matrix[
        "Score"
    ] >= 80,

    "STRONG",

    np.where(

        enterprise_risk_matrix[
            "Score"
        ] >= 60,

        "ACCEPTABLE",

        np.where(

            enterprise_risk_matrix[
                "Score"
            ] >= 40,

            "WATCHLIST",

            "CRITICAL"
        )
    )
)

# =========================================================
# TOP RISKS
# =========================================================

top_risks = (

    enterprise_risk_matrix

    .sort_values(
        "Score"
    )

    .head(3)

    .copy()
)

top_risks[
    "Risk_Level"
] = "HIGH"

# =========================================================
# RISK RECOMMENDATIONS
# =========================================================

recommendations = []

for _, row in top_risks.iterrows():

    pillar = row[
        "Risk_Pillar"
    ]

    if pillar == "Liquidity_Risk":

        recommendations.append(

            "Reduce exposure to less liquid positions."
        )

    elif pillar == "Factor_Risk":

        recommendations.append(

            "Improve factor diversification."
        )

    elif pillar == "Stress_Risk":

        recommendations.append(

            "Review scenario vulnerabilities."
        )

    elif pillar == "Historical_Risk":

        recommendations.append(

            "Validate historical crisis resilience."
        )

    elif pillar == "Market_Risk":

        recommendations.append(

            "Reduce drawdown and volatility exposure."
        )

risk_recommendations = pd.DataFrame({

    "Risk_Pillar":
    top_risks[
        "Risk_Pillar"
    ].values,

    "Recommendation":
    recommendations,
})

# =========================================================
# SAVE OUTPUTS
# =========================================================

enterprise_dashboard.to_csv(

    OUTPUT_DIR
    / "enterprise_risk_dashboard.csv",

    index=False
)

enterprise_summary.to_csv(

    OUTPUT_DIR
    / "enterprise_risk_summary.csv",

    index=False
)

enterprise_scorecard.to_csv(

    OUTPUT_DIR
    / "enterprise_risk_scorecard.csv",

    index=False
)

enterprise_risk_matrix.to_csv(

    OUTPUT_DIR
    / "enterprise_risk_matrix.csv",

    index=False
)

pillar_contributions.to_csv(

    OUTPUT_DIR
    / "enterprise_risk_contributions.csv",

    index=False
)

cio_dashboard.to_csv(

    OUTPUT_DIR
    / "cio_dashboard.csv",

    index=False
)

risk_recommendations.to_csv(

    OUTPUT_DIR
    / "risk_recommendations.csv",

    index=False
)

source_health.to_csv(

    OUTPUT_DIR
    / "risk_source_health.csv",

    index=False
)

enterprise_summary.to_csv(

    REPORT_FILE,

    index=False
)

# =========================================================
# FINAL CIO REPORT
# =========================================================

print(
    "\n"
    + "=" * 70
)

print(
    "🏁 ENTERPRISE RISK DASHBOARD COMPLETE"
)

print(
    "=" * 70
)

print(
    f"Enterprise Score : "
    f"{enterprise_risk_score:.2f}"
)

print(
    f"Risk Grade       : "
    f"{enterprise_grade}"
)

print(
    f"Healthy Pillars  : "
    f"{healthy_count}/5"
)

print(
    f"Risk Balance     : "
    f"{risk_balance_score:.2f}"
)

print(
    f"\nBest Pillar      : "
    f"{best_pillar['Risk_Pillar']}"
)

print(
    f"Score            : "
    f"{best_pillar['Score']:.2f}"
)

print(
    f"\nWorst Pillar     : "
    f"{worst_pillar['Risk_Pillar']}"
)

print(
    f"Score            : "
    f"{worst_pillar['Score']:.2f}"
)

print(
    f"\nMarket Score     : "
    f"{market_risk_score:.2f}"
)

print(
    f"Stress Score     : "
    f"{stress_risk_score_final:.2f}"
)

print(
    f"Historical Score : "
    f"{historical_score_final:.2f}"
)

print(
    f"Factor Score     : "
    f"{factor_score_final:.2f}"
)

print(
    f"Liquidity Score  : "
    f"{liquidity_score_final:.2f}"
)

print(
    f"\nOutput Directory:"
)

print(
    OUTPUT_DIR
)

print(
    "=" * 70
)