"""
=========================================================
FACTOR ENGINE
=========================================================

Purpose:
Calculate institutional equity factor exposures
for the investable universe.

Input
-----
data/raw/security_master.csv
data/raw/prices/*.parquet

Output
------
data/factors/factor_master.csv

Reports
-------
data/logs/factor_failures.csv
data/logs/factor_coverage.csv

=========================================================
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import numpy as np
import pandas as pd

from config.paths import (
    FACTOR_COVERAGE_REPORT,
    FACTOR_FAILURE_REPORT,
    FACTOR_MASTER_FILE,
    PRICE_HISTORY_DIRECTORY,
    SECURITY_MASTER_FILE,
)
from config.settings import DATE_FORMAT, ENGINE_VERSION, MAX_WORKERS, TRADING_DAYS
from orchestration.models.engine_result import EngineResult
from orchestration.models.engine_status import EngineStatus
from utils.file_utils import ensure_parent_directory
from utils.logger import get_logger
from utils.timer import Timer

# =========================================================
# CONFIG
# =========================================================

ENGINE_NAME = "FactorEngine"

logger = get_logger(__name__)

# =========================================================
# MAIN
# =========================================================


def main() -> EngineResult:
    """
    Calculate institutional factor master.
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
            # LOAD UNIVERSE
            # =================================================

            universe = pd.read_csv(SECURITY_MASTER_FILE)

            required_columns = [
                "Security_ID",
                "Symbol",
                "Company_Name",
                "Sector",
                "Industry",
                "Market_Cap",
            ]

            missing = [
                column for column in required_columns if column not in universe.columns
            ]

            if missing:
                raise ValueError(f"Missing required columns: {missing}")

            universe["Symbol"] = universe["Symbol"].astype(str).str.upper().str.strip()

            universe = universe.drop_duplicates(subset="Symbol").reset_index(drop=True)

            symbols = universe["Symbol"].dropna().tolist()

            security_lookup = universe.set_index("Symbol")

            logger.info(
                "Universe Loaded : %s securities",
                f"{len(symbols):,}",
            )

            # =================================================
            # PREPARE EXECUTION OBJECTS
            # =================================================

            failures: list[dict] = []

            records: list[dict] = []

            # =================================================
            # FACTOR CALCULATION FUNCTION
            # =================================================

            def calculate_factors(
                symbol: str,
            ) -> dict | None:
                """
                Calculate factor exposures
                for a single security.
                """

                try:
                    price_file = PRICE_HISTORY_DIRECTORY / f"{symbol}.parquet"

                    if not price_file.exists():
                        return None

                    df = pd.read_parquet(price_file)

                    required_price_columns = [
                        "Close",
                        "High",
                        "Low",
                        "Volume",
                    ]

                    if not all(
                        column in df.columns for column in required_price_columns
                    ):
                        return None

                    if len(df) < TRADING_DAYS:
                        return None

                    # =========================================
                    # PRICE SERIES
                    # =========================================

                    close = pd.to_numeric(
                        df["Close"],
                        errors="coerce",
                    ).dropna()

                    high = pd.to_numeric(
                        df["High"],
                        errors="coerce",
                    )

                    low = pd.to_numeric(
                        df["Low"],
                        errors="coerce",
                    )

                    volume = pd.to_numeric(
                        df["Volume"],
                        errors="coerce",
                    )

                    if len(close) < TRADING_DAYS:
                        return None

                    # =========================================
                    # MOMENTUM FACTORS
                    # =========================================

                    momentum_1m = close.iloc[-1] / close.iloc[-21] - 1

                    momentum_3m = close.iloc[-1] / close.iloc[-63] - 1

                    momentum_6m = close.iloc[-1] / close.iloc[-126] - 1

                    momentum_12m = close.iloc[-1] / close.iloc[-252] - 1

                    # =========================================
                    # SIZE FACTORS
                    # =========================================

                    market_cap = security_lookup.loc[
                        symbol,
                        "Market_Cap",
                    ]

                    log_market_cap = np.log(
                        max(
                            market_cap,
                            1,
                        )
                    )

                    # =========================================
                    # RETURN SERIES
                    # =========================================

                    returns = close.pct_change().dropna()

                    # =========================================
                    # DRAWDOWN
                    # =========================================

                    rolling_max = close.cummax()

                    drawdown = (close / rolling_max) - 1

                    max_drawdown = drawdown.min()

                    # =========================================
                    # VOLATILITY
                    # =========================================

                    volatility_20d = returns.tail(20).std() * np.sqrt(TRADING_DAYS)

                    volatility_60d = returns.tail(60).std() * np.sqrt(TRADING_DAYS)

                    # =========================================
                    # ATR (Average True Range)
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

                    turnover_ratio = volume.tail(20).mean()

                    # =========================================
                    # BUILD FACTOR RECORD
                    # =========================================

                    return {
                        # =====================================
                        # IDENTIFIERS
                        # =====================================
                        "Security_ID": security_lookup.loc[
                            symbol,
                            "Security_ID",
                        ],
                        "Symbol": symbol,
                        "Company_Name": security_lookup.loc[
                            symbol,
                            "Company_Name",
                        ],
                        "Sector": security_lookup.loc[
                            symbol,
                            "Sector",
                        ],
                        "Industry": security_lookup.loc[
                            symbol,
                            "Industry",
                        ],
                        # =====================================
                        # PRICE
                        # =====================================
                        "Last_Close": float(close.iloc[-1]),
                        # =====================================
                        # SIZE
                        # =====================================
                        "Market_Cap": float(market_cap),
                        "Log_Market_Cap": float(log_market_cap),
                        # =====================================
                        # MOMENTUM
                        # =====================================
                        "Momentum_1M": float(momentum_1m),
                        "Momentum_3M": float(momentum_3m),
                        "Momentum_6M": float(momentum_6m),
                        "Momentum_12M": float(momentum_12m),
                        # =====================================
                        # RISK
                        # =====================================
                        "Volatility_20D": float(volatility_20d),
                        "Volatility_60D": float(volatility_60d),
                        "ATR_14": float(atr_14),
                        "Max_Drawdown_252D": float(max_drawdown),
                        # =====================================
                        # TREND
                        # =====================================
                        "SMA_50": float(sma_50),
                        "SMA_200": float(sma_200),
                        "Distance_SMA50": float(distance_sma50),
                        "Distance_SMA200": float(distance_sma200),
                        # =====================================
                        # 52 WEEK HIGH
                        # =====================================
                        "Price_52W_High": float(high_52w),
                        "Distance_52W_High": float(distance_52w_high),
                        # =====================================
                        # LIQUIDITY
                        # =====================================
                        "ADV_20D": float(adv_20d),
                        "Dollar_Volume": float(dollar_volume),
                        "Turnover_Ratio": float(turnover_ratio),
                        # =====================================
                        # METADATA
                        # =====================================
                        "Factor_Date": datetime.now().strftime(DATE_FORMAT),
                        "Engine_Version": ENGINE_VERSION,
                    }

                except Exception as exc:
                    failures.append(
                        {
                            "Symbol": symbol,
                            "Error": str(exc),
                            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        }
                    )

                    logger.exception(
                        "Factor calculation failed for %s",
                        symbol,
                    )

                    return None

            # =================================================
            # MULTI-THREADED EXECUTION
            # =================================================

            logger.info("Calculating factor exposures...")

            with ThreadPoolExecutor(
                max_workers=MAX_WORKERS,
            ) as executor:
                results = executor.map(
                    calculate_factors,
                    symbols,
                )

                for index, result in enumerate(
                    results,
                    start=1,
                ):
                    if result is not None:
                        records.append(result)

                    if index % 100 == 0 or index == len(symbols):
                        logger.info(
                            "Processed %s/%s securities",
                            f"{index:,}",
                            f"{len(symbols):,}",
                        )

            # =================================================
            # BUILD FACTOR MASTER
            # =================================================

            factor_master = (
                pd.DataFrame(records)
                .sort_values(
                    "Market_Cap",
                    ascending=False,
                )
                .reset_index(drop=True)
            )

            # =================================================
            # BUILD COVERAGE REPORT
            # =================================================

            coverage = pd.DataFrame(
                [
                    {
                        "Factor": column,
                        "Coverage": factor_master[column].notna().sum(),
                    }
                    for column in factor_master.columns
                ]
            )

            # =================================================
            # ENSURE OUTPUT DIRECTORIES
            # =================================================

            ensure_parent_directory(FACTOR_MASTER_FILE)

            ensure_parent_directory(FACTOR_FAILURE_REPORT)

            ensure_parent_directory(FACTOR_COVERAGE_REPORT)

            # =================================================
            # SAVE OUTPUTS
            # =================================================

            factor_master.to_csv(
                FACTOR_MASTER_FILE,
                index=False,
            )

            coverage.to_csv(
                FACTOR_COVERAGE_REPORT,
                index=False,
            )

            if failures:
                pd.DataFrame(failures).to_csv(
                    FACTOR_FAILURE_REPORT,
                    index=False,
                )

            # =================================================
            # EXECUTION REPORT
            # =================================================

            logger.info("=" * 70)

            logger.info("FACTOR ENGINE COMPLETE")

            logger.info("=" * 70)

            logger.info(
                "Universe Size      : %s",
                f"{len(symbols):,}",
            )

            logger.info(
                "Factors Generated  : %s",
                f"{len(factor_master):,}",
            )

            logger.info(
                "Failures           : %s",
                f"{len(failures):,}",
            )

            logger.info(
                "Coverage Report    : %s",
                FACTOR_COVERAGE_REPORT,
            )

            logger.info(
                "Factor Master      : %s",
                FACTOR_MASTER_FILE,
            )

            logger.info("=" * 70)

            # =================================================
            # EXECUTION METADATA
            # =================================================

            execution_metadata = {
                "engine_version": ENGINE_VERSION,
                "universe_size": len(symbols),
                "records_processed": len(factor_master),
                "failed_symbols": len(failures),
                "coverage_columns": len(factor_master.columns),
                "factor_date": datetime.now().strftime(DATE_FORMAT),
            }

            # =================================================
            # RETURN RESULT
            # =================================================

            return EngineResult(
                engine=ENGINE_NAME,
                status=EngineStatus.SUCCESS,
                records=len(factor_master),
                output=FACTOR_MASTER_FILE,
                report=FACTOR_COVERAGE_REPORT,
                duration=timer.elapsed,
                metadata=execution_metadata,
            )

        # =====================================================
        # EXCEPTION HANDLING
        # =====================================================

        except Exception as exc:
            logger.exception("Factor Engine failed.")

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
