"""
=========================================================
SYMBOL METADATA ENGINE
=========================================================

Purpose:
Build / Enrich Security Master from Yahoo Finance

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
Last_Updated

=========================================================
"""

from pathlib import Path
import random
import time

import pandas as pd
import yfinance as yf

# =========================================================
# CONFIG
# =========================================================

MAX_RETRIES = 3

SAVE_INTERVAL = 50

COOLDOWN_AFTER = 100

COOLDOWN_SECONDS = 30

TODAY = pd.Timestamp.now().strftime(
    "%Y-%m-%d"
)

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
        f"Symbol column not found.\n"
        f"Available columns: {list(stocks.columns)}"
    )

symbols = (
    stocks[symbol_col]
    .dropna()
    .astype(str)
    .str.upper()
    .str.strip()
    .str.replace(
        ".NS",
        "",
        regex=False,
    )
    .drop_duplicates()
    .tolist()
)

print(
    f"Total Symbols : {len(symbols):,}"
)

# =========================================================
# LOAD CACHE
# =========================================================

metadata = []

if OUTPUT_FILE.exists():

    print(
        "\n♻️ Loading Existing Cache..."
    )

    existing = pd.read_csv(
        OUTPUT_FILE
    ).fillna("")

    required_cols = [
        "Symbol",
        "Yahoo_Symbol",
        "Company_Name",
        "Sector",
        "Industry",
        "Last_Updated",
    ]

    for col in required_cols:

        if col not in existing.columns:

            existing[col] = ""

    existing["Symbol"] = (
        existing["Symbol"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    complete_records = existing[
        (
            existing["Company_Name"]
            .astype(str)
            .str.strip()
            != ""
        )
        &
        (
            existing["Sector"]
            .astype(str)
            .str.strip()
            != ""
        )
        &
        (
            existing["Industry"]
            .astype(str)
            .str.strip()
            != ""
        )
    ].copy()

    metadata = (
        complete_records
        .to_dict("records")
    )

    completed_symbols = set(
        complete_records["Symbol"]
    )

    symbols = [
        s
        for s in symbols
        if s not in completed_symbols
    ]

    print(
        f"Cached Complete Records : "
        f"{len(complete_records):,}"
    )

else:

    print(
        "\n🆕 No Cache Found"
    )

print(
    f"Need Fetch : {len(symbols):,}"
)

# =========================================================
# FETCHER
# =========================================================

def fetch_metadata(symbol):

    yahoo_symbol = f"{symbol}.NS"

    for attempt in range(
        MAX_RETRIES
    ):

        try:

            time.sleep(
                random.uniform(
                    0.5,
                    2.0,
                )
            )

            info = (
                yf.Ticker(
                    yahoo_symbol
                )
                .get_info()
            )

            company_name = (
                info.get("longName")
                or info.get(
                    "shortName"
                )
                or ""
            )

            sector = (
                info.get(
                    "sector"
                )
                or ""
            )

            industry = (
                info.get(
                    "industry"
                )
                or ""
            )

            if company_name:

                return {
                    "Symbol": symbol,
                    "Yahoo_Symbol":
                        yahoo_symbol,
                    "Company_Name":
                        company_name,
                    "Sector":
                        sector,
                    "Industry":
                        industry,
                    "Last_Updated":
                        TODAY,
                }

        except Exception as e:

            error = str(e).lower()

            if (
                "429" in error
                or "rate limit"
                in error
                or "too many requests"
                in error
            ):

                wait_time = (
                    15
                    * (attempt + 1)
                )

                print(
                    f"⚠️ Rate Limit: "
                    f"{symbol}"
                )

                print(
                    f"⏳ Sleeping "
                    f"{wait_time}s"
                )

                time.sleep(
                    wait_time
                )

            else:

                print(
                    f"❌ {symbol}: {e}"
                )

                time.sleep(3)

    return {
        "Symbol": symbol,
        "Yahoo_Symbol":
            yahoo_symbol,
        "Company_Name": "",
        "Sector": "",
        "Industry": "",
        "Last_Updated":
            TODAY,
    }

# =========================================================
# SAVE
# =========================================================

def save_checkpoint(records):

    df = pd.DataFrame(
        records
    )

    required_cols = [
        "Symbol",
        "Yahoo_Symbol",
        "Company_Name",
        "Sector",
        "Industry",
        "Last_Updated",
    ]

    for col in required_cols:

        if col not in df.columns:

            df[col] = ""

    df = (
        df
        .sort_values(
            "Symbol"
        )
        .drop_duplicates(
            subset="Symbol",
            keep="last",
        )
        .reset_index(
            drop=True
        )
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
# PROCESS
# =========================================================

print(
    "\n📊 Fetching Metadata..."
)

total = len(symbols)

for idx, symbol in enumerate(
    symbols,
    start=1,
):

    record = fetch_metadata(
        symbol
    )

    metadata.append(
        record
    )

    print(
        f"[{idx:,}/{total:,}] "
        f"{symbol}"
    )

    if (
        idx
        % SAVE_INTERVAL
        == 0
    ):

        save_checkpoint(
            metadata
        )

        print(
            f"💾 Checkpoint Saved "
            f"({idx:,})"
        )

    if (
        idx
        % COOLDOWN_AFTER
        == 0
    ):

        print(
            "\n🛑 Cooling Yahoo..."
        )

        time.sleep(
            COOLDOWN_SECONDS
        )

# =========================================================
# FINAL SAVE
# =========================================================

print(
    "\n💾 Final Save..."
)

save_checkpoint(
    metadata
)

# =========================================================
# REPORT
# =========================================================

final_df = pd.read_csv(
    OUTPUT_FILE
).fillna("")

print("\n" + "=" * 60)

print(
    "📊 METADATA QUALITY REPORT"
)

print("=" * 60)

print(
    f"Total Symbols      : "
    f"{len(final_df):,}"
)

print(
    f"Company Names      : "
    f"{(final_df['Company_Name'] != '').sum():,}"
)

print(
    f"Sectors Available  : "
    f"{(final_df['Sector'] != '').sum():,}"
)

print(
    f"Industries Present : "
    f"{(final_df['Industry'] != '').sum():,}"
)

print("=" * 60)

print(
    f"\nSaved:\n{OUTPUT_FILE}"
)

print(
    "\n✅ Metadata Build Complete"
)