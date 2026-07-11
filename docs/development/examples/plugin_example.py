"""
Institutional Quant Platform
Production Reference Plugin

This file demonstrates the recommended plugin architecture
used throughout the platform.

Plugins extend functionality without modifying the core system.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


# ======================================================================
# Plugin Configuration
# ======================================================================

@dataclass(frozen=True)
class PluginConfig:
    """Plugin configuration."""

    name: str
    version: str
    author: str
    enabled: bool = True


# ======================================================================
# Plugin Result
# ======================================================================

@dataclass(slots=True)
class PluginResult:
    """Standard plugin execution result."""

    success: bool
    payload: Any | None = None
    message: str = ""


# ======================================================================
# Base Plugin
# ======================================================================

class BasePlugin(ABC):
    """
    Base class for every plugin.

    All plugins must inherit from this class.
    """

    def __init__(self, config: PluginConfig):
        self.config = config

    @property
    def name(self) -> str:
        return self.config.name

    @property
    def version(self) -> str:
        return self.config.version

    @abstractmethod
    def initialize(self) -> None:
        """Initialize resources."""

    @abstractmethod
    def execute(self, **kwargs: Any) -> PluginResult:
        """Execute plugin."""

    @abstractmethod
    def shutdown(self) -> None:
        """Release resources."""


# ======================================================================
# Plugin Registry
# ======================================================================

class PluginRegistry:
    """
    Central plugin registry.
    """

    def __init__(self):
        self._plugins: dict[str, BasePlugin] = {}

    def register(
        self,
        plugin: BasePlugin,
    ) -> None:

        logger.info(
            "Registering plugin: %s",
            plugin.name,
        )

        self._plugins[plugin.name] = plugin

    def unregister(
        self,
        name: str,
    ) -> None:

        if name in self._plugins:

            logger.info(
                "Removing plugin: %s",
                name,
            )

            self._plugins.pop(name)

    def get(
        self,
        name: str,
    ) -> BasePlugin:

        return self._plugins[name]

    def list_plugins(self) -> list[str]:

        return sorted(self._plugins.keys())


# ======================================================================
# Example Plugin
# ======================================================================

class AlphaScorePlugin(BasePlugin):
    """
    Example analytics plugin.
    """

    def initialize(self) -> None:

        logger.info(
            "%s initialized.",
            self.name,
        )

    def execute(
        self,
        **kwargs: Any,
    ) -> PluginResult:

        symbol = kwargs.get("symbol", "UNKNOWN")

        logger.info(
            "Calculating alpha score for %s",
            symbol,
        )

        score = 0.91

        return PluginResult(
            success=True,
            payload={
                "symbol": symbol,
                "alpha_score": score,
            },
            message="Alpha score calculated.",
        )

    def shutdown(self) -> None:

        logger.info(
            "%s shutdown.",
            self.name,
        )


# ======================================================================
# Plugin Manager
# ======================================================================

class PluginManager:
    """
    Executes registered plugins.
    """

    def __init__(
        self,
        registry: PluginRegistry,
    ):
        self.registry = registry

    def run(
        self,
        plugin_name: str,
        **kwargs: Any,
    ) -> PluginResult:

        plugin = self.registry.get(plugin_name)

        plugin.initialize()

        try:

            result = plugin.execute(**kwargs)

        finally:

            plugin.shutdown()

        return result


# ======================================================================
# Example Usage
# ======================================================================

def main() -> None:

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    registry = PluginRegistry()

    plugin = AlphaScorePlugin(
        PluginConfig(
            name="AlphaScore",
            version="1.0.0",
            author="Platform Team",
        )
    )

    registry.register(plugin)

    logger.info(
        "Available Plugins: %s",
        registry.list_plugins(),
    )

    manager = PluginManager(registry)

    result = manager.run(
        "AlphaScore",
        symbol="RELIANCE",
    )

    logger.info(result)


if __name__ == "__main__":
    main()