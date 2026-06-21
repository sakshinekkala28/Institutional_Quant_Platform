"""
=========================================================
FACTOR RISK MODEL
=========================================================

Institutional Statistical Risk Model

Purpose
-------
Decompose portfolio risk into:

• Factor Risk
• Specific Risk
• Total Risk

Built From
----------
returns_matrix_builder.py
covariance_matrix_engine.py

Methodology
-----------
Statistical PCA Risk Model

R = BFB' + D

Where:

R = Asset Covariance Matrix
B = Factor Exposure Matrix
F = Factor Covariance Matrix
D = Specific Risk Matrix

Outputs
-------
factor_covariance.parquet
specific_risk.csv
factor_risk_contribution.csv
portfolio_risk_attribution.csv
factor_risk_summary.csv

=========================================================
"""

from pathlib import Path
from datetime import datetime

import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# =========================================================
# CONFIGURATION
# =========================================================

ENGINE_NAME = "FACTOR_RISK_MODEL"

ENGINE_VERSION = "1.0.0"

TRADING_DAYS = 252

MAX_FACTOR_COUNT = None

MIN_PORTFOLIO_HOLDINGS = 5

RISK_TOLERANCE = 1e-8

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

# =========================================================
# INPUT FILES
# =========================================================

PORTFOLIO_FILE = (
    PORTFOLIO_DIR
    / "live_portfolio.csv"
)

COVARIANCE_FILE = (
    RISK_DIR
    / "shrinkage_covariance.parquet"
)

FACTOR_FILE = (
    RISK_DIR
    / "eigenfactor_risk.parquet"
)

# =========================================================
# OUTPUT FILES
# =========================================================

FACTOR_COVARIANCE_FILE = (
    RISK_DIR
    / "factor_covariance.parquet"
)

SPECIFIC_RISK_FILE = (
    RISK_DIR
    / "specific_risk.csv"
)

FACTOR_CONTRIBUTION_FILE = (
    RISK_DIR
    / "factor_risk_contribution.csv"
)

PORTFOLIO_ATTRIBUTION_FILE = (
    RISK_DIR
    / "portfolio_risk_attribution.csv"
)

SUMMARY_FILE = (
    RISK_DIR
    / "factor_risk_summary.csv"
)

AUDIT_FILE = (
    RISK_DIR
    / "factor_risk_audit.csv"
)

# =========================================================
# LOAD INPUTS
# =========================================================

print(
    "\n📥 Loading Risk Inputs..."
)

required_files = [

    PORTFOLIO_FILE,

    COVARIANCE_FILE,

    FACTOR_FILE
]

for file in required_files:

    if not file.exists():

        raise FileNotFoundError(
            f"Missing file: {file}"
        )

portfolio = pd.read_csv(
    PORTFOLIO_FILE
)

covariance_matrix = pd.read_parquet(
    COVARIANCE_FILE
)

factor_loadings = pd.read_parquet(
    FACTOR_FILE
)

# =========================================================
# PORTFOLIO VALIDATION
# =========================================================

print(
    "✔ Validating Portfolio..."
)

required_cols = [

    "Symbol",

    "Weight"
]

missing_cols = [

    c

    for c in required_cols

    if c not in portfolio.columns
]

if missing_cols:

    raise ValueError(
        f"Missing columns: {missing_cols}"
    )

if len(portfolio) < MIN_PORTFOLIO_HOLDINGS:

    raise ValueError(
        "Portfolio too small."
    )

# =========================================================
# NORMALIZE WEIGHTS
# =========================================================

portfolio = portfolio.copy()

portfolio["Weight"] = (

    portfolio["Weight"]

    /

    portfolio["Weight"].sum()
)

# =========================================================
# FACTOR LOADING VALIDATION
# =========================================================

print(
    "📈 Loading Factor Structure..."
)

if "Symbol" not in factor_loadings.columns:

    raise ValueError(
        "Factor model missing Symbol column."
    )

factor_columns = [

    c

    for c in factor_loadings.columns

    if c != "Symbol"
]

if len(factor_columns) == 0:

    raise ValueError(
        "No PCA factors found."
    )

if MAX_FACTOR_COUNT is not None:
    factor_columns = factor_columns[:MAX_FACTOR_COUNT]
    
print(
    f"Factors Loaded : "
    f"{len(factor_columns)}"
)

