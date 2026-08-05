"""
=========================================================
SECURITY MASTER ENGINE
=========================================================

Purpose:
Create institutional-grade Security Master

Input:
data/raw/updated_stocks.csv

Output:
data/raw/security_master.csv

=========================================================
"""

from datetime import datetime
import hashlib
import time

import pandas as pd

from config.paths import SECURITY_MASTER_FILE, UPDATED_STOCKS_FILE
from config.settings import (
    DATE_FORMAT,
    DEFAULT_ASSET_CLASS,
    DEFAULT_COUNTRY,
    DEFAULT_CURRENCY,
    DEFAULT_EXCHANGE,
)
from config.thresholds import MID_CAP_MAX, SMALL_CAP_MAX
from orchestration.models.engine_result import EngineResult
from orchestration.models.engine_status import EngineStatus
from utils.file_utils import ensure_parent_directory
from utils.logger import get_logger

logger = get_logger(__name__)


# =========================================================
# CONFIG
# =========================================================

ENGINE_NAME = "SecurityMaster"

# =========================================================
# MAIN
# =========================================================


def main() -> EngineResult:
    """
    Security Master Engine
    """

    start_time = time.perf_counter()

    try:
        # =====================================================
        # LOAD
        # =====================================================

        logger.info("\n📥 Loading Investable Universe...")

        df = pd.read_csv(UPDATED_STOCKS_FILE)

        # =====================================================
        # VALIDATION
        # =====================================================

        required_columns = [
            "Symbol",
            "Company_Name",
            "Sector",
            "Industry",
            "Market_Cap",
            "Last_Close",
            "ADV",
        ]

        missing = [c for c in required_columns if c not in df.columns]

        if missing:
            raise ValueError(f"Missing Columns: {missing}")

        # =====================================================
        # CLEAN
        # =====================================================

        df["Symbol"] = df["Symbol"].astype(str).str.upper().str.strip()

        original_rows = len(df)

        df = df.drop_duplicates(subset="Symbol").reset_index(drop=True)

        duplicates_removed = original_rows - len(df)

        numeric_cols = [
            "Market_Cap",
            "Last_Close",
            "ADV",
            "History_Days",
        ]

        for col in numeric_cols:
            df[col] = pd.to_numeric(
                df[col],
                errors="coerce",
            )

        df = df.dropna(
            subset=[
                "Market_Cap",
                "Last_Close",
            ]
        )

        # =====================================================
        # SECURITY IDENTIFIER
        # =====================================================

        df.insert(
            0,
            "Security_ID",
            df["Symbol"].apply(
                lambda x: "SEC" + hashlib.md5(x.encode()).hexdigest()[:8].upper()
            ),
        )

        # =====================================================
        # STATIC REFERENCE DATA
        # =====================================================

        df["Yahoo_Symbol"] = df["Symbol"] + ".NS"

        df["Exchange"] = DEFAULT_EXCHANGE

        df["Country"] = DEFAULT_COUNTRY

        df["Currency"] = DEFAULT_CURRENCY

        df["Asset_Type"] = DEFAULT_ASSET_CLASS

        df["Universe_Flag"] = 1

        today = datetime.now().strftime(DATE_FORMAT)

        df["Created_Date"] = today

        df["Last_Updated"] = today

        df["Is_Active"] = 1

        df["Market_Cap_Category"] = pd.cut(
            df["Market_Cap"],
            bins=[
                0,
                SMALL_CAP_MAX,
                MID_CAP_MAX,
                float("inf"),
            ],
            labels=[
                "Small Cap",
                "Mid Cap",
                "Large Cap",
            ],
        )

        # =====================================================
        # OPTIONAL COLUMN VALIDATION
        # =====================================================

        optional_columns = {
            "History_Days": pd.NA,
            "Missing_Close": pd.NA,
        }

        for col, default in optional_columns.items():
            if col not in df.columns:
                df[col] = default

        # =====================================================
        # COLUMN ORDER
        # =====================================================

        columns = [
            "Security_ID",
            "Symbol",
            "Yahoo_Symbol",
            "Company_Name",
            "Sector",
            "Industry",
            "Market_Cap",
            "Market_Cap_Category",
            "Last_Close",
            "ADV",
            "History_Days",
            "Missing_Close",
            "Exchange",
            "Country",
            "Currency",
            "Asset_Type",
            "Universe_Flag",
            "Is_Active",
            "Created_Date",
            "Last_Updated",
        ]

        security_master = df[columns]

        # =====================================================
        # SORT
        # =====================================================

        security_master = security_master.sort_values(
            "Market_Cap",
            ascending=False,
        ).reset_index(drop=True)

        # =====================================================
        # SAVE
        # =====================================================

        ensure_parent_directory(SECURITY_MASTER_FILE)

        security_master.to_csv(
            SECURITY_MASTER_FILE,
            index=False,
        )

        # =====================================================
        # REPORT
        # =====================================================

        print("\n" + "=" * 70)

        print("🏁 SECURITY MASTER COMPLETE")

        print("=" * 70)

        print(f"Total Securities : {len(security_master):,}")

        print(f"Largest Market Cap : {security_master['Market_Cap'].max():,.0f}")

        print(f"Median ADV : {security_master['ADV'].median():,.0f}")

        print(f"\nSaved:\n{SECURITY_MASTER_FILE}")

        print("=" * 70)

        # =====================================================
        # BUILD EXECUTION METADATA
        # =====================================================

        duration = time.perf_counter() - start_time

        execution_metadata = {
            "total_securities": len(security_master),
            "unique_symbols": (security_master["Symbol"].nunique()),
            "duplicates_removed": duplicates_removed,
            "largest_market_cap": float(security_master["Market_Cap"].max()),
            "median_adv": float(security_master["ADV"].median()),
            "column_count": len(security_master.columns),
        }

        # =====================================================
        # RETURN RESULT
        # =====================================================

        return EngineResult(
            engine=ENGINE_NAME,
            status=EngineStatus.SUCCESS,
            records=len(security_master),
            output=SECURITY_MASTER_FILE,
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
