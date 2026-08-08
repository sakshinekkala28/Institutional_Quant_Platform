"""
=========================================================
PRICE HISTORY ENGINE
=========================================================

Downloads historical OHLCV data for all stocks and stores
each symbol as an individual parquet file.

Input:
data/raw/stock_metadata.csv

Output:
data/raw/prices/*.parquet

=========================================================
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pandas as pd
import yfinance as yf


# =========================================================
# CONFIG
# =========================================================

YEARS_HISTORY = 10

MAX_WORKERS = 2


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
    / "price_history_failures.csv"
)


# =========================================================
# ENGINE
# =========================================================


def download_symbol(
    symbol: str,
) -> str:
    """
    Download historical price data for one symbol.
    """

    output_file = PRICE_DIR / f"{symbol}.parquet"

    if output_file.exists():
        return "CACHED"

    try:

        df = yf.download(
            f"{symbol}.NS",
            period=f"{YEARS_HISTORY}y",
            auto_adjust=True,
            progress=False,
            threads=False,
        )

        if df.empty:
            raise ValueError(
                "No Data Returned"
            )

        df = df.reset_index()

        if isinstance(
            df.columns,
            pd.MultiIndex,
        ):
            df.columns = [
                column[0]
                for column in df.columns
            ]

        df.columns = [
            str(column).replace(
                " ",
                "_",
            )
            for column in df.columns
        ]

        df["Symbol"] = symbol

        df.to_parquet(
            output_file,
            index=False,
        )

        return "SUCCESS"

    except Exception as exc:

        return f"FAILED: {exc}"


# =========================================================
# MAIN
# =========================================================


def main() -> dict:
    """
    Execute the price history engine.
    """

    PRICE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    FAILURE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    print(
        "\n📥 Loading Stock Metadata..."
    )

    metadata = pd.read_csv(
        METADATA_FILE
    )

    symbols = (
        metadata["Symbol"]
        .dropna()
        .astype(str)
        .str.upper()
        .str.strip()
        .unique()
        .tolist()
    )

    print(
        f"Universe Size : {len(symbols):,}"
    )

    # -----------------------------------------------------
    # CACHE
    # -----------------------------------------------------

    existing_symbols = {
        file.stem.upper()
        for file in PRICE_DIR.glob(
            "*.parquet"
        )
    }

    symbols_to_download = [
        symbol
        for symbol in symbols
        if symbol not in existing_symbols
    ]

    print(
        f"Already Cached : "
        f"{len(existing_symbols):,}"
    )

    print(
        f"Need Download  : "
        f"{len(symbols_to_download):,}"
    )

    # -----------------------------------------------------
    # STATS
    # -----------------------------------------------------

    success_count = 0

    failure_count = 0

    cached_count = len(
        existing_symbols
    )

    failures: list[dict[str, str]] = []

    # -----------------------------------------------------
    # DOWNLOAD
    # -----------------------------------------------------

    if symbols_to_download:

        print(
            "\n🚀 Downloading Price History..."
        )

        with ThreadPoolExecutor(
            max_workers=MAX_WORKERS,
        ) as executor:

            results = executor.map(
                download_symbol,
                symbols_to_download,
            )

            total = len(
                symbols_to_download
            )

            for idx, result in enumerate(
                results,
                start=1,
            ):

                if result == "SUCCESS":

                    success_count += 1

                elif result.startswith(
                    "FAILED:"
                ):

                    failure_count += 1

                    symbol = symbols_to_download[
                        idx - 1
                    ]

                    failures.append(
                        {
                            "Symbol": symbol,
                            "Error": result[
                                len("FAILED:") :
                            ].strip(),
                        }
                    )

                if idx % 25 == 0:

                    print(
                        f"{idx:,}/{total:,}"
                    )

    # -----------------------------------------------------
    # FAILURE LOG
    # -----------------------------------------------------

    if failures:

        pd.DataFrame(
            failures
        ).to_csv(
            FAILURE_FILE,
            index=False,
        )

    # -----------------------------------------------------
    # FINAL STATS
    # -----------------------------------------------------

    total_files = len(
        list(
            PRICE_DIR.glob(
                "*.parquet"
            )
        )
    )

    # -----------------------------------------------------
    # REPORT
    # -----------------------------------------------------

    print(
        "\n" + "=" * 70
    )

    print(
        "🏁 PRICE HISTORY ENGINE COMPLETE"
    )

    print(
        "=" * 70
    )

    print(
        f"Universe Size   : {len(symbols):,}"
    )

    print(
        f"Cached Files    : {cached_count:,}"
    )

    print(
        f"New Downloads   : {success_count:,}"
    )

    print(
        f"Failures        : {failure_count:,}"
    )

    print(
        f"Total Files     : {total_files:,}"
    )

    print(
        f"\nPrice Folder:\n{PRICE_DIR}"
    )

    if failures:

        print(
            f"\nFailure Log:\n{FAILURE_FILE}"
        )

    print(
        "=" * 70
    )

    return {
        "engine": "Price History Engine",
        "universe_size": len(symbols),
        "cached": cached_count,
        "downloaded": success_count,
        "failed": failure_count,
        "total_files": total_files,
        "failure_file": (
            str(FAILURE_FILE)
            if failures
            else None
        ),
    }


# =========================================================
# CLI
# =========================================================

if __name__ == "__main__":

    main()