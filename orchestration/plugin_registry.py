"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Plugin Registry

Central registry for orchestration plugins.

Responsibilities
----------------
• Plugin registration
• Plugin discovery
• Plugin lookup
• Enable / Disable plugins
• Lifecycle management

=========================================================
"""

from __future__ import annotations

import inspect
from collections.abc import Iterator

from orchestration.plugins.base_plugin import BasePlugin

# =========================================================
# PLUGIN REGISTRY
# =========================================================


class PluginRegistry:
    """
    Registry for orchestration plugins.
    """

    def __init__(self) -> None:

        self._plugins: dict[
            str,
            BasePlugin,
        ] = {}

    # =====================================================
    # REGISTRATION
    # =====================================================

    def register(
        self,
        plugin: BasePlugin,
    ) -> None:
        """
        Register plugin instance.
        """

        name = plugin.NAME.lower()

        if name in self._plugins:
            raise ValueError(f"Plugin '{plugin.NAME}' already registered.")

        self._plugins[name] = plugin

    # -----------------------------------------------------

    def unregister(
        self,
        name: str,
    ) -> None:
        """
        Remove plugin.
        """

        self._plugins.pop(
            name.lower(),
            None,
        )

    # =====================================================
    # LOOKUP
    # =====================================================

    def get(
        self,
        name: str,
    ) -> BasePlugin:
        """
        Retrieve plugin.
        """

        return self._plugins[name.lower()]

    # -----------------------------------------------------

    def exists(
        self,
        name: str,
    ) -> bool:

        return name.lower() in self._plugins

    # =====================================================
    # DISCOVERY
    # =====================================================

    def discover(
        self,
        module,
    ) -> None:
        """
        Automatically register plugins
        from a module.
        """

        for _, cls in inspect.getmembers(
            module,
            inspect.isclass,
        ):
            if not issubclass(
                cls,
                BasePlugin,
            ):
                continue

            if cls is BasePlugin:
                continue

            if not cls.ENABLED:
                continue

            self.register(cls())

    # =====================================================
    # LIFECYCLE
    # =====================================================

    def initialize_all(
        self,
    ) -> None:

        for plugin in self.enabled_plugins():
            plugin.initialize()

    # -----------------------------------------------------

    def shutdown_all(
        self,
    ) -> None:

        for plugin in self.enabled_plugins():
            plugin.shutdown()

    # =====================================================
    # ENABLE / DISABLE
    # =====================================================

    def enable(
        self,
        name: str,
    ) -> None:

        self.get(name).ENABLED = True

    # -----------------------------------------------------

    def disable(
        self,
        name: str,
    ) -> None:

        self.get(name).ENABLED = False

    # =====================================================
    # QUERIES
    # =====================================================

    def plugins(
        self,
    ) -> list[BasePlugin]:

        return list(self._plugins.values())

    # -----------------------------------------------------

    def enabled_plugins(
        self,
    ) -> list[BasePlugin]:

        return [plugin for plugin in self._plugins.values() if plugin.ENABLED]

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(
        self,
    ) -> dict:

        return {
            "registered": len(
                self._plugins,
            ),
            "enabled": len(
                self.enabled_plugins(),
            ),
            "plugins": [plugin.NAME for plugin in self.plugins()],
        }

    # =====================================================
    # DUNDER
    # =====================================================

    def __len__(
        self,
    ) -> int:

        return len(self._plugins)

    # -----------------------------------------------------

    def __contains__(
        self,
        name: str,
    ) -> bool:

        return self.exists(name)

    # -----------------------------------------------------

    def __iter__(
        self,
    ) -> Iterator[BasePlugin]:

        return iter(self._plugins.values())

    # -----------------------------------------------------

    def __repr__(
        self,
    ) -> str:

        return f"{self.__class__.__name__}(plugins={len(self)})"
