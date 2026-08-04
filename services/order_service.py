"""
======================================================================

Institutional Quant Platform

Order Service

Author
------
Institutional Quant Platform

Purpose
-------
Enterprise Order Management Service.

Responsibilities
----------------
• Order Creation
• Order Validation
• Order Routing
• Order Amendments
• Order Cancellation
• Order Lifecycle
• Broker Acknowledgements

======================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from threading import Lock, RLock
from typing import Any

from core.services.base_service import BaseService

# ============================================================
# Enums
# ============================================================


class OrderSide(str, Enum):
    BUY = "BUY"

    SELL = "SELL"


class OrderType(str, Enum):
    MARKET = "MARKET"

    LIMIT = "LIMIT"

    STOP = "STOP"

    STOP_LIMIT = "STOP_LIMIT"


class OrderStatus(str, Enum):
    NEW = "NEW"

    VALIDATED = "VALIDATED"

    ROUTED = "ROUTED"

    PARTIALLY_FILLED = "PARTIALLY_FILLED"

    FILLED = "FILLED"

    CANCELLED = "CANCELLED"

    REJECTED = "REJECTED"


# ============================================================
# Exceptions
# ============================================================


class OrderError(Exception):
    """Base order exception."""


class OrderNotFoundError(OrderError):
    """Order not found."""


# ============================================================
# Order Model
# ============================================================


@dataclass(slots=True)
class Order:
    order_id: str

    symbol: str

    side: OrderSide

    quantity: float

    order_type: OrderType

    limit_price: float | None = None

    executed_quantity: float = 0.0

    average_price: float = 0.0

    status: OrderStatus = OrderStatus.NEW

    broker: str = ""

    created_at: datetime = field(default_factory=datetime.utcnow)

    metadata: dict[str, Any] = field(default_factory=dict)


# ============================================================
# Order Service
# ============================================================


class OrderService(BaseService):
    """
    Enterprise Order Manager.
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

        self._orders: dict[str, Order] = {}

        self._enabled = True

        self._initialized = True

        self._logger.info("OrderService initialized.")

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

    def create(self, order: Order) -> None:
        """
        Register a new order.
        """

        with self._lock:
            self._orders[order.order_id] = order

    # =====================================================
    # Retrieval
    # =====================================================

    def get(self, order_id: str) -> Order:

        if order_id not in self._orders:
            raise OrderNotFoundError(order_id)

        return self._orders[order_id]

    # =====================================================
    # BaseService
    # =====================================================

    def run(self):

        return self.statistics()

    # =====================================================
    # Validation
    # =====================================================

    def validate(self, order_id: str) -> bool:
        """
        Validate order.
        """

        order = self.get(order_id)

        if order.quantity <= 0:
            raise OrderError("Quantity must be greater than zero.")

        if order.order_type == OrderType.LIMIT and order.limit_price is None:
            raise OrderError("Limit price is required.")

        order.status = OrderStatus.VALIDATED

        return True

    # =====================================================
    # Routing
    # =====================================================

    def route(self, order_id: str, broker: str) -> None:
        """
        Route order to broker.
        """

        order = self.get(order_id)

        self.validate(order_id)

        order.broker = broker

        order.status = OrderStatus.ROUTED

    # =====================================================
    # Amendment
    # =====================================================

    def amend(self, order_id: str, **updates) -> None:
        """
        Amend order.
        """

        order = self.get(order_id)

        if order.status in (OrderStatus.FILLED, OrderStatus.CANCELLED):
            raise OrderError("Cannot amend completed order.")

        for key, value in updates.items():
            if hasattr(order, key):
                setattr(order, key, value)

    # =====================================================
    # Cancellation
    # =====================================================

    def cancel(self, order_id: str) -> None:
        """
        Cancel order.
        """

        order = self.get(order_id)

        if order.status == OrderStatus.FILLED:
            raise OrderError("Filled order cannot be cancelled.")

        order.status = OrderStatus.CANCELLED

    # =====================================================
    # Fill Processing
    # =====================================================

    def record_fill(self, order_id: str, quantity: float, price: float) -> None:
        """
        Record execution fill.
        """

        order = self.get(order_id)

        previous_quantity = order.executed_quantity

        previous_value = previous_quantity * order.average_price

        new_value = quantity * price

        total_quantity = previous_quantity + quantity

        if total_quantity > order.quantity:
            raise OrderError("Fill exceeds order quantity.")

        order.executed_quantity = total_quantity

        if total_quantity > 0:
            order.average_price = (previous_value + new_value) / total_quantity

        if total_quantity == order.quantity:
            order.status = OrderStatus.FILLED

        else:
            order.status = OrderStatus.PARTIALLY_FILLED

    # =====================================================
    # Rejection
    # =====================================================

    def reject(self, order_id: str, reason: str = "") -> None:
        """
        Reject order.
        """

        order = self.get(order_id)

        order.status = OrderStatus.REJECTED

        order.metadata["rejection_reason"] = reason

    # =====================================================
    # Quantities
    # =====================================================

    def remaining_quantity(self, order_id: str) -> float:
        """
        Remaining quantity.
        """

        order = self.get(order_id)

        return order.quantity - order.executed_quantity

    def fill_percentage(self, order_id: str) -> float:
        """
        Fill percentage.
        """

        order = self.get(order_id)

        if order.quantity == 0:
            return 0.0

        return order.executed_quantity / order.quantity

    # =====================================================
    # Statistics
    # =====================================================

    def statistics(self) -> dict[str, Any]:
        """
        OMS statistics.
        """

        return {
            "orders": len(self._orders),
            "filled": sum(
                order.status == OrderStatus.FILLED for order in self._orders.values()
            ),
            "open": sum(
                order.status
                in (
                    OrderStatus.NEW,
                    OrderStatus.VALIDATED,
                    OrderStatus.ROUTED,
                    OrderStatus.PARTIALLY_FILLED,
                )
                for order in self._orders.values()
            ),
            "cancelled": sum(
                order.status == OrderStatus.CANCELLED for order in self._orders.values()
            ),
            "rejected": sum(
                order.status == OrderStatus.REJECTED for order in self._orders.values()
            ),
            "enabled": self._enabled,
        }

    # =====================================================
    # Query
    # =====================================================

    def exists(self, order_id: str) -> bool:
        """
        Check whether order exists.
        """

        return order_id in self._orders

    def orders(self) -> list[Order]:
        """
        Return all orders.
        """

        return list(self._orders.values())

    def orders_by_status(self, status: OrderStatus) -> list[Order]:
        """
        Orders filtered by status.
        """

        return [order for order in self._orders.values() if order.status == status]

    def open_orders(self) -> list[Order]:
        """
        Active orders.
        """

        return (
            self.orders_by_status(OrderStatus.NEW)
            + self.orders_by_status(OrderStatus.VALIDATED)
            + self.orders_by_status(OrderStatus.ROUTED)
            + self.orders_by_status(OrderStatus.PARTIALLY_FILLED)
        )

    def filled_orders(self) -> list[Order]:

        return self.orders_by_status(OrderStatus.FILLED)

    def cancelled_orders(self) -> list[Order]:

        return self.orders_by_status(OrderStatus.CANCELLED)

    def rejected_orders(self) -> list[Order]:

        return self.orders_by_status(OrderStatus.REJECTED)

    # =====================================================
    # Metadata
    # =====================================================

    def metadata(self, order_id: str) -> dict[str, Any]:
        """
        Return order metadata.
        """

        return dict(self.get(order_id).metadata)

    def update_metadata(self, order_id: str, **kwargs) -> None:
        """
        Update order metadata.
        """

        self.get(order_id).metadata.update(kwargs)

    # =====================================================
    # Registry
    # =====================================================

    def remove(self, order_id: str) -> None:
        """
        Remove order.
        """

        if order_id not in self._orders:
            raise OrderNotFoundError(order_id)

        del self._orders[order_id]

    def clear(self) -> None:
        """
        Remove all orders.
        """

        self._orders.clear()

    # =====================================================
    # Snapshot
    # =====================================================

    def snapshot(self, order_id: str) -> dict[str, Any]:
        """
        Order snapshot.
        """

        order = self.get(order_id)

        return {
            "order_id": order.order_id,
            "symbol": order.symbol,
            "side": order.side.value,
            "quantity": order.quantity,
            "executed_quantity": order.executed_quantity,
            "remaining_quantity": self.remaining_quantity(order_id),
            "average_price": order.average_price,
            "status": order.status.value,
            "broker": order.broker,
            "created_at": order.created_at.isoformat(),
            "metadata": dict(order.metadata),
        }

    # =====================================================
    # Health
    # =====================================================

    def health(self) -> dict[str, Any]:
        """
        OMS health.
        """

        return {
            "status": "HEALTHY" if self._enabled else "DISABLED",
            "enabled": self._enabled,
            "orders": len(self._orders),
            "open_orders": len(self.open_orders()),
        }

    # =====================================================
    # Lifecycle
    # =====================================================

    def startup(self) -> None:

        self.enable()

        self._logger.info("OrderService started.")

    def shutdown(self) -> None:

        self.clear()

        self.disable()

        self._logger.info("OrderService shutdown.")

    # =====================================================
    # Magic Methods
    # =====================================================

    def __contains__(self, order_id: str) -> bool:

        return self.exists(order_id)

    def __len__(self) -> int:

        return len(self._orders)

    def __iter__(self):

        return iter(self._orders.values())

    def __repr__(self) -> str:

        return f"{self.__class__.__name__}(orders={len(self)}, enabled={self._enabled})"


# ============================================================
# Global Singleton
# ============================================================

order_service = OrderService()
