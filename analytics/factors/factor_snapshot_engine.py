"""
=========================================================
FACTOR SNAPSHOT ENGINE
=========================================================

Purpose:
Build Monthly Institutional Factor Snapshots

Inputs:
data/raw/security_master.csv
data/raw/prices/*.parquet

Outputs:
data/factor_snapshots/*.parquet
data/factors/factor_snapshot_master.csv

=========================================================
"""

from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import numpy as np
import pandas as pd

# =========================================================
# CONFIG
# =========================================================

ENGINE_VERSION = "1.0.0"

MAX_WORKERS = 4

TRADING_DAYS = 252

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

SECURITY_MASTER = (
    ROOT
    / "data"
    / "raw"
    / "security_master.csv"
)

PRICE_DIR = (
    ROOT
    / "data"
    / "raw"
    / "prices"
)

SNAPSHOT_DIR = (
    ROOT
    / "data"
    / "factor_snapshots"
)

MASTER_FILE = (
    ROOT
    / "data"
    / "factors"
    / "factor_snapshot_master.csv"
)

REPORT_FILE = (
    ROOT
    / "data"
    / "logs"
    / "factor_snapshot_report.csv"
)

SNAPSHOT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

# =========================================================
# LOAD SECURITY MASTER
# =========================================================

print(
    "\n📥 Loading Security Master..."
)

security = pd.read_csv(
    SECURITY_MASTER
)

security_lookup = (
    security
    .set_index("Symbol")
)

symbols = (
    security["Symbol"]
    .dropna()
    .unique()
    .tolist()
)

# =========================================================
# BUILD MONTH-END CALENDAR
# =========================================================

sample_file = (
    PRICE_DIR
    / f"{symbols[0]}.parquet"
)

sample = pd.read_parquet(
    sample_file,
    columns=["Date"]
)

sample["Date"] = pd.to_datetime(
    sample["Date"]
)

month_ends = (

    sample

    .groupby(
        sample["Date"]
        .dt.to_period("M")
    )["Date"]

    .max()

    .tolist()
)

# =========================================================
# FACTOR FUNCTION
# =========================================================

def calculate_snapshot(
    symbol,
    snapshot_date,
):

    try:

        file = (
            PRICE_DIR
            / f"{symbol}.parquet"
        )

        if not file.exists():
            return None

        df = pd.read_parquet(
            file
        )

        df["Date"] = pd.to_datetime(
            df["Date"]
        )

        df = df[
            df["Date"]
            <= snapshot_date
        ]

        if len(df) < 252:
            return None

        close = pd.to_numeric(
            df["Close"],
            errors="coerce"
        )

        high = pd.to_numeric(
            df["High"],
            errors="coerce"
        )

        low = pd.to_numeric(
            df["Low"],
            errors="coerce"
        )

        volume = pd.to_numeric(
            df["Volume"],
            errors="coerce"
        )

        close = close.dropna()

        if len(close) < 252:
            return None

        returns = (
            close
            .pct_change()
            .dropna()
        )

        # -------------------------------------
        # MOMENTUM
        # -------------------------------------

        mom_1m = (
            close.iloc[-1]
            / close.iloc[-21]
            - 1
        )

        mom_3m = (
            close.iloc[-1]
            / close.iloc[-63]
            - 1
        )

        mom_6m = (
            close.iloc[-1]
            / close.iloc[-126]
            - 1
        )

        mom_12m = (
            close.iloc[-1]
            / close.iloc[-252]
            - 1
        )

        # -------------------------------------
        # VOLATILITY
        # -------------------------------------

        vol_20d = (
            returns.tail(20)
            .std()
            * np.sqrt(
                TRADING_DAYS
            )
        )

        vol_60d = (
            returns.tail(60)
            .std()
            * np.sqrt(
                TRADING_DAYS
            )
        )

        # -------------------------------------
        # ATR
        # -------------------------------------

        prev_close = (
            close.shift(1)
        )

        tr = pd.concat(
            [
                high - low,
                (high - prev_close).abs(),
                (low - prev_close).abs(),
            ],
            axis=1,
        ).max(axis=1)

        atr_14 = (
            tr.tail(14)
            .mean()
        )

        # -------------------------------------
        # DRAWDOWN
        # -------------------------------------

        rolling_max = (
            close.cummax()
        )

        drawdown = (
            close
            / rolling_max
        ) - 1

        max_dd = (
            drawdown
            .tail(252)
            .min()
        )

        # -------------------------------------
        # MOVING AVERAGES
        # -------------------------------------

        sma50 = (
            close
            .tail(50)
            .mean()
        )

        sma200 = (
            close
            .tail(200)
            .mean()
        )

        distance_sma50 = (
            close.iloc[-1]
            / sma50
        ) - 1

        distance_sma200 = (
            close.iloc[-1]
            / sma200
        ) - 1

        # -------------------------------------
        # 52W HIGH
        # -------------------------------------

        high_52w = (
            close
            .tail(252)
            .max()
        )

        distance_52w = (
            close.iloc[-1]
            / high_52w
        ) - 1

        # -------------------------------------
        # LIQUIDITY
        # -------------------------------------

        adv_20d = (
            close.tail(20)
            * volume.tail(20)
        ).mean()

        dollar_volume = adv_20d

        # -------------------------------------
        # METADATA
        # -------------------------------------

        meta = security_lookup.loc[
            symbol
        ]

        return {

            "Snapshot_Date":
            snapshot_date,

            "Security_ID":
            meta["Security_ID"],

            "Symbol":
            symbol,

            "Company_Name":
            meta.get(
                "Company_Name",
                ""
            ),

            "Sector":
            meta.get(
                "Sector",
                ""
            ),

            "Industry":
            meta.get(
                "Industry",
                ""
            ),

            "Market_Cap":
            meta.get(
                "Market_Cap",
                np.nan
            ),

            "Last_Close":
            float(close.iloc[-1]),

            "Momentum_1M":
            mom_1m,

            "Momentum_3M":
            mom_3m,

            "Momentum_6M":
            mom_6m,

            "Momentum_12M":
            mom_12m,

            "Volatility_20D":
            vol_20d,

            "Volatility_60D":
            vol_60d,

            "ATR_14":
            atr_14,

            "Max_Drawdown_252D":
            max_dd,

            "Distance_SMA50":
            distance_sma50,

            "Distance_SMA200":
            distance_sma200,

            "Distance_52W_High":
            distance_52w,

            "ADV_20D":
            adv_20d,

            "Dollar_Volume":
            dollar_volume,
        }

    except Exception:

        return None

