"""
====================================================================
Institutional Quant Platform

Capacity Model

Author : Institutional Quant Platform

Purpose
-------
Institutional strategy capacity model.

Estimates the maximum deployable capital
before execution quality materially
degrades.

Provides

• Strategy Capacity
• Capacity Utilization
• Liquidity Utilization
• ADV Utilization
• Capacity Score

Used By

• TransactionCostModel
• LiquidityModel
• Optimizers
• Live Rebalance Engine
• Portfolio Construction

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from core.models.portfolio import Portfolio


@dataclass(slots=True)
class CapacityModel:
    """
    Institutional capacity model.
    """

    max_participation_rate: float = 0.10

    utilization_warning: float = 0.70

    utilization_critical: float = 0.90

    # =====================================================
    # POSITION CAPACITY
    # =====================================================

    def position_capacity(

        self,

        position,

    ) -> float:

        adv = getattr(

            position,

            "adv_20d",

            0.0,

        )

        return (

            adv

            *

            self.max_participation_rate

        )

    # =====================================================
    # PORTFOLIO CAPACITY
    # =====================================================

    def portfolio_capacity(

        self,

        portfolio: Portfolio,

    ) -> float:

        capacity = 0.0

        for position in portfolio:

            capacity += self.position_capacity(

                position

            )

        return float(

            capacity

        )

    # =====================================================
    # UTILIZATION
    # =====================================================

    def utilization(

        self,

        portfolio: Portfolio,

    ) -> float:

        capacity = self.portfolio_capacity(

            portfolio

        )

        if capacity <= 0.0:

            return 1.0

        return (

            portfolio.nav

            /

            capacity

        )

    # =====================================================
    # REMAINING CAPACITY
    # =====================================================

    def remaining_capacity(

        self,

        portfolio: Portfolio,

    ) -> float:

        capacity = self.portfolio_capacity(

            portfolio

        )

        remaining = (

            capacity

            -

            portfolio.nav

        )

        return max(

            0.0,

            remaining,

        )

    # =====================================================
    # CAPACITY SCORE
    # =====================================================

    def capacity_score(

        self,

        portfolio: Portfolio,

    ) -> float:

        utilization = self.utilization(

            portfolio

        )

        score = (

            1.0

            -

            utilization

        )

        return max(

            0.0,

            min(

                score,

                1.0,

            ),

        )

    # =====================================================
    # STATUS
    # =====================================================

    def status(

        self,

        portfolio: Portfolio,

    ) -> str:

        utilization = self.utilization(

            portfolio

        )

        if utilization >= self.utilization_critical:

            return "CRITICAL"

        if utilization >= self.utilization_warning:

            return "WARNING"

        return "HEALTHY"

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self,

        portfolio: Portfolio,

    ) -> dict:

        return {

            "Portfolio_NAV":

                portfolio.nav,

            "Capacity":

                self.portfolio_capacity(

                    portfolio

                ),

            "Remaining_Capacity":

                self.remaining_capacity(

                    portfolio

                ),

            "Utilization":

                self.utilization(

                    portfolio

                ),

            "Capacity_Score":

                self.capacity_score(

                    portfolio

                ),

            "Status":

                self.status(

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