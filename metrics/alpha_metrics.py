"""
====================================================================
Institutional Quant Platform

Alpha Metrics

Author : Institutional Quant Platform

Purpose
-------
Institutional alpha performance metrics.

Provides

• Jensen's Alpha
• Active Return
• Excess Return
• Information Ratio
• Appraisal Ratio

Used By

• BenchmarkEngine
• PerformanceEngine
• Reporting
• Dashboard

====================================================================
"""

from __future__ import annotations

import math

import numpy as np


class AlphaMetrics:
    """
    Institutional alpha metrics.
    """

    # =====================================================
    # ACTIVE RETURN
    # =====================================================

    @staticmethod
    def active_return(

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

        if portfolio.size != benchmark.size:

            raise ValueError(

                "Return series must have equal length."

            )

        return float(

            np.mean(

                portfolio

                -

                benchmark

            )

        )

    # =====================================================
    # EXCESS RETURN
    # =====================================================

    @staticmethod
    def excess_return(

        portfolio_returns: list[float] | np.ndarray,

        risk_free_rate: float = 0.0,

    ) -> float:

        portfolio = np.asarray(

            portfolio_returns,

            dtype=np.float64,

        )

        if portfolio.size == 0:

            return 0.0

        return float(

            np.mean(

                portfolio

            )

            -

            risk_free_rate

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

        active = (

            portfolio

            -

            benchmark

        )

        if active.size < 2:

            return 0.0

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
    # INFORMATION RATIO
    # =====================================================

    @classmethod
    def information_ratio(

        cls,

        portfolio_returns: list[float] | np.ndarray,

        benchmark_returns: list[float] | np.ndarray,

        trading_days: int = 252,

    ) -> float:

        tracking_error = cls.tracking_error(

            portfolio_returns,

            benchmark_returns,

            trading_days,

        )

        if tracking_error <= 0:

            return 0.0

        return (

            cls.active_return(

                portfolio_returns,

                benchmark_returns,

            )

            *

            trading_days

        ) / tracking_error

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
    # JENSEN ALPHA
    # =====================================================

    @classmethod
    def jensen_alpha(

        cls,

        portfolio_returns: list[float] | np.ndarray,

        benchmark_returns: list[float] | np.ndarray,

        risk_free_rate: float = 0.0,

        trading_days: int = 252,

    ) -> float:

        portfolio = float(

            np.mean(

                portfolio_returns

            )

            *

            trading_days

        )

        benchmark = float(

            np.mean(

                benchmark_returns

            )

            *

            trading_days

        )

        beta = cls.beta(

            portfolio_returns,

            benchmark_returns,

        )

        return (

            portfolio

            -

            (

                risk_free_rate

                +

                beta

                *

                (

                    benchmark

                    -

                    risk_free_rate

                )

            )

        )

    # =====================================================
    # APPRAISAL RATIO
    # =====================================================

    @classmethod
    def appraisal_ratio(

        cls,

        portfolio_returns: list[float] | np.ndarray,

        benchmark_returns: list[float] | np.ndarray,

        risk_free_rate: float = 0.0,

        trading_days: int = 252,

    ) -> float:

        alpha = cls.jensen_alpha(

            portfolio_returns,

            benchmark_returns,

            risk_free_rate,

            trading_days,

        )

        tracking_error = cls.tracking_error(

            portfolio_returns,

            benchmark_returns,

            trading_days,

        )

        if tracking_error <= 0:

            return 0.0

        return alpha / tracking_error

    # =====================================================
    # SUMMARY
    # =====================================================

    @classmethod
    def summary(

        cls,

        portfolio_returns: list[float] | np.ndarray,

        benchmark_returns: list[float] | np.ndarray,

        risk_free_rate: float = 0.0,

        trading_days: int = 252,

    ) -> dict:

        return {

            "ActiveReturn":

                cls.active_return(

                    portfolio_returns,

                    benchmark_returns,

                ),

            "ExcessReturn":

                cls.excess_return(

                    portfolio_returns,

                    risk_free_rate,

                ),

            "InformationRatio":

                cls.information_ratio(

                    portfolio_returns,

                    benchmark_returns,

                    trading_days,

                ),

            "Beta":

                cls.beta(

                    portfolio_returns,

                    benchmark_returns,

                ),

            "JensenAlpha":

                cls.jensen_alpha(

                    portfolio_returns,

                    benchmark_returns,

                    risk_free_rate,

                    trading_days,

                ),

            "AppraisalRatio":

                cls.appraisal_ratio(

                    portfolio_returns,

                    benchmark_returns,

                    risk_free_rate,

                    trading_days,

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