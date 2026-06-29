"""
====================================================================
Institutional Quant Platform

Risk Statistics

Author : Institutional Quant Platform

Purpose
-------
Reusable institutional risk statistics.

Provides

• Value at Risk (VaR)
• Expected Shortfall (CVaR)
• Downside Deviation
• Tracking Error
• Beta
• Correlation

Used By

• PerformanceEngine
• BenchmarkEngine
• Reporting
• Analytics

====================================================================
"""

from __future__ import annotations

import math

import numpy as np


class RiskStatistics:
    """
    Institutional risk statistics.
    """

    # =====================================================
    # VALUE AT RISK
    # =====================================================

    @staticmethod
    def value_at_risk(

        returns: list[float] | np.ndarray,

        confidence: float = 0.95,

    ) -> float:

        values = np.asarray(

            returns,

            dtype=np.float64,

        )

        if values.size == 0:

            return 0.0

        percentile = (

            100.0

            *

            (

                1.0

                -

                confidence

            )

        )

        return float(

            -np.percentile(

                values,

                percentile,

            )

        )

    # =====================================================
    # EXPECTED SHORTFALL
    # =====================================================

    @staticmethod
    def expected_shortfall(

        returns: list[float] | np.ndarray,

        confidence: float = 0.95,

    ) -> float:

        values = np.asarray(

            returns,

            dtype=np.float64,

        )

        if values.size == 0:

            return 0.0

        var = -RiskStatistics.value_at_risk(

            values,

            confidence,

        )

        tail = values[

            values <= var

        ]

        if tail.size == 0:

            return 0.0

        return float(

            -tail.mean()

        )

    # =====================================================
    # DOWNSIDE DEVIATION
    # =====================================================

    @staticmethod
    def downside_deviation(

        returns: list[float] | np.ndarray,

        target_return: float = 0.0,

        trading_days: int = 252,

    ) -> float:

        values = np.asarray(

            returns,

            dtype=np.float64,

        )

        downside = values[

            values < target_return

        ]

        if downside.size < 2:

            return 0.0

        deviation = (

            downside

            -

            target_return

        )

        return float(

            np.std(

                deviation,

                ddof=1,

            )

            *

            math.sqrt(

                trading_days

            )

        )

    # =====================================================
    # TRACKING ERROR
    # =====================================================

    @staticmethod
    def tracking_error(

        portfolio_returns: list[float] | np.ndarray,

        benchmark_returns: list[float] | np.ndarray,

        trading_days: int = 252,

    ) -> float:

        portfolio = np.asarray(

            portfolio_returns,

            dtype=np.float64,

        )

        benchmark = np.asarray(

            benchmark_returns,

            dtype=np.float64,

        )

        if (

            portfolio.size

            != benchmark.size

        ):

            raise ValueError(

                "Return series "

                "must have equal length."

            )

        if portfolio.size < 2:

            return 0.0

        active = (

            portfolio

            -

            benchmark

        )

        return float(

            np.std(

                active,

                ddof=1,

            )

            *

            math.sqrt(

                trading_days

            )

        )

    # =====================================================
    # BETA
    # =====================================================

    @staticmethod
    def beta(

        portfolio_returns: list[float] | np.ndarray,

        benchmark_returns: list[float] | np.ndarray,

    ) -> float:

        portfolio = np.asarray(

            portfolio_returns,

            dtype=np.float64,

        )

        benchmark = np.asarray(

            benchmark_returns,

            dtype=np.float64,

        )

        if (

            portfolio.size

            != benchmark.size

        ):

            raise ValueError(

                "Return series "

                "must have equal length."

            )

        if portfolio.size < 2:

            return 0.0

        variance = np.var(

            benchmark,

            ddof=1,

        )

        if variance <= 0:

            return 0.0

        covariance = np.cov(

            portfolio,

            benchmark,

            ddof=1,

        )[0, 1]

        return float(

            covariance

            / variance

        )

    # =====================================================
    # CORRELATION
    # =====================================================

    @staticmethod
    def correlation(

        portfolio_returns: list[float] | np.ndarray,

        benchmark_returns: list[float] | np.ndarray,

    ) -> float:

        portfolio = np.asarray(

            portfolio_returns,

            dtype=np.float64,

        )

        benchmark = np.asarray(

            benchmark_returns,

            dtype=np.float64,

        )

        if (

            portfolio.size

            != benchmark.size

        ):

            raise ValueError(

                "Return series "

                "must have equal length."

            )

        if portfolio.size < 2:

            return 0.0

        return float(

            np.corrcoef(

                portfolio,

                benchmark,

            )[0, 1]

        )

    # =====================================================
    # SUMMARY
    # =====================================================

    @classmethod
    def summary(

        cls,

        portfolio_returns: list[float] | np.ndarray,

        benchmark_returns: list[float] | np.ndarray,

        confidence: float = 0.95,

    ) -> dict:

        return {

            "VaR":

                cls.value_at_risk(

                    portfolio_returns,

                    confidence,

                ),

            "ExpectedShortfall":

                cls.expected_shortfall(

                    portfolio_returns,

                    confidence,

                ),

            "DownsideDeviation":

                cls.downside_deviation(

                    portfolio_returns,

                ),

            "TrackingError":

                cls.tracking_error(

                    portfolio_returns,

                    benchmark_returns,

                ),

            "Beta":

                cls.beta(

                    portfolio_returns,

                    benchmark_returns,

                ),

            "Correlation":

                cls.correlation(

                    portfolio_returns,

                    benchmark_returns,

                ),

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}()"

        )

    __str__ = __repr__