"""
=========================================================
INCREMENTAL PRICE UPDATE ENGINE
=========================================================

Purpose:
Update existing price files with only
new candles since last update.

Input:
data/raw/updated_stocks.csv

Output:
data/raw/prices/*.parquet

Logs:
data/logs/price_update_failures.csv
data/logs/invalid_symbols.csv

=========================================================
"""

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
import yfinance as yf

# =========================================================
# CONFIG
# =========================================================

MAX_WORKERS = 2

FULL_HISTORY_YEARS = 5

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

UNIVERSE_FILE = (
    ROOT
    / "data"
    / "raw"
    / "updated_stocks.csv"
)

PRICE_DIR = (
    ROOT
    / "data"
    / "raw"
    / "prices"
)

FAILURE_FILE = (
    ROOT
    / "data"
    / "logs"
    / "price_update_failures.csv"
)

INVALID_FILE = (
    ROOT
    / "data"
    / "logs"
    / "invalid_symbols.csv"
)

PRICE_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

FAILURE_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

# =========================================================
# LOAD UNIVERSE
# =========================================================

print("\n📥 Loading Investable Universe...")

universe = pd.read_csv(
    UNIVERSE_FILE
)

symbols = (
    universe["Symbol"]
    .dropna()
    .astype(str)
    .str.upper()
    .str.strip()
    .unique()
    .tolist()
)

# =========================================================
# INVALID SYMBOL CACHE
# =========================================================

invalid_symbols = set()

