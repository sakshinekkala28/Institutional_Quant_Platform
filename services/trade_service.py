"""
======================================================================

Institutional Quant Platform

Trade Service

Author
------
Institutional Quant Platform

Purpose
-------
Enterprise Trade Management Service.

Responsibilities
----------------
• Trade Capture
• Trade Booking
• Trade Allocation
• Settlement
• Commission Calculation
• Trade History
• P&L Attribution

======================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from threading import Lock, RLock
from typing import Any

from core.services.base_service import BaseService

# ============================================================
# Enums
# ============================================================


class TradeSide(StrEnum):
    BUY = "BUY"

    SELL = "SELL"


class TradeStatus(StrEnum):
    BOOKED = "BOOKED"

    ALLOCATED = "ALLOCATED"

    SETTLED = "SETTLED"

    CANCELLED = "CANCELLED"

    RECONCILED = "RECONCILED"


# ============================================================
# Exceptions
# ============================================================


class TradeError(Exception):
    """Base trade exception."""


class TradeNotFoundError(TradeError):
    """Trade not found."""


# ============================================================
# Trade Model
# ============================================================


@dataclass(slots=True)
class Trade:
    trade_id: str

    order_id: str

    symbol: str

    side: TradeSide

    quantity: float

    price: float

    commission: float = 0.0

    fees: float = 0.0

    taxes: float = 0.0

    settlement_date: datetime | None = None

    status: TradeStatus = TradeStatus.BOOKED

    created_at: datetime = field(default_factory=datetime.utcnow)

    metadata: dict[str, Any] = field(default_factory=dict)


# ============================================================
# Trade Service
# ============================================================


class TradeService(BaseService):
    """
    Enterprise Trade Manager.
    """

    _instance = None

    _instance_lock = Lock()

    def __new__(cls, *args, **kwargs):

        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):

        if getattr(self, "_initialized", False):
            return

        super().__init__()

        self._lock = RLock()

        self._trades: dict[str, Trade] = {}

        self._enabled = True

        self._initialized = True

        self._logger.info("TradeService initialized.")

    # =====================================================
    # Lifecycle
    # =====================================================

    def enable(self):

        self._enabled = True

    def disable(self):

        self._enabled = False

    # =====================================================
    # Registration
    # =====================================================

    def book(self, trade: Trade) -> None:
        """
        Book trade.
        """

        with self._lock:
            self._trades[trade.trade_id] = trade

    # =====================================================
    # Retrieval
    # =====================================================

    def get(self, trade_id: str) -> Trade:

        if trade_id not in self._trades:
            raise TradeNotFoundError(trade_id)

        return self._trades[trade_id]

    # =====================================================
    # BaseService
    # =====================================================

    def run(self):

        return self.statistics()

    # =====================================================
    # Allocation
    # =====================================================

    def allocate(self, trade_id: str) -> None:
        """
        Allocate trade.
        """

        trade = self.get(trade_id)

        trade.status = TradeStatus.ALLOCATED

    # =====================================================
    # Settlement
    # =====================================================

    def settle(self, trade_id: str, settlement_date: datetime | None = None) -> None:
        """
        Settle trade.
        """

        trade = self.get(trade_id)

        trade.status = TradeStatus.SETTLED

        trade.settlement_date = settlement_date or datetime.utcnow()

    # =====================================================
    # Commission
    # =====================================================

    def calculate_commission(self, trade_id: str, rate: float) -> float:
        """
        Calculate commission.
        """

        trade = self.get(trade_id)

        commission = trade.quantity * trade.price * rate

        trade.commission = commission

        return commission

    # =====================================================
    # Fees
    # =====================================================

    def calculate_fees(self, trade_id: str, fees: float) -> float:
        """
        Apply exchange fees.
        """

        trade = self.get(trade_id)

        trade.fees = fees

        return fees

    # =====================================================
    # Taxes
    # =====================================================

    def calculate_taxes(self, trade_id: str, taxes: float) -> float:
        """
        Apply taxes.
        """

        trade = self.get(trade_id)

        trade.taxes = taxes

        return taxes

    # =====================================================
    # Cancellation
    # =====================================================

    def cancel(self, trade_id: str) -> None:
        """
        Cancel trade.
        """

        trade = self.get(trade_id)

        trade.status = TradeStatus.CANCELLED

    # =====================================================
    # Reconciliation
    # =====================================================

    def reconcile(self, trade_id: str) -> None:
        """
        Mark trade reconciled.
        """

        trade = self.get(trade_id)

        trade.status = TradeStatus.RECONCILED

    # =====================================================
    # Trade Value
    # =====================================================

    def trade_value(self, trade_id: str) -> float:
        """
        Gross trade value.
        """

        trade = self.get(trade_id)

        return trade.quantity * trade.price

    # =====================================================
    # Total Cost
    # =====================================================

    def total_cost(self, trade_id: str) -> float:
        """
        Total trade cost.
        """

        trade = self.get(trade_id)

        return self.trade_value(trade_id) + trade.commission + trade.fees + trade.taxes

    # =====================================================
    # Realized P&L
    # =====================================================

    def realized_pnl(
        self, buy_price: float, sell_price: float, quantity: float
    ) -> float:
        """
        Calculate realized P&L.
        """

        return (sell_price - buy_price) * quantity

    # =====================================================
    # Unrealized P&L Hook
    # =====================================================

    def unrealized_pnl(self, engine, *args, **kwargs):
        """
        Delegate unrealized P&L.
        """

        return engine.run(*args, **kwargs)

    # =====================================================
    # Validation
    # =====================================================

    def validate(self, trade_id: str) -> bool:
        """
        Validate trade.
        """

        trade = self.get(trade_id)

        if trade.quantity <= 0:
            raise TradeError("Quantity must be positive.")

        if trade.price <= 0:
            raise TradeError("Price must be positive.")

        return True

    # =====================================================
    # Statistics
    # =====================================================

    def statistics(self) -> dict[str, Any]:
        """
        Trade statistics.
        """

        return {
            "trades": len(self._trades),
            "settled": sum(
                trade.status == TradeStatus.SETTLED for trade in self._trades.values()
            ),
            "allocated": sum(
                trade.status == TradeStatus.ALLOCATED for trade in self._trades.values()
            ),
            "enabled": self._enabled,
        }

    # =====================================================
    # Query
    # =====================================================

    def exists(self, trade_id: str) -> bool:
        """
        Check whether trade exists.
        """

        return trade_id in self._trades

    def trades(self) -> list[Trade]:
        """
        Return all trades.
        """

        return list(self._trades.values())

    def trades_by_status(self, status: TradeStatus) -> list[Trade]:
        """
        Return trades filtered by status.
        """

        return [trade for trade in self._trades.values() if trade.status == status]

    def booked_trades(self) -> list[Trade]:

        return self.trades_by_status(TradeStatus.BOOKED)

    def allocated_trades(self) -> list[Trade]:

        return self.trades_by_status(TradeStatus.ALLOCATED)

    def settled_trades(self) -> list[Trade]:

        return self.trades_by_status(TradeStatus.SETTLED)

    def cancelled_trades(self) -> list[Trade]:

        return self.trades_by_status(TradeStatus.CANCELLED)

    def reconciled_trades(self) -> list[Trade]:

        return self.trades_by_status(TradeStatus.RECONCILED)

    # =====================================================
    # Metadata
    # =====================================================

    def metadata(self, trade_id: str) -> dict[str, Any]:
        """
        Return trade metadata.
        """

        return dict(self.get(trade_id).metadata)

    def update_metadata(self, trade_id: str, **kwargs) -> None:
        """
        Update trade metadata.
        """

        self.get(trade_id).metadata.update(kwargs)

    # =====================================================
    # Registry
    # =====================================================

    def remove(self, trade_id: str) -> None:
        """
        Remove trade.
        """

        if trade_id not in self._trades:
            raise TradeNotFoundError(trade_id)

        del self._trades[trade_id]

    def clear(self) -> None:
        """
        Remove all trades.
        """

        self._trades.clear()

    # =====================================================
    # Snapshot
    # =====================================================

    def snapshot(self, trade_id: str) -> dict[str, Any]:
        """
        Trade snapshot.
        """

        trade = self.get(trade_id)

        return {
            "trade_id": trade.trade_id,
            "order_id": trade.order_id,
            "symbol": trade.symbol,
            "side": trade.side.value,
            "quantity": trade.quantity,
            "price": trade.price,
            "trade_value": self.trade_value(trade_id),
            "commission": trade.commission,
            "fees": trade.fees,
            "taxes": trade.taxes,
            "total_cost": self.total_cost(trade_id),
            "status": trade.status.value,
            "settlement_date": (
                trade.settlement_date.isoformat() if trade.settlement_date else None
            ),
            "created_at": trade.created_at.isoformat(),
            "metadata": dict(trade.metadata),
        }

    # =====================================================
    # Health
    # =====================================================

    def health(self) -> dict[str, Any]:
        """
        Trade service health.
        """

        return {
            "status": "HEALTHY" if self._enabled else "DISABLED",
            "enabled": self._enabled,
            "trades": len(self._trades),
            "settled": len(self.settled_trades()),
        }

    # =====================================================
    # Lifecycle
    # =====================================================

    def startup(self) -> None:

        self.enable()

        self._logger.info("TradeService started.")

    def shutdown(self) -> None:

        self.clear()

        self.disable()

        self._logger.info("TradeService shutdown.")

    # =====================================================
    # Magic Methods
    # =====================================================

    def __contains__(self, trade_id: str) -> bool:

        return self.exists(trade_id)

    def __len__(self) -> int:

        return len(self._trades)

    def __iter__(self):

        return iter(self._trades.values())

    def __repr__(self) -> str:

        return f"{self.__class__.__name__}(trades={len(self)}, enabled={self._enabled})"


# ============================================================
# Global Singleton
# ============================================================

trade_service = TradeService()
