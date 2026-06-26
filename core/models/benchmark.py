"""
====================================================================
Institutional Quant Platform

Benchmark

Author : Institutional Quant Platform

Purpose
-------
Institutional benchmark model.

Represents an investment benchmark.

Used By

• Risk Engine
• Tracking Error
• Information Ratio
• Attribution
• Performance Engine
• Optimizer

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from datetime import date

from core.models.return_series import ReturnSeries


@dataclass(slots=True)
class Benchmark:
    """
    Institutional benchmark.
    """

    name: str

    symbol: str

    return_series: ReturnSeries

    constituents: dict[str, float] = field(

        default_factory=dict

    )

    currency: str = "INR"

    inception_date: date | None = None

    risk_free_rate: float = 0.0

    metadata: dict[str, str] = field(

        default_factory=dict

    )

    __hash__ = None

    # =====================================================
    # COLLECTION
    # =====================================================

    def __contains__(

        self,

        symbol: str

    ) -> bool:

        return symbol in self.constituents

    def __len__(

        self

    ) -> int:

        return len(

            self.constituents

        )

    def __bool__(

        self

    ) -> bool:

        return bool(

            self.constituents

        )

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

            self.constituents.values()

        )

    @property
    def fully_invested(

        self

    ) -> bool:

        return abs(

            self.total_weight - 1.0

        ) < 1e-6

    # =====================================================
    # LOOKUPS
    # =====================================================

    def weight(

        self,

        symbol: str

    ) -> float:

        return self.constituents.get(

            symbol,

            0.0

        )

    def exists(

        self,

        symbol: str

    ) -> bool:

        return symbol in self

    # =====================================================
    # RETURNS
    # =====================================================

    @property
    def annual_return(

        self

    ) -> float:

        return (

            self.return_series

            .annualized_return

        )

    @property
    def annual_volatility(

        self

    ) -> float:

        return (

            self.return_series

            .annualized_volatility

        )

    @property
    def sharpe_ratio(

        self

    ) -> float:

        return (

            self.return_series

            .sharpe_ratio

        )

    # =====================================================
    # VALIDATION
    # =====================================================

    def validate(

        self

    ) -> None:

        if not self.name:

            raise ValueError(

                "Benchmark name is required."

            )

        if not self.symbol:

            raise ValueError(

                "Benchmark symbol is required."

            )

        if not self.fully_invested:

            raise ValueError(

                "Benchmark weights must sum to 1.0."

            )

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self

    ) -> dict:

        return {

            "name": self.name,

            "symbol": self.symbol,

            "currency": self.currency,

            "holdings": self.holdings,

            "annual_return": self.annual_return,

            "annual_volatility":

                self.annual_volatility,

            "sharpe_ratio":

                self.sharpe_ratio

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self

    ) -> str:

        return (

            f"Benchmark("

            f"{self.symbol}, "

            f"{self.holdings} holdings)"

        )

    __str__ = __repr__