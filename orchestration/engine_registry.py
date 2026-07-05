"""
Institutional Quant Platform
============================

Engine Registry

Automatically discovers every engine that inherits from BaseEngine.

Author: Institutional Quant Platform
"""

from __future__ import annotations

import importlib
import inspect
import logging
import pkgutil
from pathlib import Path
from typing import Dict, List, Optional, Type

from orchestration.base_engine import BaseEngine


logger = logging.getLogger(__name__)


class EngineRegistry:
    """
    Automatically discovers and manages all engines.
    """

    DEFAULT_PACKAGES = [
        "analytics",
        "alpha",
        "automation",
        "backtesting",
    ]

    def __init__(self):

        self._engines: Dict[str, Type[BaseEngine]] = {}

    # ------------------------------------------------------------------

    def discover(
        self,
        packages: Optional[List[str]] = None,
    ) -> None:
        """
        Discover all engines inside the supplied packages.
        """

        packages = packages or self.DEFAULT_PACKAGES

        for package in packages:

            self._discover_package(package)

        logger.info("Discovered %d engines.", len(self._engines))

    # ------------------------------------------------------------------

    def _discover_package(self, package_name: str):

        try:

            package = importlib.import_module(package_name)

        except Exception as exc:

            logger.warning(
                "Unable to import package %s : %s",
                package_name,
                exc,
            )
            return

        if not hasattr(package, "__path__"):
            return

        for _, module_name, _ in pkgutil.walk_packages(
            package.__path__,
            package.__name__ + ".",
        ):

            try:

                module = importlib.import_module(module_name)

            except Exception as exc:

                logger.warning(
                    "Skipping module %s (%s)",
                    module_name,
                    exc,
                )
                continue

            self._register_module(module)

    # ------------------------------------------------------------------

    def _register_module(self, module):

        for _, obj in inspect.getmembers(module, inspect.isclass):

            if not issubclass(obj, BaseEngine):
                continue

            if obj is BaseEngine:
                continue

            if not obj.ENABLED:
                continue

            if obj.NAME in self._engines:

                raise ValueError(
                    f"Duplicate engine name detected: {obj.NAME}"
                )

            self._engines[obj.NAME] = obj

            logger.info(
                "Registered engine: %s",
                obj.NAME,
            )

    # ------------------------------------------------------------------

    def names(self) -> List[str]:

        return sorted(self._engines.keys())

    # ------------------------------------------------------------------

    def classes(self) -> List[Type[BaseEngine]]:

        return list(self._engines.values())

    # ------------------------------------------------------------------

    def create(self, name: str) -> BaseEngine:

        if name not in self._engines:

            raise KeyError(
                f"Unknown engine '{name}'"
            )

        return self._engines[name]()

    # ------------------------------------------------------------------

    def metadata(self):

        return {
            name: engine.metadata()
            for name, engine in self._engines.items()
        }

    # ------------------------------------------------------------------

    def by_stage(self):

        grouped = {}

        for engine in self._engines.values():

            grouped.setdefault(
                engine.STAGE,
                [],
            ).append(engine)

        return grouped

    # ------------------------------------------------------------------

    def outputs(self):

        outputs = {}

        for engine in self._engines.values():

            outputs[engine.NAME] = engine.OUTPUTS

        return outputs

    # ------------------------------------------------------------------

    def dependencies(self):

        deps = {}

        for engine in self._engines.values():

            deps[engine.NAME] = engine.DEPENDS_ON

        return deps

    # ------------------------------------------------------------------

    def __len__(self):

        return len(self._engines)

    # ------------------------------------------------------------------

    def __contains__(self, item):

        return item in self._engines

    # ------------------------------------------------------------------

    def __iter__(self):

        return iter(self._engines.values())

    # ------------------------------------------------------------------

    def summary(self):

        print("=" * 80)
        print("ENGINE REGISTRY")
        print("=" * 80)

        for stage, engines in sorted(self.by_stage().items()):

            print(f"\n[{stage}]")

            for engine in sorted(
                engines,
                key=lambda e: e.NAME,
            ):

                print(f"  • {engine.NAME}")

        print()
        print(f"Total Engines : {len(self)}")
        print("=" * 80)


# ----------------------------------------------------------------------


_registry: Optional[EngineRegistry] = None


def get_registry() -> EngineRegistry:
    """
    Singleton registry.
    """

    global _registry

    if _registry is None:

        _registry = EngineRegistry()

        _registry.discover()

    return _registry