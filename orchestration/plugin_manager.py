"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Plugin Manager

Central coordinator for the orchestration plugin system.

Responsibilities
----------------
• Plugin registration
• Plugin lifecycle
• Event dispatch
• Hook execution
• Plugin discovery

Architecture
------------
MasterOrchestrator
        │
        ▼
    PluginManager
        │
 ┌──────┼──────────────┐
 ▼      ▼              ▼
Registry EventBus  HookManager

=========================================================
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from orchestration.events.event_bus import (
    EventBus,
)
from orchestration.hook_manager import (
    HookManager,
)
from orchestration.plugin_registry import (
    PluginRegistry,
)
from orchestration.plugins.base_plugin import (
    BasePlugin,
)

# =========================================================
# PLUGIN MANAGER
# =========================================================


class PluginManager:
    """
    Central orchestration plugin manager.
    """

    def __init__(
        self,
    ) -> None:

        self.registry = PluginRegistry()

        self.events = EventBus()

        self.hooks = HookManager()

    # =====================================================
    # REGISTRATION
    # =====================================================

    def register(
        self,
        plugin: BasePlugin,
    ) -> None:
        """
        Register plugin.
        """

        self.registry.register(plugin)

    # -----------------------------------------------------

    def register_many(
        self,
        plugins: Iterable[BasePlugin],
    ) -> None:

        for plugin in plugins:
            self.register(plugin)

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def initialize(
        self,
    ) -> None:

        self.registry.initialize_all()

    # -----------------------------------------------------

    def shutdown(
        self,
    ) -> None:

        self.registry.shutdown_all()

    # =====================================================
    # EVENTS
    # =====================================================

    def publish(
        self,
        event: str,
        **payload: Any,
    ) -> None:

        self.events.publish(
            event,
            **payload,
        )

    # =====================================================
    # HOOKS
    # =====================================================

    def execute_hook(
        self,
        hook: str,
        **payload: Any,
    ) -> None:

        self.hooks.execute(
            hook,
            **payload,
        )

    # =====================================================
    # DISCOVERY
    # =====================================================

    def discover(
        self,
        module,
    ) -> None:

        self.registry.discover(module)

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(
        self,
    ) -> dict:

        return {
            "plugins": len(
                self.registry,
            ),
            "events": len(
                self.events,
            ),
            "hooks": len(
                self.hooks,
            ),
        }

    # =====================================================
    # DUNDER
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}("
            f"plugins={len(self.registry)}, "
            f"events={len(self.events)}, "
            f"hooks={len(self.hooks)})"
        )
