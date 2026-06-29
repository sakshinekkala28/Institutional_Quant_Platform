"""
====================================================================
Institutional Quant Platform

Base Execution Model

Author : Institutional Quant Platform

Purpose
-------
Abstract base class for all execution models.

Provides

• Validation
• Order Validation
• Execution Contract
• Report Creation
• Common Utilities

Inherited By

• MarketOrderExecution
• LimitOrderExecution
• TWAPExecution
• VWAPExecution
• POVExecution
• IcebergExecution
• AdaptiveExecution

====================================================================
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from execution.execution_report import ExecutionReport
from execution.order import Order


class BaseExecutionModel(ABC):
    """
    Institutional base execution model.
    """

    def __init__(

        self,

        allow_partial_fill: bool = True,

        validate_order: bool = True,

    ) -> None:

        self.allow_partial_fill = allow_partial_fill

        self.validate_order_flag = validate_order

    # =====================================================
    # VALIDATION
    # =====================================================

    def validate(

        self,

        order: Order,

    ) -> None:

        if not self.validate_order_flag:

            return

        if order.quantity <= 0:

            raise ValueError(

                "Order quantity must be positive."

            )

        if order.symbol == "":

            raise ValueError(

                "Order symbol cannot be empty."

            )

    # =====================================================
    # REPORT
    # =====================================================

    def create_report(

        self,

    ) -> ExecutionReport:

        return ExecutionReport()

    # =====================================================
    # EXECUTION CONTRACT
    # =====================================================

    @abstractmethod
    def execute(

        self,

        order: Order,

    ) -> ExecutionReport:
        """
        Execute order.
        """

        raise NotImplementedError

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