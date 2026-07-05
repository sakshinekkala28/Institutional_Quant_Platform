"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Engine Registry

Central registry responsible for discovering,
registering, validating and creating platform engines.

Responsibilities

• Engine Registration
• Automatic Discovery
• Dependency Validation
• Factory Creation
• Metadata Aggregation
• Category/Stage Indexing
• Runtime Queries
• Registry Reporting

=========================================================
"""

from __future__ import annotations

import importlib
import inspect
import logging
import pkgutil

from collections import defaultdict
from typing import Dict
from typing import List
from typing import Optional
from typing import Type
from typing import Iterable

from orchestration.base_engine import BaseEngine

logger = logging.getLogger(__name__)


class EngineRegistry:
    """
    Central registry for every engine available
    in the platform.

    Engines may be

    • Registered manually

    • Automatically discovered

    • Created on demand

    • Validated

    • Queried

    • Grouped by category,
      stage or tags.
    """

    # =====================================================
    # DEFAULT SEARCH LOCATIONS
    # =====================================================

    DEFAULT_PACKAGES = [

        "analytics",

        "alpha",

        "backtesting",

        "execution",

        "portfolio",

        "reporting",

        "research",

        "risk",

    ]

    # =====================================================
    # CONSTRUCTOR
    # =====================================================

    def __init__(self) -> None:

        # ---------------------------------------------
        # Primary registry
        # ---------------------------------------------

        self._engines: Dict[
            str,
            Type[BaseEngine],
        ] = {}

        # ---------------------------------------------
        # Secondary indexes
        # ---------------------------------------------

        self._categories = defaultdict(list)

        self._stages = defaultdict(list)

        self._tags = defaultdict(list)

        # ---------------------------------------------
        # Discovery status
        # ---------------------------------------------

        self._packages_scanned = []

        self._modules_scanned = []

        self._discovery_complete = False

    # =====================================================
    # BASIC INFORMATION
    # =====================================================

    @property
    def engine_count(self) -> int:

        return len(self._engines)

    @property
    def categories(self) -> List[str]:

        return sorted(

            self._categories.keys()

        )

    @property
    def stages(self) -> List[str]:

        return sorted(

            self._stages.keys()

        )

    @property
    def tags(self) -> List[str]:

        return sorted(

            self._tags.keys()

        )

    # =====================================================
    # REGISTRATION
    # =====================================================

    def register(
        self,
        engine: Type[BaseEngine],
    ) -> None:
        """
        Register an engine class.
        """

        if not issubclass(
            engine,
            BaseEngine,
        ):

            raise TypeError(

                f"{engine} is not "
                f"a BaseEngine."

            )

        if engine is BaseEngine:

            return

        if not engine.ENABLED:

            logger.info(

                "Skipping disabled engine: %s",

                engine.NAME,

            )

            return

        if engine.NAME in self._engines:

            raise ValueError(

                f"Duplicate engine "
                f"'{engine.NAME}'."

            )

        # ---------------------------------------------
        # Register
        # ---------------------------------------------

        self._engines[
            engine.NAME
        ] = engine

        # ---------------------------------------------
        # Build indexes
        # ---------------------------------------------

        self._categories[
            engine.CATEGORY
        ].append(engine)

        self._stages[
            engine.STAGE
        ].append(engine)

        for tag in engine.TAGS:

            self._tags[tag].append(
                engine
            )

        logger.info(

            "Registered engine: %s",

            engine.NAME,

        )

    # =====================================================
    # UNREGISTER
    # =====================================================

    def unregister(
        self,
        engine_name: str,
    ) -> None:
        """
        Remove an engine from the registry.
        """

        if engine_name not in self._engines:

            raise KeyError(

                f"Unknown engine "
                f"'{engine_name}'."

            )

        engine = self._engines.pop(
            engine_name
        )

        # ---------------------------------------------
        # Remove from category index
        # ---------------------------------------------

        if (
            engine.CATEGORY
            in self._categories
        ):

            self._categories[
                engine.CATEGORY
            ] = [

                cls

                for cls

                in self._categories[
                    engine.CATEGORY
                ]

                if cls.NAME != engine_name

            ]

            if not self._categories[
                engine.CATEGORY
            ]:

                del self._categories[
                    engine.CATEGORY
                ]

        # ---------------------------------------------
        # Remove from stage index
        # ---------------------------------------------

        if (
            engine.STAGE
            in self._stages
        ):

            self._stages[
                engine.STAGE
            ] = [

                cls

                for cls

                in self._stages[
                    engine.STAGE
                ]

                if cls.NAME != engine_name

            ]

            if not self._stages[
                engine.STAGE
            ]:

                del self._stages[
                    engine.STAGE
                ]

        # ---------------------------------------------
        # Remove tag index
        # ---------------------------------------------

        for tag in engine.TAGS:

            if tag not in self._tags:

                continue

            self._tags[tag] = [

                cls

                for cls

                in self._tags[tag]

                if cls.NAME != engine_name

            ]

            if not self._tags[tag]:

                del self._tags[tag]

        logger.info(

            "Unregistered engine: %s",

            engine_name,

        )

    # =====================================================
    # DISCOVERY
    # =====================================================

    def discover(
        self,
        packages: Optional[
            Iterable[str]
        ] = None,
    ) -> None:
        """
        Discover all BaseEngine implementations.
        """

        packages = list(
            packages
            or self.DEFAULT_PACKAGES
        )

        logger.info(

            "Starting engine discovery."

        )

        for package in packages:

            self._discover_package(
                package
            )

        self._discovery_complete = True

        logger.info(

            "Engine discovery complete."

        )

        logger.info(

            "Packages Scanned : %s",

            len(
                self._packages_scanned
            ),

        )

        logger.info(

            "Modules Scanned : %s",

            len(
                self._modules_scanned
            ),

        )

        logger.info(

            "Registered Engines : %s",

            self.engine_count,

        )

    # =====================================================
    # PACKAGE DISCOVERY
    # =====================================================

    def _discover_package(
        self,
        package_name: str,
    ) -> None:
        """
        Discover all engines inside
        a Python package.
        """

        try:

            package = importlib.import_module(
                package_name
            )

        except Exception as exc:

            logger.warning(

                "Unable to import "
                "%s (%s)",

                package_name,

                exc,

            )

            return

        self._packages_scanned.append(
            package_name
        )

        if not hasattr(
            package,
            "__path__",
        ):

            return

        for (
            _,
            module_name,
            _,
        ) in pkgutil.walk_packages(

            package.__path__,

            package.__name__ + ".",

        ):

            self._discover_module(
                module_name
            )

    # =====================================================
    # MODULE DISCOVERY
    # =====================================================

    def _discover_module(
        self,
        module_name: str,
    ) -> None:
        """
        Import and inspect
        a module.
        """

        try:

            module = importlib.import_module(
                module_name
            )

        except Exception as exc:

            logger.warning(

                "Skipping module %s (%s)",

                module_name,

                exc,

            )

            return

        self._modules_scanned.append(
            module_name
        )

        self._register_module(
            module
        )

    # =====================================================
    # MODULE REGISTRATION
    # =====================================================

    def _register_module(
        self,
        module,
    ) -> None:
        """
        Register every BaseEngine
        found inside a module.
        """

        for (
            _,
            obj,
        ) in inspect.getmembers(

            module,

            inspect.isclass,

        ):

            if obj is BaseEngine:

                continue

            if not issubclass(
                obj,
                BaseEngine,
            ):

                continue

            self.register(obj)

    # =====================================================
    # LOOKUP
    # =====================================================

    def exists(
        self,
        engine_name: str,
    ) -> bool:
        """
        Return True if an engine exists.
        """

        return engine_name in self._engines

    # -----------------------------------------------------

    def get(
        self,
        engine_name: str,
    ) -> Type[BaseEngine]:
        """
        Return the registered engine class.
        """

        if not self.exists(
            engine_name
        ):

            raise KeyError(

                f"Unknown engine "
                f"'{engine_name}'."

            )

        return self._engines[
            engine_name
        ]

    # -----------------------------------------------------

    def create(
        self,
        engine_name: str,
    ) -> BaseEngine:
        """
        Create a new engine instance.
        """

        return self.get(
            engine_name
        )()

    # =====================================================
    # ENGINE COLLECTIONS
    # =====================================================

    def names(
        self,
    ) -> List[str]:
        """
        Return engine names.
        """

        return sorted(

            self._engines.keys()

        )

    # -----------------------------------------------------

    def classes(
        self,
    ) -> List[
        Type[BaseEngine]
    ]:
        """
        Return all registered engine classes.
        """

        return list(

            self._engines.values()

        )

    # -----------------------------------------------------

    def instances(
        self,
    ) -> List[
        BaseEngine
    ]:
        """
        Create one instance
        of every engine.
        """

        return [

            engine()

            for engine

            in self.classes()

        ]

    # =====================================================
    # CATEGORY QUERIES
    # =====================================================

    def by_category(
        self,
        category: str,
    ) -> List[
        Type[BaseEngine]
    ]:
        """
        Return engines belonging
        to a category.
        """

        return sorted(

            self._categories.get(
                category,
                [],
            ),

            key=lambda cls: (
                cls.PRIORITY,
                cls.NAME,
            ),

        )

    # -----------------------------------------------------

    def by_stage(
        self,
        stage: str,
    ) -> List[
        Type[BaseEngine]
    ]:
        """
        Return engines for a stage.
        """

        return sorted(

            self._stages.get(
                stage,
                [],
            ),

            key=lambda cls: (
                cls.PRIORITY,
                cls.NAME,
            ),

        )

    # -----------------------------------------------------

    def by_tag(
        self,
        tag: str,
    ) -> List[
        Type[BaseEngine]
    ]:
        """
        Return engines matching a tag.
        """

        return sorted(

            self._tags.get(
                tag,
                [],
            ),

            key=lambda cls: (
                cls.PRIORITY,
                cls.NAME,
            ),

        )

    # =====================================================
    # FILTERS
    # =====================================================

    def enabled(
        self,
    ) -> List[
        Type[BaseEngine]
    ]:
        """
        Return enabled engines.
        """

        return [

            engine

            for engine

            in self.classes()

            if engine.ENABLED

        ]

    # -----------------------------------------------------

    def disabled(
        self,
    ) -> List[
        Type[BaseEngine]
    ]:
        """
        Return disabled engines.
        """

        return [

            engine

            for engine

            in self.classes()

            if not engine.ENABLED

        ]

    # -----------------------------------------------------

    def critical(
        self,
    ) -> List[
        Type[BaseEngine]
    ]:
        """
        Return critical engines.
        """

        return [

            engine

            for engine

            in self.classes()

            if engine.CRITICAL

        ]

    # -----------------------------------------------------

    def parallelizable(
        self,
    ) -> List[
        Type[BaseEngine]
    ]:
        """
        Return engines that
        may run concurrently.
        """

        return [

            engine

            for engine

            in self.classes()

            if engine.PARALLELIZABLE

        ]

    # =====================================================
    # SORTING
    # =====================================================

    def sorted_by_priority(
        self,
    ) -> List[
        Type[BaseEngine]
    ]:
        """
        Return engines sorted by
        execution priority.
        """

        return sorted(

            self.classes(),

            key=lambda cls: (

                cls.PRIORITY,

                cls.NAME,

            ),

        )

    # -----------------------------------------------------

    def sorted_by_name(
        self,
    ) -> List[
        Type[BaseEngine]
    ]:
        """
        Return engines sorted alphabetically.
        """

        return sorted(

            self.classes(),

            key=lambda cls: cls.NAME,

        )
    
    # =====================================================
    # METADATA
    # =====================================================

    def metadata(
        self,
    ) -> Dict[
        str,
        Dict,
    ]:
        """
        Return metadata for every
        registered engine.
        """

        return {

            name: engine.metadata()

            for (
                name,
                engine,
            ) in self._engines.items()

        }

    # -----------------------------------------------------

    def outputs(
        self,
    ) -> Dict[
        str,
        List[str],
    ]:
        """
        Return engine outputs.
        """

        return {

            name: engine.OUTPUTS

            for (
                name,
                engine,
            ) in self._engines.items()

        }

    # -----------------------------------------------------

    def inputs(
        self,
    ) -> Dict[
        str,
        List[str],
    ]:
        """
        Return engine inputs.
        """

        return {

            name: engine.INPUTS

            for (
                name,
                engine,
            ) in self._engines.items()

        }

    # -----------------------------------------------------

    def dependencies(
        self,
    ) -> Dict[
        str,
        List[str],
    ]:
        """
        Return dependency mapping.
        """

        return {

            name: engine.DEPENDS_ON

            for (
                name,
                engine,
            ) in self._engines.items()

        }

    # =====================================================
    # VALIDATION
    # =====================================================

    def validate_dependencies(
        self,
    ) -> List[str]:
        """
        Validate dependency graph.

        Returns list of errors.
        """

        errors: List[str] = []

        for engine in self.classes():

            for dependency in engine.DEPENDS_ON:

                if dependency not in self._engines:

                    errors.append(

                        f"{engine.NAME} "

                        f"depends on "

                        f"'{dependency}' "

                        f"which is not "

                        f"registered."

                    )

        return errors

    # -----------------------------------------------------

    def validate_outputs(
        self,
    ) -> List[str]:
        """
        Detect duplicate output files.
        """

        errors: List[str] = []

        seen = {}

        for engine in self.classes():

            for output in engine.OUTPUTS:

                if output in seen:

                    errors.append(

                        f"Duplicate output "

                        f"'{output}' "

                        f"generated by "

                        f"{engine.NAME} "

                        f"and "

                        f"{seen[output]}."

                    )

                else:

                    seen[output] = engine.NAME

        return errors

    # -----------------------------------------------------

    def validate(
        self,
    ) -> List[str]:
        """
        Run every registry validation.
        """

        errors = []

        errors.extend(

            self.validate_dependencies()

        )

        errors.extend(

            self.validate_outputs()

        )

        return errors

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(
        self,
    ) -> Dict[str, object]:
        """
        Registry summary.
        """

        return {

            "total_engines":
                self.engine_count,

            "categories":
                self.categories,

            "stages":
                self.stages,

            "tags":
                self.tags,

            "packages_scanned":
                len(
                    self._packages_scanned
                ),

            "modules_scanned":
                len(
                    self._modules_scanned
                ),

            "discovery_complete":
                self._discovery_complete,

            "validation_errors":
                self.validate(),

        }

    # =====================================================
    # DUNDER METHODS
    # =====================================================

    def __len__(
        self,
    ) -> int:

        return self.engine_count

    # -----------------------------------------------------

    def __contains__(
        self,
        engine_name: str,
    ) -> bool:

        return self.exists(
            engine_name
        )

    # -----------------------------------------------------

    def __iter__(
        self,
    ):

        return iter(

            self.sorted_by_priority()

        )

    # -----------------------------------------------------

    def __repr__(
        self,
    ) -> str:

        return (

            f"EngineRegistry("

            f"engines={self.engine_count}, "

            f"categories={len(self.categories)}, "

            f"stages={len(self.stages)})"

        )


# =========================================================
# SINGLETON
# =========================================================

_registry: Optional[
    EngineRegistry
] = None


def get_registry() -> EngineRegistry:
    """
    Return singleton registry.

    Performs discovery only once.
    """

    global _registry

    if _registry is None:

        _registry = EngineRegistry()

        _registry.discover()

    return _registry