if INVALID_FILE.exists():

    invalid_symbols = set(
        pd.read_csv(
            INVALID_FILE
        )["Symbol"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

symbols = [
    s
    for s in symbols
    if s not in invalid_symbols
]

print(
    f"Universe Size : {len(symbols):,}"
)

print(
    f"Blacklisted Symbols : "
    f"{len(invalid_symbols):,}"
)

# =========================================================
# STATS
# =========================================================

updated_count = 0
new_count = 0
skipped_count = 0
failure_count = 0

failures = []
new_invalid = []

today = pd.Timestamp.today().normalize()

if today.weekday() == 0:
    expected_date = (
        today - pd.Timedelta(days=3)
    )
else:
    expected_date = (
        today - pd.Timedelta(days=1)
    )

# =========================================================
# DOWNLOAD FUNCTION
# =========================================================

def download_full_history(symbol):

    return yf.download(
        f"{symbol}.NS",
        period=f"{FULL_HISTORY_YEARS}y",
        auto_adjust=True,
        progress=False,
        threads=False,
    )

# =========================================================
# UPDATE SYMBOL
# =========================================================

def update_symbol(symbol):

    output_file = (
        PRICE_DIR
        / f"{symbol}.parquet"
    )

    try:

        # ==========================================
        # NEW FILE
        # ==========================================

        if not output_file.exists():

            df = download_full_history(
                symbol
            )

            if len(df) < 252:

                new_invalid.append(
                    {
                        "Symbol": symbol,
                        "Reason": (
                            f"Insufficient History "
                            f"({len(df)} rows)"
                        ),
                    }
                )

                return "INVALID"

            if df.empty:

                new_invalid.append(
                    {
                        "Symbol": symbol,
                        "Reason": "No Yahoo Data",
                    }
                )

                return "INVALID"

            df = df.reset_index()

            if isinstance(
                df.columns,
                pd.MultiIndex,
            ):
                df.columns = [
                    c[0]
                    for c in df.columns
                ]

            df.columns = [
                str(c).replace(
                    " ",
                    "_"
                )
                for c in df.columns
            ]

            df["Symbol"] = symbol

            df.to_parquet(
                output_file,
                index=False,
            )

            return "NEW"

        # ==========================================
        # EXISTING FILE
        # ==========================================

        existing = pd.read_parquet(
            output_file
        )

        if len(existing) < 252:

            new_invalid.append(
                {
                    "Symbol": symbol,
                    "Reason": (
                        f"Corrupted History "
                        f"({len(existing)} rows)"
                    ),
                }
            )

            return "INVALID"

        if existing.empty:
            return "SKIPPED"

        last_date = pd.to_datetime(
            existing["Date"]
        ).max()

        if (
            last_date.normalize()
            >= expected_date
        ):
            return "SKIPPED"

        start_date = (
            last_date
            + pd.Timedelta(days=1)
        )

        new_data = yf.download(
            f"{symbol}.NS",
            start=start_date.strftime(
                "%Y-%m-%d"
            ),
            auto_adjust=True,
            progress=False,
            threads=False,
        )

        if new_data.empty:
            return "SKIPPED"

        new_data = (
            new_data
            .reset_index()
        )

        if isinstance(
            new_data.columns,
            pd.MultiIndex,
        ):
            new_data.columns = [
                c[0]
                for c in new_data.columns
            ]

        new_data.columns = [
            str(c).replace(
                " ",
                "_"
            )
            for c in new_data.columns
        ]

        new_data["Symbol"] = symbol

        updated = pd.concat(
            [
                existing,
                new_data,
            ],
            ignore_index=True,
        )

        updated = (
            updated
            .drop_duplicates(
                subset=["Date"]
            )
            .sort_values(
                "Date"
            )
        )

        updated.to_parquet(
            output_file,
            index=False,
        )

        return "UPDATED"

    except Exception as e:

        failures.append(
            {
                "Symbol": symbol,
                "Error": str(e),
            }
        )

        return "FAILED"

# =========================================================
# EXECUTION
# =========================================================

print(
    "\n🚀 Updating Price History..."
)

with ThreadPoolExecutor(
    max_workers=MAX_WORKERS
) as executor:

    results = executor.map(
        update_symbol,
        symbols,
    )

    total = len(symbols)

    for idx, result in enumerate(
        results,
        start=1,
    ):

        if result == "NEW":
            new_count += 1

        elif result == "UPDATED":
            updated_count += 1

        elif result == "SKIPPED":
            skipped_count += 1

        elif result == "FAILED":
            failure_count += 1

        elif result == "INVALID":
            failure_count += 1

        if idx % 50 == 0:

            print(
                f"{idx:,}/{total:,}"
            )

# =========================================================
# SAVE FAILURE LOG
# =========================================================

if failures:

    pd.DataFrame(
        failures
    ).to_csv(
        FAILURE_FILE,
        index=False,
    )

# =========================================================
# SAVE INVALID SYMBOLS
# =========================================================

if new_invalid:

    invalid_df = pd.DataFrame(
        new_invalid
    )

    if INVALID_FILE.exists():

        old = pd.read_csv(
            INVALID_FILE
        )

        invalid_df = pd.concat(
            [
                old,
                invalid_df,
            ],
            ignore_index=True,
        )

    invalid_df = (
        invalid_df
        .drop_duplicates(
            subset=["Symbol"],
            keep="last",
        )
        .sort_values(
            "Symbol"
        )
    )

    invalid_df.to_csv(
        INVALID_FILE,
        index=False,
    )

# =========================================================
# REPORT
# =========================================================

coverage = round(
    (
        skipped_count
        + updated_count
        + new_count
    )
    / max(len(symbols), 1)
    * 100,
    2,
)

print(
    f"Coverage          : "
    f"{coverage}%"
)

print("\n" + "=" * 70)
print("🏁 PRICE UPDATE COMPLETE")
print("=" * 70)

print(
    f"Universe Size      : {len(symbols):,}"
)

print(
    f"New Files          : {new_count:,}"
)

print(
    f"Updated Files      : {updated_count:,}"
)

print(
    f"Skipped Files      : {skipped_count:,}"
)

print(
    f"Failures           : {failure_count:,}"
)

print(
    f"Invalid Symbols    : "
    f"{len(new_invalid):,}"
)

if failures:

    print(
        f"\nFailure Log:\n"
        f"{FAILURE_FILE}"
    )

print(
    f"\nPrice Directory:\n"
    f"{PRICE_DIR}"
)

print("=" * 70)