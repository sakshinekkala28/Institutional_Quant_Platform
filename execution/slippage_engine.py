"""
====================================================================
Institutional Quant Platform

Slippage Engine

Author : Institutional Quant Platform

Purpose
-------
Institutional execution slippage engine.

Estimates execution slippage by combining

• Bid-Ask Spread
• Market Impact
• Volatility
• Execution Delay
• Trading Algorithm Penalty

Used By

• ExecutionModel
• ExecutionEngine
• BrokerSimulator
• TransactionCostModel

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from execution.market_impact import MarketImpact
from execution.order import Order


@dataclass(slots=True)
class SlippageEngine:
    """
    Institutional execution slippage engine.
    """

    spread_bps: float = 2.0

    volatility_bps: float = 3.0

    delay_bps: float = 1.0

    algorithm_penalty_bps: float = 0.5

    market_impact: MarketImpact | None = None

    # =====================================================
    # BID-ASK SPREAD
    # =====================================================

    def spread_cost(

        self,

        order: Order,

    ) -> float:

        return self.spread_bps

    # =====================================================
    # VOLATILITY COST
    # =====================================================

    def volatility_cost(

        self,

        order: Order,

    ) -> float:

        return self.volatility_bps

    # =====================================================
    # EXECUTION DELAY
    # =====================================================

    def delay_cost(

        self,

        order: Order,

    ) -> float:

        return self.delay_bps

    # =====================================================
    # ALGORITHM COST
    # =====================================================

    def algorithm_cost(

        self,

        order: Order,

    ) -> float:

        return self.algorithm_penalty_bps

    # =====================================================
    # MARKET IMPACT
    # =====================================================

    def impact_cost(

        self,

        order: Order,

    ) -> float:

        if self.market_impact is None:

            return 0.0

        return self.market_impact.calculate(

            order

        )

    # =====================================================
    # TOTAL SLIPPAGE (BPS)
    # =====================================================

    def calculate(

        self,

        order: Order,

    ) -> float:

        return (

            self.spread_cost(

                order

            )

            +

            self.volatility_cost(

                order

            )

            +

            self.delay_cost(

                order

            )

            +

            self.algorithm_cost(

                order

            )

            +

            self.impact_cost(

                order

            )

        )

    # =====================================================
    # EXECUTION PRICE
    # =====================================================

    def execution_price(

        self,

        order: Order,

    ) -> float:

        if order.price is None:

            return 0.0

        slippage = self.calculate(

            order

        )

        multiplier = (

            1.0

            +

            slippage

            / 10_000.0

        )

        if order.is_buy:

            return (

                order.price

                * multiplier

            )

        return (

            order.price

            / multiplier

        )

    # =====================================================
    # BREAKDOWN
    # =====================================================

    def breakdown(

        self,

        order: Order,

    ) -> dict:

        spread = self.spread_cost(

            order

        )

        volatility = self.volatility_cost(

            order

        )

        delay = self.delay_cost(

            order

        )

        algorithm = self.algorithm_cost(

            order

        )

        impact = self.impact_cost(

            order

        )

        total = (

            spread

            +

            volatility

            +

            delay

            +

            algorithm

            +

            impact

        )

        return {

            "Spread_bps":

                spread,

            "Volatility_bps":

                volatility,

            "Delay_bps":

                delay,

            "Algorithm_bps":

                algorithm,

            "Market_Impact_bps":

                impact,

            "Total_bps":

                total,

            "Execution_Price":

                self.execution_price(

                    order

                ),

        }

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self,

        order: Order,

    ) -> dict:

        return self.breakdown(

            order

        )

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Spread={self.spread_bps:.2f}bps)"

        )

    __str__ = __repr__