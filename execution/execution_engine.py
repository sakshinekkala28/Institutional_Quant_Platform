"""
====================================================================
Institutional Quant Platform

Execution Engine

Author : Institutional Quant Platform

Purpose
-------
Institutional execution orchestration engine.

Coordinates

• Order Validation
• Order Routing
• Execution Algorithm
• Broker
• Fill Model
• Slippage
• Market Impact

Produces

• Execution Report

====================================================================
"""

from __future__ import annotations

from execution.execution_report import ExecutionReport
from execution.order import Order
from execution.order_router import OrderRouter
from execution.execution_model import ExecutionModel


class ExecutionEngine:
    """
    Institutional execution engine.
    """

    def __init__(

        self,

        router: OrderRouter,

        execution_model: ExecutionModel,

    ) -> None:

        self.router = router

        self.execution_model = execution_model

    # =====================================================
    # VALIDATE
    # =====================================================

    def validate(

        self,

        order: Order,

    ) -> None:

        order.validate()

    # =====================================================
    # ROUTE
    # =====================================================

    def route(

        self,

        order: Order,

    ):

        return self.router.route(

            order

        )

    # =====================================================
    # EXECUTE
    # =====================================================

    def execute(

        self,

        order: Order,

    ) -> ExecutionReport:

        self.validate(

            order

        )

        routed_order = self.route(

            order

        )

        return self.execution_model.execute(

            routed_order

        )

    # =====================================================
    # BATCH EXECUTION
    # =====================================================

    def execute_all(

        self,

        orders: list[Order],

    ) -> list[ExecutionReport]:

        reports: list[ExecutionReport] = []

        for order in orders:

            reports.append(

                self.execute(

                    order

                )

            )

        return reports

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self,

        reports: list[ExecutionReport],

    ) -> dict:

        total_orders = len(

            reports

        )

        filled = sum(

            report.is_filled

            for report in reports

        )

        partial = sum(

            report.is_partial

            for report in reports

        )

        rejected = sum(

            report.is_rejected

            for report in reports

        )

        total_cost = sum(

            report.total_cost

            for report in reports

        )

        return {

            "Orders":

                total_orders,

            "Filled":

                filled,

            "Partial":

                partial,

            "Rejected":

                rejected,

            "Total_Cost":

                total_cost,

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Router={self.router.__class__.__name__}, "

            f"ExecutionModel={self.execution_model.__class__.__name__}"

            f")"

        )

    __str__ = __repr__