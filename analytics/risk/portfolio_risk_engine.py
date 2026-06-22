"""
=========================================================
PORTFOLIO RISK ENGINE
=========================================================

Purpose:
Institutional Portfolio Risk Analytics

Outputs:
- Portfolio Volatility
- VaR / CVaR
- Risk Contributions
- Factor Attribution
- Risk Budgeting
- Stress Testing

=========================================================
"""

from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd

# =========================================================
# CONFIGURATION
# =========================================================

ENGINE_VERSION = "1.0.0"

TRADING_DAYS = 252

VAR_CONFIDENCE_95 = 1.645
VAR_CONFIDENCE_99 = 2.326

MIN_WEIGHT_TOLERANCE = 1e-9

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

RISK_DIR = (
    ROOT
    / "data"
    / "risk"
)

PORTFOLIO_DIR = (
    ROOT
    / "data"
    / "portfolios"
)

LOG_DIR = (
    ROOT
    / "data"
    / "logs"
)

# =========================================================
# INPUT FILES
# =========================================================

PORTFOLIO_FILE = (
    PORTFOLIO_DIR
    / "live_portfolio.csv"
)

COVARIANCE_FILE = (
    RISK_DIR
    / "covariance_matrix.parquet"
)

FACTOR_FILE = (
    RISK_DIR
    / "eigenfactor_risk.parquet"
)

FACTOR_COVARIANCE_FILE = (
    RISK_DIR
    / "factor_covariance.parquet"
)

SPECIFIC_RISK_FILE = (
    RISK_DIR
    / "specific_risk.csv"
)

# =========================================================
# OUTPUT FILES
# =========================================================

SUMMARY_FILE = (
    RISK_DIR
    / "portfolio_risk_summary.csv"
)

AUDIT_FILE = (
    LOG_DIR
    / "portfolio_risk_audit.csv"
)

# =========================================================
# CREATE DIRECTORIES
# =========================================================

RISK_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

LOG_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

# =========================================================
# LOAD INPUTS
# =========================================================

print(
    "\n📥 Loading Portfolio Risk Inputs..."
)

# ---------------------------------------------------------
# Portfolio
# ---------------------------------------------------------

if not PORTFOLIO_FILE.exists():

    raise FileNotFoundError(
        PORTFOLIO_FILE
    )

portfolio = pd.read_csv(
    PORTFOLIO_FILE
)

# ---------------------------------------------------------
# Covariance Matrix
# ---------------------------------------------------------

if not COVARIANCE_FILE.exists():

    raise FileNotFoundError(
        COVARIANCE_FILE
    )

covariance_matrix = pd.read_parquet(
    COVARIANCE_FILE
)

# ---------------------------------------------------------
# Factor Loadings
# ---------------------------------------------------------

if not FACTOR_FILE.exists():

    raise FileNotFoundError(
        FACTOR_FILE
    )

factor_loadings = pd.read_parquet(
    FACTOR_FILE
)

# ---------------------------------------------------------
# Factor Covariance
# ---------------------------------------------------------

if not FACTOR_COVARIANCE_FILE.exists():

    raise FileNotFoundError(
        FACTOR_COVARIANCE_FILE
    )

factor_covariance = pd.read_parquet(
    FACTOR_COVARIANCE_FILE
)

# ---------------------------------------------------------
# Specific Risk
# ---------------------------------------------------------

if not SPECIFIC_RISK_FILE.exists():

    raise FileNotFoundError(
        SPECIFIC_RISK_FILE
    )

specific_risk = pd.read_csv(
    SPECIFIC_RISK_FILE
)

# =========================================================
# VALIDATE PORTFOLIO
# =========================================================

print(
    "✔ Validating Portfolio..."
)

required_columns = {

    "Symbol",
    "Weight"
}

missing_columns = (

    required_columns

    - set(
        portfolio.columns
    )
)

if missing_columns:

    raise ValueError(
        f"Missing portfolio columns: "
        f"{missing_columns}"
    )

portfolio = portfolio.copy()

