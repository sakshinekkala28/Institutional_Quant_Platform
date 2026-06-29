"""
====================================================================
Institutional Quant Platform

Event

Author : Institutional Quant Platform

Purpose
-------
Base event abstraction for the institutional
event-driven backtesting framework.

All events inherit from this class.

Inherited By

• MarketEvent
• SignalEvent
• OrderEvent
• FillEvent

====================================================================
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from dataclasses import dataclass
from dataclasses import field

from datetime import datetime


@dataclass(slots=True)
class Event(ABC):
    """
    Institutional base event.
    """

    timestamp: datetime = field(

        default_factory=datetime.utcnow

    )

    metadata: dict = field(

        default_factory=dict

    )

    __hash__ = None

    # =====================================================
    # EVENT TYPE
    # =====================================================

    @property
    @abstractmethod
    def event_type(

        self,

    ) -> str:
        """
        Event type.
        """

        raise NotImplementedError

    # =====================================================
    # SERIALIZATION
    # =====================================================

    def to_dict(

        self,

    ) -> dict:

        return {

            "Event":

                self.event_type,

            "Timestamp":

                self.timestamp.isoformat(),

            "Metadata":

                self.metadata,

        }

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self,

    ) -> dict:

        return self.to_dict()

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Type={self.event_type}, "

            f"Timestamp={self.timestamp.isoformat()}"

            f")"

        )

    __str__ = __repr__