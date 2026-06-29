"""
====================================================================
Institutional Quant Platform

Market Order Algorithm

Author : Institutional Quant Platform

Purpose
-------
Institutional market order execution.

Executes immediately at the best available
market price.

Inherited From

• ExecutionAlgorithm

====================================================================
"""

from __future__ import annotations

from execution.execution_algorithm import ExecutionAlgorithm
from execution.execution_report import ExecutionReport
from execution.order import Order


class MarketOrderAlgorithm(
    ExecutionAlgorithm
):
    """
    Institutional market order algorithm.
    """

    def __init__(

        self,

    ) -> None:

        super().__init__(

            name="Market Order"

        )

    # =====================================================
    # EXECUTE
    # =====================================================

    def execute(

        self,

        order: Order,

    ) -> ExecutionReport:

        report = ExecutionReport()

        report.order = order

        report.executed_quantity = (

            order.quantity

        )

        report.remaining_quantity = 0.0

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

        report.fill_ratio = 1.0

        report.status = "FILLED"

        report.algorithm = self.name

        report.message = (

            "Market order executed."

        )

        return report

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}()"

        )

    __str__ = __repr__