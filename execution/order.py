"""
======================================================================
Institutional Quant Platform

Execution Order Domain Model

Purpose
-------
Canonical order-domain definitions shared by:

• Execution algorithms
• Execution engine
• Order router
• Broker
• Order book
• Slippage engine
• Market impact
• Backtesting
• Execution services

======================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


# ============================================================
# ORDER SIDE
# ============================================================


class OrderSide(StrEnum):
    """
    Order direction.
    """

    BUY = "BUY"
    SELL = "SELL"


# ============================================================
# ORDER TYPE
# ============================================================


class OrderType(StrEnum):
    """
    Supported order types.
    """

    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP = "STOP"
    STOP_LIMIT = "STOP_LIMIT"


# ============================================================
# ORDER STATUS
# ============================================================


class OrderStatus(StrEnum):
    """
    Order lifecycle status.
    """

    NEW = "NEW"
    VALIDATED = "VALIDATED"
    ROUTED = "ROUTED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"


# ============================================================
# EXCEPTIONS
# ============================================================


class OrderError(Exception):
    """
    Base order-domain exception.
    """


class OrderNotFoundError(OrderError):
    """
    Raised when an order cannot be found.
    """


# ============================================================
# ORDER
# ============================================================


@dataclass(slots=True)
class Order:
    """
    Canonical execution order.

    Parameters
    ----------
    order_id:
        Unique order identifier.

    symbol:
        Security identifier.

    side:
        BUY or SELL.

    quantity:
        Requested order quantity.

    order_type:
        MARKET, LIMIT, STOP or STOP_LIMIT.

    limit_price:
        Optional limit price.

    executed_quantity:
        Quantity executed so far.

    average_price:
        Average execution price.

    status:
        Current order lifecycle status.

    broker:
        Broker identifier.

    created_at:
        Order creation timestamp.

    metadata:
        Additional order metadata.
    """

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

    created_at: datetime = field(
        default_factory=datetime.utcnow,
    )

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )
