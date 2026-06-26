"""
====================================================================
Institutional Quant Platform

Portfolio Allocation

Author : Institutional Quant Platform

Purpose
-------
Portfolio allocation calculations.

Consumes

• Portfolio
• PortfolioPosition

Provides

• Equal Weight
• Allocation Drift
• Target Allocation
• Sector Allocation
• Normalized Weights
• Active Weights

====================================================================
"""

from __future__ import annotations

from core.models.portfolio import Portfolio


class PortfolioAllocation:
    """
    Portfolio allocation calculations.
    """

    # =====================================================
    # EQUAL WEIGHT
    # =====================================================

    @staticmethod
    def equal_weight(

        portfolio: Portfolio

    ) -> float:

        """
        Equal weight allocation.
        """

        if portfolio.is_empty:

            return 0.0

        return 1.0 / portfolio.position_count

    # =====================================================
    # TARGET WEIGHTS
    # =====================================================

    @staticmethod
    def target_weights(

        portfolio: Portfolio

    ) -> dict[str, float]:

        """
        Equal-weight target allocation.
        """

        target = PortfolioAllocation.equal_weight(

            portfolio

        )

        return {

            position.symbol:

            target

            for position

            in portfolio

        }

    # =====================================================
    # CURRENT WEIGHTS
    # =====================================================

    @staticmethod
    def current_weights(

        portfolio: Portfolio

    ) -> dict[str, float]:

        """
        Current portfolio weights.
        """

        return {

            position.symbol:

            position.weight

            for position

            in portfolio

        }

    # =====================================================
    # ACTIVE WEIGHTS
    # =====================================================

    @staticmethod
    def active_weights(

        portfolio: Portfolio

    ) -> dict[str, float]:

        """
        Difference between current
        and equal-weight allocation.
        """

        target = PortfolioAllocation.equal_weight(

            portfolio

        )

        return {

            position.symbol:

            position.weight - target

            for position

            in portfolio

        }

    # =====================================================
    # DRIFT
    # =====================================================

    @staticmethod
    def allocation_drift(

        portfolio: Portfolio

    ) -> float:

        """
        Total allocation drift.
        """

        return sum(

            abs(weight)

            for weight

            in PortfolioAllocation.active_weights(

                portfolio

            ).values()

        )

    # =====================================================
    # NORMALIZED
    # =====================================================

    @staticmethod
    def normalized_weights(

        portfolio: Portfolio

    ) -> dict[str, float]:

        """
        Normalize weights to 100%.
        """

        total = portfolio.total_weight

        if total <= 0:

            return {}

        return {

            position.symbol:

            position.weight / total

            for position

            in portfolio

        }

    # =====================================================
    # SECTOR ALLOCATION
    # =====================================================

    @staticmethod
    def sector_allocation(

        portfolio: Portfolio

    ) -> dict[str, float]:

        """
        Sector allocation.
        """

        return portfolio.sector_weights()

    # =====================================================
    # MAX POSITION
    # =====================================================

    @staticmethod
    def largest_weight(

        portfolio: Portfolio

    ) -> float:

        """
        Largest portfolio weight.
        """

        if portfolio.is_empty:

            return 0.0

        return portfolio.largest_position.weight

    # =====================================================
    # MIN POSITION
    # =====================================================

    @staticmethod
    def smallest_weight(

        portfolio: Portfolio

    ) -> float:

        """
        Smallest portfolio weight.
        """

        if portfolio.is_empty:

            return 0.0

        return min(

            position.weight

            for position

            in portfolio

        )

    # =====================================================
    # SUMMARY
    # =====================================================

    @staticmethod
    def summary(

        portfolio: Portfolio

    ) -> dict:

        """
        Allocation summary.
        """

        return {

            "equal_weight":

                PortfolioAllocation.equal_weight(

                    portfolio

                ),

            "allocation_drift":

                PortfolioAllocation.allocation_drift(

                    portfolio

                ),

            "largest_weight":

                PortfolioAllocation.largest_weight(

                    portfolio

                ),

            "smallest_weight":

                PortfolioAllocation.smallest_weight(

                    portfolio

                ),

            "sector_allocation":

                PortfolioAllocation.sector_allocation(

                    portfolio

                )

        }