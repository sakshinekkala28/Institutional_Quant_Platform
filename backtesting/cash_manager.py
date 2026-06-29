"""
====================================================================
Institutional Quant Platform

Cash Manager

Author : Institutional Quant Platform

Purpose
-------
Institutional cash management engine.

Responsible For

• Cash Balance
• Trade Settlement
• Deposits
• Withdrawals
• Transaction Costs

Used By

• Backtest Engine
• Portfolio Tracker
• Performance Engine

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from backtesting.fill_event import FillEvent


@dataclass(slots=True)
class CashManager:
    """
    Institutional cash manager.
    """

    initial_cash: float

    def __post_init__(

        self,

    ) -> None:

        if self.initial_cash < 0:

            raise ValueError(

                "Initial cash cannot be negative."

            )

        self.cash = self.initial_cash

    # =====================================================
    # DEPOSIT
    # =====================================================

    def deposit(

        self,

        amount: float,

    ) -> None:

        if amount < 0:

            raise ValueError(

                "Deposit must be positive."

            )

        self.cash += amount

    # =====================================================
    # WITHDRAW
    # =====================================================

    def withdraw(

        self,

        amount: float,

    ) -> None:

        if amount < 0:

            raise ValueError(

                "Withdrawal must be positive."

            )

        if amount > self.cash:

            raise ValueError(

                "Insufficient cash."

            )

        self.cash -= amount

    # =====================================================
    # SETTLE TRADE
    # =====================================================

    def settle(

        self,

        fill: FillEvent,

    ) -> None:

        amount = (

            fill.net_execution_value

        )

        if fill.side == "BUY":

            self.cash -= amount

        else:

            self.cash += amount

    # =====================================================
    # RESET
    # =====================================================

    def reset(

        self,

    ) -> None:

        self.cash = self.initial_cash

    # =====================================================
    # PROPERTIES
    # =====================================================

    @property
    def balance(

        self,

    ) -> float:

        return self.cash

    @property
    def invested_cash(

        self,

    ) -> float:

        return (

            self.initial_cash

            -

            self.cash

        )

    @property
    def available_cash(

        self,

    ) -> float:

        return self.cash

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self,

    ) -> dict:

        return {

            "InitialCash":

                self.initial_cash,

            "CurrentCash":

                self.cash,

            "InvestedCash":

                self.invested_cash,

            "AvailableCash":

                self.available_cash,

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Cash={self.cash:,.2f}"

            f")"

        )

    __str__ = __repr__