"""
=========================================================
LIQUIDITY ENGINE
=========================================================

Purpose:
Institutional Liquidity & Capacity Analytics

Inputs:
data/raw/security_master.csv
data/portfolios/optimized_portfolio.csv
data/raw/prices/*.parquet

Outputs:
data/liquidity/liquidity_master.csv
data/liquidity/capacity_report.csv
data/liquidity/liquidity_risk_report.csv

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

PORTFOLIO_NAV = 100_000_000

PARTICIPATION_RATE = 0.10

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

SECURITY_FILE = (
    ROOT
    / "data"
    / "raw"
    / "security_master.csv"
)

PORTFOLIO_FILE = (
    ROOT
    / "data"
    / "portfolios"
    / "optimized_portfolio.csv"
)

PRICE_DIR = (
    ROOT
    / "data"
    / "raw"
    / "prices"
)

LIQUIDITY_FILE = (
    ROOT
    / "data"
    / "liquidity"
    / "liquidity_master.csv"
)

CAPACITY_FILE = (
    ROOT
    / "data"
    / "liquidity"
    / "capacity_report.csv"
)

RISK_FILE = (
    ROOT
    / "data"
    / "liquidity"
    / "liquidity_risk_report.csv"
)

REPORT_FILE = (
    ROOT
    / "data"
    / "logs"
    / "liquidity_report.csv"
)

# =========================================================
# LOAD
# =========================================================

print("\n📥 Loading Portfolio...")

portfolio = pd.read_csv(
    PORTFOLIO_FILE
)

if "Target_Value" in portfolio.columns:

    PORTFOLIO_NAV = (

        portfolio[
            "Target_Value"
        ]

        .sum()
    )

security_master = pd.read_csv(
    SECURITY_FILE
)

security_lookup = (
    security_master
    .set_index("Symbol")
)

# =========================================================
# VALIDATION
# =========================================================

required_security_cols = [
    "Symbol",
    "Market_Cap",
]

required_portfolio_cols = [
    "Symbol",
    "Optimized_Weight",
]

for col in required_security_cols:

    if col not in security_master.columns:

        raise ValueError(
            f"Missing Column: {col}"
        )

for col in required_portfolio_cols:

    if col not in portfolio.columns:

        raise ValueError(
            f"Missing Column: {col}"
        )

# =========================================================
# BUILD LIQUIDITY METRICS
# =========================================================

records = []

for symbol in portfolio["Symbol"]:

    try:

        file = (
            PRICE_DIR
            / f"{symbol}.parquet"
        )

        if not file.exists():
            continue

        df = pd.read_parquet(file)

        if len(df) < 120:
            continue

        close = pd.to_numeric(
            df["Close"],
            errors="coerce"
        )

        volume = pd.to_numeric(
            df["Volume"],
            errors="coerce"
        )

        dollar_volume = (
            close * volume
        )

        adv_20 = (
            dollar_volume
            .tail(20)
            .dropna()
            .mean()
        )

        adv_60 = (
            dollar_volume
            .tail(60)
            .dropna()
            .mean()
        )

        adv_120 = (
            dollar_volume
            .tail(120)
            .dropna()
            .mean()
        )

        volume_returns = (
            volume
            .replace(0, np.nan)
            .pct_change()
            .replace(
                [np.inf, -np.inf],
                np.nan
            )
        )

        volume_vol = (
            volume_returns
            .dropna()
            .std()
        )

        if pd.isna(volume_vol):

            volume_vol = 999

        last_close = (
            close.iloc[-1]
        )

        market_cap = (
            security_lookup
            .loc[
                symbol,
                "Market_Cap"
            ]
        )

        records.append({

            "Symbol":
            symbol,

            "Last_Close":
            last_close,

            "Market_Cap":
            market_cap,

            "ADV_20D":
            adv_20,

            "ADV_60D":
            adv_60,

            "ADV_120D":
            adv_120,

            "Volume_Volatility":
            volume_vol,
        })

    except Exception as e:

        print(
            f"Liquidity Error "
            f"{symbol}: {e}"
        )

        continue

liquidity = pd.DataFrame(
    records
)

# =========================================================
# MERGE PORTFOLIO
# =========================================================

liquidity = liquidity.merge(

    portfolio[
        [
            "Symbol",
            "Optimized_Weight"
        ]
    ],

    on="Symbol",

    how="left"
)

# =========================================================
# POSITION VALUE
# =========================================================

liquidity["Position_Value"] = (

    liquidity[
        "Optimized_Weight"
    ]

    * PORTFOLIO_NAV
)

# =========================================================
# CAPACITY
# =========================================================

liquidity["Capacity_5pct_ADV"] = (

    liquidity["ADV_20D"]

    * 0.05
)

liquidity["Capacity_10pct_ADV"] = (

    liquidity["ADV_20D"]

    * PARTICIPATION_RATE
)

liquidity["Capacity_20pct_ADV"] = (

    liquidity["ADV_20D"]

    * 0.20
)

# =========================================================
# DAYS TO LIQUIDATE
# =========================================================

liquidity["Days_To_Liquidate"] = (

    liquidity["Position_Value"]

    /

    np.maximum(
        liquidity[
            "Capacity_10pct_ADV"
        ],
        1
    )
)

liquidity["Hours_To_Liquidate"] = (

    liquidity[
        "Days_To_Liquidate"
    ]

    * 6.25
)

portfolio_capacity = (

    liquidity[
        "Capacity_10pct_ADV"
    ]
    .sum()
)

capacity_multiple = (

    portfolio_capacity
    / PORTFOLIO_NAV
)

liquidity["Capacity_Bucket"] = pd.cut(

    liquidity[
        "Days_To_Liquidate"
    ],

    bins=[
        0,
        1,
        3,
        5,
        np.inf,
    ],

    labels=[
        "Excellent",
        "Good",
        "Moderate",
        "Poor",
    ]
)

# =========================================================
# LIQUIDITY SCORE
# =========================================================

adv_rank = (

    liquidity["ADV_20D"]

    .rank(
        pct=True
    )
)

cap_rank = (

    liquidity["Market_Cap"]

    .rank(
        pct=True
    )
)

liquidity[
    "Volume_Volatility"
] = (

    liquidity[
        "Volume_Volatility"
    ]
    .replace(
        [np.inf, -np.inf],
        np.nan
    )
    .fillna(
        liquidity[
            "Volume_Volatility"
        ].median()
    )
)

vol_rank = (

    1
    -
    liquidity[
        "Volume_Volatility"
    ].rank(
        pct=True
    )
)

required = [

    "ADV_20D",
    "Market_Cap",
    "Volume_Volatility",
]

for col in required:

    liquidity[col] = (

        pd.to_numeric(
            liquidity[col],
            errors="coerce"
        )

        .replace(
            [np.inf, -np.inf],
            np.nan
        )
    )

liquidity["Liquidity_Score"] = (

      0.50 * adv_rank
    + 0.30 * cap_rank
    + 0.20 * vol_rank

) * 100

liquidity["Liquidity_Score"] = (

    liquidity[
        "Liquidity_Score"
    ]

    .replace(
        [np.inf, -np.inf],
        np.nan
    )

    .fillna(0)

    .clip(
        lower=0,
        upper=100
    )
)

liquidity["Liquidity_Score"] = (

    liquidity[
        "Liquidity_Score"
    ]

    .rank(
        pct=True
    )

    * 100
)

# =========================================================
# LIQUIDITY FLAGS
# =========================================================

liquidity["Liquidity_Flag"] = np.where(

    liquidity[
        "Days_To_Liquidate"
    ] > 5,

    "HIGH",

    np.where(

        liquidity[
            "Days_To_Liquidate"
        ] > 2,

        "MEDIUM",

        "LOW"
    )
)

# =========================================================
# CAPACITY REPORT
# =========================================================

capacity_report = pd.DataFrame({

    "Metric": [

        "Portfolio_NAV",

        "Portfolio_Capacity_5pct",

        "Portfolio_Capacity_10pct",

        "Portfolio_Capacity_20pct",

        "Average_Days_To_Liquidate",

        "Median_Liquidity_Score",
    ],

    "Value": [

        PORTFOLIO_NAV,

        liquidity[
            "Capacity_5pct_ADV"
        ].sum(),

        liquidity[
            "Capacity_10pct_ADV"
        ].sum(),

        liquidity[
            "Capacity_20pct_ADV"
        ].sum(),

        liquidity[
            "Days_To_Liquidate"
        ].mean(),

        liquidity[
            "Liquidity_Score"
        ].median(),
    ]
})

# =========================================================
# LIQUIDITY RISK
# =========================================================

risk_report = (

    liquidity

    .sort_values(
        "Days_To_Liquidate",
        ascending=False
    )

    .head(25)
)

print(
    "\nLiquidity Diagnostics"
)

print(

    liquidity[
        [
            "ADV_20D",
            "Market_Cap",
            "Volume_Volatility",
            "Liquidity_Score"
        ]
    ]

    .isna()

    .sum()
)

if liquidity.empty:

    raise ValueError(
        "Liquidity universe empty."
    )

# =========================================================
# SAVE
# =========================================================

LIQUIDITY_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

liquidity.to_csv(
    LIQUIDITY_FILE,
    index=False
)

capacity_report.to_csv(
    CAPACITY_FILE,
    index=False
)

risk_report.to_csv(
    RISK_FILE,
    index=False
)

# =========================================================
# REPORT
# =========================================================

summary = pd.DataFrame({

    "Metric": [

        "Securities",

        "Avg_Liquidity_Score",

        "Median_Days_To_Liquidate",

        "Portfolio_Capacity_10pct_ADV",

        "Run_Date",

        "Engine_Version",
    ],

    "Value": [

        len(liquidity),

        liquidity[
            "Liquidity_Score"
        ].mean(),

        liquidity[
            "Days_To_Liquidate"
        ].median(),

        liquidity[
            "Capacity_10pct_ADV"
        ].sum(),

        datetime.now()
        .strftime(
            "%Y-%m-%d"
        ),

        ENGINE_VERSION,
    ]
})

REPORT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

summary.to_csv(
    REPORT_FILE,
    index=False
)

# =========================================================
# REPORT
# =========================================================

print("\n" + "=" * 70)

print(
    "🏁 LIQUIDITY ENGINE COMPLETE"
)

print("=" * 70)

print(
    f"Securities : "
    f"{len(liquidity):,}"
)

print(
    f"Avg Liquidity Score : "
    f"{liquidity['Liquidity_Score'].mean():.2f}"
)

median_days = (
    liquidity[
        "Days_To_Liquidate"
    ]
    .median()
)

print(
    f"Capacity Multiple : "
    f"{capacity_multiple:.1f}x"
)

if median_days < 1:

    print(
        f"Median Hours To Exit : "
        f"{median_days * 6.25:.2f}"
    )

else:

    print(
        f"Median Days To Exit : "
        f"{median_days:.2f}"
    )

print(
    f"Portfolio Capacity (10% ADV) : "
    f"{liquidity['Capacity_10pct_ADV'].sum():,.0f}"
)

print(
    f"\nOutput Directory:\n"
    f"{LIQUIDITY_FILE.parent}"
)

print("=" * 70)