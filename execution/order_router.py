"""
====================================================================
Institutional Quant Platform

Order Router

Author : Institutional Quant Platform

Purpose
-------
Institutional order router.

Routes orders to brokers or execution venues.

Supports

• Smart Order Routing
• Broker Selection
• Exchange Selection
• Venue Selection

Used By

• ExecutionEngine
• Broker
• OMS

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field

from execution.order import Order


@dataclass(slots=True)
class OrderRouter:
    """
    Institutional order router.
    """

    default_broker: str = "SIMULATOR"

    venue: str = "NSE"

    routing_rules: dict = field(

        default_factory=dict

    )

    # =====================================================
    # ROUTE
    # =====================================================

    def route(

        self,

        order: Order,

    ) -> Order:

        broker = self.routing_rules.get(

            order.symbol,

            self.default_broker,

        )

        order.broker = broker

        order.metadata["venue"] = (

            self.venue

        )

        return order

    # =====================================================
    # REGISTER
    # =====================================================

    def register(

        self,

        symbol: str,

        broker: str,

    ) -> None:

        self.routing_rules[

            symbol

        ] = broker

    # =====================================================
    # REMOVE
    # =====================================================

    def unregister(

        self,

        symbol: str,

    ) -> None:

        self.routing_rules.pop(

            symbol,

            None,

        )

    # =====================================================
    # RESET
    # =====================================================

    def clear(

        self,

    ) -> None:

        self.routing_rules.clear()

    # =====================================================
    # LOOKUP
    # =====================================================

    def broker_for(

        self,

        symbol: str,

    ) -> str:

        return self.routing_rules.get(

            symbol,

            self.default_broker,

        )

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self,

    ) -> dict:

        return {

            "Default_Broker":

                self.default_broker,

            "Venue":

                self.venue,

            "Rules":

                len(

                    self.routing_rules

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

            f"Venue={self.venue}, "

            f"Broker={self.default_broker}"

            f")"

        )

    __str__ = __repr__