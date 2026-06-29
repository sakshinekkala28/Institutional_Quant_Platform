"""
====================================================================
Institutional Quant Platform

Broker Simulator

Author : Institutional Quant Platform

Purpose
-------
Institutional paper trading broker.

Simulates broker execution without connecting
to a live exchange.

Implements

• Broker Interface

Used By

• Backtesting
• Paper Trading
• Execution Engine
• Unit Testing

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field

from execution.broker import Broker
from execution.execution_report import ExecutionReport
from execution.order import Order


@dataclass(slots=True)
class BrokerSimulator(Broker):
    """
    Institutional paper-trading broker.
    """

    name: str = "SIMULATOR"

    connected: bool = False

    orders: dict[str, Order] = field(

        default_factory=dict

    )

    # =====================================================
    # CONNECTION
    # =====================================================

    def connect(

        self,

    ) -> None:

        self.connected = True

    def disconnect(

        self,

    ) -> None:

        self.connected = False

    @property
    def is_connected(

        self,

    ) -> bool:

        return self.connected

    # =====================================================
    # SUBMIT ORDER
    # =====================================================

    def submit_order(

        self,

        order: Order,

    ) -> ExecutionReport:

        if not self.connected:

            raise RuntimeError(

                "Broker is not connected."

            )

        self.orders[

            order.order_id

        ] = order

        report = ExecutionReport()

        report.order = order

        report.executed_quantity = (

            order.quantity

        )

        report.remaining_quantity = 0.0

        report.average_price = (

            order.price or 0.0

        )

        report.execution_value = (

            (order.price or 0.0)

            * order.quantity

        )

        report.fill_ratio = 1.0

        report.status = "FILLED"

        report.broker = self.name

        report.message = (

            "Paper trade executed."

        )

        return report

    # =====================================================
    # CANCEL
    # =====================================================

    def cancel_order(

        self,

        order_id: str,

    ) -> bool:

        if order_id not in self.orders:

            return False

        del self.orders[

            order_id

        ]

        return True

    # =====================================================
    # MODIFY
    # =====================================================

    def modify_order(

        self,

        order: Order,

    ) -> ExecutionReport:

        if order.order_id not in self.orders:

            raise KeyError(

                f"Unknown order "

                f"{order.order_id}"

            )

        self.orders[

            order.order_id

        ] = order

        report = ExecutionReport()

        report.order = order

        report.status = "MODIFIED"

        report.broker = self.name

        report.message = (

            "Paper order modified."

        )

        return report

    # =====================================================
    # ACCOUNT INFO
    # =====================================================

    def account_info(

        self,

    ) -> dict:

        return {

            "Broker":

                self.name,

            "Connected":

                self.connected,

            "Orders":

                len(

                    self.orders

                ),

            "Mode":

                "PAPER",

        }

    # =====================================================
    # OPEN ORDERS
    # =====================================================

    def open_orders(

        self,

    ) -> list[Order]:

        return list(

            self.orders.values()

        )

    # =====================================================
    # POSITIONS
    # =====================================================

    def positions(

        self,

    ) -> dict:

        positions: dict[str, float] = {}

        for order in self.orders.values():

            quantity = (

                order.quantity

                if order.is_buy

                else -order.quantity

            )

            positions[

                order.symbol

            ] = (

                positions.get(

                    order.symbol,

                    0.0,

                )

                +

                quantity

            )

        return positions

    # =====================================================
    # RESET
    # =====================================================

    def reset(

        self,

    ) -> None:

        self.orders.clear()

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self,

    ) -> dict:

        return {

            "Broker":

                self.name,

            "Connected":

                self.connected,

            "Orders":

                len(

                    self.orders

                ),

            "Positions":

                len(

                    self.positions()

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

            f"Orders={len(self.orders)}, "

            f"Connected={self.connected}"

            f")"

        )

    __str__ = __repr__