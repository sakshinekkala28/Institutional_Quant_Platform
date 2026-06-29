"""
====================================================================
Institutional Quant Platform

Fill Model

Author : Institutional Quant Platform

Purpose
-------
Institutional fill model.

Determines

• Fill Quantity
• Average Execution Price
• Fill Ratio
• Execution Status

Used By

• ExecutionModel
• Broker
• BrokerSimulator
• ExecutionEngine

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from execution.order import Order


# =====================================================
# FILL RESULT
# =====================================================


@dataclass(slots=True)
class FillResult:
    """
    Institutional fill result.
    """

    executed_quantity: float

    remaining_quantity: float

    average_price: float

    fill_ratio: float

    status: str


# =====================================================
# FILL MODEL
# =====================================================


class FillModel:
    """
    Institutional fill model.
    """

    def __init__(

        self,

        allow_partial_fill: bool = True,

    ) -> None:

        self.allow_partial_fill = allow_partial_fill

    # =====================================================
    # FILL
    # =====================================================

    def fill(

        self,

        order: Order,

    ) -> FillResult:

        if self.allow_partial_fill:

            executed = order.quantity

        else:

            executed = order.quantity

        remaining = max(

            0.0,

            order.quantity - executed,

        )

        ratio = (

            executed / order.quantity

            if order.quantity > 0

            else 0.0

        )

        if executed == 0:

            status = "REJECTED"

        elif remaining > 0:

            status = "PARTIALLY_FILLED"

        else:

            status = "FILLED"

        return FillResult(

            executed_quantity=executed,

            remaining_quantity=remaining,

            average_price=order.price or 0.0,

            fill_ratio=ratio,

            status=status,

        )

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"PartialFill={self.allow_partial_fill}"

            f")"

        )

    __str__ = __repr__