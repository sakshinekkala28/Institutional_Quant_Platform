"""
====================================================================
Institutional Quant Platform

Portfolio Tracker

Author : Institutional Quant Platform

Purpose
-------
Institutional portfolio tracking engine.

Coordinates

• Cash Management
• Position Management
• Portfolio Valuation
• Equity Curve
• Portfolio Returns

Used By

• Backtest Engine
• Performance Engine
• Reporting

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from backtesting.cash_manager import CashManager
from backtesting.fill_event import FillEvent
from backtesting.position_manager import PositionManager


@dataclass(slots=True)
class PortfolioTracker:
    """
    Institutional portfolio tracker.
    """

    cash_manager: CashManager

    position_manager: PositionManager

    equity_curve: list[float] = field(

        default_factory=list

    )

    portfolio_returns: list[float] = field(

        default_factory=list

    )

    # =====================================================
    # APPLY FILL
    # =====================================================

    def apply_fill(

        self,

        fill: FillEvent,

    ) -> None:

        self.cash_manager.settle(

            fill

        )

        self.position_manager.apply_fill(

            fill

        )

        self.record_equity()

    # =====================================================
    # UPDATE MARKET PRICE
    # =====================================================

    def update_price(

        self,

        symbol: str,

        price: float,

    ) -> None:

        self.position_manager.update_price(

            symbol,

            price,

        )

        self.record_equity()

    # =====================================================
    # RECORD EQUITY
    # =====================================================

    def record_equity(

        self,

    ) -> None:

        equity = (

            self.cash_manager.balance

            +

            self.position_manager.market_value

        )

        if self.equity_curve:

            previous = self.equity_curve[-1]

            if previous > 0:

                self.portfolio_returns.append(

                    (

                        equity

                        -

                        previous

                    )

                    / previous

                )

            else:

                self.portfolio_returns.append(

                    0.0

                )

        self.equity_curve.append(

            equity

        )

    # =====================================================
    # RESET
    # =====================================================

    def reset(

        self,

    ) -> None:

        self.cash_manager.reset()

        self.position_manager.reset()

        self.equity_curve.clear()

        self.portfolio_returns.clear()

    # =====================================================
    # PROPERTIES
    # =====================================================

    @property
    def equity(

        self,

    ) -> float:

        if not self.equity_curve:

            return (

                self.cash_manager.balance

                +

                self.position_manager.market_value

            )

        return self.equity_curve[-1]

    @property
    def cash(

        self,

    ) -> float:

        return self.cash_manager.balance

    @property
    def market_value(

        self,

    ) -> float:

        return self.position_manager.market_value

    @property
    def realized_pnl(

        self,

    ) -> float:

        return self.position_manager.realized_pnl

    @property
    def unrealized_pnl(

        self,

    ) -> float:

        return self.position_manager.unrealized_pnl

    @property
    def total_pnl(

        self,

    ) -> float:

        return self.position_manager.total_pnl

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self,

    ) -> dict:

        return {

            "Equity":

                self.equity,

            "Cash":

                self.cash,

            "MarketValue":

                self.market_value,

            "RealizedPnL":

                self.realized_pnl,

            "UnrealizedPnL":

                self.unrealized_pnl,

            "TotalPnL":

                self.total_pnl,

            "Observations":

                len(

                    self.equity_curve

                ),

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Equity={self.equity:,.2f}"

            f")"

        )

    __str__ = __repr__