"""
======================================================================

Institutional Quant Platform

Performance Service

Author
------
Institutional Quant Platform

Purpose
-------
Enterprise Portfolio Performance Service.

Responsibilities
----------------
• Return Calculation
• Benchmark Comparison
• Risk-adjusted Metrics
• Attribution Hooks
• Rolling Statistics
• Performance Snapshots

======================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from threading import Lock
from threading import RLock

from typing import Any
from typing import Callable
from typing import Dict
from typing import Optional

import pandas as pd

from core.services.base_service import BaseService


# ============================================================
# Exceptions
# ============================================================

class PerformanceError(Exception):
    """Base performance exception."""


class PerformanceProfileNotFound(PerformanceError):
    """Performance profile not found."""


# ============================================================
# Performance Profile
# ============================================================

@dataclass(slots=True)
class PerformanceProfile:

    name: str

    portfolio: str

    benchmark: str

    metrics: Dict[str, float] = field(

        default_factory=dict

    )

    metadata: Dict[str, Any] = field(

        default_factory=dict

    )


# ============================================================
# Performance Service
# ============================================================

class PerformanceService(BaseService):

    """
    Enterprise Performance Manager.
    """

    _instance = None

    _instance_lock = Lock()

    def __new__(

        cls,

        *args,

        **kwargs

    ):

        if cls._instance is None:

            with cls._instance_lock:

                if cls._instance is None:

                    cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(

        self

    ):

        if getattr(

            self,

            "_initialized",

            False

        ):

            return

        super().__init__()

        self._lock = RLock()

        self._profiles: Dict[str, PerformanceProfile] = {}

        self._engines: Dict[str, Callable] = {}

        self._enabled = True

        self._initialized = True

        self._logger.info(

            "PerformanceService initialized."

        )

    # =====================================================
    # Lifecycle
    # =====================================================

    def enable(

        self

    ):

        self._enabled = True

    def disable(

        self

    ):

        self._enabled = False

    def enabled(

        self

    ):

        return self._enabled

    # =====================================================
    # Registration
    # =====================================================

    def register(

        self,

        name: str,

        portfolio: str,

        benchmark: str,

        metrics: Optional[Dict[str, float]] = None,

        metadata: Optional[Dict[str, Any]] = None

    ) -> None:
        """
        Register performance profile.
        """

        profile = PerformanceProfile(

            name=name,

            portfolio=portfolio,

            benchmark=benchmark,

            metrics=metrics or {},

            metadata=metadata or {}

        )

        with self._lock:

            self._profiles[name] = profile

    # =====================================================
    # Analytics Engine
    # =====================================================

    def register_engine(

        self,

        name: str,

        engine: Callable

    ) -> None:
        """
        Register analytics engine.
        """

        self._engines[name] = engine

    # =====================================================
    # Retrieval
    # =====================================================

    def get(

        self,

        profile: str

    ) -> PerformanceProfile:

        if profile not in self._profiles:

            raise PerformanceProfileNotFound(

                profile

            )

        return self._profiles[profile]

    # =====================================================
    # BaseService
    # =====================================================

    def run(

        self

    ):

        return self.statistics()
    
    # =====================================================
    # Metrics
    # =====================================================

    def update_metric(

        self,

        profile: str,

        metric: str,

        value: float

    ) -> None:
        """
        Update performance metric.
        """

        self.get(

            profile

        ).metrics[metric] = value

    def metric(

        self,

        profile: str,

        metric: str,

        default: Optional[float] = None

    ) -> Optional[float]:
        """
        Return performance metric.
        """

        return self.get(

            profile

        ).metrics.get(

            metric,

            default

        )

    # =====================================================
    # Standard Metrics
    # =====================================================

    def total_return(

        self,

        profile: str

    ) -> Optional[float]:

        return self.metric(

            profile,

            "total_return"

        )

    def annualized_return(

        self,

        profile: str

    ) -> Optional[float]:

        return self.metric(

            profile,

            "annualized_return"

        )

    def benchmark_return(

        self,

        profile: str

    ) -> Optional[float]:

        return self.metric(

            profile,

            "benchmark_return"

        )

    def alpha(

        self,

        profile: str

    ) -> Optional[float]:

        return self.metric(

            profile,

            "alpha"

        )

    def beta(

        self,

        profile: str

    ) -> Optional[float]:

        return self.metric(

            profile,

            "beta"

        )

    def sharpe(

        self,

        profile: str

    ) -> Optional[float]:

        return self.metric(

            profile,

            "sharpe"

        )

    def sortino(

        self,

        profile: str

    ) -> Optional[float]:

        return self.metric(

            profile,

            "sortino"

        )

    def calmar(

        self,

        profile: str

    ) -> Optional[float]:

        return self.metric(

            profile,

            "calmar"

        )

    def information_ratio(

        self,

        profile: str

    ) -> Optional[float]:

        return self.metric(

            profile,

            "information_ratio"

        )

    def tracking_error(

        self,

        profile: str

    ) -> Optional[float]:

        return self.metric(

            profile,

            "tracking_error"

        )

    def maximum_drawdown(

        self,

        profile: str

    ) -> Optional[float]:

        return self.metric(

            profile,

            "maximum_drawdown"

        )

    # =====================================================
    # Analytics Hooks
    # =====================================================

    def evaluate(

        self,

        profile: str,

        engine: str,

        *args,

        **kwargs

    ):
        """
        Execute analytics engine.
        """

        if engine not in self._engines:

            raise PerformanceError(

                f"Unknown engine '{engine}'."

            )

        analytics = self._engines[

            engine

        ]

        return analytics(

            profile=self.get(

                profile

            ),

            *args,

            **kwargs

        )

    def rolling_metrics(

        self,

        profile: str,

        *args,

        **kwargs

    ):

        return self.evaluate(

            profile,

            "rolling",

            *args,

            **kwargs

        )

    def attribution(

        self,

        profile: str,

        *args,

        **kwargs

    ):

        return self.evaluate(

            profile,

            "attribution",

            *args,

            **kwargs

        )

    # =====================================================
    # Validation
    # =====================================================

    def validate(

        self,

        profile: str

    ) -> bool:
        """
        Validate performance profile.
        """

        instance = self.get(

            profile

        )

        if not instance.portfolio:

            raise PerformanceError(

                "Portfolio not assigned."

            )

        if not instance.benchmark:

            raise PerformanceError(

                "Benchmark not assigned."

            )

        return True

    # =====================================================
    # Statistics
    # =====================================================

    def statistics(

        self

    ) -> Dict[str, Any]:
        """
        Performance statistics.
        """

        return {

            "profiles":

                len(

                    self._profiles

                ),

            "analytics_engines":

                len(

                    self._engines

                ),

            "enabled":

                self._enabled

        }
    
    # =====================================================
    # Metadata
    # =====================================================

    def metadata(

        self,

        profile: str

    ) -> Dict[str, Any]:
        """
        Return performance metadata.
        """

        return dict(

            self.get(

                profile

            ).metadata

        )

    def update_metadata(

        self,

        profile: str,

        **kwargs

    ) -> None:
        """
        Update performance metadata.
        """

        self.get(

            profile

        ).metadata.update(

            kwargs

        )

    # =====================================================
    # Registry
    # =====================================================

    def exists(

        self,

        profile: str

    ) -> bool:
        """
        Check whether profile exists.
        """

        return profile in self._profiles

    def names(

        self

    ) -> list[str]:
        """
        Return registered profiles.
        """

        return sorted(

            self._profiles.keys()

        )

    def remove(

        self,

        profile: str

    ) -> None:
        """
        Remove performance profile.
        """

        if profile not in self._profiles:

            raise PerformanceProfileNotFound(

                profile

            )

        del self._profiles[

            profile

        ]

    def clear(

        self

    ) -> None:
        """
        Remove every profile.
        """

        self._profiles.clear()

        self._engines.clear()

    # =====================================================
    # Snapshot
    # =====================================================

    def snapshot(

        self,

        profile: str

    ) -> Dict[str, Any]:
        """
        Performance profile snapshot.
        """

        performance = self.get(

            profile

        )

        return {

            "name":

                performance.name,

            "portfolio":

                performance.portfolio,

            "benchmark":

                performance.benchmark,

            "metrics":

                dict(

                    performance.metrics

                ),

            "metadata":

                dict(

                    performance.metadata

                )

        }

    # =====================================================
    # Health
    # =====================================================

    def health(

        self

    ) -> Dict[str, Any]:
        """
        Performance service health.
        """

        return {

            "status":

                "HEALTHY"

                if self._enabled

                else "DISABLED",

            "enabled":

                self._enabled,

            "profiles":

                len(

                    self._profiles

                ),

            "analytics_engines":

                len(

                    self._engines

                )

        }

    # =====================================================
    # Lifecycle
    # =====================================================

    def startup(

        self

    ) -> None:

        self.enable()

        self._logger.info(

            "PerformanceService started."

        )

    def shutdown(

        self

    ) -> None:

        self.clear()

        self.disable()

        self._logger.info(

            "PerformanceService shutdown."

        )

    # =====================================================
    # Magic Methods
    # =====================================================

    def __contains__(

        self,

        profile: str

    ) -> bool:

        return self.exists(

            profile

        )

    def __len__(

        self

    ) -> int:

        return len(

            self._profiles

        )

    def __iter__(

        self

    ):

        return iter(

            self._profiles.items()

        )

    def __repr__(

        self

    ) -> str:

        return (

            f"{self.__class__.__name__}"

            f"(profiles={len(self)}, "

            f"engines={len(self._engines)}, "

            f"enabled={self._enabled})"

        )


# ============================================================
# Global Singleton
# ============================================================

performance_service = PerformanceService()