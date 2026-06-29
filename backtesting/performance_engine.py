"""
====================================================================
Institutional Quant Platform

Performance Engine

Author : Institutional Quant Platform

Purpose
-------
Institutional portfolio performance engine.

Calculates

• Returns
• CAGR
• Volatility
• Sharpe Ratio
• Sortino Ratio
• Maximum Drawdown
• Calmar Ratio

Produces

• BacktestReport

Used By

• BacktestEngine
• Reporting
• Dashboard

====================================================================
"""

from __future__ import annotations

import math

import numpy as np

from backtesting.backtest_report import BacktestReport
from backtesting.portfolio_tracker import PortfolioTracker


class PerformanceEngine:
    """
    Institutional performance engine.
    """

    def __init__(

        self,

        tracker: PortfolioTracker,

        risk_free_rate: float = 0.0,

        trading_days: int = 252,

    ) -> None:

        self.tracker = tracker

        self.risk_free_rate = risk_free_rate

        self.trading_days = trading_days

    # =====================================================
    # RETURNS
    # =====================================================

    @property
    def returns(

        self,

    ) -> np.ndarray:

        return np.asarray(

            self.tracker.portfolio_returns,

            dtype=np.float64,

        )

    # =====================================================
    # TOTAL RETURN
    # =====================================================

    @property
    def total_return(

        self,

    ) -> float:

        if len(

            self.tracker.equity_curve

        ) < 2:

            return 0.0

        start = (

            self.tracker.equity_curve[0]

        )

        end = (

            self.tracker.equity_curve[-1]

        )

        if start <= 0:

            return 0.0

        return (

            end

            / start

        ) - 1.0

    # =====================================================
    # CAGR
    # =====================================================

    @property
    def cagr(

        self,

    ) -> float:

        observations = len(

            self.tracker.equity_curve

        )

        if observations < 2:

            return 0.0

        years = (

            observations

            /

            self.trading_days

        )

        if years <= 0:

            return 0.0

        return (

            (

                1.0

                +

                self.total_return

            )

            **

            (

                1.0

                /

                years

            )

        ) - 1.0

    # =====================================================
    # VOLATILITY
    # =====================================================

    @property
    def volatility(

        self,

    ) -> float:

        if len(

            self.returns

        ) < 2:

            return 0.0

        return float(

            np.std(

                self.returns,

                ddof=1,

            )

            *

            math.sqrt(

                self.trading_days

            )

        )

    # =====================================================
    # SHARPE
    # =====================================================

    @property
    def sharpe(

        self,

    ) -> float:

        volatility = self.volatility

        if volatility <= 0:

            return 0.0

        annual_return = self.cagr

        return (

            annual_return

            -

            self.risk_free_rate

        ) / volatility

    # =====================================================
    # SORTINO
    # =====================================================

    @property
    def sortino(

        self,

    ) -> float:

        downside = self.returns[

            self.returns < 0

        ]

        if len(

            downside

        ) == 0:

            return 0.0

        downside_vol = (

            np.std(

                downside,

                ddof=1,

            )

            *

            math.sqrt(

                self.trading_days

            )

        )

        if downside_vol <= 0:

            return 0.0

        return (

            self.cagr

            -

            self.risk_free_rate

        ) / downside_vol

    # =====================================================
    # MAXIMUM DRAWDOWN
    # =====================================================

    @property
    def maximum_drawdown(

        self,

    ) -> float:

        equity = np.asarray(

            self.tracker.equity_curve,

            dtype=np.float64,

        )

        if equity.size == 0:

            return 0.0

        running_max = np.maximum.accumulate(

            equity

        )

        drawdown = (

            equity

            -

            running_max

        ) / running_max

        return float(

            abs(

                np.min(

                    drawdown

                )

            )

        )

    # =====================================================
    # CALMAR
    # =====================================================

    @property
    def calmar(

        self,

    ) -> float:

        drawdown = (

            self.maximum_drawdown

        )

        if drawdown <= 0:

            return 0.0

        return (

            self.cagr

            / drawdown

        )

    # =====================================================
    # REPORT
    # =====================================================

    def report(

        self,

    ) -> BacktestReport:

        report = BacktestReport()

        report.initial_capital = (

            self.tracker.equity_curve[0]

            if self.tracker.equity_curve

            else 0.0

        )

        report.ending_capital = (

            self.tracker.equity

        )

        report.total_return = (

            self.total_return

        )

        report.annual_return = (

            self.cagr

        )

        report.annual_volatility = (

            self.volatility

        )

        report.sharpe_ratio = (

            self.sharpe

        )

        report.sortino_ratio = (

            self.sortino

        )

        report.calmar_ratio = (

            self.calmar

        )

        report.max_drawdown = (

            self.maximum_drawdown

        )

        report.metadata.update(

            {

                "PerformanceEngine":

                    self.__class__.__name__,

                "Observations":

                    len(

                        self.tracker.equity_curve

                    ),

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

            "Return":

                self.total_return,

            "CAGR":

                self.cagr,

            "Volatility":

                self.volatility,

            "Sharpe":

                self.sharpe,

            "Sortino":

                self.sortino,

            "Calmar":

                self.calmar,

            "MaxDrawdown":

                self.maximum_drawdown,

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Sharpe={self.sharpe:.2f}"

            f")"

        )

    __str__ = __repr__