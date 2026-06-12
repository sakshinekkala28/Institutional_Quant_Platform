"""
=========================================================
REGIME ENGINE
=========================================================

Purpose:
Institutional Market Regime Detection

Inputs:
data/raw/prices/*.parquet
data/backtests/walk_forward_equity_curve.csv

Outputs:
data/regime/regime_status.csv
data/regime/regime_history.csv
data/regime/regime_dashboard.csv

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

TRADING_DAYS = 252

BREADTH_LOOKBACK = 200

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

PRICE_DIR = (
    ROOT
    / "data"
    / "raw"
    / "prices"
)

BACKTEST_FILE = (
    ROOT
    / "data"
    / "backtests"
    / "walk_forward_equity_curve.csv"
)

OUTPUT_DIR = (
    ROOT
    / "data"
    / "regime"
)

REPORT_FILE = (
    ROOT
    / "data"
    / "logs"
    / "regime_report.csv"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

# =========================================================
# LOAD EQUITY CURVE
# =========================================================

print(
    "\n📥 Loading Equity Curve..."
)

equity = pd.read_csv(
    BACKTEST_FILE
)

equity["Date"] = pd.to_datetime(
    equity["Date"]
)

# =========================================================
# TREND SCORE
# =========================================================

equity["SMA_6M"] = (
    equity["Portfolio_Value"]
    .rolling(6)
    .mean()
)

equity["SMA_12M"] = (
    equity["Portfolio_Value"]
    .rolling(12)
    .mean()
)

latest = equity.iloc[-1]

trend_score = 50

if latest["SMA_6M"] > latest["SMA_12M"]:
    trend_score = 100
else:
    trend_score = 0

# =========================================================
# VOLATILITY SCORE
# =========================================================

returns = (
    equity["Portfolio_Value"]
    .pct_change()
    .dropna()
)

annual_vol = (
    returns.std()
    * np.sqrt(12)
)

if annual_vol < 0.15:
    vol_score = 100

elif annual_vol < 0.25:
    vol_score = 60

else:
    vol_score = 20

# =========================================================
# DRAWDOWN SCORE
# =========================================================

equity["High_Water_Mark"] = (
    equity["Portfolio_Value"]
    .cummax()
)

equity["Drawdown"] = (
    equity["Portfolio_Value"]
    / equity["High_Water_Mark"]
    - 1
)

max_drawdown = (
    equity["Drawdown"]
    .min()
)

current_dd = equity["Drawdown"].iloc[-1]

if current_dd > -0.05:
    dd_score = 100

elif current_dd > -0.15:
    dd_score = 60

else:
    dd_score = 10

# =========================================================
# MARKET BREADTH
# =========================================================

print(
    "\n📊 Calculating Breadth..."
)

breadth_records = []

files = list(
    PRICE_DIR.glob("*.parquet")
)

for file in files:

    try:

        df = pd.read_parquet(
            file,
            columns=[
                "Date",
                "Close",
            ],
        )

        if len(df) < BREADTH_LOOKBACK:
            continue

        close = pd.to_numeric(
            df["Close"],
            errors="coerce"
        )

        sma200 = (
            close
            .tail(200)
            .mean()
        )

        latest_price = (
            close.iloc[-1]
        )

        breadth_records.append(

            latest_price
            > sma200

        )

    except Exception:

        continue

breadth_pct = (
    np.mean(
        breadth_records
    )
    * 100
)

if breadth_pct > 70:
    breadth_score = 100

elif breadth_pct > 40:
    breadth_score = 60

else:
    breadth_score = 20

# =========================================================
# REGIME SCORE
# =========================================================

regime_score = (

      0.35
    * trend_score

    + 0.30
    * breadth_score

    + 0.20
    * dd_score

    + 0.15
    * vol_score

)

# =========================================================
# REGIME CLASSIFICATION
# =========================================================

if regime_score >= 80:

    regime = "STRONG_BULL"

elif regime_score >= 60:

    regime = "BULL"

elif regime_score >= 40:

    regime = "NEUTRAL"

elif regime_score >= 20:

    regime = "BEAR"

else:

    regime = "CRISIS"

# =========================================================
# REGIME STATUS
# =========================================================

status = pd.DataFrame({

    "Date": [
        datetime.now()
        .strftime("%Y-%m-%d")
    ],

    "Regime": [
        regime
    ],

    "Regime_Score": [
        round(
            regime_score,
            2
        )
    ],

    "Trend_Score": [
        trend_score
    ],

    "Breadth_Score": [
        breadth_score
    ],

    "Volatility_Score": [
        vol_score
    ],

    "Drawdown_Score": [
        dd_score
    ],

    "Market_Breadth_Pct": [
        round(
            breadth_pct,
            2
        )
    ],

    "Current_Drawdown": [
        current_dd
    ],

    "Annual_Volatility": [
        annual_vol
    ],

    "Engine_Version": [
        ENGINE_VERSION
    ]
})

# =========================================================
# DASHBOARD
# =========================================================

dashboard = pd.DataFrame({

    "Metric": [

        "Regime",

        "Regime_Score",

        "Market_Breadth",

        "Current_Drawdown",

        "Annual_Volatility",
    ],

    "Value": [

        regime,

        regime_score,

        breadth_pct,

        current_dd,

        annual_vol,
    ]
})

# =========================================================
# SAVE
# =========================================================

status.to_csv(
    OUTPUT_DIR
    / "regime_status.csv",
    index=False,
)

status.to_csv(
    OUTPUT_DIR
    / "regime_history.csv",
    index=False,
)

dashboard.to_csv(
    OUTPUT_DIR
    / "regime_dashboard.csv",
    index=False,
)

dashboard.to_csv(
    REPORT_FILE,
    index=False,
)

# =========================================================
# REPORT
# =========================================================

print("\n" + "=" * 70)

print(
    "🏁 REGIME ENGINE COMPLETE"
)

print("=" * 70)

print(
    f"Regime           : {regime}"
)

print(
    f"Regime Score     : "
    f"{regime_score:.2f}"
)

print(
    f"Breadth          : "
    f"{breadth_pct:.2f}%"
)

print(
    f"Current Drawdown : "
    f"{current_dd:.2%}"
)

print(
    f"Annual Vol       : "
    f"{annual_vol:.2%}"
)

print(
    f"\nOutput Directory:\n"
    f"{OUTPUT_DIR}"
)

print("=" * 70)