"""
====================================================================
Institutional Quant Platform

Portfolio Diversification

Author : Institutional Quant Platform

Purpose
-------
Portfolio diversification calculations.

Consumes

• Portfolio

Provides

• Herfindahl-Hirschman Index (HHI)
• Effective Number of Holdings
• Concentration Ratio
• Equal Weight Score
• Diversification Score

====================================================================
"""

from __future__ import annotations

from core.models.portfolio import Portfolio


class PortfolioDiversification:
    """
    Portfolio diversification calculations.
    """

    # =====================================================
    # HHI
    # =====================================================

    @staticmethod
    def hhi(

        portfolio: Portfolio

    ) -> float:

        """
        Herfindahl-Hirschman Index.
        """

        return sum(

            position.weight ** 2

            for position

            in portfolio

        )

    # =====================================================
    # EFFECTIVE HOLDINGS
    # =====================================================

    @staticmethod
    def effective_holdings(

        portfolio: Portfolio

    ) -> float:

        """
        Effective number of holdings.

        1 / HHI
        """

        hhi = PortfolioDiversification.hhi(

            portfolio

        )

        if hhi <= 0:

            return 0.0

        return 1.0 / hhi

    # =====================================================
    # CONCENTRATION
    # =====================================================

    @staticmethod
    def concentration_ratio(

        portfolio: Portfolio,

        top_n: int = 10

    ) -> float:

        """
        Weight of largest N holdings.
        """

        if top_n < 1:

            raise ValueError(

                "top_n must be greater than zero."

            )

        return sum(

            position.weight

            for position

            in portfolio.top_holdings(

                top_n

            )

        )

    # =====================================================
    # EQUAL WEIGHT SCORE
    # =====================================================

    @staticmethod
    def equal_weight_score(

        portfolio: Portfolio

    ) -> float:

        """
        Measure closeness to equal weighting.
        """

        if portfolio.is_empty:

            return 0.0

        target = 1.0 / portfolio.position_count

        deviation = sum(

            abs(

                position.weight

                - target

            )

            for position

            in portfolio

        )

        return max(

            0.0,

            1.0

            - deviation

        )

    # =====================================================
    # DIVERSIFICATION SCORE
    # =====================================================

    @staticmethod
    def diversification_score(

        portfolio: Portfolio

    ) -> float:

        """
        Diversification score (0–100).
        """

        if portfolio.is_empty:

            return 0.0

        effective = (

            PortfolioDiversification

            .effective_holdings(

                portfolio

            )

        )

        score = (

            effective

            / portfolio.position_count

        ) * 100

        return min(

            score,

            100.0

        )

    # =====================================================
    # SUMMARY
    # =====================================================

    @staticmethod
    def summary(

        portfolio: Portfolio

    ) -> dict:

        """
        Diversification summary.
        """

        return {

            "hhi":

                PortfolioDiversification.hhi(

                    portfolio

                ),

            "effective_holdings":

                PortfolioDiversification

                .effective_holdings(

                    portfolio

                ),

            "top5_concentration":

                PortfolioDiversification

                .concentration_ratio(

                    portfolio,

                    5

                ),

            "top10_concentration":

                PortfolioDiversification

                .concentration_ratio(

                    portfolio,

                    10

                ),

            "equal_weight_score":

                PortfolioDiversification

                .equal_weight_score(

                    portfolio

                ),

            "diversification_score":

                PortfolioDiversification

                .diversification_score(

                    portfolio

                )

        }