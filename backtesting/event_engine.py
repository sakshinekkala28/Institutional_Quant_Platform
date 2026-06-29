"""
====================================================================
Institutional Quant Platform

Event Engine

Author : Institutional Quant Platform

Purpose
-------
Institutional event processing engine.

Maintains an event queue and dispatches
events in chronological order.

Processes

• MarketEvent
• SignalEvent
• OrderEvent
• FillEvent

Used By

• BacktestEngine
• Historical Backtest
• Event Driven Backtest

====================================================================
"""

from __future__ import annotations

from collections import deque

from backtesting.event import Event


class EventEngine:
    """
    Institutional event engine.
    """

    def __init__(

        self,

    ) -> None:

        self._queue: deque[Event] = deque()

        self._handlers: dict[str, list] = {}

    # =====================================================
    # REGISTER HANDLER
    # =====================================================

    def register(

        self,

        event_type: str,

        handler,

    ) -> None:

        self._handlers.setdefault(

            event_type,

            []

        ).append(

            handler

        )

    # =====================================================
    # UNREGISTER
    # =====================================================

    def unregister(

        self,

        event_type: str,

        handler,

    ) -> None:

        handlers = self._handlers.get(

            event_type,

            []

        )

        if handler in handlers:

            handlers.remove(

                handler

            )

    # =====================================================
    # PUSH EVENT
    # =====================================================

    def publish(

        self,

        event: Event,

    ) -> None:

        self._queue.append(

            event

        )

    # =====================================================
    # POP EVENT
    # =====================================================

    def next_event(

        self,

    ) -> Event | None:

        if not self._queue:

            return None

        return self._queue.popleft()

    # =====================================================
    # PROCESS ONE EVENT
    # =====================================================

    def process_next(

        self,

    ) -> Event | None:

        event = self.next_event()

        if event is None:

            return None

        for handler in self._handlers.get(

            event.event_type,

            [],

        ):

            handler(

                event

            )

        return event

    # =====================================================
    # PROCESS ALL EVENTS
    # =====================================================

    def run(

        self,

    ) -> None:

        while self.has_events:

            self.process_next()

    # =====================================================
    # CLEAR
    # =====================================================

    def clear(

        self,

    ) -> None:

        self._queue.clear()

    # =====================================================
    # PROPERTIES
    # =====================================================

    @property
    def has_events(

        self,

    ) -> bool:

        return len(

            self._queue

        ) > 0

    @property
    def size(

        self,

    ) -> int:

        return len(

            self._queue

        )

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self,

    ) -> dict:

        return {

            "QueuedEvents":

                self.size,

            "RegisteredHandlers":

                len(

                    self._handlers

                ),

            "EventTypes":

                list(

                    self._handlers.keys()

                ),

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Queue={self.size}, "

            f"Handlers={len(self._handlers)}"

            f")"

        )

    __str__ = __repr__