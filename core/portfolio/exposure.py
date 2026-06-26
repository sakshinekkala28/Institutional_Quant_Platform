"""
====================================================================
Institutional Quant Platform

Portfolio Exposure

Author : Institutional Quant Platform

Purpose
-------
Portfolio exposure calculations.

Consumes

• Portfolio
• PortfolioPosition

Provides

• Sector Exposure
• Market Cap Exposure
• Liquidity Exposure
• Top-N Exposure
• Position Exposure
• Concentration Metrics

====================================================================
"""

from __future__ import annotations

from collections import defaultdict

from core.models.portfolio import Portfolio


class PortfolioExposure:
    """
    Portfolio exposure calculations.
    """

    # =====================================================
    # SECTOR
    # =====================================================

    @staticmethod
    def sector(

        portfolio: Portfolio

    ) -> dict[str, float]:

        """
        Sector weight exposure.
        """

        exposure = defaultdict(

            float

        )

        for position in portfolio:

            exposure[

                position.sector

            ] += position.weight

        return dict(

            sorted(

                exposure.items(),

                key=lambda item: item[1],

                reverse=True

            )

        )

    # =====================================================
    # MARKET CAP
    # =====================================================

    @staticmethod
    def market_cap(

        portfolio: Portfolio

    ) -> dict[str, float]:

        """
        Market capitalization exposure.
        """

        exposure = defaultdict(

            float

        )

        for position in portfolio:

            exposure[

                position.symbol

            ] = position.market_cap

        return dict(

            sorted(

                exposure.items(),

                key=lambda item: item[1],

                reverse=True

            )

        )

    # =====================================================
    # LIQUIDITY
    # =====================================================

    @staticmethod
    def liquidity(

        portfolio: Portfolio

    ) -> dict[str, float]:

        """
        Liquidity exposure using ADV.
        """

        exposure = defaultdict(

            float

        )

        for position in portfolio:

            exposure[

                position.symbol

            ] = position.adv_20d

        return dict(

            sorted(

                exposure.items(),

                key=lambda item: item[1],

                reverse=True

            )

        )

    # =====================================================
    # POSITION
    # =====================================================

    @staticmethod
    def positions(

        portfolio: Portfolio

    ) -> dict[str, float]:

        """
        Position weight exposure.
        """

        return {

            position.symbol:

            position.weight

            for position

            in sorted(

                portfolio,

                key=lambda p: p.weight,

                reverse=True

            )

        }

    # =====================================================
    # TOP N
    # =====================================================

    @staticmethod
    def top_n(

        portfolio: Portfolio,

        n: int = 10

    ) -> float:

        """
        Combined weight of top-N holdings.
        """

        if n < 1:

            raise ValueError(

                "n must be greater than zero."

            )

        return sum(

            position.weight

            for position

            in portfolio.top_holdings(

                n

            )

        )

    # =====================================================
    # MAX POSITION
    # =====================================================

    @staticmethod
    def largest_position(

        portfolio: Portfolio

    ) -> float:

        """
        Largest position weight.
        """

        largest = portfolio.largest_position

        if largest is None:

            return 0.0

        return largest.weight

    # =====================================================
    # MAX SECTOR
    # =====================================================

    @staticmethod
    def largest_sector(

        portfolio: Portfolio

    ) -> tuple[str, float] | None:

        """
        Largest sector exposure.
        """

        return portfolio.largest_sector

    # =====================================================
    # SUMMARY
    # =====================================================

    @staticmethod
    def summary(

        portfolio: Portfolio

    ) -> dict:

        """
        Portfolio exposure summary.
        """

        return {

            "sector_exposure":

                PortfolioExposure.sector(

                    portfolio

                ),

            "largest_sector":

                PortfolioExposure.largest_sector(

                    portfolio

                ),

            "largest_position":

                PortfolioExposure.largest_position(

                    portfolio

                ),

            "top5_exposure":

                PortfolioExposure.top_n(

                    portfolio,

                    5

                ),

            "top10_exposure":

                PortfolioExposure.top_n(

                    portfolio,

                    10

                )

        }