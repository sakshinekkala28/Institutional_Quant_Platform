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

from collections import defaultdict

from core.models.portfolio_position import PortfolioPosition

import pandas as pd


@dataclass(slots=True)
class Portfolio:

    """
    Institutional Portfolio.
    """

    positions: list[PortfolioPosition]

    nav: float = 100_000_000.0

    __hash__ = None

    # =====================================================
    # COLLECTION PROTOCOL
    # =====================================================

    def __iter__(

        self

    ):

        """
        Iterate over portfolio positions.
        """

        return iter(

            self.positions

        )

    def __reversed__(

        self

    ):

        """
        Reverse iteration.
        """

        return reversed(

            self.positions

        )
        
    def __len__(

        self

    ) -> int:

        """
        Number of holdings.
        """

        return len(

            self.positions

        )
    
    def __contains__(

        self,

        symbol: str

    ) -> bool:

        """
        Membership test by symbol.
        """

        return any(

            position.symbol == symbol

            for position

            in self

        )
    
    def __getitem__(

        self,

        key: int | str

    ) -> PortfolioPosition:

        """
        Access by index or symbol.
        """

        if isinstance(

            key,

            int

        ):

            return self.positions[key]

        if isinstance(

            key,

            str

        ):

            position = self.get(

                key

            )

            if position is None:

                raise KeyError(

                    f"Portfolio position '{key}' not found."

                )

            return position

        raise TypeError(

            "Key must be int or str."

        )
    
    def __bool__(

        self

    ) -> bool:

        """
        True if portfolio has positions.
        """

        return len(

            self

        ) > 0

    # =====================================================
    # BASIC
    # =====================================================

    @property
    def holdings(

        self

    ) -> int:

        return len(

            self

        )

    @property
    def total_weight(

        self

    ) -> float:

        return sum(

            position.weight

            for position

            in self

        )

    @property
    def average_alpha(

        self

    ) -> float:

        if self.is_empty:

            return 0.0

        return (

            sum(

                position.alpha_adjusted

                for position

                in self

            )

            / len(

                self

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

            in self

        ]

    def exists(

        self,

        symbol: str

    ) -> bool:

        return symbol in self

    def get(

        self,

        symbol: str

    ) -> PortfolioPosition | None:

        for position in self:

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

        if n < 1:

            raise ValueError(

                "n must be greater than zero."

            )
    
        return sorted(

            self,

            key=lambda position: position.weight,

            reverse=True

        )[:n]

    def sector_weights(

        self

    ) -> dict[str, float]:

        weights = defaultdict(

            float

        )

        for position in self:

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

        if self.is_empty:

            return None

        return max(

            self,

            key=lambda position: position.weight

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

    @property
    def is_empty(

        self

    ) -> bool:

        """
        Whether the portfolio contains no positions.
        """

        return len(

            self

        ) == 0

    @property
    def position_count(

        self

    ) -> int:

        """
        Number of positions.
        """

        return len(

            self

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

    ) -> pd.DataFrame:

        return pd.DataFrame(

            [

                position.to_dict()

                for position

                in self

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