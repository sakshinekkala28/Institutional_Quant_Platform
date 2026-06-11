from pathlib import Path
import pandas as pd
import yfinance as yf
import time

ROOT_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = ROOT_DIR / "data/raw/valid_stocks.xlsx"
OUTPUT_FILE = ROOT_DIR / "data/raw/symbol_metadata.csv"

CHECKPOINT_INTERVAL = 50
REQUEST_DELAY = 1.5

print("\nBuilding Symbol Metadata...")

# Load symbols
df = pd.read_excel(INPUT_FILE)

SYMBOL_COL = "Stock"

if SYMBOL_COL not in df.columns:
    raise ValueError(
        f"Column '{SYMBOL_COL}' not found in {INPUT_FILE.name}"
    )

symbols = (
    df[SYMBOL_COL]
    .dropna()
    .astype(str)
    .str.strip()
    .unique()
    .tolist()
)

# Resume support
if OUTPUT_FILE.exists():
    existing_df = pd.read_csv(OUTPUT_FILE)

    processed_symbols = set(
        existing_df["Symbol"]
        .dropna()
        .astype(str)
        .str.strip()
    )

    metadata = existing_df.to_dict("records")

    symbols = [
        s for s in symbols
        if s not in processed_symbols
    ]

    print(
        f"Resuming from checkpoint. "
        f"Already processed: {len(processed_symbols)}"
    )

else:
    metadata = []

total_symbols = len(symbols)

print(f"Pending symbols: {total_symbols}")

for idx, symbol in enumerate(symbols, start=1):

    try:
        ticker = yf.Ticker(f"{symbol}.NS")

        info = {}

        try:
            info = ticker.get_info()
        except Exception as info_error:
            print(
                f"[{idx}/{total_symbols}] "
                f"Metadata unavailable for {symbol}: {info_error}"
            )

        metadata.append(
            {
                "Symbol": symbol,
                "Company_Name": info.get("longName", ""),
                "Sector": info.get("sector", ""),
                "Industry": info.get("industry", ""),
            }
        )

        print(
            f"[{idx}/{total_symbols}] "
            f"✓ {symbol}"
        )

    except Exception as e:

        print(
            f"[{idx}/{total_symbols}] "
            f"✗ {symbol}: {e}"
        )

        metadata.append(
            {
                "Symbol": symbol,
                "Company_Name": "",
                "Sector": "",
                "Industry": "",
            }
        )

    # Checkpoint save
    if idx % CHECKPOINT_INTERVAL == 0:

        checkpoint_df = (
            pd.DataFrame(metadata)
            .drop_duplicates(
                subset=["Symbol"],
                keep="last"
            )
            .sort_values("Symbol")
        )

        checkpoint_df.to_csv(
            OUTPUT_FILE,
            index=False
        )

        print(
            f"💾 Checkpoint saved "
            f"({len(checkpoint_df)} records)"
        )

    time.sleep(REQUEST_DELAY)

# Final save
final_df = (
    pd.DataFrame(metadata)
    .drop_duplicates(
        subset=["Symbol"],
        keep="last"
    )
    .sort_values("Symbol")
)

final_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print(
    f"\n✅ Completed successfully."
    f"\nRecords written: {len(final_df)}"
    f"\nOutput: {OUTPUT_FILE}"
)