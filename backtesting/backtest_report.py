"""
====================================================================
Institutional Quant Platform

Backtest Report

Author : Institutional Quant Platform

Purpose
-------
Institutional backtest report.

Represents the output of a backtesting
engine.

Produced By

• Historical Backtest
• Event Driven Backtest
• Walk Forward Backtest
• Monte Carlo Backtest

Consumed By

• Reporting
• Analytics
• Dashboard
• Performance Engine

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field


@dataclass(slots=True)
class BacktestReport:
    """
    Institutional backtest report.
    """

    # =====================================================
    # PORTFOLIO PERFORMANCE
    # =====================================================

    initial_capital: float = 0.0

    ending_capital: float = 0.0

    total_return: float = 0.0

    annual_return: float = 0.0

    annual_volatility: float = 0.0

    sharpe_ratio: float = 0.0

    sortino_ratio: float = 0.0

    calmar_ratio: float = 0.0

    information_ratio: float = 0.0

    beta: float = 0.0

    alpha: float = 0.0

    # =====================================================
    # RISK
    # =====================================================

    max_drawdown: float = 0.0

    value_at_risk: float = 0.0

    expected_shortfall: float = 0.0

    downside_deviation: float = 0.0

    tracking_error: float = 0.0

    # =====================================================
    # TRADING
    # =====================================================

    total_trades: int = 0

    winning_trades: int = 0

    losing_trades: int = 0

    win_rate: float = 0.0

    average_win: float = 0.0

    average_loss: float = 0.0

    profit_factor: float = 0.0

    turnover: float = 0.0

    # =====================================================
    # COSTS
    # =====================================================

    commissions: float = 0.0

    slippage: float = 0.0

    market_impact: float = 0.0

    transaction_cost: float = 0.0

    # =====================================================
    # BENCHMARK
    # =====================================================

    benchmark_return: float = 0.0

    excess_return: float = 0.0

    active_return: float = 0.0

    # =====================================================
    # METADATA
    # =====================================================

    metadata: dict = field(

        default_factory=dict

    )

    __hash__ = None

    # =====================================================
    # PROPERTIES
    # =====================================================

    @property
    def net_profit(

        self,

    ) -> float:

        return (

            self.ending_capital

            -

            self.initial_capital

        )

    @property
    def total_cost(

        self,

    ) -> float:

        return (

            self.commissions

            +

            self.slippage

            +

            self.market_impact

            +

            self.transaction_cost

        )

    @property
    def loss_rate(

        self,

    ) -> float:

        return max(

            0.0,

            1.0

            -

            self.win_rate,

        )

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self,

    ) -> dict:

        return {

            "Initial Capital":

                self.initial_capital,

            "Ending Capital":

                self.ending_capital,

            "Net Profit":

                self.net_profit,

            "Total Return":

                self.total_return,

            "Annual Return":

                self.annual_return,

            "Sharpe":

                self.sharpe_ratio,

            "Sortino":

                self.sortino_ratio,

            "Max Drawdown":

                self.max_drawdown,

            "Win Rate":

                self.win_rate,

            "Trades":

                self.total_trades,

            "Total Cost":

                self.total_cost,

        }

    # =====================================================
    # EXPORT
    # =====================================================

    def to_dict(

        self,

    ) -> dict:

        return {

            **self.__dict__,

            "Net_Profit":

                self.net_profit,

            "Total_Cost":

                self.total_cost,

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Return={self.total_return:.2%}, "

            f"Sharpe={self.sharpe_ratio:.2f}, "

            f"MDD={self.max_drawdown:.2%}"

            f")"

        )

    __str__ = __repr__