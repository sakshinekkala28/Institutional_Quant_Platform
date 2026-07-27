"""
=========================================================
FACTOR SNAPSHOT ENGINE
=========================================================

Purpose:
Build historical institutional factor snapshots
for every month-end.

Inputs
------
data/raw/security_master.csv
data/raw/prices/*.parquet

Outputs
-------
data/factor_snapshots/*.parquet
data/factors/factor_snapshot_master.csv

Reports
-------
data/logs/factor_snapshot_report.csv

=========================================================
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import numpy as np
import pandas as pd

from config.paths import (
    FACTOR_SNAPSHOT_DIRECTORY,
    FACTOR_SNAPSHOT_MASTER_FILE,
    FACTOR_SNAPSHOT_REPORT_FILE,
    PRICE_HISTORY_DIRECTORY,
    SECURITY_MASTER_FILE,
)
from config.settings import (
    DATE_FORMAT,
    ENGINE_VERSION,
    MAX_WORKERS,
    TRADING_DAYS,
)
from orchestration.models.engine_result import (
    EngineResult,
)
from orchestration.models.engine_status import (
    EngineStatus,
)
from utils.file_utils import (
    ensure_parent_directory,
)
from utils.logger import (
    get_logger,
)
from utils.timer import (
    Timer,
)

# =========================================================
# CONFIG
# =========================================================

ENGINE_NAME = "FactorSnapshotEngine"

logger = get_logger(__name__)

# =========================================================
# MAIN
# =========================================================


def main() -> EngineResult:
    """
    Build historical factor snapshots.
    """

    with Timer() as timer:
        try:
            # =================================================
            # VALIDATE INPUTS
            # =================================================

            logger.info("Loading Security Master...")

            if not SECURITY_MASTER_FILE.exists():
                raise FileNotFoundError(f"Missing file:\n{SECURITY_MASTER_FILE}")

            if not PRICE_HISTORY_DIRECTORY.exists():
                raise FileNotFoundError(
                    f"Missing directory:\n{PRICE_HISTORY_DIRECTORY}"
                )

            # =================================================
            # LOAD SECURITY MASTER
            # =================================================

            security = pd.read_csv(SECURITY_MASTER_FILE)

            if security.empty:
                raise ValueError("Security Master is empty.")

            required_columns = [
                "Security_ID",
                "Symbol",
                "Company_Name",
                "Sector",
                "Industry",
                "Market_Cap",
            ]

            missing = [
                column for column in required_columns if column not in security.columns
            ]

            if missing:
                raise ValueError(f"Missing columns: {missing}")

            security["Symbol"] = security["Symbol"].astype(str).str.upper().str.strip()

            security_lookup = security.set_index("Symbol")

            symbols = security["Symbol"].dropna().unique().tolist()

            logger.info(
                "Universe Loaded : %s securities",
                f"{len(symbols):,}",
            )

            # =================================================
            # BUILD MONTH-END CALENDAR
            # =================================================

            logger.info("Building month-end calendar...")

            sample_file = PRICE_HISTORY_DIRECTORY / f"{symbols[0]}.parquet"

            if not sample_file.exists():
                raise FileNotFoundError(f"Sample history missing:\n{sample_file}")

            sample = pd.read_parquet(
                sample_file,
                columns=["Date"],
            )

            sample["Date"] = pd.to_datetime(sample["Date"])

            month_ends = (
                sample.groupby(sample["Date"].dt.to_period("M"))["Date"].max().tolist()
            )

            logger.info(
                "Snapshots to Build : %s",
                len(month_ends),
            )

            # =================================================
            # PREPARE COLLECTIONS
            # =================================================

            master_rows: list[dict] = []

            failures: list[dict] = []

            # =================================================
            # SNAPSHOT CALCULATION
            # =================================================

            def calculate_snapshot(
                symbol: str,
                snapshot_date: pd.Timestamp,
            ) -> dict | None:
                """
                Calculate factor snapshot for
                a single security.
                """

                try:
                    history_file = PRICE_HISTORY_DIRECTORY / f"{symbol}.parquet"

                    if not history_file.exists():
                        return None

                    history = pd.read_parquet(history_file)

                    history["Date"] = pd.to_datetime(history["Date"])

                    history = history[history["Date"] <= snapshot_date]

                    if len(history) < TRADING_DAYS:
                        return None

                    # =========================================
                    # PRICE SERIES
                    # =========================================

                    close = pd.to_numeric(
                        history["Close"],
                        errors="coerce",
                    ).dropna()

                    high = pd.to_numeric(
                        history["High"],
                        errors="coerce",
                    )

                    low = pd.to_numeric(
                        history["Low"],
                        errors="coerce",
                    )

                    volume = pd.to_numeric(
                        history["Volume"],
                        errors="coerce",
                    )

                    if len(close) < TRADING_DAYS:
                        return None

                    returns = close.pct_change().dropna()

                    # =========================================
                    # MOMENTUM
                    # =========================================

                    momentum_1m = close.iloc[-1] / close.iloc[-21] - 1

                    momentum_3m = close.iloc[-1] / close.iloc[-63] - 1

                    momentum_6m = close.iloc[-1] / close.iloc[-126] - 1

                    momentum_12m = close.iloc[-1] / close.iloc[-252] - 1

                    # =========================================
                    # VOLATILITY
                    # =========================================

                    volatility_20d = returns.tail(20).std() * np.sqrt(TRADING_DAYS)

                    volatility_60d = returns.tail(60).std() * np.sqrt(TRADING_DAYS)

                    # =========================================
                    # ATR
                    # =========================================

                    previous_close = close.shift(1)

                    true_range = pd.concat(
                        [
                            high - low,
                            (high - previous_close).abs(),
                            (low - previous_close).abs(),
                        ],
                        axis=1,
                    ).max(axis=1)

                    atr_14 = true_range.tail(14).mean()

                    # =========================================
                    # MAXIMUM DRAWDOWN
                    # =========================================

                    rolling_max = close.cummax()

                    drawdown = (close / rolling_max) - 1

                    max_drawdown = drawdown.tail(TRADING_DAYS).min()

                    # =========================================
                    # TREND
                    # =========================================

                    sma_50 = close.tail(50).mean()

                    sma_200 = close.tail(200).mean()

                    distance_sma50 = (close.iloc[-1] / sma_50) - 1

                    distance_sma200 = (close.iloc[-1] / sma_200) - 1

                    # =========================================
                    # 52 WEEK HIGH
                    # =========================================

                    high_52w = close.tail(TRADING_DAYS).max()

                    distance_52w_high = (close.iloc[-1] / high_52w) - 1

                    # =========================================
                    # LIQUIDITY
                    # =========================================

                    adv_20d = (close.tail(20) * volume.tail(20)).mean()

                    dollar_volume = adv_20d

                    # =========================================
                    # SECURITY METADATA
                    # =========================================

                    metadata = security_lookup.loc[symbol]

                    # =========================================
                    # BUILD SNAPSHOT RECORD
                    # =========================================

                    return {
                        # ==============================
                        # SNAPSHOT INFO
                        # ==============================
                        "Snapshot_Date": snapshot_date.strftime(DATE_FORMAT),
                        # ==============================
                        # IDENTIFIERS
                        # ==============================
                        "Security_ID": metadata["Security_ID"],
                        "Symbol": symbol,
                        "Company_Name": metadata.get(
                            "Company_Name",
                            "",
                        ),
                        "Sector": metadata.get(
                            "Sector",
                            "",
                        ),
                        "Industry": metadata.get(
                            "Industry",
                            "",
                        ),
                        # ==============================
                        # SIZE
                        # ==============================
                        "Market_Cap": float(
                            metadata.get(
                                "Market_Cap",
                                np.nan,
                            )
                        ),
                        # ==============================
                        # PRICE
                        # ==============================
                        "Last_Close": float(close.iloc[-1]),
                        # ==============================
                        # MOMENTUM
                        # ==============================
                        "Momentum_1M": float(momentum_1m),
                        "Momentum_3M": float(momentum_3m),
                        "Momentum_6M": float(momentum_6m),
                        "Momentum_12M": float(momentum_12m),
                        # ==============================
                        # RISK
                        # ==============================
                        "Volatility_20D": float(volatility_20d),
                        "Volatility_60D": float(volatility_60d),
                        "ATR_14": float(atr_14),
                        "Max_Drawdown_252D": float(max_drawdown),
                        # ==============================
                        # TREND
                        # ==============================
                        "SMA_50": float(sma_50),
                        "SMA_200": float(sma_200),
                        "Distance_SMA50": float(distance_sma50),
                        "Distance_SMA200": float(distance_sma200),
                        # ==============================
                        # 52 WEEK HIGH
                        # ==============================
                        "Distance_52W_High": float(distance_52w_high),
                        # ==============================
                        # LIQUIDITY
                        # ==============================
                        "ADV_20D": float(adv_20d),
                        "Dollar_Volume": float(dollar_volume),
                        # ==============================
                        # ENGINE METADATA
                        # ==============================
                        "Engine_Version": ENGINE_VERSION,
                    }

                except Exception as exc:
                    failures.append(
                        {
                            "Snapshot_Date": snapshot_date.strftime(DATE_FORMAT),
                            "Symbol": symbol,
                            "Error": str(exc),
                            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        }
                    )

                    logger.exception(
                        "Snapshot failed for %s",
                        symbol,
                    )

                    return None

            # =================================================
            # BUILD MONTHLY SNAPSHOTS
            # =================================================

            logger.info("Building historical factor snapshots...")

            ensure_parent_directory(FACTOR_SNAPSHOT_MASTER_FILE)

            for snapshot_date in month_ends:
                logger.info(
                    "Snapshot : %s",
                    snapshot_date.strftime("%Y-%m"),
                )

                records: list[dict] = []

                with ThreadPoolExecutor(
                    max_workers=MAX_WORKERS,
                ) as executor:
                    results = executor.map(
                        lambda security: calculate_snapshot(
                            security,
                            snapshot_date,
                        ),
                        symbols,
                    )

                    for result in results:
                        if result is not None:
                            records.append(result)

                snapshot_df = pd.DataFrame(records)

                snapshot_file = FACTOR_SNAPSHOT_DIRECTORY / (
                    "factor_snapshot_" + snapshot_date.strftime("%Y_%m") + ".parquet"
                )

                ensure_parent_directory(snapshot_file)

                snapshot_df.to_parquet(
                    snapshot_file,
                    index=False,
                )

                master_rows.extend(records)

            # =================================================
            # BUILD MASTER SNAPSHOT
            # =================================================

            logger.info("Building master snapshot...")

            master_snapshot = (
                pd.DataFrame(master_rows)
                .sort_values(
                    [
                        "Snapshot_Date",
                        "Market_Cap",
                    ],
                    ascending=[
                        True,
                        False,
                    ],
                )
                .reset_index(drop=True)
            )

            master_snapshot.to_csv(
                FACTOR_SNAPSHOT_MASTER_FILE,
                index=False,
            )

            # =================================================
            # BUILD EXECUTION REPORT
            # =================================================

            report = pd.DataFrame(
                {
                    "Metric": [
                        "Snapshots",
                        "Total_Rows",
                        "Unique_Securities",
                        "Failures",
                        "Run_Date",
                        "Engine_Version",
                    ],
                    "Value": [
                        len(month_ends),
                        len(master_snapshot),
                        master_snapshot["Symbol"].nunique(),
                        len(failures),
                        datetime.now().strftime(DATE_FORMAT),
                        ENGINE_VERSION,
                    ],
                }
            )

            ensure_parent_directory(FACTOR_SNAPSHOT_REPORT_FILE)

            report.to_csv(
                FACTOR_SNAPSHOT_REPORT_FILE,
                index=False,
            )

            # =================================================
            # SAVE FAILURE REPORT
            # =================================================

            if failures:
                failure_file = (
                    FACTOR_SNAPSHOT_REPORT_FILE.parent / "factor_snapshot_failures.csv"
                )

                pd.DataFrame(failures).to_csv(
                    failure_file,
                    index=False,
                )

            # =================================================
            # EXECUTION SUMMARY
            # =================================================

            logger.info("=" * 70)

            logger.info("FACTOR SNAPSHOT ENGINE COMPLETE")

            logger.info("=" * 70)

            logger.info(
                "Snapshots Built : %s",
                len(month_ends),
            )

            logger.info(
                "Rows Generated  : %s",
                f"{len(master_snapshot):,}",
            )

            logger.info(
                "Securities      : %s",
                f"{master_snapshot['Symbol'].nunique():,}",
            )

            logger.info(
                "Failures        : %s",
                len(failures),
            )

            logger.info(
                "Snapshot Master : %s",
                FACTOR_SNAPSHOT_MASTER_FILE,
            )

            logger.info("=" * 70)

            # =================================================
            # EXECUTION METADATA
            # =================================================

            execution_metadata = {
                "engine_version": ENGINE_VERSION,
                "snapshots": len(month_ends),
                "records_processed": len(master_snapshot),
                "unique_securities": master_snapshot["Symbol"].nunique(),
                "failed_snapshots": len(failures),
                "run_date": datetime.now().strftime(DATE_FORMAT),
            }

            # =================================================
            # RETURN RESULT
            # =================================================

            return EngineResult(
                engine=ENGINE_NAME,
                status=EngineStatus.SUCCESS,
                records=len(master_snapshot),
                output=FACTOR_SNAPSHOT_MASTER_FILE,
                report=FACTOR_SNAPSHOT_REPORT_FILE,
                duration=timer.elapsed,
                metadata=execution_metadata,
            )

        # =====================================================
        # EXCEPTION HANDLING
        # =====================================================

        except Exception as exc:
            logger.exception("Factor Snapshot Engine failed.")

            return EngineResult(
                engine=ENGINE_NAME,
                status=EngineStatus.FAILED,
                duration=timer.elapsed,
                metadata={
                    "error": str(exc),
                },
            )


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    result = main()

    logger.info(
        "Engine Status : %s",
        result.status.value,
    )
