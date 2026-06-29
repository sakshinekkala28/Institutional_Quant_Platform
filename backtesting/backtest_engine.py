"""
====================================================================
Institutional Quant Platform

Backtest Engine

Author : Institutional Quant Platform

Purpose
-------
Institutional backtesting engine.

Coordinates

• Market Data
• Signal Generation
• Portfolio Updates
• Order Generation
• Execution
• Performance
• Reporting

Inherited From

• BaseBacktest

====================================================================
"""

from __future__ import annotations

from backtesting.backtest_report import BacktestReport
from backtesting.base_backtest import BaseBacktest

from execution.execution_engine import ExecutionEngine


class BacktestEngine(
    BaseBacktest
):
    """
    Institutional backtesting engine.
    """

    def __init__(

        self,

        *,

        execution_engine: ExecutionEngine,

        **kwargs,

    ) -> None:

        super().__init__(

            **kwargs

        )

        self.execution_engine = execution_engine

    # =====================================================
    # PREPARE
    # =====================================================

    def prepare(

        self,

    ) -> None:
        """
        Prepare the backtest.
        """

        pass

    # =====================================================
    # LOAD MARKET DATA
    # =====================================================

    def load_market_data(

        self,

    ) -> None:
        """
        Load historical market data.
        """

        pass

    # =====================================================
    # GENERATE SIGNALS
    # =====================================================

    def generate_signals(

        self,

    ) -> None:
        """
        Generate trading signals.
        """

        pass

    # =====================================================
    # BUILD ORDERS
    # =====================================================

    def build_orders(

        self,

    ) -> list:

        return []

    # =====================================================
    # EXECUTE ORDERS
    # =====================================================

    def execute_orders(

        self,

        orders: list,

    ) -> list:

        reports = []

        for order in orders:

            reports.append(

                self.execution_engine.execute(

                    order

                )

            )

        return reports

    # =====================================================
    # UPDATE PORTFOLIO
    # =====================================================

    def update_portfolio(

        self,

        execution_reports: list,

    ) -> None:
        """
        Update portfolio.
        """

        pass

    # =====================================================
    # PERFORMANCE
    # =====================================================

    def calculate_performance(

        self,

        report: BacktestReport,

    ) -> None:
        """
        Calculate performance statistics.
        """

        pass

    # =====================================================
    # RUN
    # =====================================================

    def run(

        self,

    ) -> BacktestReport:

        self.prepare()

        self.load_market_data()

        self.generate_signals()

        orders = self.build_orders()

        execution_reports = (

            self.execute_orders(

                orders

            )

        )

        self.update_portfolio(

            execution_reports

        )

        report = self.create_report()

        self.calculate_performance(

            report

        )

        report.metadata.update(

            {

                "BacktestEngine":

                    self.__class__.__name__,

                "ExecutionReports":

                    len(

                        execution_reports

                    ),

            }

        )

        return report

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Holdings={self.holdings}"

            f")"

        )

    __str__ = __repr__