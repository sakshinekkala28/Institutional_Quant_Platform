"""
====================================================================
Institutional Quant Platform

Portfolio Position

Author : Institutional Quant Platform

Purpose
-------
Represents a single institutional portfolio position.

Used By

• Portfolio
• PortfolioRepository
• Portfolio Optimizer
• Risk Engine
• Execution Engine
• Governance Engine

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class PortfolioPosition:

    """
    Represents one portfolio holding.
    """

    security_id: str

    symbol: str

    company_name: str

    sector: str

    rank: int

    alpha_adjusted: float

    weight: float

    last_close: float

    market_cap: float

    adv_20d: float

    portfolio_date: str

    engine_version: str

    # =====================================================
    # DERIVED PROPERTIES
    # =====================================================

    @property
    def alpha_rank(self) -> float:

        """
        Alias for ranking.
        """

        return self.alpha_adjusted

    @property
    def liquidity_ratio(self) -> float:

        """
        ADV relative to market cap.
        """

        if self.market_cap <= 0:

            return 0.0

        return self.adv_20d / self.market_cap

    @property
    def is_high_conviction(self) -> bool:

        """
        Institutional conviction.
        """

        return self.weight >= 0.02

    @property
    def market_value(self) -> float:

        """
        Portfolio-relative market value.

        Placeholder until NAV
        becomes configurable.
        """

        NAV = 100_000_000

        return NAV * self.weight

    # =====================================================
    # EXPORT
    # =====================================================

    def to_dict(

        self

    ) -> dict:

        return {

            "Security_ID": self.security_id,

            "Symbol": self.symbol,

            "Company_Name": self.company_name,

            "Sector": self.sector,

            "Rank": self.rank,

            "Alpha_Adjusted": self.alpha_adjusted,

            "Weight": self.weight,

            "Last_Close": self.last_close,

            "Market_Cap": self.market_cap,

            "ADV_20D": self.adv_20d,

            "Portfolio_Date": self.portfolio_date,

            "Engine_Version": self.engine_version

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self

    ) -> str:

        return (

            f"PortfolioPosition("

            f"{self.symbol}, "

            f"{self.weight:.2%}"

            ")"

        )

    __str__ = __repr__