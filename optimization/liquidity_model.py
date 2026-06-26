"""
====================================================================
Institutional Quant Platform

Liquidity Model

Author : Institutional Quant Platform

Purpose
-------
Institutional liquidity model.

Provides

• Average Daily Volume (ADV)
• Participation Rate
• Liquidity Ratio
• Liquidity Penalty
• Tradability Score

Used By

• TransactionCostModel
• CapacityModel
• Optimizers
• Execution Engine
• Live Rebalance

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from core.models.portfolio import Portfolio


@dataclass(slots=True)
class LiquidityModel:
    """
    Institutional liquidity model.
    """

    max_participation_rate: float = 0.10

    liquidity_penalty_bps: float = 5.0

    minimum_adv: float = 1_000_000.0

    # =====================================================
    # PARTICIPATION RATE
    # =====================================================

    def participation_rate(

        self,

        traded_value: float,

        average_daily_volume: float,

    ) -> float:

        if average_daily_volume <= 0.0:

            return 1.0

        return (

            traded_value

            /

            average_daily_volume

        )

    # =====================================================
    # LIQUIDITY PENALTY
    # =====================================================

    def penalty(

        self,

        traded_value: float,

        average_daily_volume: float,

    ) -> float:

        participation = self.participation_rate(

            traded_value,

            average_daily_volume,

        )

        if participation <= self.max_participation_rate:

            return 0.0

        excess = (

            participation

            -

            self.max_participation_rate

        )

        return (

            traded_value

            * excess

            * self.liquidity_penalty_bps

            / 10_000.0

        )

    # =====================================================
    # PORTFOLIO LIQUIDITY
    # =====================================================

    def calculate(

        self,

        portfolio: Portfolio,

    ) -> float:

        total = 0.0

        for position in portfolio:

            adv = getattr(

                position,

                "adv_20d",

                0.0,

            )

            traded = (

                position.weight

                * portfolio.nav

            )

            total += self.penalty(

                traded,

                adv,

            )

        return float(

            total

        )

    # =====================================================
    # LIQUIDITY SCORE
    # =====================================================

    def liquidity_score(

        self,

        portfolio: Portfolio,

    ) -> float:

        scores = []

        for position in portfolio:

            adv = getattr(

                position,

                "adv_20d",

                0.0,

            )

            traded = (

                position.weight

                * portfolio.nav

            )

            participation = self.participation_rate(

                traded,

                adv,

            )

            score = max(

                0.0,

                1.0

                -

                participation

            )

            scores.append(

                score

            )

        if not scores:

            return 0.0

        return float(

            sum(

                scores

            )

            /

            len(

                scores

            )

        )

    # =====================================================
    # LIQUID PORTFOLIO
    # =====================================================

    def is_liquid(

        self,

        portfolio: Portfolio,

    ) -> bool:

        for position in portfolio:

            adv = getattr(

                position,

                "adv_20d",

                0.0,

            )

            if adv < self.minimum_adv:

                return False

        return True

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self,

        portfolio: Portfolio,

    ) -> dict:

        return {

            "Liquidity_Cost":

                self.calculate(

                    portfolio

                ),

            "Liquidity_Score":

                self.liquidity_score(

                    portfolio

                ),

            "Tradable":

                self.is_liquid(

                    portfolio

                ),

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"MaxParticipation="

            f"{self.max_participation_rate:.0%}"

            f")"

        )

    __str__ = __repr__