"""
=========================================================
MARKET BREADTH ENGINE
=========================================================

Institutional Breadth Model

Measures:
- Advance / Decline Ratio
- % Above 20 DMA
- % Above 50 DMA
- % Above 200 DMA
- New 52 Week Highs
- New 52 Week Lows
- Breadth Score
- Breadth Regime

Input:
data/raw/prices/*.parquet

Output:
data/processed/market_breadth.csv

=========================================================
"""

from pathlib import Path

import pandas as pd

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

OUTPUT_FILE = (
    ROOT
    / "data"
    / "processed"
    / "market_breadth.csv"
)

# =========================================================
# LOAD FILES
# =========================================================

print("\n📥 Loading Price Files...")

price_files = list(
    PRICE_DIR.glob("*.parquet")
)

if not price_files:

    raise FileNotFoundError(
        f"No parquet files found in:\n{PRICE_DIR}"
    )

print(
    f"Price Files : {len(price_files):,}"
)

# =========================================================
# PROCESS
# =========================================================

print(
    "\n📈 Calculating Breadth Metrics..."
)

daily_stats = []

for idx, file in enumerate(
    price_files,
    start=1,
):

    try:

        df = pd.read_parquet(file)

        required = [
            "Date",
            "Close",
        ]

        if not all(
            col in df.columns
            for col in required
        ):
            continue

        df["Date"] = pd.to_datetime(
            df["Date"]
        )

        df = df.sort_values(
            "Date"
        )

        if len(df) < 252:
            continue

        # =========================================
        # MOVING AVERAGES
        # =========================================

        df["DMA20"] = (
            df["Close"]
            .rolling(
                20,
                min_periods=20,
            )
            .mean()
        )

        df["DMA50"] = (
            df["Close"]
            .rolling(
                50,
                min_periods=50,
            )
            .mean()
        )

        df["DMA200"] = (
            df["Close"]
            .rolling(
                200,
                min_periods=200,
            )
            .mean()
        )

        # =========================================
        # RETURNS
        # =========================================

        df["RET_1D"] = (
            df["Close"]
            .pct_change()
        )

        # =========================================
        # 52W HIGH / LOW
        # =========================================

        df["HIGH_252"] = (
            df["Close"]
            .rolling(
                252,
                min_periods=252,
            )
            .max()
        )

        df["LOW_252"] = (
            df["Close"]
            .rolling(
                252,
                min_periods=252,
            )
            .min()
        )

        latest = df.iloc[-1]

        daily_stats.append(
            {
                "Date": latest["Date"],
                "Advance": (
                    latest["RET_1D"] > 0
                ),
                "Decline": (
                    latest["RET_1D"] < 0
                ),
                "Above20": (
                    latest["Close"]
                    > latest["DMA20"]
                ),
                "Above50": (
                    latest["Close"]
                    > latest["DMA50"]
                ),
                "Above200": (
                    latest["Close"]
                    > latest["DMA200"]
                ),
                "NewHigh": (
                    latest["Close"]
                    >= latest["HIGH_252"]
                ),
                "NewLow": (
                    latest["Close"]
                    <= latest["LOW_252"]
                ),
            }
        )

    except Exception:
        continue

    if idx % 500 == 0:

        print(
            f"{idx:,}/{len(price_files):,}"
        )

# =========================================================
# BUILD BREADTH DATASET
# =========================================================

print(
    "\n📊 Building Breadth Dataset..."
)

breadth_raw = pd.DataFrame(
    daily_stats
)

if breadth_raw.empty:

    raise RuntimeError(
        "No breadth data generated."
    )

latest_date = (
    breadth_raw["Date"]
    .max()
)

breadth_raw = breadth_raw[
    breadth_raw["Date"]
    == latest_date
]

# =========================================================
# AGGREGATION
# =========================================================

total_stocks = len(
    breadth_raw
)

advances = (
    breadth_raw["Advance"]
    .sum()
)

declines = (
    breadth_raw["Decline"]
    .sum()
)

above20 = (
    breadth_raw["Above20"]
    .sum()
)

above50 = (
    breadth_raw["Above50"]
    .sum()
)

above200 = (
    breadth_raw["Above200"]
    .sum()
)

new_highs = (
    breadth_raw["NewHigh"]
    .sum()
)

new_lows = (
    breadth_raw["NewLow"]
    .sum()
)

# =========================================================
# RATIOS
# =========================================================

adv_dec_ratio = (
    advances
    / max(
        declines,
        1,
    )
)

pct_above20 = (
    above20
    / total_stocks
    * 100
)

pct_above50 = (
    above50
    / total_stocks
    * 100
)

pct_above200 = (
    above200
    / total_stocks
    * 100
)

new_high_low_ratio = (
    new_highs
    / max(
        new_lows,
        1,
    )
)

# =========================================================
# BREADTH SCORE
# =========================================================

breadth_score = (
    pct_above20 * 0.20
    +
    pct_above50 * 0.30
    +
    pct_above200 * 0.50
)

breadth_score = round(
    breadth_score,
    2,
)

# =========================================================
# REGIME
# =========================================================

if breadth_score >= 70:

    regime = "STRONG_BULL"

elif breadth_score >= 55:

    regime = "BULL"

elif breadth_score >= 40:

    regime = "NEUTRAL"

elif breadth_score >= 25:

    regime = "BEAR"

else:

    regime = "STRONG_BEAR"

# =========================================================
# FINAL DATASET
# =========================================================

breadth = pd.DataFrame(
    [
        {
            "Date": latest_date,
            "Total_Stocks": total_stocks,
            "Advances": advances,
            "Declines": declines,
            "Above20": above20,
            "Above50": above50,
            "Above200": above200,
            "NewHighs": new_highs,
            "NewLows": new_lows,
            "ADV_DEC_RATIO": round(
                adv_dec_ratio,
                4,
            ),
            "PCT_ABOVE_20DMA": round(
                pct_above20,
                2,
            ),
            "PCT_ABOVE_50DMA": round(
                pct_above50,
                2,
            ),
            "PCT_ABOVE_200DMA": round(
                pct_above200,
                2,
            ),
            "NEW_HIGH_LOW_RATIO": round(
                new_high_low_ratio,
                4,
            ),
            "BREADTH_SCORE": breadth_score,
            "BREADTH_REGIME": regime,
        }
    ]
)

# =========================================================
# SAVE
# =========================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

breadth.to_csv(
    OUTPUT_FILE,
    index=False,
)

# =========================================================
# REPORT
# =========================================================

latest = breadth.iloc[0]

print("\n" + "=" * 70)

print(
    "🏁 MARKET BREADTH ENGINE COMPLETE"
)

print("=" * 70)

print(
    f"Date               : {latest['Date']}"
)

print(
    f"Universe           : {latest['Total_Stocks']:,}"
)

print(
    f"Advance/Decline    : {latest['ADV_DEC_RATIO']:.2f}"
)

print(
    f"% Above 20DMA      : {latest['PCT_ABOVE_20DMA']:.2f}"
)

print(
    f"% Above 50DMA      : {latest['PCT_ABOVE_50DMA']:.2f}"
)

print(
    f"% Above 200DMA     : {latest['PCT_ABOVE_200DMA']:.2f}"
)

print(
    f"New High/Low Ratio : {latest['NEW_HIGH_LOW_RATIO']:.2f}"
)

print(
    f"Breadth Score      : {latest['BREADTH_SCORE']:.2f}"
)

print(
    f"Regime             : {latest['BREADTH_REGIME']}"
)

print(
    f"\nSaved:\n{OUTPUT_FILE}"
)

print("=" * 70)