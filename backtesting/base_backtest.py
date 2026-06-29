"""
====================================================================
Institutional Quant Platform

Base Backtest

Author : Institutional Quant Platform

Purpose
-------
Abstract base class for all institutional
backtesting engines.

Provides

• Portfolio Validation
• Benchmark Validation
• Date Validation
• Common Utilities
• Report Creation
• Execution Contract

Inherited By

• EventDrivenBacktest
• HistoricalBacktest
• WalkForwardBacktest
• MonteCarloBacktest

====================================================================
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod
from datetime import datetime

from core.models.benchmark import Benchmark
from core.models.portfolio import Portfolio

from backtesting.backtest_report import BacktestReport


class BaseBacktest(ABC):
    """
    Institutional base backtest.
    """

    def __init__(

        self,

        portfolio: Portfolio,

        benchmark: Benchmark | None = None,

        start_date: datetime | None = None,

        end_date: datetime | None = None,

    ) -> None:

        self._portfolio = portfolio

        self._benchmark = benchmark

        self._start_date = start_date

        self._end_date = end_date

        self.validate()

    # =====================================================
    # PROPERTIES
    # =====================================================

    @property
    def portfolio(

        self,

    ) -> Portfolio:

        return self._portfolio

    @property
    def benchmark(

        self,

    ) -> Benchmark | None:

        return self._benchmark

    @property
    def start_date(

        self,

    ) -> datetime | None:

        return self._start_date

    @property
    def end_date(

        self,

    ) -> datetime | None:

        return self._end_date

    # =====================================================
    # VALIDATION
    # =====================================================

    def validate(

        self,

    ) -> None:

        if self.portfolio.is_empty:

            raise ValueError(

                "Portfolio cannot be empty."

            )

        if (

            self.start_date is not None

            and

            self.end_date is not None

            and

            self.start_date > self.end_date

        ):

            raise ValueError(

                "Start date must be before end date."

            )

        if self.benchmark is not None:

            self.benchmark.validate()

    # =====================================================
    # UTILITIES
    # =====================================================

    @property
    def holdings(

        self,

    ) -> int:

        return self.portfolio.holdings

    @property
    def symbols(

        self,

    ) -> list[str]:

        return self.portfolio.symbols()

    @property
    def period_days(

        self,

    ) -> int:

        if (

            self.start_date is None

            or

            self.end_date is None

        ):

            return 0

        return (

            self.end_date

            -

            self.start_date

        ).days

    # =====================================================
    # REPORT
    # =====================================================

    def create_report(

        self,

    ) -> BacktestReport:

        report = BacktestReport()

        report.metadata.update(

            {

                "Backtest":

                    self.__class__.__name__,

                "Holdings":

                    self.holdings,

                "Start":

                    self.start_date,

                "End":

                    self.end_date,

            }

        )

        return report

    # =====================================================
    # EXECUTION
    # =====================================================

    @abstractmethod
    def run(

        self,

    ) -> BacktestReport:
        """
        Execute backtest.
        """

        raise NotImplementedError

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Holdings={self.holdings}, "

            f"Days={self.period_days}"

            f")"

        )

    __str__ = __repr__