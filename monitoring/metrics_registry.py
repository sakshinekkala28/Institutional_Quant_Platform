"""
====================================================================
Institutional Quant Platform

Metrics Registry

Author : Institutional Quant Platform

Purpose
-------
Central registry for institutional metrics.

Maintains

• Metric Definitions
• Units
• Thresholds
• Categories
• Descriptions
• Validation Rules

Used By

• Telemetry
• Monitoring
• Dashboard
• Alert Engine

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field


# ==========================================================
# METRIC DEFINITION
# ==========================================================


@dataclass(slots=True, frozen=True)
class MetricDefinition:
    """
    Institutional metric definition.
    """

    name: str

    category: str

    description: str

    unit: str

    warning_threshold: float | None = None

    critical_threshold: float | None = None

    higher_is_better: bool = True

    tags: tuple[str, ...] = ()


# ==========================================================
# METRICS REGISTRY
# ==========================================================


class MetricsRegistry:
    """
    Institutional metrics registry.
    """

    def __init__(

        self,

    ) -> None:

        self._registry: dict[
            str,
            MetricDefinition,
        ] = {}

    # =====================================================
    # REGISTER
    # =====================================================

    def register(

        self,

        metric: MetricDefinition,

    ) -> None:

        self._registry[

            metric.name

        ] = metric

    # =====================================================
    # UNREGISTER
    # =====================================================

    def unregister(

        self,

        metric_name: str,

    ) -> None:

        self._registry.pop(

            metric_name,

            None,

        )

    # =====================================================
    # EXISTS
    # =====================================================

    def exists(

        self,

        metric_name: str,

    ) -> bool:

        return (

            metric_name

            in self._registry

        )

    # =====================================================
    # GET
    # =====================================================

    def get(

        self,

        metric_name: str,

    ) -> MetricDefinition | None:

        return self._registry.get(

            metric_name

        )

    # =====================================================
    # CATEGORY
    # =====================================================

    def by_category(

        self,

        category: str,

    ) -> list[MetricDefinition]:

        return [

            metric

            for metric

            in self._registry.values()

            if metric.category

            == category

        ]

    # =====================================================
    # VALIDATE
    # =====================================================

    def validate(

        self,

        metric_name: str,

        value: float,

    ) -> str:

        metric = self.get(

            metric_name

        )

        if metric is None:

            return "UNKNOWN"

        if (

            metric.warning_threshold

            is None

        ):

            return "OK"

        if metric.higher_is_better:

            if (

                metric.critical_threshold

                is not None

                and

                value

                <

                metric.critical_threshold

            ):

                return "CRITICAL"

            if (

                value

                <

                metric.warning_threshold

            ):

                return "WARNING"

        else:

            if (

                metric.critical_threshold

                is not None

                and

                value

                >

                metric.critical_threshold

            ):

                return "CRITICAL"

            if (

                value

                >

                metric.warning_threshold

            ):

                return "WARNING"

        return "OK"

    # =====================================================
    # METRIC NAMES
    # =====================================================

    @property
    def metric_names(

        self,

    ) -> list[str]:

        return sorted(

            self._registry.keys()

        )

    # =====================================================
    # CATEGORIES
    # =====================================================

    @property
    def categories(

        self,

    ) -> list[str]:

        return sorted(

            {

                metric.category

                for metric

                in self._registry.values()

            }

        )

    # =====================================================
    # COUNT
    # =====================================================

    @property
    def count(

        self,

    ) -> int:

        return len(

            self._registry

        )

    # =====================================================
    # CLEAR
    # =====================================================

    def clear(

        self,

    ) -> None:

        self._registry.clear()

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self,

    ) -> dict:

        return {

            "Metrics":

                self.count,

            "Categories":

                self.categories,

            "MetricNames":

                self.metric_names,

        }

    # =====================================================
    # DEFAULT METRICS
    # =====================================================

    def register_defaults(

        self,

    ) -> None:

        defaults = [

            MetricDefinition(

                name="PortfolioVolatility",

                category="Risk",

                description="Annualized volatility",

                unit="%",

                warning_threshold=0.20,

                critical_threshold=0.30,

                higher_is_better=False,

            ),

            MetricDefinition(

                name="SharpeRatio",

                category="Performance",

                description="Risk-adjusted return",

                unit="Ratio",

                warning_threshold=1.0,

                critical_threshold=0.5,

                higher_is_better=True,

            ),

            MetricDefinition(

                name="MaxDrawdown",

                category="Risk",

                description="Maximum drawdown",

                unit="%",

                warning_threshold=0.15,

                critical_threshold=0.25,

                higher_is_better=False,

            ),

            MetricDefinition(

                name="FillRate",

                category="Execution",

                description="Execution fill rate",

                unit="%",

                warning_threshold=0.95,

                critical_threshold=0.90,

                higher_is_better=True,

            ),

        ]

        for metric in defaults:

            self.register(

                metric

            )

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Metrics={self.count})"

        )

    __str__ = __repr__