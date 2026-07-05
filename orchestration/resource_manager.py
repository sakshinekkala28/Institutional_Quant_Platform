"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Resource Manager

Central registry for platform resources.

Responsibilities
----------------
• Resource registration
• Lazy initialization
• Resource reuse
• Connection pooling
• Resource cleanup

Managed Resources
-----------------
• DuckDB
• SQLite
• PostgreSQL
• REST Sessions
• File Managers
• Cache
• Thread Pools

=========================================================
"""

from __future__ import annotations

import logging

from typing import Any
from typing import Callable
from typing import Dict

logger = logging.getLogger(__name__)


# =========================================================
# RESOURCE MANAGER
# =========================================================

class ResourceManager:
    """
    Central platform resource manager.
    """

    def __init__(
        self,
    ) -> None:

        self._resources: Dict[
            str,
            Any,
        ] = {}

        self._factories: Dict[
            str,
            Callable[[], Any],
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
        Register a lazy resource factory.
        """

        if name in self._factories:

            raise ValueError(

                f"Resource '{name}' already exists."

            )

        self._factories[name] = factory

    # =====================================================
    # GET RESOURCE
    # =====================================================

    def get(
        self,
        name: str,
    ) -> Any:
        """
        Return shared resource.
        """

        if name in self._resources:

            return self._resources[name]

        if name not in self._factories:

            raise KeyError(

                f"Unknown resource '{name}'."

            )

        resource = self._factories[name]()

        self._resources[name] = resource

        return resource

    # =====================================================
    # EXISTS
    # =====================================================

    def exists(
        self,
        name: str,
    ) -> bool:

        return (

            name in self._resources

            or

            name in self._factories

        )

    # =====================================================
    # REMOVE
    # =====================================================

    def unregister(
        self,
        name: str,
    ) -> None:

        resource = self._resources.pop(

            name,

            None,

        )

        self._factories.pop(

            name,

            None,

        )

        if (

            resource is not None

            and

            hasattr(

                resource,

                "close",

            )

        ):

            try:

                resource.close()

            except Exception:

                logger.exception(

                    "Failed closing resource '%s'.",

                    name,

                )

    # =====================================================
    # CLEANUP
    # =====================================================

    def shutdown(
        self,
    ) -> None:
        """
        Close every managed resource.
        """

        for name in list(

            self._resources.keys()

        ):

            self.unregister(

                name

            )

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(
        self,
    ) -> dict:

        return {

            "registered":

                len(

                    self._factories,

                ),

            "active":

                len(

                    self._resources,

                ),

            "resources":

                sorted(

                    self._factories.keys()

                ),

        }

    # =====================================================
    # DUNDER
    # =====================================================

    def __contains__(
        self,
        name: str,
    ) -> bool:

        return self.exists(

            name

        )

    # -----------------------------------------------------

    def __len__(
        self,
    ) -> int:

        return len(

            self._factories

        )

    # -----------------------------------------------------

    def __repr__(
        self,
    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"registered={len(self)}, "

            f"active={len(self._resources)})"

        )