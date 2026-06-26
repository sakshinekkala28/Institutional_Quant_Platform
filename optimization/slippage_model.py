"""
====================================================================
Institutional Quant Platform

Slippage Model

Author : Institutional Quant Platform

Purpose
-------
Institutional execution slippage model.

Provides

• Bid-Ask Spread Cost
• Volatility Cost
• Participation Cost
• Execution Slippage

Used By

• TransactionCostModel
• Execution Engine
• Optimizers
• Live Trading

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from core.models.portfolio import Portfolio


@dataclass(slots=True)
class SlippageModel:
    """
    Institutional execution slippage model.
    """

    bid_ask_spread_bps: float = 5.0

    volatility_bps: float = 3.0

    participation_penalty_bps: float = 2.0

    # =====================================================
    # BID ASK COST
    # =====================================================

    def bid_ask_cost(

        self,

        traded_value: float,

    ) -> float:

        return (

            traded_value

            * self.bid_ask_spread_bps

            / 10_000.0

        )

    # =====================================================
    # VOLATILITY COST
    # =====================================================

    def volatility_cost(

        self,

        traded_value: float,

    ) -> float:

        return (

            traded_value

            * self.volatility_bps

            / 10_000.0

        )

    # =====================================================
    # PARTICIPATION COST
    # =====================================================

    def participation_cost(

        self,

        traded_value: float,

    ) -> float:

        return (

            traded_value

            * self.participation_penalty_bps

            / 10_000.0

        )

    # =====================================================
    # TOTAL SLIPPAGE
    # =====================================================

    def calculate(

        self,

        portfolio: Portfolio,

    ) -> float:

        traded_value = portfolio.nav

        return (

            self.bid_ask_cost(

                traded_value

            )

            +

            self.volatility_cost(

                traded_value

            )

            +

            self.participation_cost(

                traded_value

            )

        )

    # =====================================================
    # BREAKDOWN
    # =====================================================

    def breakdown(

        self,

        portfolio: Portfolio,

    ) -> dict:

        traded_value = portfolio.nav

        bid_ask = self.bid_ask_cost(

            traded_value

        )

        volatility = self.volatility_cost(

            traded_value

        )

        participation = self.participation_cost(

            traded_value

        )

        total = (

            bid_ask

            +

            volatility

            +

            participation

        )

        return {

            "Bid_Ask_Cost":

                bid_ask,

            "Volatility_Cost":

                volatility,

            "Participation_Cost":

                participation,

            "Total_Slippage":

                total,

        }

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self,

        portfolio: Portfolio,

    ) -> dict:

        return self.breakdown(

            portfolio

        )

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        total_bps = (

            self.bid_ask_spread_bps

            +

            self.volatility_bps

            +

            self.participation_penalty_bps

        )

        return (

            f"{self.__class__.__name__}("

            f"Total={total_bps:.2f}bps"

            f")"

        )

    __str__ = __repr__