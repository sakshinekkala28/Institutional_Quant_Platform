"""
=========================================================
FACTOR ENGINE
=========================================================

Purpose:
Calculate institutional equity factors

Input:
data/raw/security_master.csv
data/raw/prices/*.parquet

Output:
data/factors/factor_master.csv

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

MAX_WORKERS = 4

TRADING_DAYS = 252

ENGINE_VERSION = "1.0.0"

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

OUTPUT_FILE = (
    ROOT
    / "data"
    / "factors"
    / "factor_master.csv"
)

FAILURE_FILE = (
    ROOT
    / "data"
    / "logs"
    / "factor_failures.csv"
)

COVERAGE_FILE = (
    ROOT
    / "data"
    / "logs"
    / "factor_coverage.csv"
)

# =========================================================
# LOAD UNIVERSE
# =========================================================

print("\n📥 Loading Security Master...")

universe = pd.read_csv(
    SECURITY_MASTER
)

symbols = (
    universe["Symbol"]
    .dropna()
    .astype(str)
    .str.upper()
    .unique()
    .tolist()
)

security_lookup = (
    universe.set_index("Symbol")
)

print(
    f"Universe Size : {len(symbols):,}"
)

# =========================================================
# FACTOR FUNCTION
# =========================================================

failures = []

def calculate_factors(symbol):

    try:

        file = (
            PRICE_DIR
            / f"{symbol}.parquet"
        )

        if not file.exists():
            return None

        df = pd.read_parquet(file)

        required_cols = [
            "Close",
            "High",
            "Low",
            "Volume",
        ]

        if not all(
            c in df.columns
            for c in required_cols
        ):
            return None

        if len(df) < 252:
            return None

        close = (
            pd.to_numeric(
                df["Close"],
                errors="coerce",
            )
            .dropna()
        )

        volume = pd.to_numeric(
            df["Volume"],
            errors="coerce",
        )

        if len(close) < 252:
            return None

        # =====================================
        # MOMENTUM
        # =====================================

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

        market_cap = security_lookup.loc[
            symbol,
            "Market_Cap",
        ]

        log_market_cap = np.log(
            max(
                market_cap,
                1
            )
        )

        # =====================================
        # RETURNS
        # =====================================

        returns = (
            close.pct_change()
            .dropna()
        )

        rolling_max = (
            close.cummax()
        )

        drawdown = (
            close
            / rolling_max
        ) - 1

        max_drawdown = (
            drawdown.min()
        )

        vol_20d = (
            returns.tail(20)
            .std()
            * np.sqrt(TRADING_DAYS)
        )

        vol_60d = (
            returns.tail(60)
            .std()
            * np.sqrt(TRADING_DAYS)
        )

        # =====================================
        # ATR
        # =====================================

        high = pd.to_numeric(
            df["High"],
            errors="coerce",
        )

        low = pd.to_numeric(
            df["Low"],
            errors="coerce",
        )

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

        sma50 = (
            close.tail(50)
            .mean()
        )

        sma200 = (
            close.tail(200)
            .mean()
        )

        high_52w = (
            close.tail(252)
            .max()
        )

        distance_52w_high = (
            close.iloc[-1]
            / high_52w
        ) - 1

        distance_sma50 = (
            close.iloc[-1]
            / sma50
        ) - 1

        distance_sma200 = (
            close.iloc[-1]
            / sma200
        ) - 1

        # =====================================
        # LIQUIDITY
        # =====================================

        adv_20d = (
            close.tail(20)
            * volume.tail(20)
        ).mean()

        dollar_volume = adv_20d

        turnover_ratio = (
            volume.tail(20)
            .mean()
        )

        return {

            "Security_ID":
            security_lookup.loc[
                symbol,
                "Security_ID",
            ],

            "Symbol":
            symbol,

            "Company_Name":
            security_lookup.loc[
                symbol,
                "Company_Name",
            ],

            "Sector":
            security_lookup.loc[
                symbol,
                "Sector",
            ],

            "Industry":
            security_lookup.loc[
                symbol,
                "Industry",
            ],

            "Last_Close":
            close.iloc[-1],

            # ======================
            # SIZE
            # ======================

            "Market_Cap":
            market_cap,

            "Log_Market_Cap":
            log_market_cap,

            # ======================
            # MOMENTUM
            # ======================

            "Momentum_1M":
            mom_1m,

            "Momentum_3M":
            mom_3m,

            "Momentum_6M":
            mom_6m,

            "Momentum_12M":
            mom_12m,

            # ======================
            # RISK
            # ======================

            "Volatility_20D":
            vol_20d,

            "Volatility_60D":
            vol_60d,

            "ATR_14":
            atr_14,

            "Max_Drawdown_252D":
            max_drawdown,

            # ======================
            # TREND
            # ======================

            "SMA_50":
            sma50,

            "SMA_200":
            sma200,

            "Distance_SMA50":
            distance_sma50,

            "Distance_SMA200":
            distance_sma200,

            # ======================
            # 52 WEEK HIGH
            # ======================

            "Price_52W_High":
            high_52w,

            "Distance_52W_High":
            distance_52w_high,

            # ======================
            # LIQUIDITY
            # ======================

            "ADV_20D":
            adv_20d,

            "Dollar_Volume":
            dollar_volume,

            "Turnover_Ratio":
            turnover_ratio,

            # ======================
            # META
            # ======================

            "Factor_Date":
            pd.Timestamp.today()
            .strftime("%Y-%m-%d"),

            "Engine_Version":
            ENGINE_VERSION,
        }

    except Exception as e:

        failures.append(
            {
                "Symbol": symbol,
                "Error": str(e),
                "Timestamp":
                datetime.now()
                .strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            }
        )

        return None

# =========================================================
# EXECUTION
# =========================================================

print(
    "\n📊 Calculating Factors..."
)

records = []

with ThreadPoolExecutor(
    max_workers=MAX_WORKERS
) as executor:

    results = executor.map(
        calculate_factors,
        symbols,
    )

    for idx, result in enumerate(
        results,
        start=1,
    ):

        if result is not None:
            records.append(result)

        if idx % 100 == 0:

            print(
                f"{idx:,}/{len(symbols):,}"
            )

# =========================================================
# OUTPUT
# =========================================================

factor_master = pd.DataFrame(
    records
)

factor_master = (
    factor_master
    .sort_values(
        "Market_Cap",
        ascending=False,
    )
    .reset_index(drop=True)
)

FAILURE_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

COVERAGE_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

factor_master.to_csv(
    OUTPUT_FILE,
    index=False,
)

if failures:

    pd.DataFrame(
        failures
    ).to_csv(
        FAILURE_FILE,
        index=False,
    )

coverage = []

for col in factor_master.columns:

    coverage.append(
        {
            "Factor": col,
            "Coverage":
            factor_master[col]
            .notna()
            .sum(),
        }
    )

COVERAGE_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

pd.DataFrame(
    coverage
).to_csv(
    COVERAGE_FILE,
    index=False,
)

# =========================================================
# REPORT
# =========================================================

print("\n" + "=" * 70)

print(
    "🏁 FACTOR ENGINE COMPLETE"
)

print("=" * 70)

print(
    f"Securities : "
    f"{len(factor_master):,}"
)

print(
    f"Output:\n"
    f"{OUTPUT_FILE}"
)

print("=" * 70)