"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Configuration Loader

Central configuration service.

Responsibilities
----------------
• Load configuration files
• Environment variable overrides
• Runtime overrides
• Nested configuration lookup
• Configuration validation

Supported Formats
-----------------
• JSON
• YAML
• Environment Variables

=========================================================
"""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any

try:
    import yaml

except ImportError:
    yaml = None

logger = logging.getLogger(__name__)


# =========================================================
# CONFIG LOADER
# =========================================================


class ConfigLoader:
    """
    Platform configuration manager.
    """

    def __init__(self) -> None:

        self._config: dict[
            str,
            Any,
        ] = {}

    # =====================================================
    # LOAD JSON
    # =====================================================

    def load_json(
        self,
        path: str | Path,
    ) -> None:

        path = Path(path)

        with path.open(
            "r",
            encoding="utf-8",
        ) as fp:
            self._config.update(json.load(fp))

    # =====================================================
    # LOAD YAML
    # =====================================================

    def load_yaml(
        self,
        path: str | Path,
    ) -> None:

        if yaml is None:
            raise RuntimeError("PyYAML not installed.")

        path = Path(path)

        with path.open(
            "r",
            encoding="utf-8",
        ) as fp:
            self._config.update(yaml.safe_load(fp))

    # =====================================================
    # ENVIRONMENT
    # =====================================================

    def load_environment(
        self,
        prefix: str = "IQP_",
    ) -> None:

        for key, value in os.environ.items():
            if key.startswith(prefix):
                self._config[key[len(prefix) :].lower()] = value

    # =====================================================
    # ACCESS
    # =====================================================

    def get(
        self,
        key: str,
        default: Any = None,
    ) -> Any:

        return self._config.get(
            key,
            default,
        )

    # -----------------------------------------------------

    def set(
        self,
        key: str,
        value: Any,
    ) -> None:

        self._config[key] = value

    # -----------------------------------------------------

    def update(
        self,
        values: dict[
            str,
            Any,
        ],
    ) -> None:

        self._config.update(values)

    # =====================================================
    # VALIDATION
    # =====================================================

    def require(
        self,
        *keys: str,
    ) -> None:

        missing = [key for key in keys if key not in self._config]

        if missing:
            raise KeyError(f"Missing configuration: {missing}")

    # =====================================================
    # EXPORT
    # =====================================================

    def to_dict(
        self,
    ) -> dict[str, Any]:

        return dict(self._config)

    # -----------------------------------------------------

    def save_json(
        self,
        path: str | Path,
    ) -> None:

        path = Path(path)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with path.open(
            "w",
            encoding="utf-8",
        ) as fp:
            json.dump(
                self._config,
                fp,
                indent=4,
            )

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(
        self,
    ) -> dict:

        return {
            "entries": len(
                self._config,
            ),
            "keys": sorted(self._config.keys()),
        }

    # =====================================================
    # DUNDER
    # =====================================================

    def __contains__(
        self,
        key: str,
    ) -> bool:

        return key in self._config

    # -----------------------------------------------------

    def __len__(
        self,
    ) -> int:

        return len(self._config)

    # -----------------------------------------------------

    def __repr__(
        self,
    ) -> str:

        return f"{self.__class__.__name__}(entries={len(self)})"
