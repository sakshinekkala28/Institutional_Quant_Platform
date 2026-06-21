# ==========================================================
# CONFIG MANAGER
# Institutional Configuration Framework
# ==========================================================

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml


# ==========================================================
# PORTFOLIO CONFIG
# ==========================================================

@dataclass
class PortfolioConfig:

    TARGET_HOLDINGS: int = 40

    MAX_POSITION_WEIGHT: float = 0.05

    MAX_SECTOR_WEIGHT: float = 0.30

    MIN_POSITION_WEIGHT: float = 0.0025


# ==========================================================
# RISK CONFIG
# ==========================================================

@dataclass
class RiskConfig:

    MAX_TRACKING_ERROR: float = 0.08

    MAX_HHI: float = 0.05

    MAX_BETA: float = 1.20

    MIN_BETA: float = 0.80

# ==========================================================
# EXECUTION CONFIG
# ==========================================================

@dataclass
class ExecutionConfig:

    MAX_PARTICIPATION_RATE: float = 0.10

    MAX_SLIPPAGE_BPS: float = 20

    MAX_MARKET_IMPACT_BPS: float = 30


# ==========================================================
# GOVERNANCE CONFIG
# ==========================================================

@dataclass
class GovernanceConfig:

    MAX_TURNOVER: float = 0.30

    MIN_EFFECTIVE_HOLDINGS: int = 20

    REQUIRE_APPROVAL: bool = True

# ==========================================================
# YAML LOADER
# ==========================================================

class YAMLLoader:

    @staticmethod
    def load_yaml(
        file_path
    ):

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            return yaml.safe_load(
                file
            )

    @staticmethod
    def save_yaml(
        data,
        file_path
    ):

        with open(
            file_path,
            "w",
            encoding="utf-8"
        ) as file:

            yaml.safe_dump(
                data,
                file,
                sort_keys=False
            )

        # ==========================================================
# CONFIG MANAGER
# ==========================================================

class ConfigManager:

    def __init__(self):

        self.root = Path.cwd()

        self.config_dir = (

            self.root

            / "config"
        )

        self.config_dir.mkdir(

            parents=True,

            exist_ok=True

        )

    def load(
        self,
        filename
    ):

        path = (

            self.config_dir

            / filename
        )

        return YAMLLoader.load_yaml(
            path
        )

    def save(
        self,
        filename,
        config_data
    ):

        path = (

            self.config_dir

            / filename
        )

        YAMLLoader.save_yaml(

            config_data,

            path

        )

    def exists(
        self,
        filename
    ):

        return (

            self.config_dir

            / filename

        ).exists()