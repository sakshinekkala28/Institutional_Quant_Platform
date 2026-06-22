"""
=========================================================
STOCK METADATA ENGINE
=========================================================

Purpose:
Create final institutional security master

Input:
data/raw/updated_stocks.csv

Output:
data/raw/stock_metadata.csv

=========================================================
"""

from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

# =========================================================
# CONFIG
# =========================================================

LARGE_CAP_THRESHOLD = 20_000_000_000
MID_CAP_THRESHOLD = 5_000_000_000

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    ROOT
    / "data"
    / "raw"
    / "updated_stocks.csv"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "raw"
    / "stock_metadata.csv"
)

HEALTH_REPORT = (
    ROOT
    / "data"
    / "logs"
    / "stock_metadata_health.csv"
)

# =========================================================
# LOAD
# =========================================================

print("\n📥 Loading Updated Universe...")

if not INPUT_FILE.exists():

    raise FileNotFoundError(
        f"Missing file:\n{INPUT_FILE}"
    )

df = pd.read_csv(INPUT_FILE)

# =========================================================
# STANDARDIZE COLUMNS
# =========================================================

rename_map = {
    "symbol": "Symbol",
    "company_name": "Company_Name",
    "sector": "Sector",
    "industry": "Industry",
    "market_cap": "Market_Cap",
    "avg_daily_turnover": "ADV",
}

df.rename(
    columns={
        k: v
        for k, v in rename_map.items()
        if k in df.columns
    },
    inplace=True,
)

# =========================================================
# REQUIRED COLUMNS
# =========================================================

required_columns = [
    "Symbol",
]

for col in required_columns:

    if col not in df.columns:

        raise ValueError(
            f"Missing required column: {col}"
        )

# =========================================================
# DEFAULTS
# =========================================================

defaults = {
    "Company_Name": "Unknown",
    "Sector": "Unknown",
    "Industry": "Unknown",
    "Market_Cap": 0,
    "ADV": 0,
}

for col, value in defaults.items():

    if col not in df.columns:

        df[col] = value

# =========================================================
# CLEANING
# =========================================================

df["Symbol"] = (
    df["Symbol"]
    .astype(str)
    .str.upper()
    .str.strip()
)

df["Company_Name"] = (
    df["Company_Name"]
    .astype(str)
    .str.strip()
)

df["Sector"] = (
    df["Sector"]
    .astype(str)
    .str.strip()
)

df["Industry"] = (
    df["Industry"]
    .astype(str)
    .str.strip()
)

df["Market_Cap"] = pd.to_numeric(
    df["Market_Cap"],
    errors="coerce",
).fillna(0)

df["ADV"] = pd.to_numeric(
    df["ADV"],
    errors="coerce",
).fillna(0)

# =========================================================
# STATIC METADATA
# =========================================================

df["Exchange"] = "NSE"

df["Country"] = "India"

df["Currency"] = "INR"

df["Asset_Class"] = "Equity"

df["Metadata_Source"] = (
    "Institutional_Quant_Platform"
)

df["Last_Updated"] = (
    datetime.now()
    .strftime("%Y-%m-%d")
)

# =========================================================
# MARKET CAP CLASSIFICATION
# =========================================================

df["Market_Cap_Category"] = np.select(
    [
        df["Market_Cap"]
        >= LARGE_CAP_THRESHOLD,

        (
            (df["Market_Cap"] >= MID_CAP_THRESHOLD)
            &
            (df["Market_Cap"] < LARGE_CAP_THRESHOLD)
        ),
    ],
    [
        "Large Cap",
        "Mid Cap",
    ],
    default="Small Cap",
)

# =========================================================
# LIQUIDITY CLASSIFICATION
# =========================================================

df["Liquidity_Category"] = np.select(
    [
        df["ADV"] >= 100_000_000,

        (
            (df["ADV"] >= 25_000_000)
            &
            (df["ADV"] < 100_000_000)
        ),
    ],
    [
        "Highly Liquid",
        "Liquid",
    ],
    default="Less Liquid",
)

# =========================================================
# SECTOR VALIDATION
# =========================================================

df["Sector"] = (
    df["Sector"]
    .replace(
        {
            "nan": "Unknown",
            "": "Unknown",
        }
    )
)

df["Industry"] = (
    df["Industry"]
    .replace(
        {
            "nan": "Unknown",
            "": "Unknown",
        }
    )
)

# =========================================================
# DATA HEALTH REPORT
# =========================================================

health = pd.DataFrame(
    {
        "Metric": [
            "Total Stocks",
            "Missing Sector",
            "Missing Industry",
            "Missing Market Cap",
            "Missing ADV",
        ],
        "Value": [
            len(df),
            (
                df["Sector"]
                == "Unknown"
            ).sum(),
            (
                df["Industry"]
                == "Unknown"
            ).sum(),
            (
                df["Market_Cap"]
                <= 0
            ).sum(),
            (
                df["ADV"]
                <= 0
            ).sum(),
        ],
    }
)

# =========================================================
# FINAL SORT
# =========================================================

df = (
    df
    .sort_values(
        "Market_Cap",
        ascending=False,
    )
    .drop_duplicates(
        subset=["Symbol"]
    )
    .reset_index(drop=True)
)

# =========================================================
# SAVE
# =========================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

HEALTH_REPORT.parent.mkdir(
    parents=True,
    exist_ok=True,
)

df.to_csv(
    OUTPUT_FILE,
    index=False,
)

health.to_csv(
    HEALTH_REPORT,
    index=False,
)

# =========================================================
# REPORT
# =========================================================

print("\n" + "=" * 70)

print(
    "🏁 STOCK METADATA ENGINE COMPLETE"
)

print("=" * 70)

print(
    f"Stocks              : {len(df):,}"
)

print(
    f"Large Cap           : "
    f"{(df['Market_Cap_Category']=='Large Cap').sum():,}"
)

print(
    f"Mid Cap             : "
    f"{(df['Market_Cap_Category']=='Mid Cap').sum():,}"
)

print(
    f"Small Cap           : "
    f"{(df['Market_Cap_Category']=='Small Cap').sum():,}"
)

print(
    f"Highly Liquid       : "
    f"{(df['Liquidity_Category']=='Highly Liquid').sum():,}"
)

print(
    f"Liquid              : "
    f"{(df['Liquidity_Category']=='Liquid').sum():,}"
)

print(
    f"Less Liquid         : "
    f"{(df['Liquidity_Category']=='Less Liquid').sum():,}"
)

print(
    f"\nSaved:\n{OUTPUT_FILE}"
)

print(
    f"\nHealth Report:\n{HEALTH_REPORT}"
)

print("=" * 70)