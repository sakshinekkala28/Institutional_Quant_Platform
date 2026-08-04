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
# DATA DIRECTORIES
# =========================================================

DATA_DIR = ROOT / "data"

RAW_DATA_DIR = DATA_DIR / "raw"

PROCESSED_DATA_DIR = DATA_DIR / "processed"

FEATURE_DATA_DIR = DATA_DIR / "features"

LOG_DIR = DATA_DIR / "logs"

CACHE_DIR = DATA_DIR / "cache"

REPORT_DIR = DATA_DIR / "reports"

PORTFOLIO_DIRECTORY = DATA_DIR / "portfolios"

DATABASE_DIR = DATA_DIR / "database"

# =========================================================
# RAW DATA
# =========================================================

PRICE_DIR = RAW_DATA_DIR / "prices"

# Backward compatibility
PRICE_HISTORY_DIRECTORY = PRICE_DIR

VALID_STOCKS_FILE = (
    RAW_DATA_DIR
    / "valid_stocks.xlsx"
)

SYMBOL_METADATA_FILE = (
    RAW_DATA_DIR
    / "symbol_metadata.csv"
)

UPDATED_STOCKS_FILE = (
    RAW_DATA_DIR
    / "updated_stocks.csv"
)

SECURITY_MASTER_FILE = (
    RAW_DATA_DIR
    / "security_master.csv"
)

STOCK_METADATA_FILE = (
    RAW_DATA_DIR
    / "stock_metadata.csv"
)

# =========================================================
# FEATURE OUTPUTS
# =========================================================

FACTOR_MASTER_FILE = (
    FEATURE_DATA_DIR
    / "factor_master.parquet"
)

FACTOR_RANK_MASTER_FILE = (
    FEATURE_DATA_DIR
    / "factor_rank_master.csv"
)

# =========================================================
# SNAPSHOTS
# =========================================================

SNAPSHOT_DIR = (
    DATA_DIR
    / "snapshots"
)

# Backward compatibility

FACTOR_SNAPSHOT_DIRECTORY = SNAPSHOT_DIR

FACTOR_SNAPSHOT_MASTER_FILE = (
    SNAPSHOT_DIR
    / "factor_snapshot_master.csv"
)

FACTOR_SNAPSHOT_REPORT_FILE = (
    LOG_DIR
    / "factor_snapshot_report.csv"
)

# =========================================================
# REPORTS
# =========================================================

UNIVERSE_REPORT_FILE = (
    LOG_DIR
    / "universe_report.csv"
)

STOCK_METADATA_HEALTH_FILE = (
    LOG_DIR
    / "stock_metadata_health.csv"
)

FACTOR_COVERAGE_REPORT = (
    LOG_DIR
    / "factor_coverage_report.csv"
)

FACTOR_FAILURE_REPORT = (
    LOG_DIR
    / "factor_failure_report.csv"
)

RANKING_REPORT_FILE = (
    LOG_DIR
    / "factor_ranking_report.csv"
)

FACTOR_EXPOSURE_FILE = (
    REPORT_DIR
    / "factor_exposure.csv"
)

SECTOR_EXPOSURE_FILE = (
    REPORT_DIR
    / "sector_exposure.csv"
)

MARKET_CAP_REPORT_FILE = (
    LOG_DIR
    / "market_cap_report.csv"
)

MARKET_CAP_FAILURE_FILE = (
    LOG_DIR
    / "market_cap_failures.csv"
)

# =========================================================
# CACHE
# =========================================================

MARKET_CAP_CACHE_FILE = (
    CACHE_DIR
    / "market_cap_cache.parquet"
)

# =========================================================
# LOG FILES
# =========================================================

PRICE_UPDATE_FAILURE_FILE = (
    LOG_DIR
    / "price_update_failures.csv"
)

INVALID_SYMBOL_FILE = (
    LOG_DIR
    / "invalid_symbols.csv"
)

# =========================================================
# DATABASES
# =========================================================

DUCKDB_DATABASE = (
    DATABASE_DIR
    / "institutional_quant.duckdb"
)

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
    PORTFOLIO_DIRECTORY,
    DATABASE_DIR,
    SNAPSHOT_DIR,
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