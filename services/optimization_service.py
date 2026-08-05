"""
======================================================================

Institutional Quant Platform

Optimization Service

Author
------
Institutional Quant Platform

Purpose
-------
Enterprise Portfolio Optimization Service.

Responsibilities
----------------
• Portfolio Optimization
• Constraint Management
• Objective Functions
• Risk Constraints
• Position Limits
• Turnover Constraints

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


class OptimizationError(Exception):
    """Base optimization exception."""


class OptimizerNotFoundError(OptimizationError):
    """Optimizer profile not found."""


# ============================================================
# Optimization Profile
# ============================================================


@dataclass(slots=True)
class OptimizationProfile:
    name: str

    objective: str

    constraints: dict[str, Any] = field(default_factory=dict)

    parameters: dict[str, Any] = field(default_factory=dict)

    metadata: dict[str, Any] = field(default_factory=dict)


# ============================================================
# Optimization Service
# ============================================================


class OptimizationService(BaseService):
    """
    Enterprise Portfolio Optimizer.
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

        self._profiles: dict[str, OptimizationProfile] = {}

        self._optimizers: dict[str, Callable] = {}

        self._enabled = True

        self._initialized = True

        self._logger.info("OptimizationService initialized.")

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
        objective: str,
        constraints: dict[str, Any] | None = None,
        parameters: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Register optimization profile.
        """

        profile = OptimizationProfile(
            name=name,
            objective=objective,
            constraints=constraints or {},
            parameters=parameters or {},
            metadata=metadata or {},
        )

        with self._lock:
            self._profiles[name] = profile

    # =====================================================
    # Optimizer Registration
    # =====================================================

    def register_optimizer(self, name: str, optimizer: Callable) -> None:
        """
        Register optimization engine.
        """

        self._optimizers[name] = optimizer

    # =====================================================
    # Retrieval
    # =====================================================

    def get(self, name: str) -> OptimizationProfile:

        if name not in self._profiles:
            raise OptimizerNotFoundError(name)

        return self._profiles[name]

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
        Update optimizer parameter.
        """

        self.get(profile).parameters[name] = value

    def parameter(self, profile: str, name: str, default: Any = None) -> Any:
        """
        Return optimizer parameter.
        """

        return self.get(profile).parameters.get(name, default)

    # =====================================================
    # Optimizer Execution
    # =====================================================

    def optimize(
        self, profile: str, optimizer: str, universe: pd.DataFrame, *args, **kwargs
    ) -> pd.DataFrame:
        """
        Execute optimizer.
        """

        if optimizer not in self._optimizers:
            raise OptimizationError(f"Unknown optimizer '{optimizer}'.")

        engine = self._optimizers[optimizer]

        profile_obj = self.get(profile)

        kwargs["profile"] = profile_obj
        kwargs["universe"] = universe

        return engine(
            *args,
            **kwargs,
        )

    # =====================================================
    # Standard Optimizers
    # =====================================================

    def mean_variance(
        self, profile: str, universe: pd.DataFrame, *args, **kwargs
    ) -> pd.DataFrame:

        return self.optimize(profile, "mean_variance", universe, *args, **kwargs)

    def minimum_variance(
        self, profile: str, universe: pd.DataFrame, *args, **kwargs
    ) -> pd.DataFrame:

        return self.optimize(profile, "minimum_variance", universe, *args, **kwargs)

    def maximum_sharpe(
        self, profile: str, universe: pd.DataFrame, *args, **kwargs
    ) -> pd.DataFrame:

        return self.optimize(profile, "maximum_sharpe", universe, *args, **kwargs)

    def risk_parity(
        self, profile: str, universe: pd.DataFrame, *args, **kwargs
    ) -> pd.DataFrame:

        return self.optimize(profile, "risk_parity", universe, *args, **kwargs)

    def equal_weight(
        self, profile: str, universe: pd.DataFrame, *args, **kwargs
    ) -> pd.DataFrame:

        return self.optimize(profile, "equal_weight", universe, *args, **kwargs)

    def black_litterman(
        self, profile: str, universe: pd.DataFrame, *args, **kwargs
    ) -> pd.DataFrame:

        return self.optimize(profile, "black_litterman", universe, *args, **kwargs)

    # =====================================================
    # Validation
    # =====================================================

    def validate(self, profile: str) -> bool:
        """
        Validate optimization profile.
        """

        instance = self.get(profile)

        if not instance.objective:
            raise OptimizationError("Objective function missing.")

        return True

    # =====================================================
    # Statistics
    # =====================================================

    def statistics(self) -> dict[str, Any]:
        """
        Optimization statistics.
        """

        return {
            "profiles": len(self._profiles),
            "optimizers": len(self._optimizers),
            "enabled": self._enabled,
        }

    # =====================================================
    # Metadata
    # =====================================================

    def metadata(self, profile: str) -> dict[str, Any]:
        """
        Return optimization metadata.
        """

        return dict(self.get(profile).metadata)

    def update_metadata(self, profile: str, **kwargs) -> None:
        """
        Update optimization metadata.
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
        Registered optimization profiles.
        """

        return sorted(self._profiles.keys())

    def remove(self, profile: str) -> None:
        """
        Remove optimization profile.
        """

        if profile not in self._profiles:
            raise OptimizerNotFoundError(profile)

        del self._profiles[profile]

    def clear(self) -> None:
        """
        Remove every profile and optimizer.
        """

        self._profiles.clear()

        self._optimizers.clear()

    # =====================================================
    # Snapshot
    # =====================================================

    def snapshot(self, profile: str) -> dict[str, Any]:
        """
        Optimization profile snapshot.
        """

        instance = self.get(profile)

        return {
            "name": instance.name,
            "objective": instance.objective,
            "constraints": dict(instance.constraints),
            "parameters": dict(instance.parameters),
            "metadata": dict(instance.metadata),
        }

    # =====================================================
    # Health
    # =====================================================

    def health(self) -> dict[str, Any]:
        """
        Service health.
        """

        return {
            "status": "HEALTHY" if self._enabled else "DISABLED",
            "enabled": self._enabled,
            "profiles": len(self._profiles),
            "optimizers": len(self._optimizers),
        }

    # =====================================================
    # Lifecycle
    # =====================================================

    def startup(self) -> None:

        self.enable()

        self._logger.info("OptimizationService started.")

    def shutdown(self) -> None:

        self.clear()

        self.disable()

        self._logger.info("OptimizationService shutdown.")

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
            f"optimizers={len(self._optimizers)}, "
            f"enabled={self._enabled})"
        )


# ============================================================
# Global Singleton
# ============================================================

optimization_service = OptimizationService()
