# ==========================================================
# CONSTANTS
# Institutional Platform Constants
# ==========================================================

from __future__ import annotations


# ==========================================================
# ENVIRONMENTS
# ==========================================================

class Environment:

    DEVELOPMENT = "DEVELOPMENT"

    TESTING = "TESTING"

    STAGING = "STAGING"

    PRODUCTION = "PRODUCTION"


# ==========================================================
# STATUS CODES
# ==========================================================

class Status:

    SUCCESS = "SUCCESS"

    FAILED = "FAILED"

    PENDING = "PENDING"

    RUNNING = "RUNNING"

    APPROVED = "APPROVED"

    REJECTED = "REJECTED"

# ==========================================================
# ORDER TYPES
# ==========================================================

class OrderType:

    MARKET = "MARKET"

    LIMIT = "LIMIT"

    STOP = "STOP"

    TWAP = "TWAP"

    VWAP = "VWAP"


# ==========================================================
# TRADE ACTIONS
# ==========================================================

class TradeAction:

    BUY = "BUY"

    SELL = "SELL"

    HOLD = "HOLD"


# ==========================================================
# REBALANCE FREQUENCY
# ==========================================================

class RebalanceFrequency:

    DAILY = "DAILY"

    WEEKLY = "WEEKLY"

    MONTHLY = "MONTHLY"

    QUARTERLY = "QUARTERLY"

    YEARLY = "YEARLY"

# ==========================================================
# MARKET REGIMES
# ==========================================================

class MarketRegime:

    BULL = "BULL"

    BEAR = "BEAR"

    SIDEWAYS = "SIDEWAYS"

    HIGH_VOL = "HIGH_VOL"

    LOW_VOL = "LOW_VOL"


# ==========================================================
# RISK LEVELS
# ==========================================================

class RiskLevel:

    LOW = "LOW"

    MEDIUM = "MEDIUM"

    HIGH = "HIGH"

    CRITICAL = "CRITICAL"


# ==========================================================
# REPORT TYPES
# ==========================================================

class ReportType:

    PORTFOLIO = "PORTFOLIO"

    RISK = "RISK"

    EXECUTION = "EXECUTION"

    PERFORMANCE = "PERFORMANCE"

    GOVERNANCE = "GOVERNANCE"

# ==========================================================
# NSE SECTORS
# ==========================================================

class Sector:

    BANKING = "BANKING"

    IT = "IT"

    FMCG = "FMCG"

    PHARMA = "PHARMA"

    AUTO = "AUTO"

    METALS = "METALS"

    ENERGY = "ENERGY"

    REALTY = "REALTY"

    CHEMICALS = "CHEMICALS"

    CAPITAL_GOODS = "CAPITAL_GOODS"

    TELECOM = "TELECOM"

    CONSUMPTION = "CONSUMPTION"

    INSURANCE = "INSURANCE"

    FINANCIAL_SERVICES = (
        "FINANCIAL_SERVICES"
    )


# ==========================================================
# DATABASE TABLES
# ==========================================================

class TableName:

    SECURITY_MASTER = (
        "security_master"
    )

    SIGNAL_MASTER = (
        "signal_master"
    )

    TARGET_PORTFOLIO = (
        "target_portfolio"
    )

    TRADE_LIST = (
        "trade_list"
    )

    RISK_REPORT = (
        "risk_report"
    )

    PERFORMANCE_REPORT = (
        "performance_report"
    )


# ==========================================================
# RISK CONSTANTS
# ==========================================================

class RiskConstants:
    """
    Institutional quantitative risk constants.
    """

    # Numerical tolerances
    EPSILON = 1e-12

    MIN_VARIANCE = EPSILON

    MIN_VOLATILITY = EPSILON

    MIN_DRAWDOWN = EPSILON

    MIN_TRACKING_ERROR = EPSILON

    MIN_BETA = EPSILON

    # Trading calendar
    TRADING_DAYS_PER_YEAR = 252

    TRADING_WEEKS_PER_YEAR = 52

    TRADING_MONTHS_PER_YEAR = 12

    # Confidence levels
    CONFIDENCE_LEVEL_90 = 0.90

    CONFIDENCE_LEVEL_95 = 0.95

    CONFIDENCE_LEVEL_99 = 0.99

    # Defaults
    DEFAULT_RISK_FREE_RATE = 0.0

    DEFAULT_TARGET_RETURN = 0.0

    DEFAULT_BETA = 1.0

    DEFAULT_CONFIDENCE_LEVEL = (
        CONFIDENCE_LEVEL_95
    )