# =========================================================
# BUILD SNAPSHOTS
# =========================================================

master_rows = []

print(
    "\n🚀 Building Factor Snapshots..."
)

for snapshot_date in month_ends:

    print(
        snapshot_date.strftime(
            "%Y-%m"
        )
    )

    records = []

    with ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:

        results = executor.map(

            lambda s:
            calculate_snapshot(
                s,
                snapshot_date,
            ),

            symbols,
        )

        for r in results:

            if r is not None:
                records.append(r)

    snapshot_df = pd.DataFrame(
        records
    )

    snapshot_file = (

        SNAPSHOT_DIR

        / (
            "factor_snapshot_"
            + snapshot_date.strftime(
                "%Y_%m"
            )
            + ".parquet"
        )
    )

    snapshot_df.to_parquet(
        snapshot_file,
        index=False,
    )

    master_rows.extend(
        records
    )

# =========================================================
# MASTER FILE
# =========================================================

master = pd.DataFrame(
    master_rows
)

master.to_csv(
    MASTER_FILE,
    index=False,
)

# =========================================================
# REPORT
# =========================================================

report = pd.DataFrame({

    "Metric": [

        "Snapshots",

        "Total_Rows",

        "Unique_Securities",

        "Run_Date",

        "Engine_Version",
    ],

    "Value": [

        len(month_ends),

        len(master),

        master["Symbol"]
        .nunique(),

        datetime.now()
        .strftime(
            "%Y-%m-%d"
        ),

        ENGINE_VERSION,
    ]
})

report.to_csv(
    REPORT_FILE,
    index=False,
)

# =========================================================
# COMPLETION
# =========================================================

print("\n" + "=" * 70)

print(
    "🏁 FACTOR SNAPSHOT ENGINE COMPLETE"
)

print("=" * 70)

print(
    f"Snapshots Built : "
    f"{len(month_ends):,}"
)

print(
    f"Rows Generated  : "
    f"{len(master):,}"
)

print(
    f"Securities      : "
    f"{master['Symbol'].nunique():,}"
)

print(
    f"\nSnapshot Directory:\n"
    f"{SNAPSHOT_DIR}"
)

print("=" * 70)