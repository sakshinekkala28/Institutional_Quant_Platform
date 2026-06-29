"""
====================================================================
Institutional Quant Platform

Broker Interface

Author : Institutional Quant Platform

Purpose
-------
Abstract broker interface.

Provides a common execution contract for
all broker implementations.

Implemented By

• BrokerSimulator
• InteractiveBrokersBroker
• ZerodhaBroker
• AlpacaBroker
• BinanceBroker

Used By

• ExecutionEngine
• OrderRouter

====================================================================
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from execution.execution_report import ExecutionReport
from execution.order import Order


class Broker(ABC):
    """
    Institutional broker interface.
    """

    def __init__(

        self,

        name: str,

    ) -> None:

        self.name = name

    # =====================================================
    # CONNECT
    # =====================================================

    @abstractmethod
    def connect(

        self,

    ) -> None:
        """
        Connect to broker.
        """

        raise NotImplementedError

    # =====================================================
    # DISCONNECT
    # =====================================================

    @abstractmethod
    def disconnect(

        self,

    ) -> None:
        """
        Disconnect from broker.
        """

        raise NotImplementedError

    # =====================================================
    # CONNECTION STATUS
    # =====================================================

    @property
    @abstractmethod
    def is_connected(

        self,

    ) -> bool:
        """
        Broker connection status.
        """

        raise NotImplementedError

    # =====================================================
    # SUBMIT ORDER
    # =====================================================

    @abstractmethod
    def submit_order(

        self,

        order: Order,

    ) -> ExecutionReport:
        """
        Submit order.
        """

        raise NotImplementedError

    # =====================================================
    # CANCEL ORDER
    # =====================================================

    @abstractmethod
    def cancel_order(

        self,

        order_id: str,

    ) -> bool:
        """
        Cancel order.
        """

        raise NotImplementedError

    # =====================================================
    # MODIFY ORDER
    # =====================================================

    @abstractmethod
    def modify_order(

        self,

        order: Order,

    ) -> ExecutionReport:
        """
        Modify an existing order.
        """

        raise NotImplementedError

    # =====================================================
    # ACCOUNT INFORMATION
    # =====================================================

    @abstractmethod
    def account_info(

        self,

    ) -> dict:
        """
        Return broker account information.
        """

        raise NotImplementedError

    # =====================================================
    # OPEN ORDERS
    # =====================================================

    @abstractmethod
    def open_orders(

        self,

    ) -> list[Order]:
        """
        Return all open orders.
        """

        raise NotImplementedError

    # =====================================================
    # POSITIONS
    # =====================================================

    @abstractmethod
    def positions(

        self,

    ) -> dict:
        """
        Return portfolio positions.
        """

        raise NotImplementedError

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Broker='{self.name}'"

            f")"

        )

    __str__ = __repr__