"""
=========================================================
SYMBOL METADATA ENGINE
=========================================================

Purpose:
Build Security Master from Yahoo Finance

Input:
data/raw/valid_stocks.xlsx

Output:
data/raw/symbol_metadata.csv

Fields:
Symbol
Yahoo_Symbol
Company_Name
Sector
Industry
Market_Cap

=========================================================
"""

from pathlib import Path
from concurrent.futures import (
    ThreadPoolExecutor,
    as_completed,
)

import time
import pandas as pd
import yfinance as yf

# =========================================================
# CONFIG
# =========================================================

MAX_WORKERS = 5
SAVE_INTERVAL = 50
MAX_RETRIES = 2

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    ROOT
    / "data"
    / "raw"
    / "valid_stocks.xlsx"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "raw"
    / "symbol_metadata.csv"
)

# =========================================================
# LOAD STOCKS
# =========================================================

print("\n📥 Loading Valid Stocks...")

stocks = pd.read_excel(
    INPUT_FILE
)

possible_columns = [
    "Symbol",
    "SYMBOL",
    "symbol",
    "Stock",
    "Ticker",
]

symbol_col = None

for col in possible_columns:

    if col in stocks.columns:
        symbol_col = col
        break

if symbol_col is None:

    raise ValueError(
        "Symbol column not found."
    )

symbols = (
    stocks[symbol_col]
    .astype(str)
    .str.upper()
    .str.strip()
    .str.replace(
        ".NS",
        "",
        regex=False,
    )
    .dropna()
    .drop_duplicates()
    .tolist()
)

print(
    f"Total Symbols : {len(symbols):,}"
)

# =========================================================
# RESUME SUPPORT
# =========================================================

metadata = []

