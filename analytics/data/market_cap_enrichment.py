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

from pathlib import Path

import random
import time

import pandas as pd
import yfinance as yf

from orchestration.models.engine_result import EngineResult

# =========================================================
# CONFIG
# =========================================================

ENGINE_NAME = "MarketCapEnrichment"

MAX_RETRIES = 3

SAVE_INTERVAL = 50

COOLDOWN_AFTER = 100

COOLDOWN_SECONDS = 10

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
# FETCH MARKET CAP
# =========================================================

def fetch_market_cap(symbol: str) -> float:
    """
    Fetch Market Cap from Yahoo Finance.
    """

    yahoo_symbol = f"{symbol}.NS"

    for attempt in range(MAX_RETRIES):

        try:

            ticker = yf.Ticker(
                yahoo_symbol
            )

            # ---------------------------------------------
            # FAST INFO
            # ---------------------------------------------

            try:

                market_cap = (
                    ticker.fast_info.get(
                        "marketCap",
                        0,
                    )
                )

                if (
                    market_cap
                    and market_cap > 0
                ):

                    return float(
                        market_cap
                    )

            except Exception:
                pass

            # ---------------------------------------------
            # FALLBACK
            # ---------------------------------------------

            try:

                info = (
                    ticker.get_info()
                )

                market_cap = (
                    info.get(
                        "marketCap",
                        0,
                    )
                )

                if (
                    market_cap
                    and market_cap > 0
                ):

                    return float(
                        market_cap
                    )

            except Exception:
                pass

        except Exception as e:

            error = str(e).lower()

            if (
                "429" in error
                or "rate limit" in error
                or "too many requests" in error
            ):

                wait_time = (
                    15
                    * (attempt + 1)
                )

                print(
                    f"⚠️ Rate Limit: {symbol}"
                )

                print(
                    f"⏳ Sleeping {wait_time}s"
                )

                time.sleep(
                    wait_time
                )

            else:

                print(
                    f"❌ {symbol}: {e}"
                )

                time.sleep(2)

    return 0.0


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

        print(
            "\n💰 Loading Symbol Metadata..."
        )

        df = pd.read_csv(
            INPUT_FILE
        )

        # =====================================================
        # VALIDATION
        # =====================================================

        if "Symbol" not in df.columns:

            raise ValueError(
                "Symbol column not found."
            )

        if "Market_Cap" not in df.columns:

            df["Market_Cap"] = 0.0

        df["Market_Cap"] = (
            pd.to_numeric(
                df["Market_Cap"],
                errors="coerce",
            )
            .fillna(0)
        )

        # =====================================================
        # IDENTIFY MISSING
        # =====================================================

        missing_rows = df[
            df["Market_Cap"] <= 0
        ].index

        total = len(
            missing_rows
        )

        existing = (
            df["Market_Cap"] > 0
        ).sum()

        print(
            f"Existing Market Caps : "
            f"{existing:,}"
        )

        print(
            f"Need Fetch : "
            f"{total:,}"
        )

        # =====================================================
        # NOTHING TO UPDATE
        # =====================================================

        if total == 0:

            duration = (
                time.perf_counter()
                - start_time
            )

            print(
                "\n✅ All Market Caps Available"
            )

            return EngineResult(
                engine=ENGINE_NAME,
                status="SUCCESS",
                records=len(df),
                output=INPUT_FILE,
                duration=duration,
                metadata={
                    "existing_market_caps": int(
                        existing
                    ),
                    "missing_market_caps": 0,
                    "coverage": 100.0,
                },
            )

        # =====================================================
        # PROCESS
        # =====================================================

        print(
            "\n📊 Fetching Market Caps..."
        )

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

            market_cap = (
                fetch_market_cap(
                    symbol
                )
            )

            df.loc[
                row_idx,
                "Market_Cap",
            ] = market_cap

            print(
                f"[{counter:,}/{total:,}] "
                f"{symbol:<15} "
                f"{market_cap:,.0f}"
            )

            # ================================================
            # CHECKPOINT
            # ================================================

            if (
                counter
                % SAVE_INTERVAL
                == 0
            ):

                df.to_csv(
                    INPUT_FILE,
                    index=False,
                )

                print(
                    f"💾 Checkpoint Saved "
                    f"({counter:,})"
                )

            # ================================================
            # COOLDOWN
            # ================================================

            if (
                counter
                % COOLDOWN_AFTER
                == 0
            ):

                print(
                    "\n🛑 Cooling Yahoo..."
                )

                time.sleep(
                    COOLDOWN_SECONDS
                )

        # =====================================================
        # FINAL SAVE
        # =====================================================

        df = (
            df
            .sort_values(
                "Symbol"
            )
            .reset_index(
                drop=True
            )
        )

        df.to_csv(
            INPUT_FILE,
            index=False,
        )

        # =====================================================
        # REPORT
        # =====================================================

        filled = (
            df["Market_Cap"] > 0
        ).sum()

        missing = (
            df["Market_Cap"] <= 0
        ).sum()

        coverage = (
            filled
            / len(df)
            * 100
        )

        print("\n" + "=" * 70)

        print(
            "✅ MARKET CAP ENRICHMENT COMPLETE"
        )

        print("=" * 70)

        print(
            f"Filled Market Caps : "
            f"{filled:,}"
        )

        print(
            f"Missing Market Caps : "
            f"{missing:,}"
        )

        print(
            f"Coverage : "
            f"{coverage:.2f}%"
        )

        print(
            f"\nSaved:\n{INPUT_FILE}"
        )

        print("=" * 70)

        # =====================================================
        # BUILD EXECUTION METADATA
        # =====================================================

        duration = (
            time.perf_counter()
            - start_time
        )

        execution_metadata = {
            "existing_market_caps": int(
                existing
            ),
            "filled_market_caps": int(
                filled
            ),
            "missing_market_caps": int(
                missing
            ),
            "coverage": float(
                coverage
            ),
            "symbols_processed": int(
                total
            ),
        }

        # =====================================================
        # RETURN RESULT
        # =====================================================

        return EngineResult(
            engine=ENGINE_NAME,
            status="SUCCESS",
            records=len(df),
            output=INPUT_FILE,
            duration=duration,
            metadata=execution_metadata,
        )

    # =========================================================
    # EXCEPTION HANDLING
    # =========================================================

    except Exception as e:

        duration = (
            time.perf_counter()
            - start_time
        )

        return EngineResult(
            engine=ENGINE_NAME,
            status="FAILED",
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

    print(
        f"\nEngine Status : "
        f"{result.status}"
    )