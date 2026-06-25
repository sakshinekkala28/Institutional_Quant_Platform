"""
====================================================================
Institutional Quant Platform

Portfolio

Author : Institutional Quant Platform

Purpose
-------
Institutional Portfolio Aggregate.

Represents an entire portfolio and provides
portfolio-level analytics.

Used By

• PortfolioRepository
• Optimizer
• Risk Engine
• Constraint Engine
• Execution Engine
• Governance Engine

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from collections import defaultdict

from core.models.portfolio_position import PortfolioPosition


@dataclass(slots=True)
class Portfolio:

    """
    Institutional Portfolio.
    """

    positions: list[PortfolioPosition]

    nav: float = 100_000_000.0

    # =====================================================
    # BASIC
    # =====================================================

    @property
    def holdings(

        self

    ) -> int:

        return len(

            self.positions

        )

    @property
    def total_weight(

        self

    ) -> float:

        return sum(

            position.weight

            for position

            in self.positions

        )

    @property
    def average_alpha(

        self

    ) -> float:

        if not self.positions:

            return 0.0

        return (

            sum(

                position.alpha_adjusted

                for position

                in self.positions

            )

            / len(

                self.positions

            )

        )

    # =====================================================
    # LOOKUPS
    # =====================================================

    def symbols(

        self

    ) -> list[str]:

        return [

            position.symbol

            for position

            in self.positions

        ]

    def exists(

        self,

        symbol: str

    ) -> bool:

        return any(

            position.symbol == symbol

            for position

            in self.positions

        )

    def get(

        self,

        symbol: str

    ) -> PortfolioPosition | None:

        for position in self.positions:

            if position.symbol == symbol:

                return position

        return None

    # =====================================================
    # ANALYTICS
    # =====================================================

    def top_holdings(

        self,

        n: int = 10

    ) -> list[PortfolioPosition]:

        return sorted(

            self.positions,

            key=lambda p: p.weight,

            reverse=True

        )[:n]

    def sector_weights(

        self

    ) -> dict[str, float]:

        weights = defaultdict(

            float

        )

        for position in self.positions:

            weights[

                position.sector

            ] += position.weight

        return dict(

            weights

        )

    @property
    def largest_position(

        self

    ) -> PortfolioPosition | None:

        if not self.positions:

            return None

        return max(

            self.positions,

            key=lambda p: p.weight

        )

    @property
    def largest_sector(

        self

    ) -> tuple[str, float] | None:

        sectors = self.sector_weights()

        if not sectors:

            return None

        return max(

            sectors.items(),

            key=lambda x: x[1]

        )

    # =====================================================
    # VALIDATION
    # =====================================================

    def weight_error(

        self

    ) -> float:

        return abs(

            1.0

            - self.total_weight

        )

    @property
    def fully_invested(

        self

    ) -> bool:

        return self.weight_error() < 1e-6

    # =====================================================
    # EXPORT
    # =====================================================

    def to_dataframe(

        self

    ):

        import pandas as pd

        return pd.DataFrame(

            [

                position.to_dict()

                for position

                in self.positions

            ]

        )

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self

    ) -> dict:

        return {

            "Holdings":

                self.holdings,

            "Total_Weight":

                self.total_weight,

            "Average_Alpha":

                self.average_alpha,

            "Largest_Position":

                (

                    self.largest_position.symbol

                    if self.largest_position

                    else None

                ),

            "Largest_Sector":

                (

                    self.largest_sector

                    if self.largest_sector

                    else None

                )

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self

    ) -> str:

        return (

            f"Portfolio("

            f"Holdings={self.holdings}, "

            f"Weight={self.total_weight:.2%}"

            ")"

        )

    __str__ = __repr__