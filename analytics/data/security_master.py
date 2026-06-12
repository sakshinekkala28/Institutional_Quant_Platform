"""
=========================================================
SECURITY MASTER ENGINE
=========================================================

Purpose:
Create institutional-grade Security Master

Input:
data/raw/updated_stocks.csv

Output:
data/raw/security_master.csv

=========================================================
"""

from pathlib import Path
from datetime import datetime

import hashlib
import pandas as pd

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
    / "security_master.csv"
)

# =========================================================
# LOAD
# =========================================================

print("\n📥 Loading Investable Universe...")

df = pd.read_csv(INPUT_FILE)

# =========================================================
# VALIDATION
# =========================================================

required_columns = [
    "Symbol",
    "Company_Name",
    "Sector",
    "Industry",
    "Market_Cap",
    "Last_Close",
    "ADV",
]

missing = [
    c
    for c in required_columns
    if c not in df.columns
]

if missing:

    raise ValueError(
        f"Missing Columns: {missing}"
    )

# =========================================================
# CLEAN
# =========================================================

df["Symbol"] = (
    df["Symbol"]
    .astype(str)
    .str.upper()
    .str.strip()
)

df = (
    df
    .drop_duplicates(
        subset="Symbol"
    )
    .reset_index(drop=True)
)

numeric_cols = [
    "Market_Cap",
    "Last_Close",
    "ADV",
    "History_Days",
]

for col in numeric_cols:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce",
    )

df = df.dropna(
    subset=[
        "Market_Cap",
        "Last_Close",
    ]
)

# =========================================================
# SECURITY IDENTIFIER
# =========================================================

df.insert(
    0,
    "Security_ID",
    df["Symbol"].apply(
        lambda x:
        "SEC"
        + hashlib.md5(
            x.encode()
        ).hexdigest()[:8].upper()
    ),
)

# =========================================================
# STATIC REFERENCE DATA
# =========================================================

df["Yahoo_Symbol"] = (
    df["Symbol"]
    + ".NS"
)

df["Exchange"] = "NSE"

df["Country"] = "India"

df["Currency"] = "INR"

df["Universe_Flag"] = 1

today = datetime.now().strftime(
    "%Y-%m-%d"
)

df["Created_Date"] = today

df["Last_Updated"] = today

df["Asset_Type"] = "Equity"

df["Is_Active"] = 1

df["Market_Cap_Category"] = pd.cut(
    df["Market_Cap"],
    bins=[
        0,
        5e10,
        2e11,
        float("inf"),
    ],
    labels=[
        "Small Cap",
        "Mid Cap",
        "Large Cap",
    ],
)

# =========================================================
# COLUMN ORDER
# =========================================================

columns = [

    "Security_ID",

    "Symbol",
    "Yahoo_Symbol",

    "Company_Name",

    "Sector",
    "Industry",

    "Market_Cap",
    "Market_Cap_Category",

    "Last_Close",
    "ADV",

    "History_Days",
    "Missing_Close",

    "Exchange",
    "Country",
    "Currency",
    "Asset_Type",

    "Universe_Flag",
    "Is_Active",

    "Created_Date",
    "Last_Updated",
]

security_master = df[columns]

# =========================================================
# SORT
# =========================================================

security_master = (
    security_master
    .sort_values(
        "Market_Cap",
        ascending=False,
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

security_master.to_csv(
    OUTPUT_FILE,
    index=False,
)

# =========================================================
# REPORT
# =========================================================

print("\n" + "=" * 70)

print(
    "🏁 SECURITY MASTER COMPLETE"
)

print("=" * 70)

print(
    f"Total Securities : "
    f"{len(security_master):,}"
)

print(
    f"Largest Market Cap : "
    f"{security_master['Market_Cap'].max():,.0f}"
)

print(
    f"Median ADV : "
    f"{security_master['ADV'].median():,.0f}"
)

print(
    f"\nSaved:\n{OUTPUT_FILE}"
)

print("=" * 70)