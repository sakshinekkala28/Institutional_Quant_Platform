"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Service Container

Dependency Injection (DI) container for the platform.

Responsibilities
----------------
• Service registration
• Lazy singleton creation
• Dependency resolution
• Service lookup
• Lifecycle management

=========================================================
"""

from __future__ import annotations

from collections.abc import Callable
import logging
from typing import Any

logger = logging.getLogger(__name__)


# =========================================================
# SERVICE CONTAINER
# =========================================================


class ServiceContainer:
    """
    Central dependency injection container.
    """

    def __init__(self) -> None:

        self._factories: dict[
            str,
            Callable[[], Any],
        ] = {}

        self._instances: dict[
            str,
            Any,
        ] = {}

    # =====================================================
    # REGISTRATION
    # =====================================================

    def register(
        self,
        name: str,
        factory: Callable[[], Any],
    ) -> None:
        """
        Register lazy singleton.
        """

        if name in self._factories:
            raise ValueError(f"Service '{name}' already registered.")

        self._factories[name] = factory

    # -----------------------------------------------------

    def register_instance(
        self,
        name: str,
        instance: Any,
    ) -> None:
        """
        Register existing instance.
        """

        self._instances[name] = instance

    # =====================================================
    # RESOLUTION
    # =====================================================

    def resolve(
        self,
        name: str,
    ) -> Any:
        """
        Resolve service.
        """

        if name in self._instances:
            return self._instances[name]

        if name not in self._factories:
            raise KeyError(f"Unknown service '{name}'.")

        instance = self._factories[name]()

        self._instances[name] = instance

        return instance

    # =====================================================
    # QUERIES
    # =====================================================

    def exists(
        self,
        name: str,
    ) -> bool:

        return name in self._instances or name in self._factories

    # -----------------------------------------------------

    def registered_services(
        self,
    ) -> list[str]:

        return sorted(self._factories.keys())

    # -----------------------------------------------------

    def active_services(
        self,
    ) -> list[str]:

        return sorted(self._instances.keys())

    # =====================================================
    # REMOVAL
    # =====================================================

    def unregister(
        self,
        name: str,
    ) -> None:

        self._instances.pop(
            name,
            None,
        )

        self._factories.pop(
            name,
            None,
        )

    # =====================================================
    # RESET
    # =====================================================

    def clear(
        self,
    ) -> None:

        self._instances.clear()

        self._factories.clear()

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(
        self,
    ) -> dict:

        return {
            "registered": len(
                self._factories,
            ),
            "active": len(
                self._instances,
            ),
            "services": self.registered_services(),
        }

    # =====================================================
    # DUNDER
    # =====================================================

    def __contains__(
        self,
        name: str,
    ) -> bool:

        return self.exists(name)

    # -----------------------------------------------------

    def __len__(
        self,
    ) -> int:

        return len(self._factories)

    # -----------------------------------------------------

    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}("
            f"registered={len(self._factories)}, "
            f"active={len(self._instances)})"
        )
