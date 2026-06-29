"""
====================================================================
Institutional Quant Platform

Execution Report

Author : Institutional Quant Platform

Purpose
-------
Institutional execution report.

Represents the result of an execution model.

Produced By

• ExecutionModel
• ExecutionEngine
• Broker
• FillModel

Consumed By

• OMS
• Reporting
• Monitoring
• Analytics

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field


@dataclass(slots=True)
class ExecutionReport:
    """
    Institutional execution report.
    """

    order: object | None = None

    executed_quantity: float = 0.0

    remaining_quantity: float = 0.0

    average_price: float = 0.0

    execution_value: float = 0.0

    commission: float = 0.0

    fees: float = 0.0

    taxes: float = 0.0

    slippage: float = 0.0

    market_impact: float = 0.0

    fill_ratio: float = 0.0

    execution_time_ms: float = 0.0

    venue: str = ""

    broker: str = ""

    algorithm: str = ""

    status: str = "PENDING"

    message: str = ""

    metadata: dict = field(

        default_factory=dict

    )

    __hash__ = None

    # =====================================================
    # PROPERTIES
    # =====================================================

    @property
    def total_cost(

        self

    ) -> float:

        return (

            self.commission

            +

            self.fees

            +

            self.taxes

            +

            self.slippage

            +

            self.market_impact

        )

    @property
    def is_complete(

        self

    ) -> bool:

        return (

            self.remaining_quantity

            <= 0.0

        )

    @property
    def is_partial(

        self

    ) -> bool:

        return (

            0.0

            <

            self.fill_ratio

            <

            1.0

        )

    @property
    def is_rejected(

        self

    ) -> bool:

        return (

            self.status.upper()

            ==

            "REJECTED"

        )

    @property
    def is_filled(

        self

    ) -> bool:

        return (

            self.status.upper()

            ==

            "FILLED"

        )

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self

    ) -> dict:

        return {

            "Status":

                self.status,

            "Executed":

                self.executed_quantity,

            "Remaining":

                self.remaining_quantity,

            "Average_Price":

                self.average_price,

            "Fill_Ratio":

                self.fill_ratio,

            "Execution_Value":

                self.execution_value,

            "Total_Cost":

                self.total_cost,

            "Venue":

                self.venue,

            "Broker":

                self.broker,

            "Algorithm":

                self.algorithm,

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Status={self.status}, "

            f"Fill={self.fill_ratio:.2%}, "

            f"Price={self.average_price:.2f}"

            f")"

        )

    __str__ = __repr__