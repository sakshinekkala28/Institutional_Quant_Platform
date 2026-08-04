"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Adapter Factory

Creates and manages platform adapters.

Responsibilities
----------------
• Adapter registration
• Adapter discovery
• Adapter creation
• Backend abstraction
• Dependency injection

Supported Backends
------------------
• CSV
• Parquet
• DuckDB
• SQLite
• PostgreSQL
• REST APIs
• Custom adapters

=========================================================
"""

from __future__ import annotations

from orchestration.adapters.base_adapter import BaseAdapter

# =========================================================
# ADAPTER FACTORY
# =========================================================


class AdapterFactory:
    """
    Factory for platform adapters.
    """

    _registry: dict[
        str,
        type[BaseAdapter],
    ] = {}

    # =====================================================
    # REGISTER
    # =====================================================

    @classmethod
    def register(
        cls,
        name: str,
        adapter: type[BaseAdapter],
    ) -> None:

        cls._registry[name.lower()] = adapter

    # =====================================================
    # CREATE
    # =====================================================

    @classmethod
    def create(
        cls,
        name: str,
        **kwargs,
    ) -> BaseAdapter:

        key = name.lower()

        if key not in cls._registry:
            raise KeyError(f"Unknown adapter '{name}'.")

        return cls._registry[key](**kwargs)

    # =====================================================
    # DISCOVERY
    # =====================================================

    @classmethod
    def registered(
        cls,
    ) -> list[str]:

        return sorted(cls._registry.keys())

    # =====================================================
    # EXISTS
    # =====================================================

    @classmethod
    def exists(
        cls,
        name: str,
    ) -> bool:

        return name.lower() in cls._registry

    # =====================================================
    # REMOVE
    # =====================================================

    @classmethod
    def unregister(
        cls,
        name: str,
    ) -> None:

        cls._registry.pop(
            name.lower(),
            None,
        )

    # =====================================================
    # CLEAR
    # =====================================================

    @classmethod
    def clear(
        cls,
    ) -> None:

        cls._registry.clear()

    # =====================================================
    # SUMMARY
    # =====================================================

    @classmethod
    def summary(
        cls,
    ) -> dict:

        return {
            "registered": len(cls._registry),
            "adapters": cls.registered(),
        }

    # =====================================================
    # DUNDER
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return f"{self.__class__.__name__}(registered={len(self._registry)})"
