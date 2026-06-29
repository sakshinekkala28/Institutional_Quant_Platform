"""
====================================================================
Institutional Quant Platform

Performance Statistics

Author : Institutional Quant Platform

Purpose
-------
Reusable institutional performance statistics.

Provides

• Total Return
• CAGR
• Annual Return
• Volatility
• Sharpe Ratio
• Sortino Ratio
• Calmar Ratio

Used By

• PerformanceEngine
• Reporting
• Analytics
• Dashboard

====================================================================
"""

from __future__ import annotations

import math

import numpy as np


class PerformanceStatistics:
    """
    Institutional performance statistics.
    """

    # =====================================================
    # TOTAL RETURN
    # =====================================================

    @staticmethod
    def total_return(

        equity_curve: list[float] | np.ndarray,

    ) -> float:

        equity = np.asarray(

            equity_curve,

            dtype=np.float64,

        )

        if equity.size < 2:

            return 0.0

        start = equity[0]

        end = equity[-1]

        if start <= 0:

            return 0.0

        return float(

            end / start - 1.0

        )

    # =====================================================
    # CAGR
    # =====================================================

    @staticmethod
    def cagr(

        equity_curve: list[float] | np.ndarray,

        trading_days: int = 252,

    ) -> float:

        equity = np.asarray(

            equity_curve,

            dtype=np.float64,

        )

        if equity.size < 2:

            return 0.0

        years = (

            equity.size

            / trading_days

        )

        if years <= 0:

            return 0.0

        total = (

            PerformanceStatistics

            .total_return(

                equity

            )

        )

        return float(

            (

                1.0 + total

            )

            **

            (

                1.0 / years

            )

            - 1.0

        )

    # =====================================================
    # VOLATILITY
    # =====================================================

    @staticmethod
    def volatility(

        returns: list[float] | np.ndarray,

        trading_days: int = 252,

    ) -> float:

        values = np.asarray(

            returns,

            dtype=np.float64,

        )

        if values.size < 2:

            return 0.0

        return float(

            np.std(

                values,

                ddof=1,

            )

            *

            math.sqrt(

                trading_days

            )

        )

    # =====================================================
    # SHARPE
    # =====================================================

    @staticmethod
    def sharpe_ratio(

        returns: list[float] | np.ndarray,

        risk_free_rate: float = 0.0,

        trading_days: int = 252,

    ) -> float:

        values = np.asarray(

            returns,

            dtype=np.float64,

        )

        if values.size < 2:

            return 0.0

        annual_return = float(

            np.mean(

                values

            )

            *

            trading_days

        )

        volatility = (

            PerformanceStatistics

            .volatility(

                values,

                trading_days,

            )

        )

        if volatility <= 0:

            return 0.0

        return (

            annual_return

            -

            risk_free_rate

        ) / volatility

    # =====================================================
    # SORTINO
    # =====================================================

    @staticmethod
    def sortino_ratio(

        returns: list[float] | np.ndarray,

        risk_free_rate: float = 0.0,

        trading_days: int = 252,

    ) -> float:

        values = np.asarray(

            returns,

            dtype=np.float64,

        )

        downside = values[

            values < 0

        ]

        if downside.size < 2:

            return 0.0

        downside_volatility = float(

            np.std(

                downside,

                ddof=1,

            )

            *

            math.sqrt(

                trading_days

            )

        )

        if downside_volatility <= 0:

            return 0.0

        annual_return = float(

            np.mean(

                values

            )

            *

            trading_days

        )

        return (

            annual_return

            -

            risk_free_rate

        ) / downside_volatility

    # =====================================================
    # MAXIMUM DRAWDOWN
    # =====================================================

    @staticmethod
    def maximum_drawdown(

        equity_curve: list[float] | np.ndarray,

    ) -> float:

        equity = np.asarray(

            equity_curve,

            dtype=np.float64,

        )

        if equity.size == 0:

            return 0.0

        running_max = np.maximum.accumulate(

            equity

        )

        drawdowns = (

            equity

            -

            running_max

        ) / running_max

        return float(

            abs(

                np.min(

                    drawdowns

                )

            )

        )

    # =====================================================
    # CALMAR
    # =====================================================

    @staticmethod
    def calmar_ratio(

        equity_curve: list[float] | np.ndarray,

        trading_days: int = 252,

    ) -> float:

        cagr = (

            PerformanceStatistics

            .cagr(

                equity_curve,

                trading_days,

            )

        )

        drawdown = (

            PerformanceStatistics

            .maximum_drawdown(

                equity_curve

            )

        )

        if drawdown <= 0:

            return 0.0

        return cagr / drawdown

    # =====================================================
    # SUMMARY
    # =====================================================

    @classmethod
    def summary(

        cls,

        equity_curve: list[float] | np.ndarray,

        returns: list[float] | np.ndarray,

        risk_free_rate: float = 0.0,

        trading_days: int = 252,

    ) -> dict:

        return {

            "TotalReturn":

                cls.total_return(

                    equity_curve

                ),

            "CAGR":

                cls.cagr(

                    equity_curve,

                    trading_days,

                ),

            "Volatility":

                cls.volatility(

                    returns,

                    trading_days,

                ),

            "Sharpe":

                cls.sharpe_ratio(

                    returns,

                    risk_free_rate,

                    trading_days,

                ),

            "Sortino":

                cls.sortino_ratio(

                    returns,

                    risk_free_rate,

                    trading_days,

                ),

            "MaxDrawdown":

                cls.maximum_drawdown(

                    equity_curve

                ),

            "Calmar":

                cls.calmar_ratio(

                    equity_curve,

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