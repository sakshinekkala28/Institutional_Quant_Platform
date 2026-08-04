"""
=========================================================
PLATFORM THRESHOLDS
=========================================================

Purpose:
Centralized quantitative thresholds used throughout
the Institutional Quant Platform.

=========================================================
"""

# =========================================================
# UNIVERSE CONSTRUCTION
# =========================================================

MIN_MARKET_CAP = 100e7  # ₹100 Crore

MIN_PRICE = 20.0  # ₹20

MIN_ADV = 1e7  # ₹1 Crore

FULL_HISTORY_YEARS = 5

MIN_HISTORY_DAYS = 252  # 1 Trading Year

MAX_MISSING_PCT = 0.10  # 10%

# =========================================================
# MARKET CAP CLASSIFICATION
# =========================================================

SMALL_CAP_MAX = 5e10  # ₹5,000 Crore

MID_CAP_MAX = 2e11  # ₹20,000 Crore

# =========================================================
# STOCK METADATA
# =========================================================

LARGE_CAP_THRESHOLD = 20e9

MID_CAP_THRESHOLD = 5e9

# =========================================================
# LIQUIDITY CLASSIFICATION
# =========================================================

HIGH_LIQUIDITY_ADV = 100e6

MEDIUM_LIQUIDITY_ADV = 25e6

# =========================================================
# DATA QUALITY
# =========================================================

MIN_SYMBOL_COVERAGE = 0.95

MIN_METADATA_COVERAGE = 0.90

MIN_PRICE_COVERAGE = 0.90

# =========================================================
# YAHOO FINANCE
# =========================================================

MAX_WORKERS = 3

MAX_RETRIES = 3

SAVE_INTERVAL = 50

COOLDOWN_AFTER = 100

COOLDOWN_SECONDS = 10
