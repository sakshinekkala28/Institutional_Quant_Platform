"""
====================================================================
Institutional Quant Platform

Transaction Cost Model

Author : Institutional Quant Platform

Purpose
-------
Institutional transaction cost model.

Provides

• Commission Cost
• Exchange Fees
• Taxes
• Slippage
• Market Impact
• Liquidity Cost
• Total Trading Cost

Used By

• Optimizers
• Execution Engine
• Live Rebalance
• Capacity Model

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from core.models.portfolio import Portfolio

from optimization.turnover_model import TurnoverModel
from optimization.slippage_model import SlippageModel
from optimization.liquidity_model import LiquidityModel


@dataclass(slots=True)
class TransactionCostModel:
    """
    Institutional transaction cost model.
    """

    commission_bps: float = 2.0

    exchange_fee_bps: float = 0.5

    tax_bps: float = 0.0

    turnover_model: TurnoverModel | None = None

    slippage_model: SlippageModel | None = None

    liquidity_model: LiquidityModel | None = None

    # =====================================================
    # COMMISSION
    # =====================================================

    def commission_cost(

        self,

        traded_value: float,

    ) -> float:

        return (

            traded_value

            * self.commission_bps

            / 10_000.0

        )

    # =====================================================
    # EXCHANGE FEES
    # =====================================================

    def exchange_fee(

        self,

        traded_value: float,

    ) -> float:

        return (

            traded_value

            * self.exchange_fee_bps

            / 10_000.0

        )

    # =====================================================
    # TAXES
    # =====================================================

    def tax_cost(

        self,

        traded_value: float,

    ) -> float:

        return (

            traded_value

            * self.tax_bps

            / 10_000.0

        )

    # =====================================================
    # SLIPPAGE
    # =====================================================

    def slippage_cost(

        self,

        portfolio: Portfolio,

    ) -> float:

        if self.slippage_model is None:

            return 0.0

        return self.slippage_model.calculate(

            portfolio

        )

    # =====================================================
    # LIQUIDITY
    # =====================================================

    def liquidity_cost(

        self,

        portfolio: Portfolio,

    ) -> float:

        if self.liquidity_model is None:

            return 0.0

        return self.liquidity_model.calculate(

            portfolio

        )

    # =====================================================
    # TURNOVER
    # =====================================================

    def turnover(

        self,

        current: Portfolio,

        target: Portfolio,

    ) -> float:

        if self.turnover_model is None:

            return 0.0

        return self.turnover_model.calculate(

            current,

            target,

        )

    # =====================================================
    # TOTAL COST
    # =====================================================

    def total_cost(

        self,

        current: Portfolio,

        target: Portfolio,

    ) -> float:

        traded_value = (

            self.turnover(

                current,

                target,

            )

            * current.nav

        )

        total = (

            self.commission_cost(

                traded_value

            )

            +

            self.exchange_fee(

                traded_value

            )

            +

            self.tax_cost(

                traded_value

            )

            +

            self.slippage_cost(

                target

            )

            +

            self.liquidity_cost(

                target

            )

        )

        return float(

            total

        )

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Commission={self.commission_bps:.2f}bps, "

            f"ExchangeFee={self.exchange_fee_bps:.2f}bps"

            f")"

        )

    __str__ = __repr__