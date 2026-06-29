"""
====================================================================
Institutional Quant Platform

Turnover Metrics

Author : Institutional Quant Platform

Purpose
-------
Reusable institutional turnover analytics.

Provides

• Portfolio Turnover
• Average Holding Period
• Trade Frequency
• Portfolio Churn
• Average Trade Size
• Capacity Utilization

Used By

• Performance Engine
• Reporting
• Dashboard
• Portfolio Analytics

====================================================================
"""

from __future__ import annotations

import numpy as np


class TurnoverMetrics:
    """
    Institutional turnover analytics.
    """

    # =====================================================
    # PORTFOLIO TURNOVER
    # =====================================================

    @staticmethod
    def portfolio_turnover(

        buy_value: float,

        sell_value: float,

        average_portfolio_value: float,

    ) -> float:

        if average_portfolio_value <= 0:

            return 0.0

        return (

            min(

                buy_value,

                sell_value,

            )

            /

            average_portfolio_value

        )

    # =====================================================
    # GROSS TURNOVER
    # =====================================================

    @staticmethod
    def gross_turnover(

        traded_value: float,

        average_portfolio_value: float,

    ) -> float:

        if average_portfolio_value <= 0:

            return 0.0

        return (

            traded_value

            /

            average_portfolio_value

        )

    # =====================================================
    # TRADE FREQUENCY
    # =====================================================

    @staticmethod
    def trade_frequency(

        number_of_trades: int,

        periods: int,

    ) -> float:

        if periods <= 0:

            return 0.0

        return (

            number_of_trades

            /

            periods

        )

    # =====================================================
    # AVERAGE HOLDING PERIOD
    # =====================================================

    @staticmethod
    def average_holding_period(

        holding_periods: list[int] | np.ndarray,

    ) -> float:

        periods = np.asarray(

            holding_periods,

            dtype=np.float64,

        )

        if periods.size == 0:

            return 0.0

        return float(

            np.mean(

                periods

            )

        )

    # =====================================================
    # AVERAGE TRADE SIZE
    # =====================================================

    @staticmethod
    def average_trade_size(

        trade_values: list[float] | np.ndarray,

    ) -> float:

        values = np.asarray(

            trade_values,

            dtype=np.float64,

        )

        if values.size == 0:

            return 0.0

        return float(

            np.mean(

                values

            )

        )

    # =====================================================
    # PORTFOLIO CHURN
    # =====================================================

    @staticmethod
    def portfolio_churn(

        trades_executed: int,

        holdings: int,

    ) -> float:

        if holdings <= 0:

            return 0.0

        return (

            trades_executed

            /

            holdings

        )

    # =====================================================
    # CAPACITY UTILIZATION
    # =====================================================

    @staticmethod
    def capacity_utilization(

        traded_value: float,

        average_daily_volume: float,

    ) -> float:

        if average_daily_volume <= 0:

            return 0.0

        return (

            traded_value

            /

            average_daily_volume

        )

    # =====================================================
    # SUMMARY
    # =====================================================

    @classmethod
    def summary(

        cls,

        buy_value: float,

        sell_value: float,

        traded_value: float,

        average_portfolio_value: float,

        trade_values: list[float] | np.ndarray,

        holding_periods: list[int] | np.ndarray,

        number_of_trades: int,

        periods: int,

        holdings: int,

        average_daily_volume: float,

    ) -> dict:

        return {

            "PortfolioTurnover":

                cls.portfolio_turnover(

                    buy_value,

                    sell_value,

                    average_portfolio_value,

                ),

            "GrossTurnover":

                cls.gross_turnover(

                    traded_value,

                    average_portfolio_value,

                ),

            "TradeFrequency":

                cls.trade_frequency(

                    number_of_trades,

                    periods,

                ),

            "AverageHoldingPeriod":

                cls.average_holding_period(

                    holding_periods,

                ),

            "AverageTradeSize":

                cls.average_trade_size(

                    trade_values,

                ),

            "PortfolioChurn":

                cls.portfolio_churn(

                    number_of_trades,

                    holdings,

                ),

            "CapacityUtilization":

                cls.capacity_utilization(

                    traded_value,

                    average_daily_volume,

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