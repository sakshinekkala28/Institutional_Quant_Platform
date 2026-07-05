"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Hook Manager

Manages orchestration lifecycle hooks.

Responsibilities
----------------
• Register lifecycle hooks
• Execute hooks
• Plugin integration
• Hook ordering
• Error isolation

Supported Hooks
---------------
• before_platform
• after_platform
• before_pipeline
• after_pipeline
• before_engine
• after_engine

=========================================================
"""

from __future__ import annotations

import logging

from collections import defaultdict
from typing import Any
from typing import Callable
from typing import DefaultDict
from typing import Dict
from typing import List

logger = logging.getLogger(__name__)


# =========================================================
# HOOK MANAGER
# =========================================================

class HookManager:
    """
    Lifecycle hook dispatcher.
    """

    VALID_HOOKS = {

        "before_platform",

        "after_platform",

        "before_pipeline",

        "after_pipeline",

        "before_engine",

        "after_engine",

    }

    def __init__(
        self,
    ) -> None:

        self._hooks: DefaultDict[
            str,
            List[Callable[..., Any]]
        ] = defaultdict(list)

    # =====================================================
    # REGISTRATION
    # =====================================================

    def register(
        self,
        hook: str,
        callback: Callable[..., Any],
    ) -> None:
        """
        Register lifecycle hook.
        """

        if hook not in self.VALID_HOOKS:

            raise ValueError(

                f"Unknown hook '{hook}'."

            )

        if callback not in self._hooks[hook]:

            self._hooks[hook].append(

                callback

            )

    # -----------------------------------------------------

    def unregister(
        self,
        hook: str,
        callback: Callable[..., Any],
    ) -> None:

        if callback in self._hooks.get(

            hook,

            [],

        ):

            self._hooks[hook].remove(

                callback

            )

    # =====================================================
    # EXECUTION
    # =====================================================

    def execute(
        self,
        hook: str,
        **kwargs: Any,
    ) -> None:
        """
        Execute all callbacks for a hook.

        Individual callback failures are logged but
        do not stop execution of remaining callbacks.
        """

        if hook not in self.VALID_HOOKS:

            raise ValueError(

                f"Unknown hook '{hook}'."

            )

        for callback in self._hooks.get(

            hook,

            [],

        ):

            try:

                callback(

                    **kwargs

                )

            except Exception:

                logger.exception(

                    "Hook '%s' failed: %s",

                    hook,

                    callback,

                )

    # =====================================================
    # DISCOVERY
    # =====================================================

    def hooks(
        self,
    ) -> List[str]:

        return sorted(

            self._hooks.keys()

        )

    # -----------------------------------------------------

    def callbacks(
        self,
        hook: str,
    ) -> List[Callable[..., Any]]:

        return list(

            self._hooks.get(

                hook,

                [],

            )

        )

    # =====================================================
    # CLEANUP
    # =====================================================

    def clear(
        self,
    ) -> None:

        self._hooks.clear()

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(
        self,
    ) -> Dict[str, int]:

        return {

            hook: len(callbacks)

            for hook, callbacks

            in self._hooks.items()

        }

    # =====================================================
    # DUNDER
    # =====================================================

    def __len__(
        self,
    ) -> int:

        return sum(

            len(callbacks)

            for callbacks

            in self._hooks.values()

        )

    # -----------------------------------------------------

    def __contains__(
        self,
        hook: str,
    ) -> bool:

        return hook in self._hooks

    # -----------------------------------------------------

    def __repr__(
        self,
    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"hooks={len(self._hooks)}, "

            f"callbacks={len(self)})"

        )