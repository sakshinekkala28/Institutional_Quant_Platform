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

    TARGET_HOLDINGS: int = 40

    MIN_POSITION_WEIGHT: float = 0.0025

    MAX_POSITION_WEIGHT: float = 0.05

    MAX_SECTOR_WEIGHT: float = 0.30

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


# ==========================================================
# GLOBAL SETTINGS
# ==========================================================

settings = Settings()