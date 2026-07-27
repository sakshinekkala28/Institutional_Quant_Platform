"""
======================================================================
Institutional Quant Platform

Configuration Service

Author
------
Institutional Quant Platform

Purpose
-------
Enterprise configuration management service.

Responsibilities
----------------
* Central configuration access
* Runtime overrides
* Configuration validation
* Environment awareness
* Path resolution
* Immutable default settings
* Snapshot generation
* Service lifecycle management

This service wraps core.settings and becomes the single entry point
for configuration throughout the platform.
======================================================================
"""

from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
from threading import RLock
from typing import Any

from core.services.base_service import BaseService
from core.settings import settings

# ============================================================
# Exceptions
# ============================================================


class ConfigServiceError(Exception):
    """Base configuration exception."""


class ConfigurationNotFound(ConfigServiceError):
    """Raised when configuration section/key is missing."""


class ConfigurationValidationError(ConfigServiceError):
    """Raised when configuration validation fails."""


# ============================================================
# Config Service
# ============================================================


class ConfigService(BaseService):
    """
    Enterprise configuration service.

    Thread-safe singleton.

    Features
    --------
    • Configuration registry
    • Runtime overrides
    • Validation
    • Environment helpers
    • Snapshot support
    • Health checks
    """

    _instance: ConfigService | None = None

    _instance_lock = RLock()

    # --------------------------------------------------------

    def __new__(cls, *args, **kwargs):

        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)

        return cls._instance

    # --------------------------------------------------------

    def __init__(self) -> None:

        if getattr(self, "_initialized", False):
            return

        super().__init__()

        self._settings = settings

        self._runtime_overrides: dict[str, Any] = {}

        self._validators: dict[str, Any] = {}

        self._feature_flags: dict[str, bool] = {}

        self._lock = RLock()

        self._configuration_registry: dict[str, Any] = {}

        self._registered_sections: set[str] = set()

        self._initialized = True

        self._build_registry()

        self._register_default_validators()

        self._logger.info("Configuration service initialized.")

    # ========================================================
    # Registry
    # ========================================================

    def _build_registry(self) -> None:
        """
        Register all configuration sections.
        """

        registry = {
            "environment": self._settings.environment,
            "portfolio": self._settings.portfolio,
            "risk": self._settings.risk,
            "execution": self._settings.execution,
            "governance": self._settings.governance,
            "database": self._settings.database,
            "surveillance": self._settings.surveillance,
            "performance": self._settings.performance,
            "regime": self._settings.regime,
            "forecast": self._settings.forecast,
        }

        self._configuration_registry = registry

        self._registered_sections = set(registry.keys())

    # ========================================================
    # Validators
    # ========================================================

    def _register_default_validators(self) -> None:
        """
        Register validation handlers.
        """

        self._validators = {
            "portfolio": self._validate_portfolio,
            "risk": self._validate_risk,
            "execution": self._validate_execution,
            "governance": self._validate_governance,
            "database": self._validate_database,
            "environment": self._validate_environment,
        }

    # ========================================================
    # Registration API
    # ========================================================

    def register_validator(self, section: str, validator) -> None:
        """
        Register custom validator.
        """

        with self._lock:
            self._validators[section] = validator

    def register_feature_flag(self, name: str, enabled: bool) -> None:
        """
        Register feature flag.
        """

        with self._lock:
            self._feature_flags[name] = enabled

    def register_section(self, name: str, configuration: Any) -> None:
        """
        Register additional configuration section.
        """

        with self._lock:
            self._configuration_registry[name] = configuration

            self._registered_sections.add(name)

    # ========================================================
    # Runtime Overrides
    # ========================================================

    def set_runtime_override(self, key: str, value: Any) -> None:
        """
        Override a configuration value at runtime.
        """

        with self._lock:
            self._runtime_overrides[key] = value

            self._logger.info("Runtime override applied: %s", key)

    def clear_runtime_override(self, key: str) -> None:
        """
        Remove runtime override.
        """

        with self._lock:
            self._runtime_overrides.pop(key, None)

    def clear_all_runtime_overrides(self) -> None:
        """
        Remove every runtime override.
        """

        with self._lock:
            self._runtime_overrides.clear()

    # ========================================================
    # Metadata
    # ========================================================

    @property
    def sections(self) -> list[str]:

        return sorted(self._registered_sections)

    @property
    def runtime_overrides(self) -> dict[str, Any]:

        return deepcopy(self._runtime_overrides)

    @property
    def feature_flags(self) -> dict[str, bool]:

        return deepcopy(self._feature_flags)

    # ========================================================
    # Service Entry Point
    # ========================================================

    def run(self):
        """
        BaseService entry point.
        """

        return self.snapshot()

    # ========================================================
    # Configuration Lookup
    # ========================================================

    def get(self, section: str, key: str | None = None, default: Any = None) -> Any:
        """
        Retrieve a configuration value.

        Resolution Order
        ----------------
        1. Runtime Override
        2. Environment Variable
        3. core.settings
        4. Default
        """

        section = section.lower()

        if section not in self._configuration_registry:
            if default is not None:
                return default

            raise ConfigurationNotFound(f"Unknown configuration section '{section}'.")

        configuration = self._configuration_registry[section]

        if key is None:
            return configuration

        override_key = f"{section}.{key}"

        if override_key in self._runtime_overrides:
            return self._runtime_overrides[override_key]

        env_key = override_key.upper().replace(".", "_")

        env_value = os.getenv(env_key)

        if env_value is not None:
            return self._cast_environment_value(env_value)

        if hasattr(configuration, key):
            return getattr(configuration, key)

        if default is not None:
            return default

        raise ConfigurationNotFound(f"Configuration '{override_key}' not found.")

    # ========================================================
    # Exists
    # ========================================================

    def exists(self, section: str, key: str | None = None) -> bool:
        """
        Determine whether a configuration exists.
        """

        section = section.lower()

        if section not in self._configuration_registry:
            return False

        if key is None:
            return True

        configuration = self._configuration_registry[section]

        return hasattr(configuration, key)

    # ========================================================
    # Typed Section Accessors
    # ========================================================

    def get_environment(self):

        return self._configuration_registry["environment"]

    def get_portfolio(self):

        return self._configuration_registry["portfolio"]

    def get_risk(self):

        return self._configuration_registry["risk"]

    def get_execution(self):

        return self._configuration_registry["execution"]

    def get_governance(self):

        return self._configuration_registry["governance"]

    def get_database(self):

        return self._configuration_registry["database"]

    def get_surveillance(self):

        return self._configuration_registry["surveillance"]

    def get_performance(self):

        return self._configuration_registry["performance"]

    def get_regime(self):

        return self._configuration_registry["regime"]

    def get_forecast(self):

        return self._configuration_registry["forecast"]

    # ========================================================
    # Section Utilities
    # ========================================================

    def list_sections(self) -> list[str]:

        return sorted(self._registered_sections)

    def list_keys(self, section: str) -> list[str]:
        """
        List configuration keys.
        """

        configuration = self.get(section)

        return sorted(
            [
                attribute
                for attribute in vars(configuration)
                if not attribute.startswith("_")
            ]
        )

    # ========================================================
    # Environment Helpers
    # ========================================================

    def environment(self) -> str:

        return self.get("environment", "ENVIRONMENT")

    def is_production(self) -> bool:

        return self.environment().upper() == "PRODUCTION"

    def is_development(self) -> bool:

        return self.environment().upper() == "DEVELOPMENT"

    def is_testing(self) -> bool:

        return self.environment().upper() == "TESTING"

    def debug_enabled(self) -> bool:

        return bool(self.get("environment", "DEBUG"))

    # ========================================================
    # Feature Flags
    # ========================================================

    def feature_enabled(self, name: str) -> bool:
        """
        Determine whether a feature flag is enabled.
        """

        return bool(self._feature_flags.get(name, False))

    # ========================================================
    # Path Resolution
    # ========================================================

    def root_directory(self) -> Path:

        return self.get("environment", "ROOT_DIR")

    def resolve_path(self, *paths: str) -> Path:
        """
        Resolve a path relative to project root.
        """

        return self.root_directory().joinpath(*paths).resolve()

    def data_directory(self) -> Path:

        return self.resolve_path("data")

    def logs_directory(self) -> Path:

        return self.resolve_path("logs")

    def reports_directory(self) -> Path:

        return self.resolve_path("data", "reports")

    # ========================================================
    # Internal Helpers
    # ========================================================

    @staticmethod
    def _cast_environment_value(value: str) -> Any:
        """
        Convert environment variables into native types.
        """

        lowered = value.lower()

        if lowered in {"true", "false"}:
            return lowered == "true"

        try:
            return int(value)

        except ValueError:
            pass

        try:
            return float(value)

        except ValueError:
            pass

        return value

    # ========================================================
    # Validation
    # ========================================================

    def validate(self) -> bool:
        """
        Validate every registered configuration section.
        """

        for section, validator in self._validators.items():
            validator()

        self._logger.info("Configuration validation completed successfully.")

        return True

    def _validate_environment(self) -> None:

        environment = self.get_environment()

        if environment.ENVIRONMENT not in {
            "DEVELOPMENT",
            "TESTING",
            "UAT",
            "PRODUCTION",
        }:
            raise ConfigurationValidationError(
                f"Invalid environment '{environment.ENVIRONMENT}'."
            )

    def _validate_portfolio(self) -> None:

        portfolio = self.get_portfolio()

        if portfolio.MIN_POSITION_WEIGHT <= 0:
            raise ConfigurationValidationError(
                "Minimum position weight must be positive."
            )

        if portfolio.MAX_POSITION_WEIGHT <= portfolio.MIN_POSITION_WEIGHT:
            raise ConfigurationValidationError(
                "Maximum position weight must exceed minimum position weight."
            )

        if portfolio.TARGET_HOLDINGS <= 0:
            raise ConfigurationValidationError(
                "Target holdings must be greater than zero."
            )

    def _validate_risk(self) -> None:

        risk = self.get_risk()

        if risk.MIN_BETA >= risk.MAX_BETA:
            raise ConfigurationValidationError("MIN_BETA must be less than MAX_BETA.")

        if not (0.0 < risk.VAR_CONFIDENCE < 1.0):
            raise ConfigurationValidationError(
                "VAR_CONFIDENCE must be between 0 and 1."
            )

    def _validate_execution(self) -> None:

        execution = self.get_execution()

        if execution.MAX_PARTICIPATION_RATE <= 0:
            raise ConfigurationValidationError("Participation rate must be positive.")

    def _validate_governance(self) -> None:

        governance = self.get_governance()

        if governance.MAX_TURNOVER <= 0:
            raise ConfigurationValidationError("MAX_TURNOVER must be positive.")

    def _validate_database(self) -> None:

        database = self.get_database()

        if not database.DATABASE_NAME:
            raise ConfigurationValidationError("Database name cannot be empty.")

    # ========================================================
    # Snapshot
    # ========================================================

    def snapshot(self) -> dict[str, Any]:
        """
        Return a complete immutable configuration snapshot.
        """

        snapshot = {}

        for section in self.list_sections():
            configuration = self.get(section)

            snapshot[section] = vars(configuration).copy()

        snapshot["runtime_overrides"] = deepcopy(self._runtime_overrides)

        snapshot["feature_flags"] = deepcopy(self._feature_flags)

        return snapshot

    # ========================================================
    # Export
    # ========================================================

    def export_json(self, output_file: Path) -> Path:
        """
        Export configuration snapshot to JSON.
        """

        output_file.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with output_file.open("w", encoding="utf-8") as handle:
            json.dump(
                self.snapshot(),
                handle,
                indent=4,
                default=str,
            )

        self._logger.info(
            "Configuration exported to %s",
            output_file,
        )

        return output_file

    # ========================================================
    # Reload
    # ========================================================

    def reload(self) -> None:
        """
        Reload configuration registry.
        """

        with self._lock:
            self._build_registry()

            self.validate()

            self._logger.info("Configuration registry reloaded.")

    def reset(self) -> None:
        """
        Clear runtime state.
        """

        with self._lock:
            self._runtime_overrides.clear()

            self._feature_flags.clear()

            self._logger.info("Runtime configuration reset.")

    # ========================================================
    # Health
    # ========================================================

    def health(self) -> dict[str, Any]:
        """
        Configuration service health report.
        """

        try:
            self.validate()

            status = "HEALTHY"

        except Exception as exc:
            status = "FAILED"

            return {
                "status": status,
                "error": str(exc),
            }

        return {
            "status": status,
            "environment": self.environment(),
            "registered_sections": len(self._registered_sections),
            "runtime_overrides": len(self._runtime_overrides),
            "feature_flags": len(self._feature_flags),
        }

    # ========================================================
    # Diagnostics
    # ========================================================

    def statistics(self) -> dict[str, Any]:
        """
        Service statistics.
        """

        return {
            "service": self.__class__.__name__,
            "sections": self.list_sections(),
            "section_count": len(self._registered_sections),
            "validator_count": len(self._validators),
            "runtime_override_count": len(self._runtime_overrides),
            "feature_flag_count": len(self._feature_flags),
        }

    # ========================================================
    # Magic Methods
    # ========================================================

    def __contains__(self, section: str) -> bool:

        return self.exists(section)

    def __len__(self) -> int:

        return len(self._registered_sections)

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(environment='{self.environment()}', "
            f"sections={len(self)})"
        )


# ============================================================
# Global Singleton
# ============================================================

config_service = ConfigService()
