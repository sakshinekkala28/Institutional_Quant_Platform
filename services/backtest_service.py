"""
======================================================================

Institutional Quant Platform

Backtest Service

Author
------
Institutional Quant Platform

Purpose
-------
Enterprise Backtesting Service.

Responsibilities
----------------
• Historical Simulation
• Strategy Validation
• Walk Forward Testing
• Performance Analysis
• Benchmark Comparison
• Scenario Testing
• Monte Carlo Hooks

======================================================================
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock, RLock
from typing import Any

from core.services.base_service import BaseService

# ============================================================
# Exceptions
# ============================================================


class BacktestError(Exception):
    """Base backtest exception."""


class BacktestProfileNotFound(BacktestError):
    """Backtest profile not found."""


class BacktestEngineNotFound(BacktestError):
    """Backtest engine not registered."""


# ============================================================
# Backtest Profile
# ============================================================


@dataclass(slots=True)
class BacktestProfile:
    name: str

    strategy: str

    benchmark: str

    start_date: datetime | None = None

    end_date: datetime | None = None

    parameters: dict[str, Any] = field(default_factory=dict)

    metadata: dict[str, Any] = field(default_factory=dict)


# ============================================================
# Backtest Service
# ============================================================


class BacktestService(BaseService):
    """
    Enterprise Backtesting Manager.
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

        self._profiles: dict[str, BacktestProfile] = {}

        self._engines: dict[str, Callable] = {}

        self._enabled = True

        self._initialized = True

        self._logger.info("BacktestService initialized.")

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
        strategy: str,
        benchmark: str,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        parameters: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Register backtest profile.
        """

        profile = BacktestProfile(
            name=name,
            strategy=strategy,
            benchmark=benchmark,
            start_date=start_date,
            end_date=end_date,
            parameters=parameters or {},
            metadata=metadata or {},
        )

        with self._lock:
            self._profiles[name] = profile

    # =====================================================
    # Backtest Engine
    # =====================================================

    def register_engine(self, name: str, engine: Callable) -> None:
        """
        Register backtest engine.
        """

        self._engines[name] = engine

    # =====================================================
    # Retrieval
    # =====================================================

    def get(self, profile: str) -> BacktestProfile:

        if profile not in self._profiles:
            raise BacktestProfileNotFound(profile)

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
        Update backtest parameter.
        """

        self.get(profile).parameters[name] = value

    def parameter(self, profile: str, name: str, default: Any = None) -> Any:
        """
        Return backtest parameter.
        """

        return self.get(profile).parameters.get(name, default)

    # =====================================================
    # Backtest Execution
    # =====================================================

    def execute(self, profile: str, engine: str, *args, **kwargs):
        """
        Execute backtest engine.
        """

        if engine not in self._engines:
            raise BacktestEngineNotFound(engine)

        backtest_engine = self._engines[engine]

        return backtest_engine(profile=self.get(profile), *args, **kwargs)

    # =====================================================
    # Standard Backtests
    # =====================================================

    def historical(self, profile: str, *args, **kwargs):

        return self.execute(profile, "historical", *args, **kwargs)

    def walk_forward(self, profile: str, *args, **kwargs):

        return self.execute(profile, "walk_forward", *args, **kwargs)

    def monte_carlo(self, profile: str, *args, **kwargs):

        return self.execute(profile, "monte_carlo", *args, **kwargs)

    def scenario_analysis(self, profile: str, *args, **kwargs):

        return self.execute(profile, "scenario_analysis", *args, **kwargs)

    def benchmark_comparison(self, profile: str, *args, **kwargs):

        return self.execute(profile, "benchmark_comparison", *args, **kwargs)

    def attribution(self, profile: str, *args, **kwargs):

        return self.execute(profile, "attribution", *args, **kwargs)

    # =====================================================
    # Validation
    # =====================================================

    def validate(self, profile: str) -> bool:
        """
        Validate backtest profile.
        """

        instance = self.get(profile)

        if not instance.strategy:
            raise BacktestError("Strategy is required.")

        if not instance.benchmark:
            raise BacktestError("Benchmark is required.")

        if (
            instance.start_date
            and instance.end_date
            and instance.start_date > instance.end_date
        ):
            raise BacktestError("Start date must be before end date.")

        return True

    # =====================================================
    # Statistics
    # =====================================================

    def statistics(self) -> dict[str, Any]:
        """
        Backtest statistics.
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
        Return backtest metadata.
        """

        return dict(self.get(profile).metadata)

    def update_metadata(self, profile: str, **kwargs) -> None:
        """
        Update backtest metadata.
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
        Return registered profiles.
        """

        return sorted(self._profiles.keys())

    def remove(self, profile: str) -> None:
        """
        Remove backtest profile.
        """

        if profile not in self._profiles:
            raise BacktestProfileNotFound(profile)

        del self._profiles[profile]

    def clear(self) -> None:
        """
        Clear all profiles and engines.
        """

        self._profiles.clear()

        self._engines.clear()

    # =====================================================
    # Snapshot
    # =====================================================

    def snapshot(self, profile: str) -> dict[str, Any]:
        """
        Backtest profile snapshot.
        """

        backtest = self.get(profile)

        return {
            "name": backtest.name,
            "strategy": backtest.strategy,
            "benchmark": backtest.benchmark,
            "start_date": (
                backtest.start_date.isoformat() if backtest.start_date else None
            ),
            "end_date": (backtest.end_date.isoformat() if backtest.end_date else None),
            "parameters": dict(backtest.parameters),
            "metadata": dict(backtest.metadata),
        }

    # =====================================================
    # Health
    # =====================================================

    def health(self) -> dict[str, Any]:
        """
        Backtest service health.
        """

        return {
            "status": "HEALTHY" if self._enabled else "DISABLED",
            "enabled": self._enabled,
            "profiles": len(self._profiles),
            "engines": len(self._engines),
        }

    # =====================================================
    # Lifecycle
    # =====================================================

    def startup(self) -> None:

        self.enable()

        self._logger.info("BacktestService started.")

    def shutdown(self) -> None:

        self.clear()

        self.disable()

        self._logger.info("BacktestService shutdown.")

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

backtest_service = BacktestService()
