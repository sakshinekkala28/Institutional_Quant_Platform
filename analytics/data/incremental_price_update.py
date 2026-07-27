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
import time

import pandas as pd
import yfinance as yf

from config.paths import (
    INVALID_SYMBOL_FILE,
    PRICE_DIR,
    PRICE_UPDATE_FAILURE_FILE,
    UPDATED_STOCKS_FILE,
)
from config.thresholds import (
    FULL_HISTORY_YEARS,
    MAX_WORKERS,
)
from orchestration.models.engine_result import (
    EngineResult,
)
from orchestration.models.engine_status import (
    EngineStatus,
)
from utils.file_utils import (
    ensure_directory,
    ensure_parent_directory,
)
from utils.logger import get_logger

logger = get_logger(__name__)

# =========================================================
# CONFIG
# =========================================================

ENGINE_NAME = "IncrementalPriceUpdate"

# =========================================================
# DOWNLOAD FULL HISTORY
# =========================================================


def download_full_history(
    symbol: str,
) -> pd.DataFrame:
    """
    Download full historical price data
    from Yahoo Finance.
    """

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


def update_symbol(
    symbol: str,
    price_dir: Path,
    expected_date: pd.Timestamp,
    failures: list,
    new_invalid: list,
) -> str:
    """
    Update a single symbol's price history.
    """

    output_file = price_dir / f"{symbol}.parquet"

    try:
        # =====================================================
        # NEW FILE
        # =====================================================

        if not output_file.exists():
            df = download_full_history(symbol)

            if len(df) < 252:
                new_invalid.append(
                    {
                        "Symbol": symbol,
                        "Reason": (f"Insufficient History ({len(df)} rows)"),
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
                df.columns = [c[0] for c in df.columns]

            df.columns = [
                str(c).replace(
                    " ",
                    "_",
                )
                for c in df.columns
            ]

            df["Symbol"] = symbol

            output_file.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            df.to_parquet(
                output_file,
                index=False,
            )

            return "NEW"

        # =====================================================
        # EXISTING FILE
        # =====================================================

        existing = pd.read_parquet(output_file)

        if len(existing) < 252:
            new_invalid.append(
                {
                    "Symbol": symbol,
                    "Reason": (f"Corrupted History ({len(existing)} rows)"),
                }
            )

            return "INVALID"

        if existing.empty:
            return "SKIPPED"

        last_date = pd.to_datetime(existing["Date"]).max()

        if last_date.normalize() >= expected_date:
            return "SKIPPED"

        start_date = last_date + pd.Timedelta(days=1)

        new_data = yf.download(
            f"{symbol}.NS",
            start=start_date.strftime("%Y-%m-%d"),
            auto_adjust=True,
            progress=False,
            threads=False,
        )

        if new_data.empty:
            return "SKIPPED"

        new_data = new_data.reset_index()

        if isinstance(
            new_data.columns,
            pd.MultiIndex,
        ):
            new_data.columns = [c[0] for c in new_data.columns]

        new_data.columns = [
            str(c).replace(
                " ",
                "_",
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

        updated = updated.drop_duplicates(subset=["Date"]).sort_values("Date")

        updated.to_parquet(
            output_file,
            index=False,
        )

        return "UPDATED"

    # =========================================================
    # EXCEPTION HANDLING
    # =========================================================

    except Exception as e:
        failures.append(
            {
                "Symbol": symbol,
                "Error": str(e),
            }
        )

        return "FAILED"


# =========================================================
# MAIN
# =========================================================


def main() -> EngineResult:
    """
    Incremental Price Update Engine
    """

    start_time = time.perf_counter()

    try:
        # =====================================================
        # PREPARE DIRECTORIES
        # =====================================================

        ensure_directory(PRICE_DIR)

        ensure_parent_directory(PRICE_UPDATE_FAILURE_FILE)

        # =====================================================
        # LOAD UNIVERSE
        # =====================================================

        logger.info("\n📥 Loading Investable Universe...")

        universe = pd.read_csv(UPDATED_STOCKS_FILE)

        symbols = (
            universe["Symbol"]
            .dropna()
            .astype(str)
            .str.upper()
            .str.strip()
            .unique()
            .tolist()
        )

        # =====================================================
        # INVALID SYMBOL CACHE
        # =====================================================

        invalid_symbols = set()

        if INVALID_SYMBOL_FILE.exists():
            invalid_symbols = set(
                pd.read_csv(INVALID_SYMBOL_FILE)["Symbol"]
                .astype(str)
                .str.upper()
                .str.strip()
            )

        symbols = [s for s in symbols if s not in invalid_symbols]

        print(f"Universe Size : {len(symbols):,}")

        print(f"Blacklisted Symbols : {len(invalid_symbols):,}")

        # =====================================================
        # EXECUTION STATE
        # =====================================================

        updated_count = 0
        new_count = 0
        skipped_count = 0
        failure_count = 0

        failures = []
        new_invalid = []

        today = pd.Timestamp.today().normalize()

        if today.weekday() == 0:
            expected_date = today - pd.Timedelta(days=3)

        else:
            expected_date = today - pd.Timedelta(days=1)

        # =====================================================
        # EXECUTION
        # =====================================================

        print("\n🚀 Updating Price History...")

        with ThreadPoolExecutor(
            max_workers=MAX_WORKERS,
        ) as executor:
            results = executor.map(
                lambda symbol: update_symbol(
                    symbol=symbol,
                    price_dir=PRICE_DIR,
                    expected_date=expected_date,
                    failures=failures,
                    new_invalid=new_invalid,
                ),
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

                elif result in (
                    "FAILED",
                    "INVALID",
                ):
                    failure_count += 1

                if idx % 50 == 0:
                    print(f"{idx:,}/{total:,}")

        # =====================================================
        # SAVE FAILURE LOG
        # =====================================================

        if failures:
            pd.DataFrame(failures).to_csv(
                PRICE_UPDATE_FAILURE_FILE,
                index=False,
            )

        # =====================================================
        # SAVE INVALID SYMBOLS
        # =====================================================

        if new_invalid:
            invalid_df = pd.DataFrame(new_invalid)

            if INVALID_SYMBOL_FILE.exists():
                old = pd.read_csv(INVALID_SYMBOL_FILE)

                invalid_df = pd.concat(
                    [
                        old,
                        invalid_df,
                    ],
                    ignore_index=True,
                )

            invalid_df = invalid_df.drop_duplicates(
                subset=["Symbol"],
                keep="last",
            ).sort_values("Symbol")

            invalid_df.to_csv(
                INVALID_SYMBOL_FILE,
                index=False,
            )

        # =====================================================
        # REPORT
        # =====================================================

        coverage = round(
            (skipped_count + updated_count + new_count)
            / max(
                len(symbols),
                1,
            )
            * 100,
            2,
        )

        print(f"Coverage          : {coverage}%")

        print("\n" + "=" * 70)

        print("🏁 PRICE UPDATE COMPLETE")

        print("=" * 70)

        print(f"Universe Size      : {len(symbols):,}")

        print(f"New Files          : {new_count:,}")

        print(f"Updated Files      : {updated_count:,}")

        print(f"Skipped Files      : {skipped_count:,}")

        print(f"Failures           : {failure_count:,}")

        print(f"Invalid Symbols    : {len(new_invalid):,}")

        if failures:
            print(f"\nFailure Log:\n{PRICE_UPDATE_FAILURE_FILE}")

        print(f"\nPrice Directory:\n{PRICE_DIR}")

        print("=" * 70)

        # =====================================================
        # BUILD EXECUTION METADATA
        # =====================================================

        duration = time.perf_counter() - start_time

        execution_metadata = {
            "universe_size": len(symbols),
            "new_files": new_count,
            "updated_files": updated_count,
            "skipped_files": skipped_count,
            "failed_files": failure_count,
            "invalid_symbols": len(new_invalid),
            "coverage": coverage,
        }

        # =====================================================
        # RETURN RESULT
        # =====================================================

        return EngineResult(
            engine=ENGINE_NAME,
            status=EngineStatus.SUCCESS,
            records=(new_count + updated_count),
            output=PRICE_DIR,
            report=PRICE_UPDATE_FAILURE_FILE
            if PRICE_UPDATE_FAILURE_FILE.exists()
            else None,
            duration=duration,
            metadata=execution_metadata,
        )

    # =========================================================
    # EXCEPTION HANDLING
    # =========================================================

    except Exception as e:
        duration = time.perf_counter() - start_time

        return EngineResult(
            engine=ENGINE_NAME,
            status=EngineStatus.FAILED,
            duration=duration,
            metadata={
                "error": str(e),
            },
        )


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    result = main()

    print(f"\nEngine Status : {result.status}")
