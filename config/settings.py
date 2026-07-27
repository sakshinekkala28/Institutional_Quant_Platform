"""
=========================================================
PLATFORM SETTINGS
=========================================================

Purpose:
Centralized runtime configuration for the
Institutional Quant Platform.

=========================================================
"""

from __future__ import annotations

# =========================================================
# PLATFORM
# =========================================================

PLATFORM_NAME = "Institutional Quant Platform"

PLATFORM_VERSION = "1.0.0"

ENVIRONMENT = "development"
# development
# testing
# production

# =========================================================
# EXECUTION
# =========================================================

STOP_ON_FAILURE = True

ENABLE_PARALLEL_PIPELINES = False

ENABLE_PIPELINE_TIMING = True

ENABLE_ENGINE_TIMING = True

# =========================================================
# LOGGING
# =========================================================

LOG_LEVEL = "INFO"

ENABLE_CONSOLE_LOGGING = True

ENABLE_FILE_LOGGING = True

# =========================================================
# DATA
# =========================================================

DEFAULT_EXCHANGE = "NSE"

DEFAULT_COUNTRY = "India"

DEFAULT_CURRENCY = "INR"

DEFAULT_ASSET_CLASS = "Equity"

# =========================================================
# MARKET DATA
# =========================================================

DEFAULT_PRICE_COLUMN = "Close"

FALLBACK_PRICE_COLUMN = "Adj Close"

DEFAULT_VOLUME_COLUMN = "Volume"

# =========================================================
# DATE & TIME
# =========================================================

DATE_FORMAT = "%Y-%m-%d"

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

TIMEZONE = "Asia/Kolkata"

# =========================================================
# OUTPUT
# =========================================================

CSV_INDEX = False

FLOAT_PRECISION = 4

ENCODING = "utf-8"

# =========================================================
# DATA QUALITY
# =========================================================

STRICT_VALIDATION = True

FAIL_ON_MISSING_COLUMNS = True

FAIL_ON_EMPTY_DATAFRAME = True

# =========================================================
# REPORTING
# =========================================================

SHOW_PROGRESS = True

SHOW_SUMMARY = True

SHOW_BANNER = True

EXPORT_HEALTH_REPORTS = True
