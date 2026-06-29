"""
====================================================================
Institutional Quant Platform

Position Manager

Author : Institutional Quant Platform

Purpose
-------
Institutional position management engine.

Responsible For

• Position Creation
• Position Updates
• Average Cost
• Market Value
• Realized P&L
• Unrealized P&L

Used By

• Portfolio Tracker
• Backtest Engine
• Performance Engine

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from backtesting.fill_event import FillEvent


# =====================================================
# POSITION
# =====================================================


@dataclass(slots=True)
class Position:
    """
    Single portfolio position.
    """

    symbol: str

    quantity: float = 0.0

    average_cost: float = 0.0

    market_price: float = 0.0

    realized_pnl: float = 0.0

    # =====================================================
    # PROPERTIES
    # =====================================================

    @property
    def market_value(

        self,

    ) -> float:

        return (

            self.quantity

            *

            self.market_price

        )

    @property
    def unrealized_pnl(

        self,

    ) -> float:

        return (

            self.market_price

            -

            self.average_cost

        ) * self.quantity


# =====================================================
# POSITION MANAGER
# =====================================================


@dataclass(slots=True)
class PositionManager:
    """
    Institutional position manager.
    """

    positions: dict[str, Position] = field(

        default_factory=dict

    )

    # =====================================================
    # APPLY FILL
    # =====================================================

    def apply_fill(

        self,

        fill: FillEvent,

    ) -> None:

        position = self.positions.setdefault(

            fill.symbol,

            Position(

                symbol=fill.symbol

            ),

        )

        if fill.side == "BUY":

            total_cost = (

                position.average_cost

                * position.quantity

            ) + (

                fill.execution_price

                * fill.executed_quantity

            )

            position.quantity += (

                fill.executed_quantity

            )

            if position.quantity > 0:

                position.average_cost = (

                    total_cost

                    / position.quantity

                )

        else:

            realized = (

                fill.execution_price

                -

                position.average_cost

            ) * fill.executed_quantity

            position.realized_pnl += (

                realized

            )

            position.quantity -= (

                fill.executed_quantity

            )

            if position.quantity <= 0:

                position.quantity = 0.0

                position.average_cost = 0.0

    # =====================================================
    # UPDATE PRICE
    # =====================================================

    def update_price(

        self,

        symbol: str,

        price: float,

    ) -> None:

        if symbol not in self.positions:

            return

        self.positions[

            symbol

        ].market_price = price

    # =====================================================
    # GET POSITION
    # =====================================================

    def position(

        self,

        symbol: str,

    ) -> Position | None:

        return self.positions.get(

            symbol

        )

    # =====================================================
    # TOTAL MARKET VALUE
    # =====================================================

    @property
    def market_value(

        self,

    ) -> float:

        return sum(

            position.market_value

            for position

            in self.positions.values()

        )

    # =====================================================
    # REALIZED PNL
    # =====================================================

    @property
    def realized_pnl(

        self,

    ) -> float:

        return sum(

            position.realized_pnl

            for position

            in self.positions.values()

        )

    # =====================================================
    # UNREALIZED PNL
    # =====================================================

    @property
    def unrealized_pnl(

        self,

    ) -> float:

        return sum(

            position.unrealized_pnl

            for position

            in self.positions.values()

        )

    # =====================================================
    # PORTFOLIO PNL
    # =====================================================

    @property
    def total_pnl(

        self,

    ) -> float:

        return (

            self.realized_pnl

            +

            self.unrealized_pnl

        )

    # =====================================================
    # RESET
    # =====================================================

    def reset(

        self,

    ) -> None:

        self.positions.clear()

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self,

    ) -> dict:

        return {

            "Positions":

                len(

                    self.positions

                ),

            "MarketValue":

                self.market_value,

            "RealizedPnL":

                self.realized_pnl,

            "UnrealizedPnL":

                self.unrealized_pnl,

            "TotalPnL":

                self.total_pnl,

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Positions={len(self.positions)}"

            f")"

        )

    __str__ = __repr__