portfolio_set = set(
    portfolio["Symbol"]
)

factor_set = set(
    factor_loadings["Symbol"]
)

overlap = portfolio_set.intersection(
    factor_set
)

print(
    f"Portfolio Symbols : "
    f"{len(portfolio_set)}"
)

print(
    f"Factor Symbols    : "
    f"{len(factor_set)}"
)

print(
    f"Overlap           : "
    f"{len(overlap)}"
)

# =========================================================
# SYMBOL NORMALIZATION
# =========================================================

portfolio["Symbol"] = (
    portfolio["Symbol"]
    .astype(str)
    .str.strip()
    .str.upper()
)

factor_loadings["Symbol"] = (
    factor_loadings["Symbol"]
    .astype(str)
    .str.strip()
    .str.upper()
)

# Add NSE suffix if portfolio doesn't contain it

portfolio["Symbol"] = np.where(
    portfolio["Symbol"].str.endswith(".NS"),
    portfolio["Symbol"],
    portfolio["Symbol"] + ".NS"
)
# =========================================================
# ALIGN UNIVERSE
# =========================================================

portfolio["Symbol"] = (
    portfolio["Symbol"]
    .astype(str)
    .str.strip()
    .str.upper()
)

factor_loadings["Symbol"] = (
    factor_loadings["Symbol"]
    .astype(str)
    .str.strip()
    .str.upper()
)

portfolio_factor = portfolio.merge(

    factor_loadings[
        ["Symbol"] + factor_columns
    ],

    on="Symbol",

    how="inner"
)

matched_symbols = set(
    portfolio_factor["Symbol"]
)

missing_symbols = sorted(
    set(portfolio["Symbol"])
    - matched_symbols
)

print(
    "\nMissing Factor Exposures:"
)

print(
    missing_symbols
)

pd.DataFrame({

    "Symbol": missing_symbols

}).to_csv(

    RISK_DIR
    / "missing_factor_symbols.csv",

    index=False
)

if portfolio_factor.empty:

    raise ValueError(
        "No overlap between portfolio and factor universe."
    )

matched_holdings = len(
    portfolio_factor
)

print(
    f"Matched Holdings : "
    f"{matched_holdings}"
)

# =========================================================
# ALIGN COVARIANCE MATRIX
# =========================================================

portfolio_symbols = (

    portfolio_factor[
        "Symbol"
    ]

    .tolist()
)

valid_symbols = [

    s

    for s in portfolio_symbols

    if s in covariance_matrix.index
]

portfolio_factor = (

    portfolio_factor[
        portfolio_factor[
            "Symbol"
        ]

        .isin(
            valid_symbols
        )
    ]
)

if len(portfolio_factor) == 0:

    raise ValueError(
        "No symbols found in covariance matrix."
    )

covariance_matrix = (

    covariance_matrix.loc[
        valid_symbols,
        valid_symbols
    ]
)

# =========================================================
# BUILD EXPOSURE MATRIX
# =========================================================

print(
    "🏗 Building Factor Exposure Matrix..."
)

B = (

    portfolio_factor[
        factor_columns
    ]

    .astype(
        np.float64
    )

    .values
)

weights = (

    portfolio_factor[
        "Weight"
    ]

    .values

    .astype(
        np.float64
    )
)

symbols = (

    portfolio_factor[
        "Symbol"
    ]

    .tolist()
)

n_assets = len(
    symbols
)

n_factors = len(
    factor_columns
)

print(
    f"Assets  : {n_assets}"
)

print(
    f"Factors : {n_factors}"
)

# =========================================================
# PORTFOLIO FACTOR EXPOSURE
# =========================================================

portfolio_factor_exposure = (

    weights

    @

    B
)

factor_exposure_df = pd.DataFrame({

    "Factor":
    factor_columns,

    "Exposure":
    portfolio_factor_exposure
})

# =========================================================
# AUDIT OBJECT
# =========================================================

audit_metrics = {

    "Engine":
    ENGINE_NAME,

    "Version":
    ENGINE_VERSION,

    "Run_Time":
    datetime.now(),

    "Assets":
    n_assets,

    "Factors":
    n_factors
}

# =========================================================
# PART 2 STARTS HERE
# =========================================================

#
# Next:
#
# Factor Covariance Matrix
# Specific Risk Matrix
# Common Risk
# Idiosyncratic Risk
#
# =========================================================

