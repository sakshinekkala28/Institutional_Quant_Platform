"""
====================================================================
Institutional Quant Platform

Benchmark Engine

Author : Institutional Quant Platform

Purpose
-------
Institutional benchmark analytics engine.

Calculates

• Benchmark Return
• Excess Return
• Active Return
• Tracking Error
• Information Ratio
• Beta
• Alpha

Produces

• BacktestReport

Used By

• Performance Engine
• Backtest Engine
• Reporting

====================================================================
"""

from __future__ import annotations

import math

import numpy as np

from backtesting.backtest_report import BacktestReport


class BenchmarkEngine:
    """
    Institutional benchmark analytics engine.
    """

    def __init__(

        self,

        portfolio_returns: list[float] | np.ndarray,

        benchmark_returns: list[float] | np.ndarray,

        risk_free_rate: float = 0.0,

        trading_days: int = 252,

    ) -> None:

        self.portfolio_returns = np.asarray(

            portfolio_returns,

            dtype=np.float64,

        )

        self.benchmark_returns = np.asarray(

            benchmark_returns,

            dtype=np.float64,

        )

        self.risk_free_rate = risk_free_rate

        self.trading_days = trading_days

        self.validate()

    # =====================================================
    # VALIDATION
    # =====================================================

    def validate(

        self,

    ) -> None:

        if (

            self.portfolio_returns.size

            == 0

        ):

            raise ValueError(

                "Portfolio returns cannot be empty."

            )

        if (

            self.portfolio_returns.size

            !=

            self.benchmark_returns.size

        ):

            raise ValueError(

                "Return series must have equal length."

            )

    # =====================================================
    # RETURNS
    # =====================================================

    @property
    def portfolio_return(

        self,

    ) -> float:

        return float(

            np.prod(

                1.0

                +

                self.portfolio_returns

            )

            -

            1.0

        )

    @property
    def benchmark_return(

        self,

    ) -> float:

        return float(

            np.prod(

                1.0

                +

                self.benchmark_returns

            )

            -

            1.0

        )

    # =====================================================
    # ACTIVE RETURN
    # =====================================================

    @property
    def active_return(

        self,

    ) -> float:

        return (

            self.portfolio_return

            -

            self.benchmark_return

        )

    @property
    def excess_return(

        self,

    ) -> float:

        return (

            self.portfolio_return

            -

            self.risk_free_rate

        )

    # =====================================================
    # TRACKING ERROR
    # =====================================================

    @property
    def tracking_error(

        self,

    ) -> float:

        active = (

            self.portfolio_returns

            -

            self.benchmark_returns

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

                self.trading_days

            )

        )

    # =====================================================
    # INFORMATION RATIO
    # =====================================================

    @property
    def information_ratio(

        self,

    ) -> float:

        tracking = (

            self.tracking_error

        )

        if tracking <= 0:

            return 0.0

        return (

            self.active_return

            / tracking

        )

    # =====================================================
    # BETA
    # =====================================================

    @property
    def beta(

        self,

    ) -> float:

        variance = np.var(

            self.benchmark_returns,

            ddof=1,

        )

        if variance <= 0:

            return 0.0

        covariance = np.cov(

            self.portfolio_returns,

            self.benchmark_returns,

            ddof=1,

        )[0, 1]

        return float(

            covariance

            / variance

        )

    # =====================================================
    # ALPHA
    # =====================================================

    @property
    def alpha(

        self,

    ) -> float:

        benchmark = float(

            np.mean(

                self.benchmark_returns

            )

        )

        portfolio = float(

            np.mean(

                self.portfolio_returns

            )

        )

        return (

            portfolio

            -

            (

                self.risk_free_rate

                +

                self.beta

                *

                (

                    benchmark

                    -

                    self.risk_free_rate

                )

            )

        )

    # =====================================================
    # REPORT
    # =====================================================

    def update_report(

        self,

        report: BacktestReport,

    ) -> BacktestReport:

        report.benchmark_return = (

            self.benchmark_return

        )

        report.excess_return = (

            self.excess_return

        )

        report.active_return = (

            self.active_return

        )

        report.tracking_error = (

            self.tracking_error

        )

        report.information_ratio = (

            self.information_ratio

        )

        report.beta = (

            self.beta

        )

        report.alpha = (

            self.alpha

        )

        report.metadata.update(

            {

                "BenchmarkEngine":

                    self.__class__.__name__

            }

        )

        return report

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self,

    ) -> dict:

        return {

            "BenchmarkReturn":

                self.benchmark_return,

            "ActiveReturn":

                self.active_return,

            "ExcessReturn":

                self.excess_return,

            "TrackingError":

                self.tracking_error,

            "InformationRatio":

                self.information_ratio,

            "Beta":

                self.beta,

            "Alpha":

                self.alpha,

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"IR={self.information_ratio:.2f}, "

            f"Beta={self.beta:.2f}"

            f")"

        )

    __str__ = __repr__