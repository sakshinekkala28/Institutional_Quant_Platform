"""
======================================================================

Institutional Quant Platform

Execution Service

Author
------
Institutional Quant Platform

Purpose
-------
Enterprise Order Execution Service.

Responsibilities
----------------
• Order Routing
• Execution Algorithms
• Broker Integration
• Fill Processing
• Partial Fills
• Slippage Monitoring
• Execution Analytics

======================================================================
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from threading import Lock, RLock
from typing import Any

import pandas as pd

from core.services.base_service import BaseService

# ============================================================
# Exceptions
# ============================================================


class ExecutionError(Exception):
    """Base execution exception."""


class ExecutionProfileNotFound(ExecutionError):
    """Execution profile not found."""


class ExecutionEngineNotFound(ExecutionError):
    """Execution engine not registered."""


# ============================================================
# Execution Profile
# ============================================================


@dataclass(slots=True)
class ExecutionProfile:
    name: str

    broker: str

    algorithm: str

    parameters: dict[str, Any] = field(default_factory=dict)

    metadata: dict[str, Any] = field(default_factory=dict)


# ============================================================
# Execution Service
# ============================================================


class ExecutionService(BaseService):
    """
    Institutional Execution Manager.
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

        self._profiles: dict[str, ExecutionProfile] = {}

        self._engines: dict[str, Callable] = {}

        self._enabled = True

        self._initialized = True

        self._logger.info("ExecutionService initialized.")

    # =====================================================
    # Lifecycle
    # =====================================================

    def enable(self):

        self._enabled = True

    def disable(self):

        self._enabled = False

    def enabled(self):

        return self._enabled

    # =====================================================
    # Registration
    # =====================================================

    def register(
        self,
        name: str,
        broker: str,
        algorithm: str,
        parameters: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Register execution profile.
        """

        profile = ExecutionProfile(
            name=name,
            broker=broker,
            algorithm=algorithm,
            parameters=parameters or {},
            metadata=metadata or {},
        )

        with self._lock:
            self._profiles[name] = profile

    # =====================================================
    # Execution Engine
    # =====================================================

    def register_engine(self, name: str, engine: Callable) -> None:
        """
        Register execution engine.
        """

        self._engines[name] = engine

    # =====================================================
    # Retrieval
    # =====================================================

    def get(self, profile: str) -> ExecutionProfile:

        if profile not in self._profiles:
            raise ExecutionProfileNotFound(profile)

        return self._profiles[profile]

    # =====================================================
    # BaseService
    # =====================================================

    def run(self):

        return self.statistics()

    # =====================================================
    # Parameter Management
    # =====================================================

    def update_parameter(self, profile: str, name: str, value: Any) -> None:
        """
        Update execution parameter.
        """

        self.get(profile).parameters[name] = value

    def parameter(self, profile: str, name: str, default: Any = None) -> Any:
        """
        Return execution parameter.
        """

        return self.get(profile).parameters.get(name, default)

    # =====================================================
    # Execution
    # =====================================================

    def execute(
        self, profile: str, orders: pd.DataFrame, *args, **kwargs
    ) -> pd.DataFrame:
        """
        Execute orders using the configured
        execution algorithm.
        """

        execution_profile = self.get(profile)

        algorithm = execution_profile.algorithm

        if algorithm not in self._engines:
            raise ExecutionEngineNotFound(algorithm)

        engine = self._engines[algorithm]

        return engine(profile=execution_profile, orders=orders, *args, **kwargs)

    # =====================================================
    # Standard Execution Algorithms
    # =====================================================

    def market(
        self, profile: str, orders: pd.DataFrame, *args, **kwargs
    ) -> pd.DataFrame:

        return self.execute(profile, orders, *args, **kwargs)

    def vwap(self, profile: str, orders: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:

        return self.execute(profile, orders, *args, **kwargs)

    def twap(self, profile: str, orders: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:

        return self.execute(profile, orders, *args, **kwargs)

    def pov(self, profile: str, orders: pd.DataFrame, *args, **kwargs) -> pd.DataFrame:

        return self.execute(profile, orders, *args, **kwargs)

    def iceberg(
        self, profile: str, orders: pd.DataFrame, *args, **kwargs
    ) -> pd.DataFrame:

        return self.execute(profile, orders, *args, **kwargs)

    # =====================================================
    # Slippage
    # =====================================================

    def slippage(self, expected_price: float, executed_price: float) -> float:
        """
        Calculate execution slippage.
        """

        if expected_price == 0:
            return 0.0

        return (executed_price - expected_price) / expected_price

    # =====================================================
    # Fill Statistics
    # =====================================================

    def fill_rate(self, ordered_quantity: float, executed_quantity: float) -> float:
        """
        Fill percentage.
        """

        if ordered_quantity == 0:
            return 0.0

        return executed_quantity / ordered_quantity

    def remaining_quantity(
        self, ordered_quantity: float, executed_quantity: float
    ) -> float:
        """
        Remaining quantity.
        """

        return max(0.0, ordered_quantity - executed_quantity)

    # =====================================================
    # Validation
    # =====================================================

    def validate(self, profile: str) -> bool:
        """
        Validate execution profile.
        """

        execution_profile = self.get(profile)

        if execution_profile.algorithm not in self._engines:
            raise ExecutionEngineNotFound(execution_profile.algorithm)

        return True

    # =====================================================
    # Statistics
    # =====================================================

    def statistics(self) -> dict[str, Any]:
        """
        Execution statistics.
        """

        return {
            "profiles": len(self._profiles),
            "engines": len(self._engines),
            "enabled": self._enabled,
        }

    # =====================================================
    # Metadata
    # =====================================================

    def metadata(self, profile: str) -> dict[str, Any]:
        """
        Return execution metadata.
        """

        return dict(self.get(profile).metadata)

    def update_metadata(self, profile: str, **kwargs) -> None:
        """
        Update execution metadata.
        """

        self.get(profile).metadata.update(kwargs)

    # =====================================================
    # Registry
    # =====================================================

    def exists(self, profile: str) -> bool:
        """
        Check whether profile exists.
        """

        return profile in self._profiles

    def names(self) -> list[str]:
        """
        Registered execution profiles.
        """

        return sorted(self._profiles.keys())

    def remove(self, profile: str) -> None:
        """
        Remove execution profile.
        """

        if profile not in self._profiles:
            raise ExecutionProfileNotFound(profile)

        del self._profiles[profile]

    def clear(self) -> None:
        """
        Clear profiles and execution engines.
        """

        self._profiles.clear()

        self._engines.clear()

    # =====================================================
    # Snapshot
    # =====================================================

    def snapshot(self, profile: str) -> dict[str, Any]:
        """
        Execution profile snapshot.
        """

        execution_profile = self.get(profile)

        return {
            "name": execution_profile.name,
            "broker": execution_profile.broker,
            "algorithm": execution_profile.algorithm,
            "parameters": dict(execution_profile.parameters),
            "metadata": dict(execution_profile.metadata),
        }

    # =====================================================
    # Health
    # =====================================================

    def health(self) -> dict[str, Any]:
        """
        Execution service health.
        """

        return {
            "status": "HEALTHY" if self._enabled else "DISABLED",
            "enabled": self._enabled,
            "profiles": len(self._profiles),
            "execution_engines": len(self._engines),
        }

    # =====================================================
    # Lifecycle
    # =====================================================

    def startup(self) -> None:

        self.enable()

        self._logger.info("ExecutionService started.")

    def shutdown(self) -> None:

        self.clear()

        self.disable()

        self._logger.info("ExecutionService shutdown.")

    # =====================================================
    # Magic Methods
    # =====================================================

    def __contains__(self, profile: str) -> bool:

        return self.exists(profile)

    def __len__(self) -> int:

        return len(self._profiles)

    def __iter__(self):

        return iter(self._profiles.items())

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(profiles={len(self)}, "
            f"engines={len(self._engines)}, "
            f"enabled={self._enabled})"
        )


# ============================================================
# Global Singleton
# ============================================================

execution_service = ExecutionService()
