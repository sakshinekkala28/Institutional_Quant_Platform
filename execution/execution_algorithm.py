"""
====================================================================
Institutional Quant Platform

Execution Algorithm

Author : Institutional Quant Platform

Purpose
-------
Abstract base class for all execution algorithms.

Provides

• Common validation
• Execution contract
• Order validation
• Report generation

Inherited By

• MarketOrderAlgorithm
• LimitOrderAlgorithm
• TWAPAlgorithm
• VWAPAlgorithm
• POVAlgorithm
• IcebergAlgorithm
• AdaptiveAlgorithm

====================================================================
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from execution.execution_report import ExecutionReport
from execution.order import Order


class ExecutionAlgorithm(ABC):
    """
    Institutional execution algorithm.
    """

    def __init__(

        self,

        name: str,

    ) -> None:

        self.name = name

    # =====================================================
    # VALIDATION
    # =====================================================

    def validate(

        self,

        order: Order,

    ) -> None:

        order.validate()

    # =====================================================
    # PRE EXECUTION
    # =====================================================

    def pre_execute(

        self,

        order: Order,

    ) -> None:
        """
        Hook before execution.
        """

        pass

    # =====================================================
    # POST EXECUTION
    # =====================================================

    def post_execute(

        self,

        report: ExecutionReport,

    ) -> None:
        """
        Hook after execution.
        """

        pass

    # =====================================================
    # EXECUTION CONTRACT
    # =====================================================

    @abstractmethod
    def execute(

        self,

        order: Order,

    ) -> ExecutionReport:
        """
        Execute order using algorithm.
        """

        raise NotImplementedError

    # =====================================================
    # CALLABLE
    # =====================================================

    def __call__(

        self,

        order: Order,

    ) -> ExecutionReport:

        self.validate(

            order

        )

        self.pre_execute(

            order

        )

        report = self.execute(

            order

        )

        self.post_execute(

            report

        )

        return report

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Name='{self.name}'"

            f")"

        )

    __str__ = __repr__