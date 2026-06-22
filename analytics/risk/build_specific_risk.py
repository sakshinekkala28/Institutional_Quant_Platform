from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[2]

FACTOR_MASTER_FILE = (
    ROOT
    / "data"
    / "factors"
    / "factor_master.csv"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "risk"
    / "specific_risk.parquet"
)

print(
    "\nLoading Factor Master..."
)

df = pd.read_csv(
    FACTOR_MASTER_FILE
)

print(
    "Universe:",
    len(df)
)

# ====================================================
# VOLATILITY SOURCE
# ====================================================

vol_col = None

for candidate in [

    "Volatility_252D",
    "Volatility_60D",
    "Volatility_20D"

]:

    if candidate in df.columns:

        vol_col = candidate
        break

if vol_col is None:

    raise ValueError(
        "No volatility column found."
    )

print(
    "Using:",
    vol_col
)

# ====================================================
# SPECIFIC RISK
# ====================================================

specific_risk = df[[
    "Symbol",
    vol_col
]].copy()

specific_risk["Specific_Risk"] = (

    specific_risk[vol_col]

    * 0.30

)

specific_risk["Specific_Risk"] = (

    specific_risk["Specific_Risk"]

    .fillna(
        specific_risk["Specific_Risk"]
        .median()
    )

    .clip(
        lower=0.01
    )

)

# =====================================
# INSTITUTIONAL RESIDUAL RISK CAP
# =====================================

specific_risk["Specific_Risk"] = (

    specific_risk["Specific_Risk"]

    .clip(
        upper=0.40
    )

)

specific_risk = specific_risk[[
    "Symbol",
    "Specific_Risk"
]]

# ====================================================
# SAVE
# ====================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

specific_risk.to_parquet(
    OUTPUT_FILE,
    index=False
)

print(
    "\nSpecific Risk Shape:",
    specific_risk.shape
)

print(
    specific_risk.head()
)

print(
    "\nSummary:"
)

print(
    specific_risk["Specific_Risk"]
    .describe()
)