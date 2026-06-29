"""
====================================================================
Institutional Quant Platform

TWAP Algorithm

Author : Institutional Quant Platform

Purpose
-------
Institutional Time Weighted Average Price
(TWAP) execution algorithm.

Splits a large order into equal-sized slices
executed over a specified time interval.

Inherited From

• ExecutionAlgorithm

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from execution.execution_algorithm import ExecutionAlgorithm
from execution.execution_report import ExecutionReport
from execution.order import Order


@dataclass(slots=True)
class TWAPAlgorithm(
    ExecutionAlgorithm
):
    """
    Institutional TWAP execution algorithm.
    """

    intervals: int = 10

    def __post_init__(

        self,

    ) -> None:

        super().__init__(

            name="TWAP"

        )

    # =====================================================
    # ORDER SCHEDULE
    # =====================================================

    def schedule(

        self,

        order: Order,

    ) -> list[float]:

        if self.intervals <= 0:

            raise ValueError(

                "Intervals must be positive."

            )

        quantity = (

            order.quantity

            / self.intervals

        )

        return [

            quantity

            for _

            in range(

                self.intervals

            )

        ]

    # =====================================================
    # EXECUTE
    # =====================================================

    def execute(

        self,

        order: Order,

    ) -> ExecutionReport:

        schedule = self.schedule(

            order

        )

        report = ExecutionReport()

        report.order = order

        report.executed_quantity = sum(

            schedule

        )

        report.remaining_quantity = max(

            0.0,

            order.quantity

            -

            report.executed_quantity,

        )

        report.average_price = (

            order.price

            if order.price is not None

            else 0.0

        )

        report.execution_value = (

            report.executed_quantity

            *

            report.average_price

        )

        report.fill_ratio = (

            report.executed_quantity

            /

            order.quantity

        )

        report.algorithm = self.name

        report.status = "FILLED"

        report.message = (

            f"TWAP executed "

            f"{self.intervals} slices."

        )

        report.metadata[

            "Slices"

        ] = schedule

        return report

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Intervals={self.intervals}"

            f")"

        )

    __str__ = __repr__