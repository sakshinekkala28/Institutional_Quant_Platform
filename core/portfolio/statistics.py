"""
====================================================================
Institutional Quant Platform

Portfolio Statistics

Author : Institutional Quant Platform

Purpose
-------
Portfolio-level statistical calculations.

Consumes

• Portfolio
• PortfolioPosition

Provides

• Holdings
• Total Weight
• Average Alpha
• Weighted Alpha
• Largest Position
• Largest Sector
• Market Cap Statistics
• Liquidity Statistics

====================================================================
"""

from __future__ import annotations

from statistics import mean

from core.models.portfolio import Portfolio

from core.models.portfolio_position import PortfolioPosition


class PortfolioStatistics:
    """
    Portfolio statistical calculations.
    """

    @staticmethod
    def holdings(

        portfolio: Portfolio

    ) -> int:

        return portfolio.holdings

    @staticmethod
    def total_weight(

        portfolio: Portfolio

    ) -> float:

        return portfolio.total_weight

    @staticmethod
    def average_alpha(

        portfolio: Portfolio

    ) -> float:

        if not portfolio.positions:

            return 0.0

        return mean(

            position.alpha_adjusted

            for position

            in portfolio.positions

        )

    @staticmethod
    def weighted_average_alpha(

        portfolio: Portfolio

    ) -> float:

        total_weight = portfolio.total_weight

        if total_weight <= 0:

            return 0.0

        return (

            sum(

                position.alpha_adjusted

                * position.weight

                for position

                in portfolio.positions

            )

            / total_weight

        )

    @staticmethod
    def average_market_cap(

        portfolio: Portfolio

    ) -> float:

        if not portfolio.positions:

            return 0.0

        return mean(

            position.market_cap

            for position

            in portfolio.positions

        )

    @staticmethod
    def average_liquidity(

        portfolio: Portfolio

    ) -> float:

        if not portfolio.positions:

            return 0.0

        return mean(

            position.adv_20d

            for position

            in portfolio.positions

        )

    @staticmethod
    def largest_position(

        portfolio: Portfolio

    ) -> PortfolioPosition | None:

        return portfolio.largest_position

    @staticmethod
    def largest_sector(

        portfolio: Portfolio

    ) -> tuple[str, float] | None:

        return portfolio.largest_sector

    @staticmethod
    def cash_weight(

        portfolio: Portfolio

    ) -> float:

        return max(

            0.0,

            1.0

            - portfolio.total_weight

        )

    @staticmethod
    def invested_weight(

        portfolio: Portfolio

    ) -> float:

        return portfolio.total_weight

    @staticmethod
    def summary(

        portfolio: Portfolio

    ) -> dict:

        largest = (

            portfolio.largest_position

        )

        sector = (

            portfolio.largest_sector

        )

        return {

            "holdings":

                PortfolioStatistics.holdings(

                    portfolio

                ),

            "total_weight":

                PortfolioStatistics.total_weight(

                    portfolio

                ),

            "cash_weight":

                PortfolioStatistics.cash_weight(

                    portfolio

                ),

            "average_alpha":

                PortfolioStatistics.average_alpha(

                    portfolio

                ),

            "weighted_average_alpha":

                PortfolioStatistics.weighted_average_alpha(

                    portfolio

                ),

            "average_market_cap":

                PortfolioStatistics.average_market_cap(

                    portfolio

                ),

            "average_liquidity":

                PortfolioStatistics.average_liquidity(

                    portfolio

                ),

            "largest_position":

                (

                    largest.symbol

                    if largest

                    else None

                ),

            "largest_position_weight":

                (

                    largest.weight

                    if largest

                    else 0.0

                ),

            "largest_sector":

                (

                    sector[0]

                    if sector

                    else None

                ),

            "largest_sector_weight":

                (

                    sector[1]

                    if sector

                    else 0.0

                )

        }
