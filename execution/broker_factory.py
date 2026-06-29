"""
====================================================================
Institutional Quant Platform

Broker Factory

Author : Institutional Quant Platform

Purpose
-------
Institutional broker factory.

Creates broker implementations.

Supports

• Simulator
• Interactive Brokers
• Zerodha
• Alpaca
• Binance

Used By

• ExecutionEngine
• Live Trading
• Paper Trading

====================================================================
"""

from __future__ import annotations

from execution.broker import Broker
from execution.broker_simulator import BrokerSimulator


class BrokerFactory:
    """
    Institutional broker factory.
    """

    _registry: dict[str, type[Broker]] = {

        "SIMULATOR": BrokerSimulator,

    }

    # =====================================================
    # REGISTER
    # =====================================================

    @classmethod
    def register(

        cls,

        name: str,

        broker: type[Broker],

    ) -> None:

        cls._registry[

            name.upper()

        ] = broker

    # =====================================================
    # REMOVE
    # =====================================================

    @classmethod
    def unregister(

        cls,

        name: str,

    ) -> None:

        cls._registry.pop(

            name.upper(),

            None,

        )

    # =====================================================
    # CREATE
    # =====================================================

    @classmethod
    def create(

        cls,

        broker_name: str,

        **kwargs,

    ) -> Broker:

        try:

            broker = cls._registry[

                broker_name.upper()

            ]

        except KeyError as exc:

            available = ", ".join(

                sorted(

                    cls._registry.keys()

                )

            )

            raise ValueError(

                f"Unknown broker "

                f"'{broker_name}'. "

                f"Available: {available}"

            ) from exc

        return broker(

            **kwargs

        )

    # =====================================================
    # AVAILABLE
    # =====================================================

    @classmethod
    def available(

        cls,

    ) -> list[str]:

        return sorted(

            cls._registry.keys()

        )

    # =====================================================
    # EXISTS
    # =====================================================

    @classmethod
    def exists(

        cls,

        broker_name: str,

    ) -> bool:

        return (

            broker_name.upper()

            in cls._registry

        )

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Brokers={len(self._registry)}"

            f")"

        )

    __str__ = __repr__