portfolio["Symbol"] = (

    portfolio["Symbol"]

    .astype(str)

    .str.upper()

    .str.strip()
)

portfolio["Weight"] = pd.to_numeric(

    portfolio["Weight"],

    errors="coerce"
)

portfolio = portfolio.dropna(
    subset=["Weight"]
)

if portfolio.empty:

    raise ValueError(
        "Portfolio empty."
    )

# =========================================================
# NORMALIZE WEIGHTS
# =========================================================

portfolio["Weight"] = (

    portfolio["Weight"]

    /

    portfolio["Weight"].sum()
)

weight_sum = (

    portfolio["Weight"]

    .sum()
)

if not np.isclose(
    weight_sum,
    1.0,
    atol=1e-6
):

    raise ValueError(
        "Portfolio weights invalid."
    )

# =========================================================
# NORMALIZE SYMBOLS
# =========================================================

factor_loadings["Symbol"] = (

    factor_loadings["Symbol"]

    .astype(str)

    .str.upper()

    .str.strip()
)

specific_risk["Symbol"] = (

    specific_risk["Symbol"]

    .astype(str)

    .str.upper()

    .str.strip()
)

portfolio["Symbol"] = np.where(

    portfolio["Symbol"]

    .str.endswith(".NS"),

    portfolio["Symbol"],

    portfolio["Symbol"] + ".NS"
)

# =========================================================
# PORTFOLIO ALIGNMENT
# =========================================================

portfolio_factor = portfolio.merge(

    factor_loadings,

    on="Symbol",

    how="left"
)

portfolio_specific = portfolio.merge(

    specific_risk,

    on="Symbol",

    how="left"
)

missing_factor = (

    portfolio_factor

    .iloc[:, 2:]

    .isna()

    .all(axis=1)

    .sum()
)

print(
    f"Portfolio Holdings : "
    f"{len(portfolio):,}"
)

print(
    f"Missing Factors     : "
    f"{missing_factor:,}"
)

# =========================================================
# FACTOR LIST
# =========================================================

factor_columns = [

    c

    for c in factor_loadings.columns

    if c.startswith("PC_")
]

if len(
    factor_columns
) == 0:

    raise ValueError(
        "No PCA factors found."
    )

print(
    f"Factors Loaded      : "
    f"{len(factor_columns)}"
)

# =========================================================
# BUILD PORTFOLIO UNIVERSE
# =========================================================

risk_universe = portfolio.merge(

    factor_loadings,

    on="Symbol",

    how="left"
)

risk_universe = risk_universe.merge(

    specific_risk,

    on="Symbol",

    how="left"
)

risk_universe = risk_universe.fillna(0)

matched_assets = (

    risk_universe["Symbol"]

    .nunique()
)

print(
    f"Risk Assets         : "
    f"{matched_assets:,}"
)

# =========================================================
# AUDIT CONTAINER
# =========================================================

audit_metrics = {}

audit_metrics[
    "Portfolio_Holdings"
] = len(
    portfolio
)

audit_metrics[
    "Risk_Assets"
] = matched_assets

audit_metrics[
    "Missing_Factor_Loadings"
] = int(
    missing_factor
)

audit_metrics[
    "Engine_Version"
] = ENGINE_VERSION

# =========================================================
# PART 2 STARTS HERE
# =========================================================
#
# Portfolio Volatility
# Portfolio Variance
# Covariance Alignment
# Marginal Risk
# Component Risk
#
# =========================================================

# =========================================================
# ALIGN COVARIANCE UNIVERSE
# =========================================================

print(
    "\n⚖ Building Portfolio Volatility..."
)

covariance_matrix.index = (
    covariance_matrix.index
    .astype(str)
    .str.upper()
    .str.strip()
)

covariance_matrix.columns = (
    covariance_matrix.columns
    .astype(str)
    .str.upper()
    .str.strip()
)

portfolio_symbols = (
    risk_universe["Symbol"]
    .tolist()
)

valid_symbols = [

    s

    for s in portfolio_symbols

    if (
        s in covariance_matrix.index
        and
        s in covariance_matrix.columns
    )
]

