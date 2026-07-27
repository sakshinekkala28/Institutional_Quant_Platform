"""
=========================================================
PLATFORM PATHS
=========================================================

Purpose:
Centralized filesystem paths used throughout the
Institutional Quant Platform.

=========================================================
"""

from pathlib import Path

# =========================================================
# ROOT
# =========================================================

ROOT = Path(__file__).resolve().parents[1]

# =========================================================
# DATA
# =========================================================

DATA_DIR = ROOT / "data"

RAW_DATA_DIR = DATA_DIR / "raw"

PROCESSED_DATA_DIR = DATA_DIR / "processed"

FEATURE_DATA_DIR = DATA_DIR / "features"

LOG_DIR = DATA_DIR / "logs"

CACHE_DIR = DATA_DIR / "cache"

REPORT_DIR = DATA_DIR / "reports"

# =========================================================
# RAW DATA
# =========================================================

PRICE_DIR = RAW_DATA_DIR / "prices"

VALID_STOCKS_FILE = RAW_DATA_DIR / "valid_stocks.xlsx"

SYMBOL_METADATA_FILE = RAW_DATA_DIR / "symbol_metadata.csv"

UPDATED_STOCKS_FILE = RAW_DATA_DIR / "updated_stocks.csv"

SECURITY_MASTER_FILE = RAW_DATA_DIR / "security_master.csv"

STOCK_METADATA_FILE = RAW_DATA_DIR / "stock_metadata.csv"

# =========================================================
# REPORTS
# =========================================================

UNIVERSE_REPORT_FILE = LOG_DIR / "universe_report.csv"

STOCK_METADATA_HEALTH_FILE = LOG_DIR / "stock_metadata_health.csv"

# =========================================================
# DIRECTORIES
# =========================================================

DIRECTORIES = [
    DATA_DIR,
    RAW_DATA_DIR,
    PROCESSED_DATA_DIR,
    FEATURE_DATA_DIR,
    PRICE_DIR,
    CACHE_DIR,
    LOG_DIR,
    REPORT_DIR,
]

# =========================================================
# INITIALIZER
# =========================================================


def initialize_directories() -> None:
    """
    Create all platform directories.
    """

    for directory in DIRECTORIES:
        directory.mkdir(
            parents=True,
            exist_ok=True,
        )
