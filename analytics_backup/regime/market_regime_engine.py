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
    / "regime"
    / "market_regime.csv"
)

# =========================================================
# LOAD DATA
# =========================================================

print("\n📥 Loading Regime Inputs...")

breadth = pd.read_csv(
    BREADTH_FILE
)

# prepare breadth dates
breadth["Date"] = pd.to_datetime(breadth["Date"])
breadth = breadth.sort_values("Date")

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

# =========================================================
# BUILD HISTORICAL REGIME SERIES
# =========================================================

regime_history = []

for idx in range(200, len(benchmark)):

    row = benchmark.iloc[idx]

    date = row["Date"]

    close = row["Close"]

    dma200 = row["DMA200"]

    volatility = row["VOL20"]

    # Use latest available breadth up to this date
    mask = breadth["Date"] <= date
    if mask.any():
        latest_breadth = breadth.loc[mask].iloc[-1]
    else:
        latest_breadth = breadth.iloc[0]

    breadth_score = latest_breadth["BREADTH_SCORE"]

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

    if volatility >= 25:

        regime += "_HIGH_VOL"

    elif volatility <= 15:

        regime += "_LOW_VOL"

    regime_history.append({

        "Date":
        date,

        "Regime":
        regime,

        "Close":
        close,

        "DMA200":
        dma200,

        "VOL20":
        volatility,

        "BREADTH_SCORE":
        breadth_score,
    })

# =========================================================
# SAVE
# =========================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

regime_df = pd.DataFrame(regime_history)

regime_df.to_csv(
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

# derive simple target exposures for reporting
if regime.startswith("BULL"):
    equity_exposure = 1.0
elif regime.startswith("BEAR"):
    equity_exposure = 0.0
else:
    equity_exposure = 0.5

# adjust for volatility
if "HIGH_VOL" in regime:
    equity_exposure = max(0.0, equity_exposure - 0.1)
elif "LOW_VOL" in regime:
    equity_exposure = min(1.0, equity_exposure + 0.1)

cash_weight = 1.0 - equity_exposure

print(f"Target Exposure    : {equity_exposure:.0%}")
print(f"Cash Allocation    : {cash_weight:.0%}")

print(
    f"\nSaved:\n{OUTPUT_FILE}"
)

print("=" * 70)