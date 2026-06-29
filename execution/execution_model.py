"""
====================================================================
Institutional Quant Platform

Execution Model

Author : Institutional Quant Platform

Purpose
-------
Institutional execution model.

Coordinates

• Order Validation
• Execution Algorithm
• Broker
• Fill Model
• Slippage Engine
• Market Impact

Inherited From

• BaseExecutionModel

====================================================================
"""

from __future__ import annotations

from execution.base_execution_model import BaseExecutionModel
from execution.execution_report import ExecutionReport
from execution.fill_model import FillModel
from execution.market_impact import MarketImpact
from execution.order import Order
from execution.slippage_engine import SlippageEngine


class ExecutionModel(
    BaseExecutionModel
):
    """
    Institutional execution model.
    """

    def __init__(

        self,

        fill_model: FillModel,

        slippage_engine: SlippageEngine,

        market_impact: MarketImpact,

        allow_partial_fill: bool = True,

        validate_order: bool = True,

    ) -> None:

        super().__init__(

            allow_partial_fill=allow_partial_fill,

            validate_order=validate_order,

        )

        self.fill_model = fill_model

        self.slippage_engine = slippage_engine

        self.market_impact = market_impact

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

        report = self.create_report()

        report.order = order

        report.market_impact = (

            self.market_impact.calculate(

                order

            )

        )

        report.slippage = (

            self.slippage_engine.calculate(

                order

            )

        )

        fill = self.fill_model.fill(

            order

        )

        report.executed_quantity = (

            fill.executed_quantity

        )

        report.average_price = (

            fill.average_price

        )

        report.fill_ratio = (

            fill.fill_ratio

        )

        report.status = (

            fill.status

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

            f"FillModel={self.fill_model.__class__.__name__}, "

            f"Slippage={self.slippage_engine.__class__.__name__}"

            f")"

        )

    __str__ = __repr__