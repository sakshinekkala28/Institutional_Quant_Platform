"""
======================================================================

Institutional Quant Platform

Risk Service

Author
------
Institutional Quant Platform

Purpose
-------
Enterprise Risk Management Service.

Responsibilities
----------------
• Portfolio Risk
• Factor Risk
• Exposure Monitoring
• VaR
• Stress Testing
• Concentration Risk
• Risk Constraints

======================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from threading import Lock
from threading import RLock

from typing import Any
from typing import Dict
from typing import Optional

import pandas as pd

from core.services.base_service import BaseService


# ============================================================
# Exceptions
# ============================================================

class RiskError(Exception):
    """Base risk exception."""


class RiskProfileNotFound(RiskError):
    """Risk profile not found."""


# ============================================================
# Risk Profile
# ============================================================

@dataclass(slots=True)
class RiskProfile:

    name: str

    portfolio: str

    metrics: Dict[str, float] = field(

        default_factory=dict

    )

    limits: Dict[str, float] = field(

        default_factory=dict

    )

    metadata: Dict[str, Any] = field(

        default_factory=dict

    )


# ============================================================
# Risk Service
# ============================================================

class RiskService(BaseService):

    """
    Enterprise Risk Manager.
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

        self._profiles: Dict[str, RiskProfile] = {}

        self._enabled = True

        self._initialized = True

        self._logger.info(

            "RiskService initialized."

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

        metrics: Optional[Dict[str, float]] = None,

        limits: Optional[Dict[str, float]] = None,

        metadata: Optional[Dict[str, Any]] = None

    ) -> None:
        """
        Register risk profile.
        """

        profile = RiskProfile(

            name=name,

            portfolio=portfolio,

            metrics=metrics or {},

            limits=limits or {},

            metadata=metadata or {}

        )

        with self._lock:

            self._profiles[name] = profile

    # =====================================================
    # Retrieval
    # =====================================================

    def get(

        self,

        name: str

    ) -> RiskProfile:

        if name not in self._profiles:

            raise RiskProfileNotFound(

                name

            )

        return self._profiles[name]

    # =====================================================
    # Metrics
    # =====================================================

    def metrics(

        self,

        profile: str

    ) -> Dict[str, float]:

        return dict(

            self.get(

                profile

            ).metrics

        )

    def limits(

        self,

        profile: str

    ) -> Dict[str, float]:

        return dict(

            self.get(

                profile

            ).limits

        )

    # =====================================================
    # BaseService
    # =====================================================

    def run(

        self

    ):

        return self.statistics()
    
    # =====================================================
    # Risk Metrics
    # =====================================================

    def update_metric(

        self,

        profile: str,

        metric: str,

        value: float

    ) -> None:
        """
        Update a risk metric.
        """

        self.get(

            profile

        ).metrics[metric] = value

    # -----------------------------------------------------

    def metric(

        self,

        profile: str,

        metric: str,

        default: Optional[float] = None

    ) -> Optional[float]:
        """
        Get a risk metric.
        """

        return self.get(

            profile

        ).metrics.get(

            metric,

            default

        )

    # =====================================================
    # Risk Limits
    # =====================================================

    def update_limit(

        self,

        profile: str,

        metric: str,

        limit: float

    ) -> None:
        """
        Update risk limit.
        """

        self.get(

            profile

        ).limits[metric] = limit

    # -----------------------------------------------------

    def limit(

        self,

        profile: str,

        metric: str,

        default: Optional[float] = None

    ) -> Optional[float]:

        return self.get(

            profile

        ).limits.get(

            metric,

            default

        )

    # =====================================================
    # Limit Monitoring
    # =====================================================

    def breached_limits(

        self,

        profile: str

    ) -> Dict[str, Dict[str, float]]:
        """
        Return breached limits.
        """

        instance = self.get(

            profile

        )

        breaches = {}

        for metric, value in instance.metrics.items():

            limit = instance.limits.get(

                metric

            )

            if limit is None:

                continue

            if value > limit:

                breaches[metric] = {

                    "value": value,

                    "limit": limit

                }

        return breaches

    # -----------------------------------------------------

    def within_limits(

        self,

        profile: str

    ) -> bool:
        """
        Check whether all metrics
        satisfy configured limits.
        """

        return (

            len(

                self.breached_limits(

                    profile

                )

            )

            == 0

        )

    # =====================================================
    # Standard Risk Metrics
    # =====================================================

    def beta(

        self,

        profile: str

    ) -> Optional[float]:

        return self.metric(

            profile,

            "beta"

        )

    def volatility(

        self,

        profile: str

    ) -> Optional[float]:

        return self.metric(

            profile,

            "volatility"

        )

    def tracking_error(

        self,

        profile: str

    ) -> Optional[float]:

        return self.metric(

            profile,

            "tracking_error"

        )

    def var95(

        self,

        profile: str

    ) -> Optional[float]:

        return self.metric(

            profile,

            "var95"

        )

    def cvar95(

        self,

        profile: str

    ) -> Optional[float]:

        return self.metric(

            profile,

            "cvar95"

        )

    # =====================================================
    # Analytics Hooks
    # =====================================================

    def update_from_engine(

        self,

        profile: str,

        metrics: Dict[str, float]

    ) -> None:
        """
        Update metrics from an external
        analytics engine.
        """

        instance = self.get(

            profile

        )

        instance.metrics.update(

            metrics

        )

    def stress_test(

        self,

        profile: str,

        engine,

        *args,

        **kwargs

    ):
        """
        Delegate stress testing.
        """

        return engine.run(

            self.get(

                profile

            ),

            *args,

            **kwargs

        )

    def value_at_risk(

        self,

        profile: str,

        engine,

        *args,

        **kwargs

    ):
        """
        Delegate VaR calculation.
        """

        return engine.run(

            self.get(

                profile

            ),

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
        Validate profile.
        """

        instance = self.get(

            profile

        )

        if not instance.portfolio:

            raise RiskError(

                "Portfolio not assigned."

            )

        return True

    # =====================================================
    # Statistics
    # =====================================================

    def statistics(

        self

    ) -> Dict[str, Any]:
        """
        Risk service statistics.
        """

        breached = sum(

            len(

                self.breached_limits(

                    profile

                )

            )

            for profile

            in self._profiles

        )

        return {

            "profiles":

                len(

                    self._profiles

                ),

            "breached_limits":

                breached,

            "enabled":

                self._enabled

        }
    
    # =====================================================
    # Exposure
    # =====================================================

    def portfolio_exposure(

        self,

        holdings: pd.DataFrame,

        weight_column: str = "weight"

    ) -> float:
        """
        Calculate gross portfolio exposure.
        """

        if weight_column not in holdings.columns:

            raise RiskError(

                f"Missing column '{weight_column}'."

            )

        return float(

            holdings[weight_column]

            .abs()

            .sum()

        )

    # -----------------------------------------------------

    def net_exposure(

        self,

        holdings: pd.DataFrame,

        weight_column: str = "weight"

    ) -> float:
        """
        Net exposure.
        """

        if weight_column not in holdings.columns:

            raise RiskError(

                f"Missing column '{weight_column}'."

            )

        return float(

            holdings[weight_column].sum()

        )

    # -----------------------------------------------------

    def long_exposure(

        self,

        holdings: pd.DataFrame,

        weight_column: str = "weight"

    ) -> float:

        return float(

            holdings.loc[

                holdings[weight_column] > 0,

                weight_column

            ].sum()

        )

    # -----------------------------------------------------

    def short_exposure(

        self,

        holdings: pd.DataFrame,

        weight_column: str = "weight"

    ) -> float:

        return abs(

            float(

                holdings.loc[

                    holdings[weight_column] < 0,

                    weight_column

                ].sum()

            )

        )

    # =====================================================
    # Concentration
    # =====================================================

    def concentration_index(

        self,

        holdings: pd.DataFrame,

        weight_column: str = "weight"

    ) -> float:
        """
        Herfindahl-Hirschman Index.
        """

        weights = holdings[

            weight_column

        ]

        return float(

            (weights ** 2).sum()

        )

    # =====================================================
    # Metadata
    # =====================================================

    def metadata(

        self,

        profile: str

    ) -> Dict[str, Any]:

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

        return profile in self._profiles

    def names(

        self

    ) -> list[str]:

        return sorted(

            self._profiles.keys()

        )

    def remove(

        self,

        profile: str

    ) -> None:

        if profile not in self._profiles:

            raise RiskProfileNotFound(

                profile

            )

        del self._profiles[profile]

    def clear(

        self

    ) -> None:

        self._profiles.clear()

    # =====================================================
    # Snapshot
    # =====================================================

    def snapshot(

        self,

        profile: str

    ) -> Dict[str, Any]:
        """
        Risk profile snapshot.
        """

        instance = self.get(

            profile

        )

        return {

            "name":

                instance.name,

            "portfolio":

                instance.portfolio,

            "metrics":

                dict(

                    instance.metrics

                ),

            "limits":

                dict(

                    instance.limits

                ),

            "breaches":

                self.breached_limits(

                    profile

                ),

            "metadata":

                dict(

                    instance.metadata

                )

        }

    # =====================================================
    # Health
    # =====================================================

    def health(

        self

    ) -> Dict[str, Any]:
        """
        Risk service health.
        """

        breached_profiles = sum(

            not self.within_limits(

                profile

            )

            for profile

            in self._profiles

        )

        return {

            "status":

                "HEALTHY"

                if breached_profiles == 0

                else "WARNING",

            "enabled":

                self._enabled,

            "profiles":

                len(

                    self._profiles

                ),

            "profiles_with_breaches":

                breached_profiles

        }

    # =====================================================
    # Lifecycle
    # =====================================================

    def startup(

        self

    ) -> None:

        self.enable()

        self._logger.info(

            "RiskService started."

        )

    def shutdown(

        self

    ) -> None:

        self.clear()

        self.disable()

        self._logger.info(

            "RiskService shutdown."

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

            f"enabled={self._enabled})"

        )


# ============================================================
# Global Singleton
# ============================================================

risk_service = RiskService()