# =========================================================
# FACTOR COVARIANCE MATRIX
# =========================================================

print(
    "\n📊 Building Factor Covariance Matrix..."
)

# ---------------------------------------------------------
# PCA Statistical Risk Model
#
# R = BFB' + D
#
# Estimate:
#
# F = (B'B)^(-1) B' R B (B'B)^(-1)
#
# ---------------------------------------------------------

BtB = (

    B.T

    @

    B
)

# Numerical stability

BtB += (

    np.eye(
        BtB.shape[0]
    )

    * 1e-8
)

BtB_inv = np.linalg.pinv(
    BtB
)

R = covariance_matrix.values.astype(
    np.float64
)

F = (

    BtB_inv

    @

    B.T

    @

    R

    @

    B

    @

    BtB_inv
)

# Symmetrize

F = (

    F
    +
    F.T
) / 2.0

factor_covariance = pd.DataFrame(

    F,

    index=factor_columns,

    columns=factor_columns
)

print(
    f"Factor Covariance Shape : "
    f"{factor_covariance.shape}"
)

# =========================================================
# COMMON RISK MATRIX
# =========================================================

print(
    "🏗 Building Common Risk Matrix..."
)

common_risk = (

    B

    @

    F

    @

    B.T
)

common_risk = (

    common_risk
    +
    common_risk.T
) / 2.0

common_risk_df = pd.DataFrame(

    common_risk,

    index=symbols,

    columns=symbols
)

# =========================================================
# SPECIFIC RISK MATRIX
# =========================================================

print(
    "🔍 Estimating Specific Risk..."
)

specific_risk_matrix = (

    R
    -
    common_risk
)

specific_risk_matrix = (

    specific_risk_matrix
    +
    specific_risk_matrix.T
) / 2.0

# =========================================================
# REPAIR NEGATIVE DIAGONALS
# =========================================================

specific_diag = np.diag(
    specific_risk_matrix
)

specific_diag = np.maximum(

    specific_diag,

    RISK_TOLERANCE
)

specific_risk_matrix = np.diag(
    specific_diag
)

specific_risk_df = pd.DataFrame({

    "Symbol":
    symbols,

    "Specific_Variance":
    specific_diag,

    "Specific_Volatility":
    np.sqrt(
        specific_diag
    )
})

# =========================================================
# TOTAL RISK VECTOR
# =========================================================

total_variance = np.diag(
    R
)

common_variance = np.diag(
    common_risk
)

specific_variance = specific_diag

asset_risk = pd.DataFrame({

    "Symbol":
    symbols,

    "Total_Variance":
    total_variance,

    "Common_Variance":
    common_variance,

    "Specific_Variance":
    specific_variance
})

# ---------------------------------------------------------
# Convert to percentages
# ---------------------------------------------------------

asset_risk[
    "Factor_Risk_Pct"
] = (

    asset_risk[
        "Common_Variance"
    ]

    /

    np.maximum(
        asset_risk[
            "Total_Variance"
        ],
        RISK_TOLERANCE
    )

    * 100
)

asset_risk[
    "Specific_Risk_Pct"
] = (

    asset_risk[
        "Specific_Variance"
    ]

    /

    np.maximum(
        asset_risk[
            "Total_Variance"
        ],
        RISK_TOLERANCE
    )

    * 100
)

# =========================================================
# FACTOR IMPORTANCE
# =========================================================

print(
    "📈 Building Factor Importance..."
)

factor_variance = np.diag(
    F
)

factor_importance = pd.DataFrame({

    "Factor":
    factor_columns,

    "Variance":
    factor_variance
})

factor_importance[
    "Risk_Contribution_Pct"
] = (

    factor_importance[
        "Variance"
    ]

    /

    factor_importance[
        "Variance"
    ].sum()

    * 100
)

factor_importance = (

    factor_importance

    .sort_values(

        "Risk_Contribution_Pct",

        ascending=False
    )
)

# =========================================================
# COMMON VS SPECIFIC RISK
# =========================================================

portfolio_common_variance = (
    weights.T
    @
    common_risk
    @
    weights
)

portfolio_specific_variance = (
    weights.T
    @
    specific_risk_matrix
    @
    weights
)

portfolio_total_variance = (

    portfolio_common_variance

    +

    portfolio_specific_variance
)

