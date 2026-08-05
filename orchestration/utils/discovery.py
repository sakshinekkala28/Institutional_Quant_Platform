"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Discovery Utilities

Centralized discovery utilities.

Responsibilities
----------------
• Module discovery
• Class discovery
• Plugin discovery
• Engine discovery
• Pipeline discovery
• Adapter discovery

=========================================================
"""

from __future__ import annotations

import importlib
import inspect
import logging
import pkgutil
from pathlib import Path
from types import ModuleType
from typing import Any

logger = logging.getLogger(__name__)


# =========================================================
# DISCOVERY
# =========================================================


class Discovery:
    """
    Platform discovery utilities.
    """

    # =====================================================
    # MODULE
    # =====================================================

    @staticmethod
    def import_module(
        module_name: str,
    ) -> ModuleType:
        """
        Import module.
        """

        return importlib.import_module(module_name)

    # =====================================================
    # PACKAGE
    # =====================================================

    @staticmethod
    def discover_modules(
        package: str,
    ) -> list[str]:
        """
        Discover modules inside a package.
        """

        module = importlib.import_module(package)

        modules = []

        for info in pkgutil.iter_modules(module.__path__):
            modules.append(f"{package}.{info.name}")

        return sorted(modules)

    # =====================================================
    # CLASSES
    # =====================================================

    @staticmethod
    def discover_classes(
        module_name: str,
        *,
        base_class: type | None = None,
    ) -> list[type]:
        """
        Discover classes in module.
        """

        module = Discovery.import_module(module_name)

        classes = []

        for _, obj in inspect.getmembers(
            module,
            inspect.isclass,
        ):
            if obj.__module__ != module_name:
                continue

            if base_class is not None and not issubclass(
                obj,
                base_class,
            ):
                continue

            if obj is base_class:
                continue

            classes.append(obj)

        return classes

    # =====================================================
    # RECURSIVE
    # =====================================================

    @staticmethod
    def discover_package_classes(
        package: str,
        *,
        base_class: type | None = None,
    ) -> list[type]:
        """
        Discover classes recursively.
        """

        discovered = []

        for module in Discovery.discover_modules(package):
            discovered.extend(
                Discovery.discover_classes(
                    module,
                    base_class=base_class,
                )
            )

        return discovered

    # =====================================================
    # FILES
    # =====================================================

    @staticmethod
    def discover_files(
        directory: str | Path,
        pattern: str = "*.py",
    ) -> list[Path]:
        """
        Discover files.
        """

        return sorted(Path(directory).rglob(pattern))

    # =====================================================
    # FILTER
    # =====================================================

    @staticmethod
    def filter_by_attribute(
        objects: list[Any],
        attribute: str,
    ) -> list[Any]:
        """
        Filter objects that contain attribute.
        """

        return [
            obj
            for obj in objects
            if hasattr(
                obj,
                attribute,
            )
        ]

    # =====================================================
    # SUMMARY
    # =====================================================

    @staticmethod
    def summary(
        package: str,
    ) -> dict:
        """
        Package summary.
        """

        modules = Discovery.discover_modules(package)

        return {
            "package": package,
            "modules": len(modules),
            "names": modules,
        }

    # =====================================================
    # DUNDER
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return f"{self.__class__.__name__}()"
