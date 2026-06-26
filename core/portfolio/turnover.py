"""
====================================================================
Institutional Quant Platform

Portfolio Turnover

Author : Institutional Quant Platform

Purpose
-------
Portfolio turnover calculations.

Consumes

• Portfolio

Provides

• One-Way Turnover
• Two-Way Turnover
• Buy Turnover
• Sell Turnover
• Weight Changes
• Rebalance Summary

====================================================================
"""

from __future__ import annotations

from core.models.portfolio import Portfolio


class PortfolioTurnover:
    """
    Portfolio turnover calculations.
    """

    # =====================================================
    # WEIGHT CHANGES
    # =====================================================

    @staticmethod
    def weight_changes(

        current: Portfolio,

        target: Portfolio

    ) -> dict[str, float]:

        """
        Weight difference between two portfolios.
        """

        symbols = set(

            current.symbols()

        ) | set(

            target.symbols()

        )

        changes = {}

        for symbol in symbols:

            current_position = current.get(

                symbol

            )

            target_position = target.get(

                symbol

            )

            current_weight = (

                current_position.weight

                if current_position

                else 0.0

            )

            target_weight = (

                target_position.weight

                if target_position

                else 0.0

            )

            changes[symbol] = (

                target_weight

                - current_weight

            )

        return dict(

            sorted(

                changes.items()

            )

        )

    # =====================================================
    # BUY TURNOVER
    # =====================================================

    @staticmethod
    def buy_turnover(

        current: Portfolio,

        target: Portfolio

    ) -> float:

        """
        Total buy turnover.
        """

        return sum(

            max(

                change,

                0.0

            )

            for change

            in PortfolioTurnover

            .weight_changes(

                current,

                target

            ).values()

        )

    # =====================================================
    # SELL TURNOVER
    # =====================================================

    @staticmethod
    def sell_turnover(

        current: Portfolio,

        target: Portfolio

    ) -> float:

        """
        Total sell turnover.
        """

        return sum(

            abs(

                min(

                    change,

                    0.0

                )

            )

            for change

            in PortfolioTurnover

            .weight_changes(

                current,

                target

            ).values()

        )

    # =====================================================
    # ONE-WAY TURNOVER
    # =====================================================

    @staticmethod
    def one_way_turnover(

        current: Portfolio,

        target: Portfolio

    ) -> float:

        """
        Institutional one-way turnover.
        """

        return max(

            PortfolioTurnover.buy_turnover(

                current,

                target

            ),

            PortfolioTurnover.sell_turnover(

                current,

                target

            )

        )

    # =====================================================
    # TWO-WAY TURNOVER
    # =====================================================

    @staticmethod
    def two_way_turnover(

        current: Portfolio,

        target: Portfolio

    ) -> float:

        """
        Gross turnover.
        """

        return (

            PortfolioTurnover.buy_turnover(

                current,

                target

            )

            +

            PortfolioTurnover.sell_turnover(

                current,

                target

            )

        )

    # =====================================================
    # REBALANCE REQUIRED
    # =====================================================

    @staticmethod
    def rebalance_required(

        current: Portfolio,

        target: Portfolio,

        threshold: float = 0.01

    ) -> bool:

        """
        Check if rebalance is required.
        """

        return (

            PortfolioTurnover

            .one_way_turnover(

                current,

                target

            )

            > threshold

        )

    # =====================================================
    # SUMMARY
    # =====================================================

    @staticmethod
    def summary(

        current: Portfolio,

        target: Portfolio

    ) -> dict:

        """
        Turnover summary.
        """

        return {

            "buy_turnover":

                PortfolioTurnover.buy_turnover(

                    current,

                    target

                ),

            "sell_turnover":

                PortfolioTurnover.sell_turnover(

                    current,

                    target

                ),

            "one_way_turnover":

                PortfolioTurnover.one_way_turnover(

                    current,

                    target

                ),

            "two_way_turnover":

                PortfolioTurnover.two_way_turnover(

                    current,

                    target

                ),

            "rebalance_required":

                PortfolioTurnover

                .rebalance_required(

                    current,

                    target

                )

        }