factor_share = (

    portfolio_common_variance

    /

    max(
        portfolio_total_variance,
        RISK_TOLERANCE
    )
)

specific_share = (

    portfolio_specific_variance

    /

    max(
        portfolio_total_variance,
        RISK_TOLERANCE
    )
)

print(
    f"Factor Risk Share   : "
    f"{factor_share:.2%}"
)

print(
    f"Specific Risk Share : "
    f"{specific_share:.2%}"
)

# =========================================================
# FACTOR DIVERSIFICATION
# =========================================================

factor_weights = (

    factor_importance[
        "Risk_Contribution_Pct"
    ]

    / 100
)

factor_hhi = np.sum(
    factor_weights ** 2
)

effective_factors = (

    1

    /

    max(
        factor_hhi,
        RISK_TOLERANCE
    )
)

print(
    f"Effective Factors : "
    f"{effective_factors:.2f}"
)

# =========================================================
# AUDIT
# =========================================================

audit_metrics[
    "Factor_Risk_Share"
] = float(
    factor_share
)

audit_metrics[
    "Specific_Risk_Share"
] = float(
    specific_share
)

audit_metrics[
    "Effective_Factors"
] = float(
    effective_factors
)

audit_metrics[
    "Factor_HHI"
] = float(
    factor_hhi
)

# =========================================================
# PART 3 STARTS HERE
# =========================================================

#
# Next:
#
# Portfolio Risk Attribution
# Marginal Risk
# Component Risk
# Factor Contributions
# Portfolio Risk Decomposition
#
# =========================================================

# =========================================================
# PORTFOLIO RISK ATTRIBUTION
# =========================================================

print(
    "\n⚖ Building Portfolio Risk Attribution..."
)

# ---------------------------------------------------------
# Portfolio Variance
#
# σ² = w'Rw
#
# ---------------------------------------------------------

portfolio_variance = (

    weights.T

    @

    R

    @

    weights
)

portfolio_variance = max(
    portfolio_variance,
    RISK_TOLERANCE
)

portfolio_volatility = np.sqrt(
    portfolio_variance
)

print(
    f"Portfolio Volatility : "
    f"{portfolio_volatility:.2%}"
)

# =========================================================
# MARGINAL RISK CONTRIBUTION
# =========================================================

print(
    "📈 Building Marginal Risk..."
)

marginal_risk = (

    R

    @

    weights
)

marginal_risk = (

    marginal_risk

    /

    portfolio_volatility
)

# =========================================================
# COMPONENT RISK CONTRIBUTION
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
        RISK_TOLERANCE
    )
)

asset_risk_contribution = pd.DataFrame({

    "Symbol":
    symbols,

    "Weight":
    weights,

    "Marginal_Risk":
    marginal_risk,

    "Component_Risk":
    component_risk,

    "Risk_Contribution_Pct":
    component_risk_pct * 100
})

asset_risk_contribution = (

    asset_risk_contribution

    .sort_values(

        "Risk_Contribution_Pct",

        ascending=False
    )
)

# =========================================================
# FACTOR RISK CONTRIBUTION
# =========================================================

print(
    "🏛 Building Factor Risk Attribution..."
)

portfolio_factor_exposure = (

    weights

    @

    B
)

factor_marginal_risk = (

    F

    @

    portfolio_factor_exposure
)

factor_component_risk = (

    portfolio_factor_exposure

    *

    factor_marginal_risk
)

factor_total_risk = np.sum(
    np.abs(
        factor_component_risk
    )
)

factor_risk_contribution = pd.DataFrame({

    "Factor":
    factor_columns,

    "Exposure":
    portfolio_factor_exposure,

    "Marginal_Risk":
    factor_marginal_risk,

    "Component_Risk":
    factor_component_risk
})

factor_risk_contribution[
    "Risk_Contribution_Pct"
] = (

    np.abs(

        factor_risk_contribution[
            "Component_Risk"
        ]
    )

    /

    max(
        factor_total_risk,
        RISK_TOLERANCE
    )

    * 100
)

factor_risk_contribution = (

    factor_risk_contribution

    .sort_values(

        "Risk_Contribution_Pct",

        ascending=False
    )
)

# =========================================================
# TOP RISK FACTOR
# =========================================================

dominant_factor = (

    factor_risk_contribution

    .iloc[0]

    ["Factor"]
)

