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

FACTOR_COV_FILE = (
    ROOT
    / "data"
    / "risk"
    / "factor_covariance.parquet"
)

SPECIFIC_RISK_FILE = (
    ROOT
    / "data"
    / "risk"
    / "specific_risk.parquet"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "risk"
    / "factor_risk_covariance.parquet"
)

print("\nLoading Inputs...")

B_df = pd.read_parquet(
    EXPOSURE_FILE
)

F = pd.read_parquet(
    FACTOR_COV_FILE
)

D_df = pd.read_parquet(
    SPECIFIC_RISK_FILE
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

symbols = (
    B_df["Symbol"]
    .tolist()
)

B = (
    B_df[factor_cols]
    .values
)

F = F.loc[
    factor_cols,
    factor_cols
].values

# =====================================
# FACTOR RISK
# =====================================

factor_risk = (

    B
    @
    F
    @
    B.T

)

# =====================================
# SPECIFIC RISK
# =====================================

D_df = (
    D_df
    .set_index("Symbol")
    .reindex(symbols)
)

specific_var = (

    D_df["Specific_Risk"]
    .fillna(
        D_df["Specific_Risk"]
        .median()
    )

    ** 2

)

D = np.diag(
    specific_var
)

# =====================================
# TOTAL RISK
# =====================================

Sigma = (

    factor_risk

    +

    D

)

# =====================================
# PSD REPAIR
# =====================================

eigvals, eigvecs = np.linalg.eigh(
    Sigma
)

eigvals = np.maximum(
    eigvals,
    1e-8
)

Sigma = (

    eigvecs
    @
    np.diag(eigvals)
    @
    eigvecs.T

)

cov_matrix = pd.DataFrame(
    Sigma,
    index=symbols,
    columns=symbols
)

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

cov_matrix.to_parquet(
    OUTPUT_FILE
)

print(
    "\nFactor Risk Covariance Shape:",
    cov_matrix.shape
)

print(
    "Min Eigenvalue:",
    np.min(
        np.linalg.eigvals(
            Sigma
        )
    )
)

print(
    "Max Eigenvalue:",
    np.max(
        np.linalg.eigvals(
            Sigma
        )
    )
)