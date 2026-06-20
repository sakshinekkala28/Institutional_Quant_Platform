from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[2]

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
    / "factor_covariance.parquet"
)

print(
    "\nLoading Factor Returns..."
)

factor_returns = pd.read_parquet(
    FACTOR_RETURNS_FILE
)

factor_returns = factor_returns.sort_values(
    "Date"
)

factor_returns = factor_returns.drop(
    columns=["Date"],
    errors="ignore"
)

print(
    "Factor Returns Shape:",
    factor_returns.shape
)

# =====================================================
# ROBUST COVARIANCE
# =====================================================

factor_cov = factor_returns.cov()

# =====================================================
# PSD REPAIR
# =====================================================

eigvals, eigvecs = np.linalg.eigh(
    factor_cov.values
)

eigvals = np.maximum(
    eigvals,
    1e-8
)

factor_cov_psd = (
    eigvecs
    @ np.diag(eigvals)
    @ eigvecs.T
)

factor_cov = pd.DataFrame(
    factor_cov_psd,
    index=factor_cov.index,
    columns=factor_cov.columns
)

# =====================================================
# SAVE
# =====================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

factor_cov.to_parquet(
    OUTPUT_FILE
)

print(
    "\nFactor Covariance Shape:",
    factor_cov.shape
)

print(
    "\nFactor Covariance Matrix:"
)

print(
    factor_cov.round(6)
)

print(
    "\nEigenvalues:"
)

print(
    np.round(
        np.linalg.eigvals(
            factor_cov
        ),
        8
    )
)