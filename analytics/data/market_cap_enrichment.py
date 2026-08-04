"""
=========================================================
MARKET CAP ENRICHMENT ENGINE
=========================================================

Purpose:
Populate missing Market_Cap values

Input:
data/raw/symbol_metadata.csv

Output:
data/raw/symbol_metadata.csv

=========================================================
"""

import time
import traceback

import pandas as pd

from analytics.data.providers.yahoo_market_cap_provider import fetch_market_cap
from config.paths import SYMBOL_METADATA_FILE
from config.thresholds import COOLDOWN_AFTER, COOLDOWN_SECONDS, SAVE_INTERVAL
from orchestration.models.engine_result import EngineResult
from orchestration.models.engine_status import EngineStatus
from utils.file_utils import ensure_parent_directory
from utils.logger import get_logger

logger = get_logger(__name__)

# =========================================================
# CONFIG
# =========================================================

ENGINE_NAME = "MarketCapEnrichment"


# =========================================================
# MAIN
# =========================================================


def main() -> EngineResult:
    """
    Market Cap Enrichment Engine
    """

    start_time = time.perf_counter()

    try:
        # =====================================================
        # LOAD
        # =====================================================

        logger.info("\n💰 Loading Symbol Metadata...")

        df = pd.read_csv(SYMBOL_METADATA_FILE)

        # =====================================================
        # VALIDATION
        # =====================================================

        if "Symbol" not in df.columns:
            raise ValueError("Symbol column not found.")

        if "Market_Cap" not in df.columns:
            df["Market_Cap"] = 0.0

        metadata_columns = {
            "Market_Cap_Status": "UNKNOWN",
            "Market_Cap_Source": "Yahoo",
            "Market_Cap_Last_Updated": "",
            "Market_Cap_Attempts": 0,
            "Market_Cap_Last_Error": "",
        }

        for column, default in metadata_columns.items():
            if column not in df.columns:
                df[column] = default

        df["Market_Cap"] = pd.to_numeric(
            df["Market_Cap"],
            errors="coerce",
        ).fillna(0)

        # =====================================================
        # IDENTIFY MISSING
        # =====================================================

        missing_rows = df[df["Market_Cap"] <= 0].index

        total = len(missing_rows)

        existing = int((df["Market_Cap"] > 0).sum())

        print(f"Existing Market Caps : {existing:,}")

        print(f"Need Fetch : {total:,}")

        filled = (df["Market_Cap"] > 0).sum()

        missing = (df["Market_Cap"] <= 0).sum()

        coverage = filled / len(df) * 100

        newly_filled = filled - existing

        # =====================================================
        # NOTHING TO UPDATE
        # =====================================================

        if total == 0:
            duration = time.perf_counter() - start_time

            print("\n✅ All Market Caps Available")

            return EngineResult(
                engine=ENGINE_NAME,
                status=EngineStatus.SUCCESS,
                records=len(df),
                output=SYMBOL_METADATA_FILE,
                duration=duration,
                metadata={
                    "existing_market_caps": int(existing),
                    "missing_market_caps": 0,
                    "coverage": 100.0,
                },
            )

        # =====================================================
        # PROCESS
        # =====================================================

        print("\n📊 Fetching Market Caps...")

        for counter, row_idx in enumerate(
            missing_rows,
            start=1,
        ):
            symbol = (
                str(
                    df.loc[
                        row_idx,
                        "Symbol",
                    ]
                )
                .strip()
                .upper()
            )

            # =====================================================
            # FETCH MARKET CAP
            # =====================================================

            result = fetch_market_cap(symbol)

            # =====================================================
            # UPDATE DATAFRAME
            # =====================================================

            df.loc[
                row_idx,
                "Market_Cap",
            ] = result.market_cap

            df.loc[
                row_idx,
                "Market_Cap_Status",
            ] = result.status

            df.loc[
                row_idx,
                "Market_Cap_Source",
            ] = result.source

            df.loc[
                row_idx,
                "Market_Cap_Attempts",
            ] = result.attempts

            df.loc[
                row_idx,
                "Market_Cap_Last_Error",
            ] = result.error or ""

            df.loc[
                row_idx,
                "Market_Cap_Last_Updated",
            ] = pd.Timestamp.now(
                tz="UTC",
            ).isoformat()

            # =====================================================
            # PROGRESS
            # =====================================================

            print(
                f"[{counter:,}/{total:,}] "
                f"{symbol:<15} "
                f"{result.market_cap:,.0f} "
                f"[{result.status}]"
            )

            # ================================================
            # CHECKPOINT
            # ================================================

            if counter % SAVE_INTERVAL == 0:
                ensure_parent_directory(SYMBOL_METADATA_FILE)

                df.to_csv(
                    SYMBOL_METADATA_FILE,
                    index=False,
                )

                # =====================================================
                # FINAL STATISTICS
                # =====================================================

                filled = int((df["Market_Cap"] > 0).sum())

                missing = int((df["Market_Cap"] <= 0).sum())

                coverage = filled / len(df) * 100 if len(df) else 0.0

                newly_filled = max(
                    0,
                    filled - existing,
                )

                print(f"💾 Checkpoint Saved ({counter:,})")

            # ================================================
            # COOLDOWN
            # ================================================

            if counter % COOLDOWN_AFTER == 0:
                print("\n🛑 Cooling Yahoo...")

                time.sleep(COOLDOWN_SECONDS)

        # =====================================================
        # FINAL SAVE
        # =====================================================

        df = df.sort_values("Symbol").reset_index(drop=True)

        ensure_parent_directory(SYMBOL_METADATA_FILE)

        df.to_csv(
            SYMBOL_METADATA_FILE,
            index=False,
        )

        # =====================================================
        # REPORT
        # =====================================================

        print("\n" + "=" * 70)

        print("✅ MARKET CAP ENRICHMENT COMPLETE")

        print("=" * 70)

        print(f"Filled Market Caps : {filled:,}")

        print(f"Missing Market Caps : {missing:,}")

        print(f"Coverage : {coverage:.2f}%")

        print(f"\nSaved:\n{SYMBOL_METADATA_FILE}")

        print("=" * 70)

        # =====================================================
        # BUILD EXECUTION METADATA
        # =====================================================

        duration = time.perf_counter() - start_time

        execution_metadata = {
            "existing_market_caps": int(existing),
            "newly_filled_market_caps": int(newly_filled),
            "filled_market_caps": int(filled),
            "missing_market_caps": int(missing),
            "coverage": float(coverage),
            "symbols_processed": int(total),
        }

        # =====================================================
        # RETURN RESULT
        # =====================================================

        return EngineResult(
            engine=ENGINE_NAME,
            status=EngineStatus.SUCCESS,
            records=len(df),
            output=SYMBOL_METADATA_FILE,
            duration=duration,
            metadata=execution_metadata,
        )

    # =========================================================
    # EXCEPTION HANDLING
    # =========================================================

    except Exception as exc:

        duration = time.perf_counter() - start_time

        print("\n" + "=" * 80)
        print("❌ MARKET CAP ENRICHMENT FAILED")
        print("=" * 80)
        print(f"Exception Type : {type(exc).__name__}")
        print(f"Exception      : {exc}")
        print("\nTraceback:")
        traceback.print_exc()
        print("=" * 80)

        return EngineResult(
            engine=ENGINE_NAME,
            status=EngineStatus.FAILED,
            duration=duration,
            metadata={
                "error": str(exc),
                "exception_type": type(exc).__name__,
                "traceback": traceback.format_exc(),
            },
        )


if __name__ == "__main__":
    result = main()

    print("\n" + "=" * 80)
    print(f"Engine Status : {result.status}")

    if result.metadata:
        print("\nMetadata:")
        for key, value in result.metadata.items():
            print(f"{key}:")
            print(value)
            print()

    print("=" * 80)