if len(valid_symbols) == 0:

    raise ValueError(
        "No portfolio symbols found "
        "inside covariance matrix."
    )

risk_universe = (

    risk_universe[
        risk_universe["Symbol"]
        .isin(valid_symbols)
    ]

    .copy()
)

# =========================================================
# BUILD WEIGHT VECTOR
# =========================================================

weights = (

    risk_universe

    .set_index("Symbol")

    ["Weight"]

    .reindex(valid_symbols)

    .fillna(0)

    .values
)

weights = (
    weights
    /
    weights.sum()
)

# =========================================================
# BUILD COVARIANCE MATRIX
# =========================================================

portfolio_covariance = (

    covariance_matrix

    .loc[
        valid_symbols,
        valid_symbols
    ]

    .astype(np.float64)
)

Sigma = (
    portfolio_covariance
    .values
)

# =========================================================
# PORTFOLIO VARIANCE
# =========================================================

portfolio_variance = (

    weights.T

    @

    Sigma

    @

    weights
)

portfolio_variance = float(

    np.maximum(
        portfolio_variance,
        MIN_WEIGHT_TOLERANCE
    )
)

# =========================================================
# PORTFOLIO VOLATILITY
# =========================================================

portfolio_volatility = np.sqrt(
    portfolio_variance
)

print(
    f"Portfolio Volatility : "
    f"{portfolio_volatility:.2%}"
)

# =========================================================
# MARGINAL RISK
# =========================================================

print(
    "📈 Building Marginal Risk..."
)

marginal_risk = (

    Sigma

    @

    weights
)

marginal_risk = (

    marginal_risk

    /

    portfolio_volatility
)

# =========================================================
# COMPONENT RISK
# =========================================================

component_risk = (

    weights

    *

    marginal_risk
)

component_risk_pct = (

    component_risk

    /

    np.maximum(
        component_risk.sum(),
        MIN_WEIGHT_TOLERANCE
    )
)

# =========================================================
# POSITION RISK TABLE
# =========================================================

position_risk = pd.DataFrame({

    "Symbol":
    valid_symbols,

    "Weight":
    weights,

    "Marginal_Risk":
    marginal_risk,

    "Component_Risk":
    component_risk,

    "Risk_Contribution_Pct":
    component_risk_pct * 100
})

position_risk = (

    position_risk

    .sort_values(

        "Risk_Contribution_Pct",

        ascending=False
    )

    .reset_index(
        drop=True
    )
)

# =========================================================
# TOP RISK CONTRIBUTORS
# =========================================================

top_risk_positions = (

    position_risk

    .head(20)

    .copy()
)

largest_risk_position = (

    position_risk

    .iloc[0]

    ["Symbol"]
)

largest_risk_pct = (

    position_risk

    .iloc[0]

    ["Risk_Contribution_Pct"]
)

print(
    f"Largest Risk Position : "
    f"{largest_risk_position}"
)

print(
    f"Risk Contribution     : "
    f"{largest_risk_pct:.2f}%"
)

# =========================================================
# EFFECTIVE POSITIONS
# =========================================================

risk_hhi = np.sum(
    component_risk_pct ** 2
)

effective_positions = (

    1

    /

    np.maximum(
        risk_hhi,
        MIN_WEIGHT_TOLERANCE
    )
)

print(
    f"Effective Positions : "
    f"{effective_positions:.2f}"
)

# =========================================================
# PORTFOLIO CONCENTRATION
# =========================================================

weight_hhi = np.sum(
    weights ** 2
)

effective_holdings = (

    1

    /

    np.maximum(
        weight_hhi,
        MIN_WEIGHT_TOLERANCE
    )
)

print(
    f"Effective Holdings : "
    f"{effective_holdings:.2f}"
)

# =========================================================
# RISK BUCKETS
# =========================================================

