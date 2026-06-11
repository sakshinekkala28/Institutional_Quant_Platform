"""
=========================================================
MARKET CAP ENRICHMENT ENGINE
=========================================================

Input:
data/raw/symbol_metadata.csv

Output:
data/raw/symbol_metadata.csv

Adds:
Market_Cap

=========================================================
"""

from pathlib import Path
import warnings
import time

import pandas as pd
import yfinance as yf

warnings.filterwarnings("ignore")

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    ROOT
    / "data"
    / "raw"
    / "symbol_metadata.csv"
)

# =========================================================
# CONFIG
# =========================================================

MAX_RETRIES = 3

SAVE_INTERVAL = 100

# =========================================================
# FETCHER
# =========================================================

def fetch_market_cap(symbol: str) -> float:

    yahoo_symbol = f"{symbol}.NS"

    for attempt in range(MAX_RETRIES):

        try:

            ticker = yf.Ticker(
                yahoo_symbol
            )

            # Fast path

            try:

                market_cap = (
                    ticker.fast_info.get(
                        "marketCap",
                        0,
                    )
                )

                if (
                    market_cap is not None
                    and market_cap > 0
                ):
                    return float(
                        market_cap
                    )

            except Exception:
                pass

            # Fallback

            try:

                info = ticker.info

                market_cap = (
                    info.get(
                        "marketCap",
                        0,
                    )
                )

                if (
                    market_cap is not None
                    and market_cap > 0
                ):
                    return float(
                        market_cap
                    )

            except Exception:
                pass

        except Exception:
            pass

        time.sleep(0.5)

    return 0.0


# =========================================================
# LOAD
# =========================================================

print("\n💰 Loading Universe...")

df = pd.read_csv(
    INPUT_FILE
)

if "Market_Cap" not in df.columns:

    df["Market_Cap"] = 0.0

df["Market_Cap"] = pd.to_numeric(
    df["Market_Cap"],
    errors="coerce",
).fillna(0.0)

# Force float column

df["Market_Cap"] = (
    df["Market_Cap"]
    .astype(float)
)

# =========================================================
# IDENTIFY MISSING
# =========================================================

missing_rows = df[
    df["Market_Cap"] <= 0
].index

total = len(
    missing_rows
)

print(
    f"Fetching Market Caps for "
    f"{total:,} stocks..."
)

# =========================================================
# ENRICH
# =========================================================

for counter, row_idx in enumerate(
    missing_rows,
    start=1,
):

    symbol = df.loc[
        row_idx,
        "Symbol",
    ]

    market_cap = fetch_market_cap(
        symbol
    )

    df.loc[
        row_idx,
        "Market_Cap",
    ] = float(
        market_cap
    )

    print(
        f"[{counter:,}/{total:,}] "
        f"{symbol:<15} "
        f"MarketCap = "
        f"{market_cap:,.0f}"
    )

    # Save checkpoint

    if counter % SAVE_INTERVAL == 0:

        df.to_csv(
            INPUT_FILE,
            index=False,
        )

        print(
            f"\n💾 Checkpoint Saved "
            f"({counter:,}/{total:,})\n"
        )

# =========================================================
# SAVE
# =========================================================

df.to_csv(
    INPUT_FILE,
    index=False,
)

# =========================================================
# REPORT
# =========================================================

filled = (
    df["Market_Cap"] > 0
).sum()

missing = (
    df["Market_Cap"] <= 0
).sum()

print("\n" + "=" * 70)

print(
    "✅ MARKET CAP ENRICHMENT COMPLETE"
)

print("=" * 70)

print(
    f"Filled Market Caps : {filled:,}"
)

print(
    f"Missing Market Caps: {missing:,}"
)

print(
    f"\nSaved:\n{INPUT_FILE}"
)

print("=" * 70)