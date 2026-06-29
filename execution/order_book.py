"""
====================================================================
Institutional Quant Platform

Order Book

Author : Institutional Quant Platform

Purpose
-------
Institutional order book.

Maintains all execution orders.

Provides

• Add Order
• Remove Order
• Lookup Order
• Filled Orders
• Active Orders
• Cancelled Orders
• Rejected Orders

Used By

• Execution Engine
• Order Router
• Broker
• OMS
• EMS

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field

from execution.order import Order


@dataclass(slots=True)
class OrderBook:
    """
    Institutional Order Book.
    """

    orders: dict[str, Order] = field(

        default_factory=dict

    )

    # =====================================================
    # ADD
    # =====================================================

    def add(

        self,

        order: Order,

    ) -> None:

        if order.order_id in self.orders:

            raise ValueError(

                f"Order '{order.order_id}' already exists."

            )

        self.orders[

            order.order_id

        ] = order

    # =====================================================
    # REMOVE
    # =====================================================

    def remove(

        self,

        order_id: str,

    ) -> None:

        self.orders.pop(

            order_id,

            None,

        )

    # =====================================================
    # GET
    # =====================================================

    def get(

        self,

        order_id: str,

    ) -> Order:

        try:

            return self.orders[

                order_id

            ]

        except KeyError as exc:

            raise KeyError(

                f"Unknown order '{order_id}'."

            ) from exc

    # =====================================================
    # EXISTS
    # =====================================================

    def exists(

        self,

        order_id: str,

    ) -> bool:

        return (

            order_id

            in self.orders

        )

    # =====================================================
    # ACTIVE
    # =====================================================

    def active_orders(

        self,

    ) -> list[Order]:

        return [

            order

            for order

            in self.orders.values()

            if getattr(

                order,

                "status",

                "NEW",

            )

            not in {

                "FILLED",

                "CANCELLED",

                "REJECTED",

            }

        ]

    # =====================================================
    # FILLED
    # =====================================================

    def filled_orders(

        self,

    ) -> list[Order]:

        return [

            order

            for order

            in self.orders.values()

            if getattr(

                order,

                "status",

                "",

            )

            == "FILLED"

        ]

    # =====================================================
    # CANCELLED
    # =====================================================

    def cancelled_orders(

        self,

    ) -> list[Order]:

        return [

            order

            for order

            in self.orders.values()

            if getattr(

                order,

                "status",

                "",

            )

            == "CANCELLED"

        ]

    # =====================================================
    # REJECTED
    # =====================================================

    def rejected_orders(

        self,

    ) -> list[Order]:

        return [

            order

            for order

            in self.orders.values()

            if getattr(

                order,

                "status",

                "",

            )

            == "REJECTED"

        ]

    # =====================================================
    # CLEAR
    # =====================================================

    def clear(

        self,

    ) -> None:

        self.orders.clear()

    # =====================================================
    # COLLECTION
    # =====================================================

    def __len__(

        self,

    ) -> int:

        return len(

            self.orders

        )

    def __iter__(

        self,

    ):

        return iter(

            self.orders.values()

        )

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self,

    ) -> dict:

        return {

            "Total":

                len(

                    self.orders

                ),

            "Active":

                len(

                    self.active_orders()

                ),

            "Filled":

                len(

                    self.filled_orders()

                ),

            "Cancelled":

                len(

                    self.cancelled_orders()

                ),

            "Rejected":

                len(

                    self.rejected_orders()

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

            f"Orders={len(self.orders)}"

            f")"

        )

    __str__ = __repr__