position_risk[
    "Risk_Bucket"
] = pd.cut(

    position_risk[
        "Risk_Contribution_Pct"
    ],

    bins=[
        -np.inf,
        1,
        3,
        5,
        np.inf
    ],

    labels=[
        "Low",
        "Medium",
        "High",
        "Critical"
    ]
)

risk_bucket_summary = (

    position_risk

    .groupby(
        "Risk_Bucket",
        observed=False
    )

    ["Risk_Contribution_Pct"]

    .sum()

    .reset_index()
)

# =========================================================
# PORTFOLIO RISK SUMMARY
# =========================================================

portfolio_risk_stats = pd.DataFrame({

    "Metric": [

        "Portfolio_Variance",

        "Portfolio_Volatility",

        "Effective_Holdings",

        "Effective_Risk_Positions",

        "Largest_Risk_Position",

        "Largest_Risk_Contribution_Pct"
    ],

    "Value": [

        portfolio_variance,

        portfolio_volatility,

        effective_holdings,

        effective_positions,

        largest_risk_position,

        largest_risk_pct
    ]
})

# =========================================================
# AUDIT METRICS
# =========================================================

audit_metrics[
    "Portfolio_Volatility"
] = float(
    portfolio_volatility
)

audit_metrics[
    "Effective_Holdings"
] = float(
    effective_holdings
)

audit_metrics[
    "Effective_Risk_Positions"
] = float(
    effective_positions
)

audit_metrics[
    "Largest_Risk_Position"
] = str(
    largest_risk_position
)

audit_metrics[
    "Largest_Risk_Contribution"
] = float(
    largest_risk_pct
)

# =========================================================
# PART 3 STARTS HERE
# =========================================================

#
# Next:
#
# Parametric VaR
# Historical VaR
# CVaR
# Expected Shortfall
# Downside Risk
#
# =========================================================

# =========================================================
# LOAD RETURN MATRIX
# =========================================================

print(
    "\n📉 Building VaR Analytics..."
)

RETURNS_MATRIX_FILE = (
    RISK_DIR
    / "returns_matrix.parquet"
)

if not RETURNS_MATRIX_FILE.exists():

    raise FileNotFoundError(
        RETURNS_MATRIX_FILE
    )

returns_matrix = pd.read_parquet(
    RETURNS_MATRIX_FILE
)

returns_matrix.columns = (

    returns_matrix.columns

    .astype(str)

    .str.upper()

    .str.strip()
)

# =========================================================
# PORTFOLIO RETURNS
# =========================================================

portfolio_return_symbols = [

    s

    for s in valid_symbols

    if s in returns_matrix.columns
]

portfolio_return_weights = (

    risk_universe

    .set_index("Symbol")

    .loc[
        portfolio_return_symbols,
        "Weight"
    ]

    .values
)

portfolio_return_weights = (

    portfolio_return_weights

    /

    portfolio_return_weights.sum()
)

portfolio_returns = (

    returns_matrix[
        portfolio_return_symbols
    ]

    .fillna(0)

    .values

    @

    portfolio_return_weights
)

portfolio_returns = pd.Series(
    portfolio_returns
)

# =========================================================
# PARAMETRIC VaR
# =========================================================

portfolio_daily_vol = (

    portfolio_volatility

    /

    np.sqrt(
        TRADING_DAYS
    )
)

parametric_var_95 = (
    VAR_CONFIDENCE_95
    *
    portfolio_daily_vol
)

parametric_var_99 = (
    VAR_CONFIDENCE_99
    *
    portfolio_daily_vol
)

print(
    f"Parametric VaR 95 : "
    f"-{parametric_var_95:.2%}"
)

print(
    f"Parametric VaR 99 : "
    f"-{parametric_var_99:.2%}"
)

# =========================================================
# HISTORICAL VaR
# =========================================================

historical_var_95 = abs(

    np.percentile(
        portfolio_returns,
        5
    )
)

historical_var_99 = abs(

    np.percentile(
        portfolio_returns,
        1
    )
)

print(
    f"Historical VaR 95 : "
    f"-{historical_var_95:.2%}"
)

print(
    f"Historical VaR 99 : "
    f"-{historical_var_99:.2%}"
)

