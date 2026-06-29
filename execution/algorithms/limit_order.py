"""
====================================================================
Institutional Quant Platform

Limit Order Algorithm

Author : Institutional Quant Platform

Purpose
-------
Institutional limit order execution.

Executes an order only if the market price
satisfies the specified limit price.

Inherited From

• ExecutionAlgorithm

====================================================================
"""

from __future__ import annotations

from execution.execution_algorithm import ExecutionAlgorithm
from execution.execution_report import ExecutionReport
from execution.order import Order


class LimitOrderAlgorithm(
    ExecutionAlgorithm
):
    """
    Institutional limit order algorithm.
    """

    def __init__(

        self,

    ) -> None:

        super().__init__(

            name="Limit Order"

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

        report.algorithm = self.name

        if (

            order.price is None

            or

            order.limit_price is None

        ):

            report.status = "REJECTED"

            report.message = (

                "Missing market or limit price."

            )

            return report

        executable = (

            (

                order.is_buy

                and

                order.price <= order.limit_price

            )

            or

            (

                order.is_sell

                and

                order.price >= order.limit_price

            )

        )

        if executable:

            report.executed_quantity = (

                order.quantity

            )

            report.remaining_quantity = 0.0

            report.average_price = (

                order.price

            )

            report.execution_value = (

                report.executed_quantity

                *

                report.average_price

            )

            report.fill_ratio = 1.0

            report.status = "FILLED"

            report.message = (

                "Limit order executed."

            )

        else:

            report.executed_quantity = 0.0

            report.remaining_quantity = (

                order.quantity

            )

            report.average_price = 0.0

            report.execution_value = 0.0

            report.fill_ratio = 0.0

            report.status = "PENDING"

            report.message = (

                "Waiting for limit price."

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