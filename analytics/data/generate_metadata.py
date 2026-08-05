"""
=========================================================
STOCK METADATA ENGINE
=========================================================

Purpose:
Create final institutional security master

Input:
data/raw/updated_stocks.csv

Output:
data/raw/stock_metadata.csv

=========================================================
"""

import time
from datetime import datetime

import numpy as np
import pandas as pd

from config.paths import (STOCK_METADATA_FILE, STOCK_METADATA_HEALTH_FILE,
                          UPDATED_STOCKS_FILE)
from config.settings import (DATE_FORMAT, DEFAULT_ASSET_CLASS, DEFAULT_COUNTRY,
                             DEFAULT_CURRENCY, DEFAULT_EXCHANGE, PLATFORM_NAME)
from config.thresholds import LARGE_CAP_THRESHOLD, MID_CAP_THRESHOLD
from orchestration.models.engine_result import EngineResult
from orchestration.models.engine_status import EngineStatus
from utils.file_utils import ensure_parent_directory
from utils.logger import get_logger

logger = get_logger(__name__)

# =========================================================
# CONFIG
# =========================================================

ENGINE_NAME = "StockMetadata"

# =========================================================
# MAIN
# =========================================================


def main() -> EngineResult:
    """
    Stock Metadata Engine
    """

    start_time = time.perf_counter()

    try:
        # =====================================================
        # LOAD
        # =====================================================

        logger.info("\n📥 Loading Updated Universe...")

        if not UPDATED_STOCKS_FILE.exists():
            raise FileNotFoundError(f"Missing file:\n{UPDATED_STOCKS_FILE}")

        df = pd.read_csv(UPDATED_STOCKS_FILE)

        # =====================================================
        # STANDARDIZE COLUMNS
        # =====================================================

        rename_map = {
            "symbol": "Symbol",
            "company_name": "Company_Name",
            "sector": "Sector",
            "industry": "Industry",
            "market_cap": "Market_Cap",
            "avg_daily_turnover": "ADV",
        }

        df.rename(
            columns={k: v for k, v in rename_map.items() if k in df.columns},
            inplace=True,
        )

        # =====================================================
        # REQUIRED COLUMNS
        # =====================================================

        required_columns = [
            "Symbol",
        ]

        for col in required_columns:
            if col not in df.columns:
                raise ValueError(f"Missing required column: {col}")

        # =====================================================
        # DEFAULTS
        # =====================================================

        defaults = {
            "Company_Name": "Unknown",
            "Sector": "Unknown",
            "Industry": "Unknown",
            "Market_Cap": 0,
            "ADV": 0,
        }

        for col, value in defaults.items():
            if col not in df.columns:
                df[col] = value

        # =====================================================
        # CLEANING
        # =====================================================

        df["Symbol"] = df["Symbol"].astype(str).str.upper().str.strip()

        df["Company_Name"] = df["Company_Name"].astype(str).str.strip()

        df["Sector"] = df["Sector"].astype(str).str.strip()

        df["Industry"] = df["Industry"].astype(str).str.strip()

        df["Market_Cap"] = pd.to_numeric(
            df["Market_Cap"],
            errors="coerce",
        ).fillna(0)

        df["ADV"] = pd.to_numeric(
            df["ADV"],
            errors="coerce",
        ).fillna(0)

        # =====================================================
        # STATIC METADATA
        # =====================================================

        df["Exchange"] = DEFAULT_EXCHANGE

        df["Country"] = DEFAULT_COUNTRY

        df["Currency"] = DEFAULT_CURRENCY

        df["Asset_Class"] = DEFAULT_ASSET_CLASS

        df["Metadata_Source"] = PLATFORM_NAME

        df["Last_Updated"] = datetime.now().strftime(DATE_FORMAT)

        # =====================================================
        # MARKET CAP CLASSIFICATION
        # =====================================================

        df["Market_Cap_Category"] = np.select(
            [
                df["Market_Cap"] >= LARGE_CAP_THRESHOLD,
                (
                    (df["Market_Cap"] >= MID_CAP_THRESHOLD)
                    & (df["Market_Cap"] < LARGE_CAP_THRESHOLD)
                ),
            ],
            [
                "Large Cap",
                "Mid Cap",
            ],
            default="Small Cap",
        )

        # =====================================================
        # LIQUIDITY CLASSIFICATION
        # =====================================================

        df["Liquidity_Category"] = np.select(
            [
                df["ADV"] >= 100_000_000,
                ((df["ADV"] >= 25_000_000) & (df["ADV"] < 100_000_000)),
            ],
            [
                "Highly Liquid",
                "Liquid",
            ],
            default="Less Liquid",
        )

        # =====================================================
        # SECTOR VALIDATION
        # =====================================================

        df["Sector"] = df["Sector"].replace(
            {
                "": "Unknown",
                "nan": "Unknown",
                "None": "Unknown",
            }
        )

        df["Industry"] = df["Industry"].replace(
            {
                "": "Unknown",
                "nan": "Unknown",
                "None": "Unknown",
            }
        )

        # =====================================================
        # DATA HEALTH REPORT
        # =====================================================

        health = pd.DataFrame(
            {
                "Metric": [
                    "Total Stocks",
                    "Missing Sector",
                    "Missing Industry",
                    "Missing Market Cap",
                    "Missing ADV",
                ],
                "Value": [
                    len(df),
                    (df["Sector"] == "Unknown").sum(),
                    (df["Industry"] == "Unknown").sum(),
                    (df["Market_Cap"] <= 0).sum(),
                    (df["ADV"] <= 0).sum(),
                ],
            }
        )

        # =====================================================
        # FINAL SORT
        # =====================================================

        original_rows = len(df)

        df = (
            df.sort_values(
                "Market_Cap",
                ascending=False,
            )
            .drop_duplicates(subset=["Symbol"])
            .reset_index(drop=True)
        )

        duplicates_removed = original_rows - len(df)

        # =====================================================
        # SAVE
        # =====================================================

        ensure_parent_directory(STOCK_METADATA_FILE)

        ensure_parent_directory(STOCK_METADATA_HEALTH_FILE)

        df.to_csv(
            STOCK_METADATA_FILE,
            index=False,
        )

        health.to_csv(
            STOCK_METADATA_HEALTH_FILE,
            index=False,
        )

        # =====================================================
        # REPORT
        # =====================================================

        print("\n" + "=" * 70)

        print("🏁 STOCK METADATA ENGINE COMPLETE")

        print("=" * 70)

        print(f"Stocks              : {len(df):,}")

        print(
            f"Large Cap           : "
            f"{(df['Market_Cap_Category'] == 'Large Cap').sum():,}"
        )

        print(
            f"Mid Cap             : {(df['Market_Cap_Category'] == 'Mid Cap').sum():,}"
        )

        print(
            f"Small Cap           : "
            f"{(df['Market_Cap_Category'] == 'Small Cap').sum():,}"
        )

        print(
            f"Highly Liquid       : "
            f"{(df['Liquidity_Category'] == 'Highly Liquid').sum():,}"
        )

        print(f"Liquid              : {(df['Liquidity_Category'] == 'Liquid').sum():,}")

        print(
            f"Less Liquid         : "
            f"{(df['Liquidity_Category'] == 'Less Liquid').sum():,}"
        )

        print(f"\nSaved:\n{STOCK_METADATA_FILE}")

        print(f"\nHealth Report:\n{STOCK_METADATA_HEALTH_FILE}")

        print("=" * 70)

        # =====================================================
        # BUILD EXECUTION METADATA
        # =====================================================

        duration = time.perf_counter() - start_time

        execution_metadata = {
            "total_stocks": len(df),
            "unique_symbols": (df["Symbol"].nunique()),
            "duplicates_removed": (duplicates_removed),
            "large_cap": (df["Market_Cap_Category"].eq("Large Cap").sum()),
            "mid_cap": (df["Market_Cap_Category"].eq("Mid Cap").sum()),
            "small_cap": (df["Market_Cap_Category"].eq("Small Cap").sum()),
            "highly_liquid": (df["Liquidity_Category"].eq("Highly Liquid").sum()),
            "liquid": (df["Liquidity_Category"].eq("Liquid").sum()),
            "less_liquid": (df["Liquidity_Category"].eq("Less Liquid").sum()),
        }

        # =====================================================
        # RETURN RESULT
        # =====================================================

        return EngineResult(
            engine=ENGINE_NAME,
            status=EngineStatus.SUCCESS,
            records=len(df),
            output=STOCK_METADATA_FILE,
            report=STOCK_METADATA_HEALTH_FILE,
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