# =========================================================
# CONDITIONAL VaR (CVaR)
# =========================================================

tail_95 = portfolio_returns[
    portfolio_returns
    <=
    np.percentile(
        portfolio_returns,
        5
    )
]

tail_99 = portfolio_returns[
    portfolio_returns
    <=
    np.percentile(
        portfolio_returns,
        1
    )
]

cvar_95 = abs(
    tail_95.mean()
)

cvar_99 = abs(
    tail_99.mean()
)

print(
    f"CVaR 95 : "
    f"-{cvar_95:.2%}"
)

print(
    f"CVaR 99 : "
    f"-{cvar_99:.2%}"
)

# =========================================================
# DOWNSIDE VOLATILITY
# =========================================================

negative_returns = portfolio_returns[
    portfolio_returns < 0
]

if len(
    negative_returns
) > 0:

    downside_volatility = (

        negative_returns.std()

        *

        np.sqrt(
            TRADING_DAYS
        )
    )

else:

    downside_volatility = 0.0

print(
    f"Downside Volatility : "
    f"{downside_volatility:.2%}"
)

# =========================================================
# SEMI VARIANCE
# =========================================================

semi_variance = np.mean(

    np.minimum(
        portfolio_returns,
        0
    ) ** 2
)

semi_deviation = np.sqrt(
    semi_variance
)

# =========================================================
# MAX DRAWDOWN
# =========================================================

cumulative_returns = (

    1
    +
    portfolio_returns
).cumprod()

running_max = np.maximum.accumulate(
    cumulative_returns
)

drawdown = (

    cumulative_returns

    /

    running_max

    - 1
)

max_drawdown = abs(
    drawdown.min()
)

print(
    f"Max Drawdown : "
    f"-{max_drawdown:.2%}"
)

# =========================================================
# RETURN DISTRIBUTION
# =========================================================

mean_daily_return = (
    portfolio_returns.mean()
)

annualized_return = (

    mean_daily_return

    *

    TRADING_DAYS
)

annualized_volatility = (
    portfolio_volatility
)

if annualized_volatility > 0:

    sharpe_ratio = (

        annualized_return

        /

        annualized_volatility
    )

else:

    sharpe_ratio = 0.0

# =========================================================
# VaR SUMMARY TABLE
# =========================================================

var_summary = pd.DataFrame({

    "Metric": [

        "Parametric_VaR_95",

        "Parametric_VaR_99",

        "Historical_VaR_95",

        "Historical_VaR_99",

        "CVaR_95",

        "CVaR_99",

        "Downside_Volatility",

        "Semi_Deviation",

        "Max_Drawdown",

        "Sharpe_Ratio"
    ],

    "Value": [

        parametric_var_95,

        parametric_var_99,

        historical_var_95,

        historical_var_99,

        cvar_95,

        cvar_99,

        downside_volatility,

        semi_deviation,

        max_drawdown,

        sharpe_ratio
    ]
})

# =========================================================
# RISK CLASSIFICATION
# =========================================================

if portfolio_volatility < 0.10:

    risk_level = "Low"

elif portfolio_volatility < 0.20:

    risk_level = "Moderate"

elif portfolio_volatility < 0.30:

    risk_level = "High"

else:

    risk_level = "Very High"

print(
    f"Risk Classification : "
    f"{risk_level}"
)

# =========================================================
# AUDIT METRICS
# =========================================================

audit_metrics[
    "Parametric_VaR_95"
] = float(
    parametric_var_95
)

audit_metrics[
    "Historical_VaR_95"
] = float(
    historical_var_95
)

audit_metrics[
    "CVaR_95"
] = float(
    cvar_95
)

audit_metrics[
    "Max_Drawdown"
] = float(
    max_drawdown
)

audit_metrics[
    "Sharpe_Ratio"
] = float(
    sharpe_ratio
)

audit_metrics[
    "Risk_Level"
] = risk_level

# =========================================================
# PART 4 STARTS HERE
# =========================================================

