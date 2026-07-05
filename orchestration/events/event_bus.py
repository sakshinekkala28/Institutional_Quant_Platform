"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Event Bus

Central event dispatcher for the orchestration framework.

Responsibilities
----------------
• Event publication
• Event subscription
• Event dispatch
• Listener management
• Plugin integration

=========================================================
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any
from typing import Callable
from typing import DefaultDict
from typing import Dict
from typing import List


# =========================================================
# EVENT BUS
# =========================================================

class EventBus:
    """
    Publish / Subscribe event dispatcher.
    """

    def __init__(self) -> None:

        self._listeners: DefaultDict[
            str,
            List[Callable[..., Any]]
        ] = defaultdict(list)

    # =====================================================
    # SUBSCRIBE
    # =====================================================

    def subscribe(
        self,
        event: str,
        listener: Callable[..., Any],
    ) -> None:
        """
        Register an event listener.
        """

        if listener not in self._listeners[event]:

            self._listeners[event].append(
                listener
            )

    # -----------------------------------------------------

    def unsubscribe(
        self,
        event: str,
        listener: Callable[..., Any],
    ) -> None:
        """
        Remove an event listener.
        """

        if listener in self._listeners[event]:

            self._listeners[event].remove(
                listener
            )

    # =====================================================
    # PUBLISH
    # =====================================================

    def publish(
        self,
        event: str,
        **payload: Any,
    ) -> None:
        """
        Publish an event.
        """

        for listener in self._listeners.get(
            event,
            [],
        ):

            listener(
                **payload
            )

    # =====================================================
    # MANAGEMENT
    # =====================================================

    def clear(
        self,
    ) -> None:
        """
        Remove all listeners.
        """

        self._listeners.clear()

    # -----------------------------------------------------

    def events(
        self,
    ) -> List[str]:

        return sorted(

            self._listeners.keys()

        )

    # -----------------------------------------------------

    def listeners(
        self,
        event: str,
    ) -> List[Callable[..., Any]]:

        return list(

            self._listeners.get(
                event,
                [],
            )

        )

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(
        self,
    ) -> Dict[str, int]:

        return {

            event: len(listeners)

            for event, listeners

            in self._listeners.items()

        }

    # =====================================================
    # DUNDER
    # =====================================================

    def __len__(
        self,
    ) -> int:

        return sum(

            len(listeners)

            for listeners

            in self._listeners.values()

        )

    # -----------------------------------------------------

    def __contains__(
        self,
        event: str,
    ) -> bool:

        return event in self._listeners

    # -----------------------------------------------------

    def __repr__(
        self,
    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"events={len(self._listeners)}, "

            f"listeners={len(self)})"

        )