dominant_factor_pct = (

    factor_risk_contribution

    .iloc[0]

    ["Risk_Contribution_Pct"]
)

print(
    f"Dominant Factor : "
    f"{dominant_factor}"
)

print(
    f"Factor Risk Share : "
    f"{dominant_factor_pct:.2f}%"
)

# =========================================================
# FACTOR VS SPECIFIC ATTRIBUTION
# =========================================================

factor_variance_contribution = (

    portfolio_factor_exposure

    @

    F

    @

    portfolio_factor_exposure
)

specific_variance_contribution = (

    weights.T

    @

    specific_risk_matrix

    @

    weights
)

factor_variance_contribution = max(
    factor_variance_contribution,
    0.0
)

specific_variance_contribution = max(
    specific_variance_contribution,
    0.0
)

total_variance_check = (

    factor_variance_contribution

    +

    specific_variance_contribution
)

factor_pct = (

    factor_variance_contribution

    /

    max(
        total_variance_check,
        RISK_TOLERANCE
    )

    * 100
)

specific_pct = (

    specific_variance_contribution

    /

    max(
        total_variance_check,
        RISK_TOLERANCE
    )

    * 100
)

risk_decomposition = pd.DataFrame({

    "Risk_Source": [

        "Factor_Risk",

        "Specific_Risk"
    ],

    "Variance": [

        factor_variance_contribution,

        specific_variance_contribution
    ],

    "Contribution_Pct": [

        factor_pct,

        specific_pct
    ]
})

print(
    f"Factor Risk   : "
    f"{factor_pct:.2f}%"
)

print(
    f"Specific Risk : "
    f"{specific_pct:.2f}%"
)

# =========================================================
# EFFECTIVE RISK CONTRIBUTORS
# =========================================================

asset_hhi = np.sum(
    component_risk_pct ** 2
)

effective_risk_positions = (

    1

    /

    max(
        asset_hhi,
        RISK_TOLERANCE
    )
)

print(
    f"Effective Risk Positions : "
    f"{effective_risk_positions:.2f}"
)

# =========================================================
# PORTFOLIO ATTRIBUTION TABLE
# =========================================================

portfolio_attribution = pd.DataFrame({

    "Metric": [

        "Portfolio_Volatility",

        "Portfolio_Variance",

        "Factor_Risk_Pct",

        "Specific_Risk_Pct",

        "Effective_Risk_Positions",

        "Effective_Factors",

        "Dominant_Factor"
    ],

    "Value": [

        portfolio_volatility,

        portfolio_variance,

        factor_pct,

        specific_pct,

        effective_risk_positions,

        effective_factors,

        dominant_factor
    ]
})

# =========================================================
# TOP RISK CONTRIBUTORS
# =========================================================

top_risk_positions = (

    asset_risk_contribution

    .head(20)

    .copy()
)

top_risk_factors = (

    factor_risk_contribution

    .head(10)

    .copy()
)

# =========================================================
# AUDIT METRICS
# =========================================================

audit_metrics[
    "Portfolio_Volatility"
] = float(
    portfolio_volatility
)

audit_metrics[
    "Factor_Risk_Pct"
] = float(
    factor_pct
)

audit_metrics[
    "Specific_Risk_Pct"
] = float(
    specific_pct
)

audit_metrics[
    "Effective_Risk_Positions"
] = float(
    effective_risk_positions
)

audit_metrics[
    "Dominant_Factor"
] = str(
    dominant_factor
)

# =========================================================
# PART 4 STARTS HERE
# =========================================================

#
# Next:
#
# Exports
# Validation
# Audit Reports
# Production Summary
#
# =========================================================

# =========================================================
# FINAL VALIDATION
# =========================================================

print(
    "\n✔ Running Final Validation..."
)

if factor_covariance.empty:

    raise ValueError(
        "Factor covariance matrix empty."
    )

if factor_risk_contribution.empty:

    raise ValueError(
        "Factor risk contribution empty."
    )

if asset_risk_contribution.empty:

    raise ValueError(
        "Asset risk attribution empty."
    )

if portfolio_volatility <= 0:

    raise ValueError(
        "Portfolio volatility invalid."
    )

if np.isnan(
    portfolio_volatility
):

    raise ValueError(
        "Portfolio volatility NaN."
    )

# =========================================================
# FACTOR COVARIANCE VALIDATION
# =========================================================

