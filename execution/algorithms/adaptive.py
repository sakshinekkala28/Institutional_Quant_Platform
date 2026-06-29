"""
====================================================================
Institutional Quant Platform

Adaptive Execution Algorithm

Author : Institutional Quant Platform

Purpose
-------
Institutional adaptive execution algorithm.

Dynamically adjusts execution strategy
based on market conditions.

Adapts To

• Liquidity
• Volatility
• Bid-Ask Spread
• Participation Rate

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
class AdaptiveAlgorithm(
    ExecutionAlgorithm
):
    """
    Institutional adaptive execution algorithm.
    """

    liquidity_threshold: float = 0.50

    volatility_threshold: float = 0.25

    spread_threshold_bps: float = 10.0

    def __post_init__(

        self,

    ) -> None:

        super().__init__(

            name="Adaptive"

        )

    # =====================================================
    # STRATEGY SELECTION
    # =====================================================

    def select_strategy(

        self,

        liquidity: float,

        volatility: float,

        spread_bps: float,

    ) -> str:

        if liquidity < self.liquidity_threshold:

            return "ICEBERG"

        if volatility > self.volatility_threshold:

            return "TWAP"

        if spread_bps > self.spread_threshold_bps:

            return "VWAP"

        return "MARKET"

    # =====================================================
    # EXECUTE
    # =====================================================

    def execute(

        self,

        order: Order,

    ) -> ExecutionReport:

        #
        # In production these values
        # come from the Market Data
        # service.
        #

        liquidity = 0.80

        volatility = 0.15

        spread_bps = 4.0

        strategy = self.select_strategy(

            liquidity,

            volatility,

            spread_bps,

        )

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

            f"Adaptive execution "

            f"selected "

            f"{strategy}."

        )

        report.metadata[

            "Strategy"

        ] = strategy

        report.metadata[

            "Liquidity"

        ] = liquidity

        report.metadata[

            "Volatility"

        ] = volatility

        report.metadata[

            "Spread_bps"

        ] = spread_bps

        return report

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"LiquidityThreshold="

            f"{self.liquidity_threshold:.2f}, "

            f"VolatilityThreshold="

            f"{self.volatility_threshold:.2f}"

            f")"

        )

    __str__ = __repr__