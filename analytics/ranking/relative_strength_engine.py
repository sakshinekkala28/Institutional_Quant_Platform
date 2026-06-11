"""
=========================================================
RELATIVE STRENGTH ENGINE
=========================================================

Institutional Momentum Model

Output:
data/processed/relative_strength_scores.csv

=========================================================
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import pandas as pd
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler

# =========================================================
# CONFIG
# =========================================================

MAX_WORKERS = 4

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

METADATA_FILE = (
    ROOT
    / "data"
    / "raw"
    / "stock_metadata.csv"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "processed"
    / "relative_strength_scores.csv"
)

# =========================================================
# LOAD UNIVERSE
# =========================================================

print("\n📥 Loading Universe...")

universe = pd.read_csv(
    METADATA_FILE
)

symbols = (
    universe["Symbol"]
    .dropna()
    .astype(str)
    .str.upper()
    .unique()
    .tolist()
)

print(
    f"Universe Size: {len(symbols):,}"
)

# =========================================================
# CALCULATE RETURNS
# =========================================================


def calculate_rs(symbol):

    try:

        df = yf.download(
            f"{symbol}.NS",
            period="18mo",
            auto_adjust=True,
            progress=False,
            threads=False,
        )

        if len(df) < 252:

            return None

        close = df["Close"]

        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]

        r3 = (
            close.iloc[-1]
            / close.iloc[-63]
            - 1
        )

        r6 = (
            close.iloc[-1]
            / close.iloc[-126]
            - 1
        )

        r12 = (
            close.iloc[-1]
            / close.iloc[-252]
            - 1
        )

        rs = (
            r12 * 0.40
            + r6 * 0.35
            + r3 * 0.25
        )

        return {
            "Symbol": symbol,
            "RETURN_3M": round(r3 * 100, 2),
            "RETURN_6M": round(r6 * 100, 2),
            "RETURN_12M": round(r12 * 100, 2),
            "RS_RAW": rs,
        }

    except Exception:

        return None


# =========================================================
# RUN
# =========================================================

print(
    "\n🚀 Calculating Relative Strength..."
)

results = []

with ThreadPoolExecutor(
    max_workers=MAX_WORKERS
) as executor:

    futures = {
        executor.submit(
            calculate_rs,
            symbol,
        ): symbol
        for symbol in symbols
    }

    total = len(futures)

    for idx, future in enumerate(
        as_completed(futures),
        start=1,
    ):

        result = future.result()

        if result:

            results.append(result)

        if idx % 50 == 0:

            print(
                f"{idx:,}/{total:,}"
            )

# =========================================================
# DATAFRAME
# =========================================================

rs_df = pd.DataFrame(
    results
)

if rs_df.empty:
    raise ValueError(
        "No Relative Strength data generated."
    )

# =========================================================
# SCORE
# =========================================================

scaler = MinMaxScaler()

rs_df["RS_SCORE"] = (
    scaler.fit_transform(
        rs_df[["RS_RAW"]]
    )
    * 100
)

rs_df["RS_SCORE"] = (
    rs_df["RS_SCORE"]
    .round(2)
)

# =========================================================
# RANK
# =========================================================

rs_df = rs_df.sort_values(
    "RS_SCORE",
    ascending=False,
)

rs_df["RS_RANK"] = (
    range(
        1,
        len(rs_df) + 1,
    )
)

rs_df = rs_df.drop(
    columns=["RS_RAW"]
)

# =========================================================
# SAVE
# =========================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

rs_df.to_csv(
    OUTPUT_FILE,
    index=False,
)

# =========================================================
# REPORT
# =========================================================

print("\n" + "=" * 70)

print(
    "🏁 RELATIVE STRENGTH ENGINE COMPLETE"
)

print("=" * 70)

print(
    f"Stocks Processed : {len(rs_df):,}"
)

print(
    f"\nSaved:\n{OUTPUT_FILE}"
)

print("=" * 70)