#
# Next:
#
# Factor Attribution
# Risk Budgeting
# Stress Testing
# Export Layer
#
# =========================================================

# =========================================================
# FACTOR ATTRIBUTION
# =========================================================

print(
    "\n🏛 Building Factor Attribution..."
)

available_factors = [

    f

    for f in factor_columns

    if (
        f in factor_covariance.index
        and
        f in factor_covariance.columns
    )
]

if len(available_factors) == 0:

    raise ValueError(
        "No common factors found between "
        "factor loadings and factor covariance."
    )

factor_columns = available_factors

factor_covariance = (

    factor_covariance

    .loc[
        factor_columns,
        factor_columns
    ]
)

factor_exposure_vector = np.array([

    (
        risk_universe[factor]
        *
        risk_universe["Weight"]
    ).sum()

    for factor in factor_columns

], dtype=np.float64)

F = factor_covariance.values.astype(
    np.float64
)

factor_variance = float(

    factor_exposure_vector.T

    @

    F

    @

    factor_exposure_vector
)

factor_marginal_risk = (
    F
    @
    factor_exposure_vector
)

factor_component_risk = (

    factor_exposure_vector
    *
    factor_marginal_risk
)

factor_total = np.maximum(

    np.abs(
        factor_component_risk
    ).sum(),

    MIN_WEIGHT_TOLERANCE
)

factor_attribution = pd.DataFrame({

    "Factor":
    factor_columns,

    "Exposure":
    factor_exposure_vector,

    "Marginal_Risk":
    factor_marginal_risk,

    "Component_Risk":
    factor_component_risk
})

factor_attribution[
    "Risk_Contribution_Pct"
] = (

    np.abs(
        factor_attribution[
            "Component_Risk"
        ]
    )

    /

    factor_total

    * 100
)

factor_attribution = (

    factor_attribution

    .sort_values(
        "Risk_Contribution_Pct",
        ascending=False
    )

    .reset_index(drop=True)
)

if factor_attribution.empty:

    dominant_factor = "NONE"
    dominant_factor_pct = 0.0

else:

    dominant_factor = str(
        factor_attribution.iloc[0]["Factor"]
    )

    dominant_factor_pct = float(
        factor_attribution.iloc[0][
            "Risk_Contribution_Pct"
        ]
    )

print(
    f"Dominant Factor : "
    f"{dominant_factor}"
)

print(
    f"Factor Share    : "
    f"{dominant_factor_pct:.2f}%"
)

# =========================================================
# STRESS TESTS
# =========================================================

print(
    "⚠ Building Stress Tests..."
)

stress_tests = pd.DataFrame({

    "Scenario": [

        "Market_Crash_10",

        "Market_Crash_20",

        "Market_Crash_30",

        "Vol_Shock_25",

        "Vol_Shock_50"
    ],

    "Portfolio_Impact_Pct": [

        -10.0,

        -20.0,

        -30.0,

        -portfolio_volatility
        * 100
        * 1.25,

        -portfolio_volatility
        * 100
        * 1.50
    ]
})

# =========================================================
# RISK BUDGET
# =========================================================

print(
    "📊 Building Risk Budget..."
)

risk_budget = position_risk[
    [
        "Symbol",
        "Weight",
        "Risk_Contribution_Pct"
    ]
].copy()

risk_budget[
    "Budget_Gap"
] = (

    risk_budget[
        "Risk_Contribution_Pct"
    ]

    -

    risk_budget[
        "Weight"
    ] * 100
)

# =========================================================
# TRACKING ERROR
# =========================================================

print(
    "📈 Building Tracking Error..."
)

equal_weight = np.repeat(

    1.0 / len(weights),

    len(weights)
)

active_weights = (
    weights
    -
    equal_weight
)

tracking_error = np.sqrt(

    active_weights.T

    @

    Sigma

    @

    active_weights
)

# =========================================================
# SUMMARY
# =========================================================

