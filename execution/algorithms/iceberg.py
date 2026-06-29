"""
====================================================================
Institutional Quant Platform

Iceberg Algorithm

Author : Institutional Quant Platform

Purpose
-------
Institutional Iceberg execution algorithm.

Executes a large order while exposing only
a small visible quantity to the market.

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
class IcebergAlgorithm(
    ExecutionAlgorithm
):
    """
    Institutional Iceberg execution algorithm.
    """

    display_quantity: float

    def __post_init__(

        self,

    ) -> None:

        super().__init__(

            name="Iceberg"

        )

        if self.display_quantity <= 0.0:

            raise ValueError(

                "Display quantity "

                "must be positive."

            )

    # =====================================================
    # ORDER SLICES
    # =====================================================

    def slices(

        self,

        order: Order,

    ) -> list[float]:

        slices: list[float] = []

        remaining = order.quantity

        while remaining > 0.0:

            quantity = min(

                remaining,

                self.display_quantity,

            )

            slices.append(

                quantity

            )

            remaining -= quantity

        return slices

    # =====================================================
    # EXECUTE
    # =====================================================

    def execute(

        self,

        order: Order,

    ) -> ExecutionReport:

        order_slices = self.slices(

            order

        )

        report = ExecutionReport()

        report.order = order

        report.executed_quantity = sum(

            order_slices

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

            "Iceberg execution completed."

        )

        report.metadata[

            "DisplayQuantity"

        ] = self.display_quantity

        report.metadata[

            "NumberOfSlices"

        ] = len(

            order_slices

        )

        report.metadata[

            "Slices"

        ] = order_slices

        return report

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Display="

            f"{self.display_quantity:.2f}"

            f")"

        )

    __str__ = __repr__