"""
====================================================================
Institutional Quant Platform

Constraint Engine

Author : Institutional Quant Platform

Purpose
-------
Institutional optimization constraint engine.

Validates portfolio constraints before
and after optimization.

Provides

• Weight Constraints
• Holdings Constraints
• Sector Constraints
• Position Constraints
• Long Only Constraints
• Fully Invested Constraints

Used By

• Optimization Service
• All Optimizers

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field

from core.models.portfolio import Portfolio


@dataclass(slots=True)
class ConstraintEngine:
    """
    Institutional constraint engine.
    """

    min_weight: float = 0.0

    max_weight: float = 0.10

    min_holdings: int = 20

    max_holdings: int = 200

    fully_invested: bool = True

    long_only: bool = True

    max_sector_weight: float = 0.30

    tolerance: float = 1e-6

    violations: list[str] = field(

        default_factory=list

    )

    # =====================================================
    # VALIDATE
    # =====================================================

    def validate(

        self,

        portfolio: Portfolio,

    ) -> None:

        self.violations.clear()

        self._validate_holdings(

            portfolio

        )

        self._validate_weights(

            portfolio

        )

        self._validate_fully_invested(

            portfolio

        )

        self._validate_long_only(

            portfolio

        )

        self._validate_sector_limits(

            portfolio

        )

        if self.violations:

            raise ValueError(

                "\n".join(

                    self.violations

                )

            )

    # =====================================================
    # HOLDINGS
    # =====================================================

    def _validate_holdings(

        self,

        portfolio: Portfolio,

    ) -> None:

        if portfolio.holdings < self.min_holdings:

            self.violations.append(

                f"Minimum holdings: {self.min_holdings}"

            )

        if portfolio.holdings > self.max_holdings:

            self.violations.append(

                f"Maximum holdings: {self.max_holdings}"

            )

    # =====================================================
    # POSITION WEIGHTS
    # =====================================================

    def _validate_weights(

        self,

        portfolio: Portfolio,

    ) -> None:

        for position in portfolio:

            if position.weight < self.min_weight:

                self.violations.append(

                    f"{position.symbol}: below minimum weight."

                )

            if position.weight > self.max_weight:

                self.violations.append(

                    f"{position.symbol}: above maximum weight."

                )

    # =====================================================
    # FULLY INVESTED
    # =====================================================

    def _validate_fully_invested(

        self,

        portfolio: Portfolio,

    ) -> None:

        if (

            self.fully_invested

            and

            abs(

                portfolio.total_weight

                - 1.0

            )

            > self.tolerance

        ):

            self.violations.append(

                "Portfolio is not fully invested."

            )

    # =====================================================
    # LONG ONLY
    # =====================================================

    def _validate_long_only(

        self,

        portfolio: Portfolio,

    ) -> None:

        if not self.long_only:

            return

        for position in portfolio:

            if position.weight < 0.0:

                self.violations.append(

                    f"{position.symbol}: negative weight."

                )

    # =====================================================
    # SECTOR LIMITS
    # =====================================================

    def _validate_sector_limits(

        self,

        portfolio: Portfolio,

    ) -> None:

        sectors = portfolio.sector_weights()

        for sector, weight in sectors.items():

            if weight > self.max_sector_weight:

                self.violations.append(

                    f"{sector}: sector limit exceeded."

                )

    # =====================================================
    # STATUS
    # =====================================================

    @property
    def is_valid(

        self,

    ) -> bool:

        return len(

            self.violations

        ) == 0

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self,

    ) -> dict:

        return {

            "valid":

                self.is_valid,

            "violations":

                self.violations,

            "count":

                len(

                    self.violations

                )

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Valid={self.is_valid}, "

            f"Violations={len(self.violations)}"

            f")"

        )

    __str__ = __repr__