"""
====================================================================
Institutional Quant Platform

Market Impact Model

Author : Institutional Quant Platform

Purpose
-------
Institutional market impact model.

Provides

• Temporary Impact
• Permanent Impact
• Participation Rate
• Total Market Impact

Used By

• ExecutionModel
• ExecutionEngine
• BrokerSimulator
• TransactionCostModel

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from execution.order import Order


@dataclass(slots=True)
class MarketImpact:
    """
    Institutional market impact model.
    """

    impact_coefficient: float = 15.0

    participation_limit: float = 0.10

    # =====================================================
    # PARTICIPATION RATE
    # =====================================================

    def participation_rate(

        self,

        order: Order,

        average_daily_volume: float,

    ) -> float:

        if average_daily_volume <= 0.0:

            return 1.0

        return (

            order.quantity

            /

            average_daily_volume

        )

    # =====================================================
    # TEMPORARY IMPACT
    # =====================================================

    def temporary_impact(

        self,

        participation_rate: float,

    ) -> float:

        return (

            self.impact_coefficient

            *

            participation_rate ** 0.50

        )

    # =====================================================
    # PERMANENT IMPACT
    # =====================================================

    def permanent_impact(

        self,

        participation_rate: float,

    ) -> float:

        return (

            0.50

            *

            self.temporary_impact(

                participation_rate

            )

        )

    # =====================================================
    # TOTAL IMPACT (BPS)
    # =====================================================

    def calculate(

        self,

        order: Order,

        average_daily_volume: float = 1_000_000.0,

    ) -> float:

        participation = self.participation_rate(

            order,

            average_daily_volume,

        )

        temporary = self.temporary_impact(

            participation

        )

        permanent = self.permanent_impact(

            participation

        )

        return (

            temporary

            +

            permanent

        )

    # =====================================================
    # EXECUTION PRICE
    # =====================================================

    def impacted_price(

        self,

        order: Order,

        average_daily_volume: float = 1_000_000.0,

    ) -> float:

        if order.price is None:

            return 0.0

        impact = self.calculate(

            order,

            average_daily_volume,

        )

        multiplier = (

            1.0

            +

            impact

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
    # SUMMARY
    # =====================================================

    def summary(

        self,

        order: Order,

        average_daily_volume: float = 1_000_000.0,

    ) -> dict:

        participation = self.participation_rate(

            order,

            average_daily_volume,

        )

        temporary = self.temporary_impact(

            participation

        )

        permanent = self.permanent_impact(

            participation

        )

        return {

            "Participation_Rate":

                participation,

            "Temporary_Impact_bps":

                temporary,

            "Permanent_Impact_bps":

                permanent,

            "Total_Impact_bps":

                temporary + permanent,

            "Impacted_Price":

                self.impacted_price(

                    order,

                    average_daily_volume,

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

            f"Coefficient={self.impact_coefficient:.2f}"

            f")"

        )

    __str__ = __repr__