"""
=========================================================
MARKET REGIME ENGINE
=========================================================

Classifies market into:

- BULL
- BEAR
- SIDEWAYS
- HIGH_VOL
- LOW_VOL

Output:
data/processed/market_regime.csv
=========================================================
"""

from pathlib import Path

import numpy as np
import pandas as pd

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

BREADTH_FILE = (
    ROOT
    / "data"
    / "processed"
    / "market_breadth.csv"
)

BENCHMARK_FILE = (
    ROOT
    / "data"
    / "raw"
    / "benchmark_prices.csv"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "processed"
    / "market_regime.csv"
)

# =========================================================
# LOAD DATA
# =========================================================

print("\n📥 Loading Regime Inputs...")

breadth = pd.read_csv(
    BREADTH_FILE
)

benchmark = pd.read_csv(
    BENCHMARK_FILE
)

benchmark["Date"] = pd.to_datetime(
    benchmark["Date"]
)

benchmark = benchmark.sort_values(
    "Date"
)

# =========================================================
# BENCHMARK INDICATORS
# =========================================================

print(
    "\n📈 Calculating Trend Indicators..."
)

benchmark["DMA200"] = (
    benchmark["Close"]
    .rolling(
        200,
        min_periods=200,
    )
    .mean()
)

benchmark["RET"] = (
    benchmark["Close"]
    .pct_change()
)

benchmark["VOL20"] = (
    benchmark["RET"]
    .rolling(
        20,
        min_periods=20,
    )
    .std()
    * np.sqrt(252)
    * 100
)

latest_benchmark = benchmark.iloc[-1]

# =========================================================
# BREADTH
# =========================================================

latest_breadth = breadth.iloc[-1]

breadth_score = (
    latest_breadth["BREADTH_SCORE"]
)

# =========================================================
# REGIME CLASSIFICATION
# =========================================================

close = latest_benchmark["Close"]

dma200 = latest_benchmark["DMA200"]

volatility = latest_benchmark["VOL20"]

regime = "SIDEWAYS"

if (
    close > dma200
    and breadth_score >= 60
):
    regime = "BULL"

elif (
    close < dma200
    and breadth_score <= 40
):
    regime = "BEAR"

# volatility overlay

if volatility >= 25:
    regime = f"{regime}_HIGH_VOL"

elif volatility <= 15:
    regime = f"{regime}_LOW_VOL"

# =========================================================
# RISK BUDGET
# =========================================================

if "BULL" in regime:

    equity_exposure = 1.00
    cash_weight = 0.00

elif "BEAR" in regime:

    equity_exposure = 0.40
    cash_weight = 0.60

else:

    equity_exposure = 0.70
    cash_weight = 0.30

# =========================================================
# OUTPUT
# =========================================================

output = pd.DataFrame(
    {
        "DATE": [latest_benchmark["Date"]],
        "REGIME": [regime],
        "BENCHMARK_CLOSE": [close],
        "DMA200": [dma200],
        "VOL20": [round(volatility, 2)],
        "BREADTH_SCORE": [round(breadth_score, 2)],
        "TARGET_EQUITY_EXPOSURE": [
            equity_exposure
        ],
        "TARGET_CASH_WEIGHT": [
            cash_weight
        ],
    }
)

# =========================================================
# SAVE
# =========================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

output.to_csv(
    OUTPUT_FILE,
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
    f"Regime             : {regime}"
)

print(
    f"Breadth Score      : {breadth_score:.2f}"
)

print(
    f"20D Volatility     : {volatility:.2f}%"
)

print(
    f"Target Exposure    : {equity_exposure:.0%}"
)

print(
    f"Cash Allocation    : {cash_weight:.0%}"
)

print(
    f"\nSaved:\n{OUTPUT_FILE}"
)

print("=" * 70)