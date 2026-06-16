"""
=========================================================
COVARIANCE MATRIX ENGINE
=========================================================

Institutional Quant Platform

Purpose
-------
Build institutional-grade covariance and
correlation matrices for:

• Portfolio Optimization
• Risk Modeling
• Factor Models
• Stress Testing
• Risk Attribution

Inputs
------
returns_matrix.parquet
log_returns_matrix.parquet

Outputs
-------
covariance_matrix.parquet
correlation_matrix.parquet
shrinkage_covariance.parquet
eigenfactor_risk.parquet
covariance_audit.csv

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

ENGINE_NAME = "COVARIANCE_MATRIX_ENGINE"

ENGINE_VERSION = "2.0.0"

TRADING_DAYS = 252

USE_LOG_RETURNS = True

MIN_SECURITIES = 100

MIN_OBSERVATIONS = 252

MAX_ALLOWED_MISSING = 0.05

# Ledoit-Wolf Shrinkage

ENABLE_SHRINKAGE = True

# PCA Risk Model

ENABLE_PCA = True

N_PCA_FACTORS = 20

# Numerical Stability

EIGENVALUE_FLOOR = 1e-8

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

RISK_DIR = (
    ROOT
    / "data"
    / "risk"
)

RETURNS_FILE = (
    RISK_DIR
    / "returns_matrix.parquet"
)

LOG_RETURNS_FILE = (
    RISK_DIR
    / "log_returns_matrix.parquet"
)

COVARIANCE_FILE = (
    RISK_DIR
    / "covariance_matrix.parquet"
)

CORRELATION_FILE = (
    RISK_DIR
    / "correlation_matrix.parquet"
)

SHRINKAGE_FILE = (
    RISK_DIR
    / "shrinkage_covariance.parquet"
)

PCA_FILE = (
    RISK_DIR
    / "eigenfactor_risk.parquet"
)

AUDIT_FILE = (
    RISK_DIR
    / "covariance_audit.csv"
)

# =========================================================
# LOAD INPUTS
# =========================================================

print(
    "\n📥 Loading Return Matrices..."
)

if USE_LOG_RETURNS:

    input_file = LOG_RETURNS_FILE

else:

    input_file = RETURNS_FILE

if not input_file.exists():

    raise FileNotFoundError(
        f"Missing file: {input_file}"
    )

returns_matrix = pd.read_parquet(
    input_file
)

PORTFOLIO_FILE = (
    ROOT
    / "data"
    / "portfolios"
    / "live_portfolio.csv"
)

portfolio_symbols = set()

if PORTFOLIO_FILE.exists():

    portfolio_df = pd.read_csv(
        PORTFOLIO_FILE
    )

    portfolio_symbols = set(

        portfolio_df["Symbol"]
        .astype(str)
        .str.upper()
        .str.strip()
        + ".NS"
    )

# =========================================================
# INDEX VALIDATION
# =========================================================

if not isinstance(
    returns_matrix.index,
    pd.DatetimeIndex
):

    try:

        returns_matrix.index = pd.to_datetime(
            returns_matrix.index
        )

    except Exception:

        raise ValueError(
            "Date index invalid."
        )

# =========================================================
# MATRIX VALIDATION
# =========================================================

print(
    "✔ Validating Return Matrix..."
)

rows, cols = returns_matrix.shape

if cols < MIN_SECURITIES:

    raise ValueError(
        f"Only {cols} securities."
    )

if rows < MIN_OBSERVATIONS:

    raise ValueError(
        f"Only {rows} observations."
    )

# =========================================================
# NUMERIC VALIDATION
# =========================================================

returns_matrix = returns_matrix.apply(
    pd.to_numeric,
    errors="coerce"
)

# =========================================================
# COVERAGE CHECK
# =========================================================

coverage = (
    returns_matrix
    .notna()
    .mean()
)

coverage_stats = pd.DataFrame({

    "Symbol":
    coverage.index,

    "Coverage":
    coverage.values,

    "Observations":
    returns_matrix.notna().sum().values
})

# ---------------------------------------------------------
# KEEP RULE
#
# 1. Normal securities:
#    coverage >= 95%
#
# 2. Recent IPOs:
#    >= 252 observations
#
# ---------------------------------------------------------

MIN_IPO_HISTORY = 252

keep_symbols = set(

    coverage_stats.loc[
        (
            coverage_stats["Coverage"]
            >= (1 - MAX_ALLOWED_MISSING)
        )
        |
        (
            coverage_stats["Observations"]
            >= MIN_IPO_HISTORY
        ),
        "Symbol"
    ]
)

keep_symbols |= portfolio_symbols

keep_symbols = sorted(
    keep_symbols.intersection(
        returns_matrix.columns
    )
)

removed_symbols = (
    len(coverage_stats)
    -
    len(keep_symbols)
)

print(
    f"Coverage Filter Removed: "
    f"{removed_symbols:,}"
)

coverage_stats.loc[
    ~coverage_stats["Symbol"].isin(
        keep_symbols
    )
].to_csv(
    RISK_DIR / "coverage_rejections_covariance.csv",
    index=False
)

returns_matrix = (
    returns_matrix[
        keep_symbols
    ]
)

# =========================================================
# FINAL CLEANING
# =========================================================

returns_matrix = (

    returns_matrix

    .replace(
        [np.inf, -np.inf],
        np.nan
    )
)

returns_matrix = (

    returns_matrix

    .dropna(
        axis=1,
        how="all"
    )
)

returns_matrix = (

    returns_matrix

    .dropna(
        axis=0,
        how="all"
    )
)

# =========================================================
# DIMENSIONS
# =========================================================

n_days = returns_matrix.shape[0]

n_assets = returns_matrix.shape[1]

print(
    f"Trading Days : "
    f"{n_days:,}"
)

print(
    f"Securities   : "
    f"{n_assets:,}"
)

# =========================================================
# MATRIX DIAGNOSTICS
# =========================================================

print(
    "🔍 Building Diagnostics..."
)

matrix_density = (

    returns_matrix

    .notna()

    .mean()

    .mean()
)

missing_cells = (

    returns_matrix

    .isna()

    .sum()

    .sum()
)

print(
    f"Matrix Density : "
    f"{matrix_density:.2%}"
)

print(
    f"Missing Cells  : "
    f"{missing_cells:,}"
)

# =========================================================
# VOLATILITY VECTOR
# =========================================================

asset_volatility = (

    returns_matrix

    .std()

    * np.sqrt(
        TRADING_DAYS
    )
)

volatility_summary = pd.DataFrame({

    "Metric": [

        "Mean",

        "Median",

        "Min",

        "Max"
    ],

    "Value": [

        asset_volatility.mean(),

        asset_volatility.median(),

        asset_volatility.min(),

        asset_volatility.max()
    ]
})

print(
    f"Average Volatility : "
    f"{asset_volatility.mean():.2%}"
)

# =========================================================
# PREPARE MATRIX
# =========================================================

returns_matrix = (

    returns_matrix

    .astype(
        np.float32
    )
)

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

    "Trading_Days":

    n_days,

    "Securities":

    n_assets,

    "Density":

    matrix_density,

    "Missing_Cells":

    int(
        missing_cells
    )
}

# =========================================================
# PART 2 STARTS HERE
# =========================================================

#
# Next:
#
# Covariance Matrix
# Correlation Matrix
# Annualization
# Volatility Surface
#
# =========================================================
# =========================================================
# SAMPLE COVARIANCE MATRIX
# =========================================================

print(
    "\n📊 Building Covariance Matrix..."
)

covariance_matrix = (

    returns_matrix

    .cov(
        min_periods=MIN_OBSERVATIONS
    )
)

# =========================================================
# ANNUALIZE COVARIANCE
# =========================================================

annualized_covariance = (

    covariance_matrix

    * TRADING_DAYS
)

# =========================================================
# CORRELATION MATRIX
# =========================================================

print(
    "🔗 Building Correlation Matrix..."
)

correlation_matrix = (

    returns_matrix

    .corr(
        min_periods=MIN_OBSERVATIONS
    )
)

# =========================================================
# NUMERICAL CLEANUP
# =========================================================

covariance_matrix = (

    covariance_matrix

    .replace(
        [np.inf, -np.inf],
        np.nan
    )
)

correlation_matrix = (

    correlation_matrix

    .replace(
        [np.inf, -np.inf],
        np.nan
    )
)

covariance_matrix = (

    covariance_matrix

    .fillna(0.0)
)

correlation_matrix = (

    correlation_matrix

    .fillna(0.0)
)

# =========================================================
# FORCE SYMMETRY
# =========================================================

covariance_matrix = pd.DataFrame(

    (
        covariance_matrix.values
        +
        covariance_matrix.values.T
    )
    / 2.0,

    index=covariance_matrix.index,

    columns=covariance_matrix.columns
)

annualized_covariance = pd.DataFrame(

    (
        annualized_covariance.values
        +
        annualized_covariance.values.T
    )
    / 2.0,

    index=annualized_covariance.index,

    columns=annualized_covariance.columns
)

correlation_matrix = pd.DataFrame(

    (
        correlation_matrix.values
        +
        correlation_matrix.values.T
    )
    / 2.0,

    index=correlation_matrix.index,

    columns=correlation_matrix.columns
)

# =========================================================
# DIAGONAL VALIDATION
# =========================================================

diag_labels = correlation_matrix.index.intersection(
    correlation_matrix.columns
)

for label in diag_labels:
    correlation_matrix.loc[label, label] = 1.0

# =========================================================
# VOLATILITY VECTOR
# =========================================================

vol_vector = np.sqrt(
    np.maximum(
        np.diag(
            annualized_covariance.values
        ),
        0
    )
)

volatility_vector = pd.DataFrame({

    "Symbol":
    annualized_covariance.index,

    "Annualized_Volatility":
    vol_vector
})

# =========================================================
# COVARIANCE DIAGNOSTICS
# =========================================================

print(
    "🔍 Running Covariance Diagnostics..."
)

cov_diag = np.diag(
    annualized_covariance.values
)

covariance_summary = pd.DataFrame({

    "Metric": [

        "Mean_Variance",

        "Median_Variance",

        "Min_Variance",

        "Max_Variance"
    ],

    "Value": [

        np.mean(cov_diag),

        np.median(cov_diag),

        np.min(cov_diag),

        np.max(cov_diag)
    ]
})

# =========================================================
# CORRELATION DIAGNOSTICS
# =========================================================

corr_values = (
    correlation_matrix.values
)

corr_values = corr_values[
    ~np.eye(
        corr_values.shape[0],
        dtype=bool
    )
]

average_correlation = np.nanmean(
    corr_values
)

median_correlation = np.nanmedian(
    corr_values
)

min_correlation = np.nanmin(
    corr_values
)

max_correlation = np.nanmax(
    corr_values
)

correlation_summary = pd.DataFrame({

    "Metric": [

        "Average_Correlation",

        "Median_Correlation",

        "Min_Correlation",

        "Max_Correlation"
    ],

    "Value": [

        average_correlation,

        median_correlation,

        min_correlation,

        max_correlation
    ]
})

print(
    f"Average Correlation : "
    f"{average_correlation:.4f}"
)

# =========================================================
# POSITIVE SEMI-DEFINITE CHECK
# =========================================================

print(
    "⚠ Checking Matrix Stability..."
)

try:

    eigenvalues = np.linalg.eigvalsh(
        annualized_covariance.values
    )

    min_eigenvalue = np.min(
        eigenvalues
    )

except Exception:

    min_eigenvalue = np.nan

audit_metrics[
    "Min_Eigenvalue"
] = float(
    min_eigenvalue
)

# =========================================================
# CONDITION NUMBER
# =========================================================

try:

    condition_number = np.linalg.cond(
        annualized_covariance.values
    )

except Exception:

    condition_number = np.nan

audit_metrics[
    "Condition_Number"
] = float(
    condition_number
)

print(
    f"Condition Number : "
    f"{condition_number:,.2f}"
)

# =========================================================
# VOLATILITY RANKING
# =========================================================

highest_volatility = (

    volatility_vector

    .sort_values(
        "Annualized_Volatility",
        ascending=False
    )

    .head(25)
)

lowest_volatility = (

    volatility_vector

    .sort_values(
        "Annualized_Volatility",
        ascending=True
    )

    .head(25)
)

# =========================================================
# MATRIX DIMENSIONS
# =========================================================

print(
    f"Covariance Shape : "
    f"{annualized_covariance.shape}"
)

print(
    f"Correlation Shape : "
    f"{correlation_matrix.shape}"
)

# =========================================================
# PART 3 STARTS HERE
# =========================================================
#
# Next:
#
# Ledoit-Wolf Shrinkage
# Eigen Decomposition
# PCA Risk Factors
# Risk Concentration
#
# =========================================================

# =========================================================
# SHRINKAGE COVARIANCE
# =========================================================

print(
    "\n🛡 Building Shrinkage Covariance..."
)

if ENABLE_SHRINKAGE:

    try:

        from sklearn.covariance import LedoitWolf

        lw = LedoitWolf()

        lw.fit(
            returns_matrix
            .fillna(0.0)
            .to_numpy()
        )

        shrinkage_covariance = pd.DataFrame(

            lw.covariance_ * TRADING_DAYS,

            index=returns_matrix.columns,

            columns=returns_matrix.columns
        )

        shrinkage_intensity = float(
            lw.shrinkage_
        )

    except Exception as e:

        print(
            f"Shrinkage failed: {e}"
        )

        shrinkage_covariance = (
            annualized_covariance.copy()
        )

        shrinkage_intensity = np.nan

else:

    shrinkage_covariance = (
        annualized_covariance.copy()
    )

    shrinkage_intensity = np.nan

audit_metrics[
    "Shrinkage_Intensity"
] = shrinkage_intensity

print(
    f"Shrinkage Intensity : "
    f"{shrinkage_intensity:.4f}"
)

# =========================================================
# POSITIVE DEFINITE REPAIR
# =========================================================

print(
    "🔧 Repairing Eigenvalues..."
)

eigvals, eigvecs = np.linalg.eigh(
    shrinkage_covariance.values
)

eigvals = np.maximum(
    eigvals,
    EIGENVALUE_FLOOR
)

repaired_covariance = (

    eigvecs

    @

    np.diag(
        eigvals
    )

    @

    eigvecs.T
)

shrinkage_covariance = pd.DataFrame(

    repaired_covariance,

    index=shrinkage_covariance.index,

    columns=shrinkage_covariance.columns
)

audit_metrics[
    "Min_Repaired_Eigenvalue"
] = float(
    eigvals.min()
)

# =========================================================
# PCA RISK MODEL
# =========================================================

print(
    "📈 Building PCA Risk Model..."
)

if ENABLE_PCA:

    centered_returns = (

        returns_matrix

        .fillna(0.0)

        -

        returns_matrix

        .fillna(0.0)

        .mean()
    )

    covariance_for_pca = (
        shrinkage_covariance.values
    )

    pca_eigenvalues, pca_eigenvectors = (

        np.linalg.eigh(
            covariance_for_pca
        )
    )

    sort_order = np.argsort(
        pca_eigenvalues
    )[::-1]

    pca_eigenvalues = (

        pca_eigenvalues[
            sort_order
        ]
    )

    pca_eigenvectors = (

        pca_eigenvectors[
            :,
            sort_order
        ]
    )

    factor_count = min(

        N_PCA_FACTORS,

        len(
            pca_eigenvalues
        )
    )

    factor_loadings = pd.DataFrame(

        pca_eigenvectors[
            :,
            :factor_count
        ],

        index=returns_matrix.columns,

        columns=[

            f"PC_{i+1}"

            for i in range(
                factor_count
            )
        ]
    )

    explained_variance_ratio = (

        pca_eigenvalues

        /

        pca_eigenvalues.sum()
    )

    explained_variance = pd.DataFrame({

        "Factor": [

            f"PC_{i+1}"

            for i in range(
                factor_count
            )
        ],

        "Eigenvalue":

        pca_eigenvalues[
            :factor_count
        ],

        "Explained_Variance":

        explained_variance_ratio[
            :factor_count
        ],

        "Cumulative_Variance":

        np.cumsum(

            explained_variance_ratio[
                :factor_count
            ]
        )
    })

else:

    factor_loadings = pd.DataFrame()

    explained_variance = pd.DataFrame()

# =========================================================
# PCA DIAGNOSTICS
# =========================================================

if not explained_variance.empty:

    print(
        f"PC1 Explained Variance : "
        f"{explained_variance.iloc[0]['Explained_Variance']:.2%}"
    )

    print(
        f"Top 5 Factors Variance : "
        f"{explained_variance.iloc[:5]['Explained_Variance'].sum():.2%}"
    )

    print(
        f"Top 20 Factors Variance : "
        f"{explained_variance['Explained_Variance'].sum():.2%}"
    )

# =========================================================
# RISK CONTRIBUTION
# =========================================================

print(
    "⚖ Building Risk Concentration Metrics..."
)

portfolio_weights = np.repeat(

    1 / n_assets,

    n_assets
)

portfolio_variance = (

    portfolio_weights.T

    @

    shrinkage_covariance.values

    @

    portfolio_weights
)

portfolio_volatility = np.sqrt(
    portfolio_variance
)

marginal_risk = (

    shrinkage_covariance.values

    @

    portfolio_weights
)

risk_contribution = (

    portfolio_weights

    *

    marginal_risk

    /

    portfolio_volatility
)

risk_contribution_df = pd.DataFrame({

    "Symbol":
    returns_matrix.columns,

    "Risk_Contribution":
    risk_contribution
})

risk_contribution_df[
    "Risk_Contribution_Pct"
] = (

    risk_contribution_df[
        "Risk_Contribution"
    ]

    /

    risk_contribution_df[
        "Risk_Contribution"
    ].sum()
)

# =========================================================
# HERFINDAHL RISK INDEX
# =========================================================

risk_hhi = np.sum(

    risk_contribution_df[
        "Risk_Contribution_Pct"
    ] ** 2
)

effective_risk_bets = (

    1

    /

    risk_hhi
)

audit_metrics[
    "Portfolio_Volatility"
] = float(
    portfolio_volatility
)

audit_metrics[
    "Effective_Risk_Bets"
] = float(
    effective_risk_bets
)

print(
    f"Portfolio Volatility : "
    f"{portfolio_volatility:.2%}"
)

print(
    f"Effective Risk Bets : "
    f"{effective_risk_bets:.2f}"
)

# =========================================================
# FACTOR EXPORT DATA
# =========================================================

eigenfactor_risk = (

    factor_loadings

    .reset_index()

    .rename(
        columns={
            "index":
            "Symbol"
        }
    )
)

# =========================================================
# RISK SUMMARY
# =========================================================

risk_summary = pd.DataFrame({

    "Metric": [

        "Portfolio_Volatility",

        "Effective_Risk_Bets",

        "Shrinkage_Intensity",

        "Min_Eigenvalue",

        "Condition_Number"
    ],

    "Value": [

        portfolio_volatility,

        effective_risk_bets,

        shrinkage_intensity,

        eigvals.min(),

        condition_number
    ]
})

# =========================================================
# PART 4 STARTS HERE
# =========================================================
#
# Next:
#
# Export Covariance Matrix
# Export Correlation Matrix
# Export Shrinkage Covariance
# Export PCA Factors
# Validation
# Audit Reports
# Production Completion
#
# =========================================================

# =========================================================
# OUTPUT FILES
# =========================================================

print(
    "\n💾 Saving Outputs..."
)

VOLATILITY_FILE = (
    RISK_DIR
    / "volatility_vector.csv"
)

RISK_CONTRIBUTION_FILE = (
    RISK_DIR
    / "risk_contribution.csv"
)

EXPLAINED_VARIANCE_FILE = (
    RISK_DIR
    / "explained_variance.csv"
)

RISK_SUMMARY_FILE = (
    RISK_DIR
    / "risk_summary.csv"
)

METADATA_FILE = (
    RISK_DIR
    / "covariance_metadata.csv"
)

# =========================================================
# FINAL VALIDATION
# =========================================================

print(
    "✔ Running Final Validation..."
)

if annualized_covariance.empty:

    raise ValueError(
        "Covariance matrix empty."
    )

if correlation_matrix.empty:

    raise ValueError(
        "Correlation matrix empty."
    )

if annualized_covariance.shape[0] != annualized_covariance.shape[1]:

    raise ValueError(
        "Covariance matrix not square."
    )

if correlation_matrix.shape[0] != correlation_matrix.shape[1]:

    raise ValueError(
        "Correlation matrix not square."
    )

# =========================================================
# PSD VALIDATION
# =========================================================

try:

    final_eigenvalues = np.linalg.eigvalsh(
        shrinkage_covariance.values
    )

    min_final_eigenvalue = (
        final_eigenvalues.min()
    )

except Exception:

    min_final_eigenvalue = np.nan

audit_metrics[
    "Final_Min_Eigenvalue"
] = float(
    min_final_eigenvalue
)

# =========================================================
# MATRIX SIZE
# =========================================================

covariance_elements = (

    annualized_covariance.shape[0]

    *

    annualized_covariance.shape[1]
)

# =========================================================
# MEMORY OPTIMIZATION
# =========================================================

annualized_covariance = (

    annualized_covariance

    .astype(
        np.float32
    )
)

correlation_matrix = (

    correlation_matrix

    .astype(
        np.float32
    )
)

shrinkage_covariance = (

    shrinkage_covariance

    .astype(
        np.float32
    )
)

# =========================================================
# EXPORT MATRICES
# =========================================================

print(
    "📊 Saving Covariance Matrices..."
)

annualized_covariance.to_parquet(
    COVARIANCE_FILE
)

correlation_matrix.to_parquet(
    CORRELATION_FILE
)

shrinkage_covariance.to_parquet(
    SHRINKAGE_FILE
)

# =========================================================
# EXPORT PCA
# =========================================================

if not eigenfactor_risk.empty:

    eigenfactor_risk.to_parquet(
        PCA_FILE,
        index=False
    )

if not explained_variance.empty:

    explained_variance.to_csv(
        EXPLAINED_VARIANCE_FILE,
        index=False
    )

# =========================================================
# EXPORT REPORTS
# =========================================================

volatility_vector.to_csv(
    VOLATILITY_FILE,
    index=False
)

risk_contribution_df.to_csv(
    RISK_CONTRIBUTION_FILE,
    index=False
)

risk_summary.to_csv(
    RISK_SUMMARY_FILE,
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
# METADATA
# =========================================================

metadata = pd.DataFrame({

    "Metric": [

        "Engine_Name",

        "Engine_Version",

        "Build_Time",

        "Trading_Days",

        "Securities",

        "Average_Correlation",

        "Median_Correlation",

        "Portfolio_Volatility",

        "Effective_Risk_Bets",

        "Shrinkage_Intensity"
    ],

    "Value": [

        ENGINE_NAME,

        ENGINE_VERSION,

        datetime.now(),

        n_days,

        n_assets,

        average_correlation,

        median_correlation,

        portfolio_volatility,

        effective_risk_bets,

        shrinkage_intensity
    ]
})

metadata.to_csv(
    METADATA_FILE,
    index=False
)

# =========================================================
# FINAL SUMMARY
# =========================================================

print(
    "\n=========================================================="
)

print(
    "🏁 COVARIANCE MATRIX ENGINE COMPLETE"
)

print(
    "=========================================================="
)

print(
    f"Trading Days           : "
    f"{n_days:,}"
)

print(
    f"Securities             : "
    f"{n_assets:,}"
)

print(
    f"Covariance Shape       : "
    f"{annualized_covariance.shape}"
)

print(
    f"Correlation Shape      : "
    f"{correlation_matrix.shape}"
)

print(
    f"Matrix Elements        : "
    f"{covariance_elements:,}"
)

print(
    f"Average Correlation    : "
    f"{average_correlation:.4f}"
)

print(
    f"Median Correlation     : "
    f"{median_correlation:.4f}"
)

print(
    f"Portfolio Volatility   : "
    f"{portfolio_volatility:.2%}"
)

print(
    f"Effective Risk Bets    : "
    f"{effective_risk_bets:.2f}"
)

print(
    f"Shrinkage Intensity    : "
    f"{shrinkage_intensity:.4f}"
)

print(
    f"Minimum Eigenvalue     : "
    f"{min_final_eigenvalue:.8f}"
)

if not explained_variance.empty:

    print(
        f"Top Factor Variance    : "
        f"{explained_variance.iloc[0]['Explained_Variance']:.2%}"
    )

    print(
        f"Top 5 Factors Variance : "
        f"{explained_variance.iloc[:5]['Explained_Variance'].sum():.2%}"
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