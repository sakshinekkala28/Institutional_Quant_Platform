"""
====================================================================
Institutional Quant Platform

Portfolio Constraints

Author : Institutional Quant Platform

Purpose
-------
Institutional portfolio constraint engine.

Provides

• Fully Invested
• Long Only
• Weight Limits
• Position Limits
• Empty Portfolio Check
• Concentration Check

Used By

• PortfolioService
• OptimizationService
• GovernanceService
• Portfolio Optimizer

====================================================================
"""

from __future__ import annotations

from core.models.portfolio import Portfolio


class PortfolioConstraints:
    """
    Institutional portfolio constraint engine.
    """

    # =====================================================
    # CONFIGURATION
    # =====================================================

    MIN_WEIGHT = 0.0

    MAX_WEIGHT = 0.10

    MIN_HOLDINGS = 1

    MAX_HOLDINGS = 500

    WEIGHT_TOLERANCE = 1e-6

    # =====================================================
    # BASIC CONSTRAINTS
    # =====================================================

    @classmethod
    def fully_invested(cls, portfolio: Portfolio) -> bool:

        return portfolio.weight_error() <= cls.WEIGHT_TOLERANCE

    @classmethod
    def non_empty(cls, portfolio: Portfolio) -> bool:

        return not portfolio.is_empty

    @classmethod
    def long_only(cls, portfolio: Portfolio) -> bool:

        return all(position.weight >= cls.MIN_WEIGHT for position in portfolio)

    @classmethod
    def weight_limits(cls, portfolio: Portfolio) -> bool:

        return all(
            cls.MIN_WEIGHT <= position.weight <= cls.MAX_WEIGHT
            for position in portfolio
        )

    @classmethod
    def holdings_limit(cls, portfolio: Portfolio) -> bool:

        return cls.MIN_HOLDINGS <= portfolio.holdings <= cls.MAX_HOLDINGS

    # =====================================================
    # CONCENTRATION
    # =====================================================

    @classmethod
    def concentration(cls, portfolio: Portfolio) -> bool:

        largest = portfolio.largest_position

        if largest is None:
            return False

        return largest.weight <= cls.MAX_WEIGHT

    # =====================================================
    # VALIDATION
    # =====================================================

    @classmethod
    def validate(cls, portfolio: Portfolio) -> dict[str, bool]:

        return {
            "non_empty": cls.non_empty(portfolio),
            "fully_invested": cls.fully_invested(portfolio),
            "long_only": cls.long_only(portfolio),
            "weight_limits": cls.weight_limits(portfolio),
            "holdings_limit": cls.holdings_limit(portfolio),
            "concentration": cls.concentration(portfolio),
        }

    # =====================================================
    # OVERALL STATUS
    # =====================================================

    @classmethod
    def passed(cls, portfolio: Portfolio) -> bool:

        return all(cls.validate(portfolio).values())

    # =====================================================
    # FAILED CONSTRAINTS
    # =====================================================

    @classmethod
    def failed(cls, portfolio: Portfolio) -> list[str]:

        return [name for name, passed in cls.validate(portfolio).items() if not passed]

    # =====================================================
    # SUMMARY
    # =====================================================

    @classmethod
    def summary(cls, portfolio: Portfolio) -> dict:

        validation = cls.validate(portfolio)

        return {
            "passed": all(validation.values()),
            "constraints": validation,
            "failed": cls.failed(portfolio),
        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(self) -> str:

        return f"{self.__class__.__name__}()"

    __str__ = __repr__
