# ==========================================================
# SETTINGS
# Institutional Configuration Framework
# ==========================================================

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

# ==========================================================
# ENVIRONMENT
# ==========================================================

@dataclass(frozen=True)
class EnvironmentSettings:

    ENVIRONMENT: str = "PRODUCTION"

    DEBUG: bool = False

    VERSION: str = "2.0.0"

    PROJECT_NAME: str = (
        "Institutional Quant Platform"
    )

    ROOT_DIR: Path = (
        Path.cwd()
    )

# ==========================================================
# PORTFOLIO SETTINGS
# ==========================================================

@dataclass(frozen=True)
class PortfolioSettings:

    PORTFOLIO_NAV: float = (
        100_000_000.0
    )

    AUM_SCENARIOS: tuple = (

        100_000_000.0,

        500_000_000.0,

        1_000_000_000.0,

        5_000_000_000.0,

        10_000_000_000.0

    )

    BENCHMARK: str = (
        "NIFTY500"
    )

    TARGET_HOLDINGS: int = 25

    MIN_POSITION_WEIGHT: float = 0.0025

    MAX_POSITION_WEIGHT: float = 0.05

    MAX_SECTOR_WEIGHT: float = 0.30

    MAX_SINGLE_STOCK_ADV: float = 0.05

    REBALANCE_FREQUENCY: str = "WEEKLY"

# ==========================================================
# RISK SETTINGS
# ==========================================================

@dataclass(frozen=True)
class RiskSettings:

    MAX_TRACKING_ERROR: float = 0.08

    MAX_HHI: float = 0.05

    MAX_BETA: float = 1.20

    MIN_BETA: float = 0.80

    VAR_CONFIDENCE: float = 0.95

# ==========================================================
# EXECUTION SETTINGS
# ==========================================================

@dataclass(frozen=True)
class ExecutionSettings:

    MAX_PARTICIPATION_RATE: float = 0.10

    MAX_SLIPPAGE_BPS: float = 20

    MAX_MARKET_IMPACT_BPS: float = 30


# ==========================================================
# GOVERNANCE SETTINGS
# ==========================================================

@dataclass(frozen=True)
class GovernanceSettings:

    MAX_TURNOVER: float = 0.30

    MIN_EFFECTIVE_HOLDINGS: int = 20

    REQUIRE_APPROVAL: bool = True


# ==========================================================
# DATABASE SETTINGS
# ==========================================================

@dataclass(frozen=True)
class DatabaseSettings:

    DATABASE_NAME: str = (
        "institutional_quant.db"
    )

    DATABASE_SCHEMA: str = "main"

# ==========================================================
# SURVEILLANCE SETTINGS
# ==========================================================

@dataclass(frozen=True)

class SurveillanceSettings:

    MIN_SHARPE: float = 0.75

    MIN_INFORMATION_RATIO: float = 0.50

    MIN_ALPHA: float = 0.00

    MIN_HIT_RATIO: float = 0.50

    MAX_VAR95: float = 0.03

    MAX_CVAR95: float = 0.05

    CRITICAL_DRAWDOWN: float = 0.50

    WARNING_DRAWDOWN: float = 0.35

    MAX_TRACKING_ERROR: float = 0.20

    MIN_REGIME_SCORE: float = 50.0

    MIN_ROLLING_SCORE: float = 50.0

@dataclass(frozen=True)
class PerformanceSettings:

    TRADING_DAYS: int = 252

    RISK_FREE_RATE: float = 0.06

    ROLLING_WINDOW: int = 63

    MIN_HISTORY_DAYS: int = 252

@dataclass(frozen=True)
class RegimeSettings:

    BULL_THRESHOLD: float = 0.15

    BEAR_THRESHOLD: float = -0.15

    MIN_REGIME_DAYS: int = 20

    MIN_REGIME_SCORE: float = 50.0

@dataclass(frozen=True)
class ForecastSettings:

    FORECAST_HORIZON_1M: int = 21

    FORECAST_HORIZON_3M: int = 63

    FORECAST_HORIZON_12M: int = 252

    RETURN_WEIGHT_ROLLING: float = 0.40

    RETURN_WEIGHT_REGIME: float = 0.30

    RETURN_WEIGHT_HISTORICAL: float = 0.20

    RETURN_WEIGHT_ALPHA: float = 0.10

    VOL_WEIGHT_ROLLING: float = 0.70

    VOL_WEIGHT_REGIME: float = 0.30

# ==========================================================
# SETTINGS CONTAINER
# ==========================================================

class Settings:

    def __init__(self):

        self.environment = (
            EnvironmentSettings()
        )

        self.portfolio = (
            PortfolioSettings()
        )

        self.risk = (
            RiskSettings()
        )

        self.execution = (
            ExecutionSettings()
        )  

        self.governance = (
            GovernanceSettings()
        )

        self.database = (
            DatabaseSettings()
        )

        self.surveillance = (
            SurveillanceSettings()
        )

        self.performance = (
            PerformanceSettings()
        )

        self.regime = (
            RegimeSettings()
        ) 

        self.forecast = (
            ForecastSettings()
        )

# ==========================================================
# GLOBAL SETTINGS
# ==========================================================

settings = Settings()