factor_covariance = pd.DataFrame(

    (
        factor_covariance.values
        +
        factor_covariance.values.T
    )

    / 2.0,

    index=factor_covariance.index,

    columns=factor_covariance.columns
)

# =========================================================
# EIGENVALUE CHECK
# =========================================================

try:

    factor_eigenvalues = (

        np.linalg.eigvalsh(

            factor_covariance.values
        )
    )

    min_factor_eigenvalue = float(

        factor_eigenvalues.min()
    )

except Exception:

    min_factor_eigenvalue = np.nan

audit_metrics[
    "Min_Factor_Eigenvalue"
] = min_factor_eigenvalue

# =========================================================
# MEMORY OPTIMIZATION
# =========================================================

factor_covariance = (

    factor_covariance

    .astype(
        np.float32
    )
)

# =========================================================
# OUTPUT FILES
# =========================================================

print(
    "💾 Saving Outputs..."
)

TOP_RISK_POSITIONS_FILE = (

    RISK_DIR

    / "top_risk_positions.csv"
)

TOP_RISK_FACTORS_FILE = (

    RISK_DIR

    / "top_risk_factors.csv"
)

# =========================================================
# EXPORT PARQUET
# =========================================================

factor_covariance.to_parquet(

    FACTOR_COVARIANCE_FILE
)

# =========================================================
# EXPORT CSV
# =========================================================

specific_risk_df.to_csv(

    SPECIFIC_RISK_FILE,

    index=False
)

factor_risk_contribution.to_csv(

    FACTOR_CONTRIBUTION_FILE,

    index=False
)

portfolio_attribution.to_csv(

    PORTFOLIO_ATTRIBUTION_FILE,

    index=False
)

top_risk_positions.to_csv(

    TOP_RISK_POSITIONS_FILE,

    index=False
)

top_risk_factors.to_csv(

    TOP_RISK_FACTORS_FILE,

    index=False
)

# =========================================================
# SUMMARY REPORT
# =========================================================

summary = pd.DataFrame({

    "Metric": [

        "Portfolio_Volatility",

        "Factor_Risk_Pct",

        "Specific_Risk_Pct",

        "Effective_Factors",

        "Effective_Risk_Positions",

        "Dominant_Factor",

        "Assets",

        "Factors",

        "Engine_Version",

        "Run_Date"
    ],

    "Value": [

        portfolio_volatility,

        factor_pct,

        specific_pct,

        effective_factors,

        effective_risk_positions,

        dominant_factor,

        n_assets,

        n_factors,

        ENGINE_VERSION,

        datetime.now()

        .strftime(
            "%Y-%m-%d"
        )
    ]
})

summary.to_csv(

    SUMMARY_FILE,

    index=False
)

# =========================================================
# AUDIT REPORT
# =========================================================

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
# RISK QUALITY SCORE
# =========================================================

quality_score = 100.0

if factor_pct < 50:

    quality_score -= 15

if effective_factors < 3:

    quality_score -= 10

if effective_risk_positions < 10:

    quality_score -= 10

if np.isnan(
    min_factor_eigenvalue
):

    quality_score -= 15

quality_score = max(
    quality_score,
    0
)

audit_metrics[
    "Quality_Score"
] = quality_score

# =========================================================
# FINAL REPORT
# =========================================================

print(
    "\n=========================================================="
)

print(
    "🏁 FACTOR RISK MODEL COMPLETE"
)

print(
    "=========================================================="
)

print(
    f"Assets                  : "
    f"{n_assets:,}"
)

print(
    f"Factors                 : "
    f"{n_factors}"
)

print(
    f"Portfolio Volatility    : "
    f"{portfolio_volatility:.2%}"
)

print(
    f"Factor Risk             : "
    f"{factor_pct:.2f}%"
)

print(
    f"Specific Risk           : "
    f"{specific_pct:.2f}%"
)

print(
    f"Effective Factors       : "
    f"{effective_factors:.2f}"
)

print(
    f"Effective Risk Positions: "
    f"{effective_risk_positions:.2f}"
)

print(
    f"Dominant Factor         : "
    f"{dominant_factor}"
)

print(
    f"Min Factor Eigenvalue   : "
    f"{min_factor_eigenvalue:.8f}"
)

print(
    f"Quality Score           : "
    f"{quality_score:.2f}"
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