summary = pd.DataFrame({

    "Metric": [

        "Portfolio_Volatility",

        "Parametric_VaR_95",

        "Parametric_VaR_99",

        "Historical_VaR_95",

        "Historical_VaR_99",

        "CVaR_95",

        "CVaR_99",

        "Tracking_Error",

        "Effective_Holdings",

        "Effective_Risk_Positions",

        "Dominant_Factor",

        "Dominant_Factor_Pct",

        "Engine_Version",

        "Run_Date"
    ],

    "Value": [

        portfolio_volatility,

        parametric_var_95,

        parametric_var_99,

        historical_var_95,

        historical_var_99,

        cvar_95,

        cvar_99,

        tracking_error,

        effective_holdings,

        effective_positions,

        dominant_factor,

        dominant_factor_pct,

        ENGINE_VERSION,

        datetime.now().strftime(
            "%Y-%m-%d"
        )
    ]
})

# =========================================================
# OUTPUT FILES
# =========================================================

POSITION_RISK_FILE = (
    RISK_DIR
    / "portfolio_risk_contributions.csv"
)

VAR_FILE = (
    RISK_DIR
    / "portfolio_var.csv"
)

FACTOR_ATTRIBUTION_FILE = (
    RISK_DIR
    / "portfolio_factor_attribution.csv"
)

STRESS_FILE = (
    RISK_DIR
    / "portfolio_stress_tests.csv"
)

RISK_BUDGET_FILE = (
    RISK_DIR
    / "portfolio_risk_budget.csv"
)

TRACKING_ERROR_FILE = (
    RISK_DIR
    / "portfolio_tracking_error.csv"
)

# =========================================================
# SAVE OUTPUTS
# =========================================================

print(
    "💾 Saving Outputs..."
)

summary.to_csv(
    SUMMARY_FILE,
    index=False
)

position_risk.to_csv(
    POSITION_RISK_FILE,
    index=False
)

var_summary.to_csv(
    VAR_FILE,
    index=False
)

factor_attribution.to_csv(
    FACTOR_ATTRIBUTION_FILE,
    index=False
)

stress_tests.to_csv(
    STRESS_FILE,
    index=False
)

risk_budget.to_csv(
    RISK_BUDGET_FILE,
    index=False
)

pd.DataFrame({

    "Metric": [
        "Tracking_Error"
    ],

    "Value": [
        tracking_error
    ]

}).to_csv(

    TRACKING_ERROR_FILE,

    index=False
)

# =========================================================
# AUDIT REPORT
# =========================================================

audit_metrics[
    "Tracking_Error"
] = float(
    tracking_error
)

audit_metrics[
    "Dominant_Factor"
] = dominant_factor

audit_metrics[
    "Dominant_Factor_Pct"
] = float(
    dominant_factor_pct
)

audit_report = pd.DataFrame({

    "Metric":
    list(
        audit_metrics.keys()
    ),

    "Value":
    list(
        audit_metrics.values()
    )
})

audit_report.to_csv(
    AUDIT_FILE,
    index=False
)

# =========================================================
# FINAL REPORT
# =========================================================

print(
    "\n=========================================================="
)

print(
    "🏁 PORTFOLIO RISK ENGINE COMPLETE"
)

print(
    "=========================================================="
)

print(
    f"Portfolio Volatility : "
    f"{portfolio_volatility:.2%}"
)

print(
    f"Historical VaR 95    : "
    f"{historical_var_95:.2%}"
)

print(
    f"CVaR 95              : "
    f"{cvar_95:.2%}"
)

print(
    f"Tracking Error       : "
    f"{tracking_error:.2%}"
)

print(
    f"Effective Holdings   : "
    f"{effective_holdings:.2f}"
)

print(
    f"Risk Positions       : "
    f"{effective_positions:.2f}"
)

print(
    f"Dominant Factor      : "
    f"{dominant_factor}"
)

print(
    f"Factor Share         : "
    f"{dominant_factor_pct:.2f}%"
)

print(
    "\nOutput Directory:"
)

print(
    RISK_DIR
)

print(
    "=========================================================="
)

# =========================================================
# END OF FILE
# =========================================================