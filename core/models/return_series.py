"""
====================================================================
Institutional Quant Platform

Return Series

Author : Institutional Quant Platform

Purpose
-------
Immutable time-series of returns.

Used By

• Risk Engine
• Optimizer
• Performance Attribution
• Factor Models
• Tracking Error
• VaR
• CVaR
• Sharpe Ratio
• Sortino Ratio

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from datetime import datetime

from math import sqrt
from statistics import fmean
from statistics import stdev


@dataclass(slots=True, frozen=True)
class ReturnObservation:
    """
    Single return observation.
    """

    timestamp: datetime

    value: float


@dataclass(slots=True)
class ReturnSeries:
    """
    Institutional return series.
    """

    observations: list[ReturnObservation]

    frequency: str = "daily"

    risk_free_rate: float = 0.0

    __hash__ = None

    # =====================================================
    # COLLECTION PROTOCOL
    # =====================================================

    def __iter__(

        self

    ):

        return iter(

            self.observations

        )

    def __len__(

        self

    ) -> int:

        return len(

            self.observations

        )

    def __getitem__(

        self,

        index: int

    ) -> ReturnObservation:

        return self.observations[index]

    def __bool__(

        self

    ) -> bool:

        return len(

            self

        ) > 0

    # =====================================================
    # BASIC
    # =====================================================

    @property
    def values(

        self

    ) -> list[float]:

        return [

            observation.value

            for observation

            in self

        ]

    @property
    def dates(

        self

    ) -> list[datetime]:

        return [

            observation.timestamp

            for observation

            in self

        ]

    @property
    def count(

        self

    ) -> int:

        return len(

            self

        )

    @property
    def is_empty(

        self

    ) -> bool:

        return len(

            self

        ) == 0

    # =====================================================
    # STATISTICS
    # =====================================================

    @property
    def mean(

        self

    ) -> float:

        if self.is_empty:

            return 0.0

        return fmean(

            self.values

        )

    @property
    def volatility(

        self

    ) -> float:

        if self.count < 2:

            return 0.0

        return stdev(

            self.values

        )

    @property
    def variance(

        self

    ) -> float:

        sigma = self.volatility

        return sigma * sigma

    @property
    def annualization_factor(

        self

    ) -> int:

        mapping = {

            "daily": 252,

            "weekly": 52,

            "monthly": 12,

            "quarterly": 4,

            "yearly": 1

        }

        return mapping.get(

            self.frequency,

            252

        )

    @property
    def annualized_return(

        self

    ) -> float:

        return (

            self.mean

            * self.annualization_factor

        )

    @property
    def annualized_volatility(

        self

    ) -> float:

        return (

            self.volatility

            * sqrt(

                self.annualization_factor

            )

        )

    # =====================================================
    # RISK
    # =====================================================

    @property
    def sharpe_ratio(

        self

    ) -> float:

        sigma = self.annualized_volatility

        if sigma <= 0:

            return 0.0

        return (

            self.annualized_return

            - self.risk_free_rate

        ) / sigma

    # =====================================================
    # EXPORT
    # =====================================================

    def to_list(

        self

    ) -> list[float]:

        return self.values.copy()

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self

    ) -> dict:

        return {

            "count": self.count,

            "frequency": self.frequency,

            "mean": self.mean,

            "volatility": self.volatility,

            "annualized_return": self.annualized_return,

            "annualized_volatility": self.annualized_volatility,

            "sharpe_ratio": self.sharpe_ratio

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self

    ) -> str:

        return (

            f"ReturnSeries("

            f"count={self.count}, "

            f"frequency='{self.frequency}'"

            f")"

        )

    __str__ = __repr__