if OUTPUT_FILE.exists():

    existing = pd.read_csv(
        OUTPUT_FILE
    )

    existing["Symbol"] = (
        existing["Symbol"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    existing["Market_Cap"] = pd.to_numeric(
        existing["Market_Cap"],
        errors="coerce",
    ).fillna(0)

    existing["Company_Name"] = (
        existing["Company_Name"]
        .fillna("")
        .astype(str)
    )

    # Good records
    good_records = existing[
        (existing["Market_Cap"] > 0)
        &
        (existing["Company_Name"] != "")
    ]

    # Bad records to refetch
    bad_records = existing[
        (existing["Market_Cap"] <= 0)
        |
        (existing["Company_Name"] == "")
    ]

    good_symbols = set(
        good_records["Symbol"]
    )

    metadata = (
        good_records.to_dict(
            "records"
        )
    )

    symbols = [
        s
        for s in symbols
        if s not in good_symbols
    ]

    print(
        f"♻️ Existing Good Records : "
        f"{len(good_records):,}"
    )

    print(
        f"🔄 Records To Re-Fetch : "
        f"{len(bad_records):,}"
    )

print(
    f"Remaining Symbols : "
    f"{len(symbols):,}"
)

# =========================================================
# FETCHER
# =========================================================
failed_symbols = []

def fetch_metadata(symbol):

    yahoo_symbol = f"{symbol}.NS"

    for attempt in range(MAX_RETRIES):

        try:

            ticker = yf.Ticker(
                yahoo_symbol
            )

            market_cap = 0

            try:

                fast_info = ticker.fast_info

                market_cap = float(
                    fast_info.get(
                        "market_cap",
                        0
                    ) or 0
                )

            except Exception:
                pass

            fast_info = {}

            try:
                fast_info = ticker.fast_info
            except Exception:
                pass

            info = {}

            try:
                info = ticker.info
            except Exception:
                pass

            company_name = (
                info.get(
                    "longName",
                    ""
                )
                or ""
            )

            sector = (
                info.get(
                    "sector",
                    ""
                )
                or ""
            )

            industry = (
                info.get(
                    "industry",
                    ""
                )
                or ""
            )

            if market_cap > 0:

                print(
                    f"✓ {symbol} "
                    f"MCAP={market_cap:,.0f}"
                )

                return {
                    "Symbol": symbol,
                    "Yahoo_Symbol": yahoo_symbol,
                    "Company_Name": company_name,
                    "Sector": sector,
                    "Industry": industry,
                    "Market_Cap": market_cap,
                    "Last_Updated": pd.Timestamp.now().strftime("%Y-%m-%d"),
                }

        except Exception:

            pass

        time.sleep(1)

    return {
        "Symbol": symbol,
        "Yahoo_Symbol": yahoo_symbol,
        "Company_Name": "",
        "Sector": "",
        "Industry": "",
        "Market_Cap": 0,
    }

# =========================================================
# SAVE CHECKPOINT
# =========================================================

def save_checkpoint(records):

    df = pd.DataFrame(records)

    required_columns = [
        "Symbol",
        "Yahoo_Symbol",
        "Company_Name",
        "Sector",
        "Industry",
        "Market_Cap",
    ]

    for col in required_columns:

        if col not in df.columns:

            if col == "Market_Cap":
                df[col] = 0
            else:
                df[col] = ""

    df["Market_Cap"] = (
        pd.to_numeric(
            df["Market_Cap"],
            errors="coerce",
        )
        .fillna(0)
        .astype("int64")
    )

    df = (
        df
        .sort_values("Symbol")
        .drop_duplicates(
            subset="Symbol"
        )
        .reset_index(drop=True)
    )

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False,
    )

# =========================================================
# FETCH METADATA
# =========================================================

print(
    "\n📊 Fetching Metadata..."
)

completed = 0

with ThreadPoolExecutor(
    max_workers=MAX_WORKERS
) as executor:

    future_map = {
        executor.submit(
            fetch_metadata,
            symbol,
        ): symbol
        for symbol in symbols
    }

    for future in as_completed(
        future_map
    ):

        symbol = (
            future_map[
                future
            ]
        )

        try:

            record = (
                future.result()
            )

        except Exception:

            record = {
                "Symbol": symbol,
                "Yahoo_Symbol": (
                    f"{symbol}.NS"
                ),
                "Company_Name": "",
                "Sector": "",
                "Industry": "",
                "Market_Cap": 0,
            }

        metadata.append(
            record
        )

        completed += 1

        print(
            f"[{completed:,}/"
            f"{len(symbols):,}] "
            f"{symbol}"
        )

        # checkpoint save
        if (
            completed
            % SAVE_INTERVAL
            == 0
        ):

            save_checkpoint(
                metadata
            )

            print(
                f"💾 Checkpoint Saved "
                f"({completed:,})"
            )

# =========================================================
# FINAL SAVE
# =========================================================

save_checkpoint(
    metadata
)

metadata_df = pd.read_csv(
    OUTPUT_FILE
)

print("\n📊 METADATA QUALITY REPORT")
print("=" * 60)

print(
    f"Total Symbols      : "
    f"{len(metadata_df):,}"
)

print(
    f"Company Names      : "
    f"{(metadata_df['Company_Name'] != '').sum():,}"
)

print(
    f"Sectors Available  : "
    f"{(metadata_df['Sector'] != '').sum():,}"
)

print(
    f"Industries Present : "
    f"{(metadata_df['Industry'] != '').sum():,}"
)

print(
    f"Market Caps Filled : "
    f"{(metadata_df['Market_Cap'] > 0).sum():,}"
)

print(
    f"Missing Market Cap : "
    f"{(metadata_df['Market_Cap'] <= 0).sum():,}"
)

# =========================================================
# REPORT
# =========================================================

final_df = pd.read_csv(OUTPUT_FILE)

print("\n📊 METADATA QUALITY REPORT")
print("=" * 60)

print(f"Total Symbols      : {len(final_df):,}")
print(f"Company Names      : {(final_df['Company_Name'].fillna('') != '').sum():,}")
print(f"Sectors Available  : {(final_df['Sector'].fillna('') != '').sum():,}")
print(f"Industries Present : {(final_df['Industry'].fillna('') != '').sum():,}")
print(f"Market Caps Filled : {(final_df['Market_Cap'] > 0).sum():,}")
print(f"Missing Market Cap : {(final_df['Market_Cap'] <= 0).sum():,}")