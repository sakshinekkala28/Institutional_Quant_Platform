"""
======================================================================

Institutional Quant Platform

Telemetry Service

Author
------
Institutional Quant Platform

Purpose
-------
Enterprise telemetry framework.

Responsibilities
----------------
• Metrics
• Counters
• Gauges
• Histograms
• Timers
• Execution Tracing
• Performance Monitoring
• Health Metrics

======================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock, RLock
import time
from typing import Any

from core.services.base_service import BaseService

# ============================================================
# Exceptions
# ============================================================


class TelemetryError(Exception):
    """Base telemetry exception."""


class MetricAlreadyExistsError(TelemetryError):
    """Metric already registered."""


class MetricNotFoundError(TelemetryError):
    """Metric not found."""


# ============================================================
# Metric Models
# ============================================================


@dataclass(slots=True)
class CounterMetric:
    name: str

    value: int = 0

    description: str = ""

    labels: dict[str, str] = field(default_factory=dict)

    def increment(self, amount: int = 1):

        self.value += amount


# ------------------------------------------------------------


@dataclass(slots=True)
class GaugeMetric:
    name: str

    value: float = 0.0

    description: str = ""

    labels: dict[str, str] = field(default_factory=dict)

    def set(self, value: float):

        self.value = value


# ------------------------------------------------------------


@dataclass(slots=True)
class HistogramMetric:
    name: str

    values: list[float] = field(default_factory=list)

    description: str = ""

    labels: dict[str, str] = field(default_factory=dict)

    def observe(self, value: float):

        self.values.append(value)


# ------------------------------------------------------------


@dataclass(slots=True)
class TimerMetric:
    name: str

    started: float = field(default_factory=time.perf_counter)

    elapsed: float = 0.0

    running: bool = True

    def stop(self):

        if self.running:
            self.elapsed = time.perf_counter() - self.started

            self.running = False

        return self.elapsed


# ============================================================
# Telemetry Service
# ============================================================


class TelemetryService(BaseService):
    """
    Enterprise telemetry manager.

    Thread-safe singleton.

    Supports

    • Counters
    • Gauges
    • Histograms
    • Timers
    • Execution metrics
    • Health metrics
    """

    _instance = None

    _instance_lock = Lock()

    # --------------------------------------------------------

    def __new__(cls, *args, **kwargs):

        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)

        return cls._instance

    # --------------------------------------------------------

    def __init__(self):

        if getattr(self, "_initialized", False):
            return

        super().__init__()

        self._lock = RLock()

        self._counters: dict[str, CounterMetric] = {}

        self._gauges: dict[str, GaugeMetric] = {}

        self._histograms: dict[str, HistogramMetric] = {}

        self._timers: dict[str, TimerMetric] = {}

        self._service_metadata: dict[str, Any] = {}

        self._enabled = True

        self._initialized = True

        self._logger.info("TelemetryService initialized.")

    # =====================================================
    # Lifecycle
    # =====================================================

    def enable(self):

        self._enabled = True

    def disable(self):

        self._enabled = False

    def enabled(self) -> bool:

        return self._enabled

    # =====================================================
    # Registry
    # =====================================================

    def register_counter(self, name: str, description: str = ""):

        with self._lock:
            if name in self._counters:
                raise MetricAlreadyExistsError(name)

            self._counters[name] = CounterMetric(name=name, description=description)

    def register_gauge(self, name: str, description: str = ""):

        with self._lock:
            if name in self._gauges:
                raise MetricAlreadyExistsError(name)

            self._gauges[name] = GaugeMetric(name=name, description=description)

    def register_histogram(self, name: str, description: str = ""):

        with self._lock:
            if name in self._histograms:
                raise MetricAlreadyExistsError(name)

            self._histograms[name] = HistogramMetric(name=name, description=description)

    # =====================================================
    # BaseService
    # =====================================================

    def run(self):

        return self.statistics()

    # =====================================================
    # Counter Operations
    # =====================================================

    def increment_counter(self, name: str, amount: int = 1) -> int:
        """
        Increment a counter.
        """

        with self._lock:
            if name not in self._counters:
                self.register_counter(name)

            counter = self._counters[name]

            counter.increment(amount)

            return counter.value

    def decrement_counter(self, name: str, amount: int = 1) -> int:
        """
        Decrement a counter.
        """

        return self.increment_counter(name, -amount)

    def counter_value(self, name: str) -> int:
        """
        Return counter value.
        """

        if name not in self._counters:
            raise MetricNotFoundError(name)

        return self._counters[name].value

    # =====================================================
    # Gauge Operations
    # =====================================================

    def set_gauge(self, name: str, value: float) -> None:
        """
        Set gauge value.
        """

        with self._lock:
            if name not in self._gauges:
                self.register_gauge(name)

            self._gauges[name].set(value)

    def increment_gauge(self, name: str, amount: float = 1.0) -> float:
        """
        Increment gauge.
        """

        with self._lock:
            if name not in self._gauges:
                self.register_gauge(name)

            gauge = self._gauges[name]

            gauge.value += amount

            return gauge.value

    def gauge_value(self, name: str) -> float:

        if name not in self._gauges:
            raise MetricNotFoundError(name)

        return self._gauges[name].value

    # =====================================================
    # Histogram Operations
    # =====================================================

    def observe(self, name: str, value: float) -> None:
        """
        Record histogram observation.
        """

        with self._lock:
            if name not in self._histograms:
                self.register_histogram(name)

            self._histograms[name].observe(value)

    def histogram_values(self, name: str) -> list[float]:

        if name not in self._histograms:
            raise MetricNotFoundError(name)

        return list(self._histograms[name].values)

    # =====================================================
    # Timer Operations
    # =====================================================

    def start_timer(self, name: str) -> None:
        """
        Start execution timer.
        """

        with self._lock:
            self._timers[name] = TimerMetric(name=name)

    def stop_timer(self, name: str) -> float:
        """
        Stop execution timer.
        """

        with self._lock:
            timer = self._timers.get(name)

            if timer is None:
                raise MetricNotFoundError(name)

            elapsed = timer.stop()

            self.observe(f"{name}_duration", elapsed)

            return elapsed

    def timer_elapsed(self, name: str) -> float:

        timer = self._timers.get(name)

        if timer is None:
            raise MetricNotFoundError(name)

        if timer.running:
            return time.perf_counter() - timer.started

        return timer.elapsed

    # =====================================================
    # Metadata
    # =====================================================

    def register_metadata(self, key: str, value: Any) -> None:
        """
        Register service metadata.
        """

        with self._lock:
            self._service_metadata[key] = value

    def metadata(self) -> dict[str, Any]:

        return dict(self._service_metadata)

    # =====================================================
    # Retrieval
    # =====================================================

    def counters(self) -> dict[str, CounterMetric]:

        return dict(self._counters)

    def gauges(self) -> dict[str, GaugeMetric]:

        return dict(self._gauges)

    def histograms(self) -> dict[str, HistogramMetric]:

        return dict(self._histograms)

    def timers(self) -> dict[str, TimerMetric]:

        return dict(self._timers)

    # =====================================================
    # Reset
    # =====================================================

    def reset_counter(self, name: str) -> None:

        if name in self._counters:
            self._counters[name].value = 0

    def reset_all(self) -> None:
        """
        Reset all metrics.
        """

        with self._lock:
            self._counters.clear()

            self._gauges.clear()

            self._histograms.clear()

            self._timers.clear()

            self._service_metadata.clear()

    # =====================================================
    # Histogram Analytics
    # =====================================================

    def histogram_count(self, name: str) -> int:

        histogram = self._histograms.get(name)

        if histogram is None:
            raise MetricNotFoundError(name)

        return len(histogram.values)

    def histogram_min(self, name: str) -> float:

        histogram = self._histograms.get(name)

        if histogram is None:
            raise MetricNotFoundError(name)

        if not histogram.values:
            return 0.0

        return min(histogram.values)

    def histogram_max(self, name: str) -> float:

        histogram = self._histograms.get(name)

        if histogram is None:
            raise MetricNotFoundError(name)

        if not histogram.values:
            return 0.0

        return max(histogram.values)

    def histogram_mean(self, name: str) -> float:

        histogram = self._histograms.get(name)

        if histogram is None:
            raise MetricNotFoundError(name)

        if not histogram.values:
            return 0.0

        return sum(histogram.values) / len(histogram.values)

    # =====================================================
    # Percentiles
    # =====================================================

    def percentile(self, name: str, percentile: float) -> float:
        """
        Compute percentile.
        """

        histogram = self._histograms.get(name)

        if histogram is None:
            raise MetricNotFoundError(name)

        if not histogram.values:
            return 0.0

        values = sorted(histogram.values)

        index = int((len(values) - 1) * percentile)

        return values[index]

    def p50(self, name: str) -> float:

        return self.percentile(name, 0.50)

    def p90(self, name: str) -> float:

        return self.percentile(name, 0.90)

    def p95(self, name: str) -> float:

        return self.percentile(name, 0.95)

    def p99(self, name: str) -> float:

        return self.percentile(name, 0.99)

    # =====================================================
    # Timing Context
    # =====================================================

    class TimerContext:
        def __init__(self, telemetry, metric_name: str):

            self.telemetry = telemetry

            self.metric_name = metric_name

            self.started = None

        def __enter__(self):

            self.started = time.perf_counter()

            return self

        def __exit__(self, exc_type, exc, tb):

            elapsed = time.perf_counter() - self.started

            self.telemetry.observe(self.metric_name, elapsed)

    def timer(self, metric_name: str):
        """
        Usage

        with telemetry.timer("optimizer"):
            ...
        """

        return self.TimerContext(self, metric_name)

    # =====================================================
    # Trace Events
    # =====================================================

    def trace(self, operation: str, duration: float, success: bool = True) -> None:

        self.observe(f"{operation}_duration", duration)

        self.increment_counter(f"{operation}_calls")

        if success:
            self.increment_counter(f"{operation}_success")

        else:
            self.increment_counter(f"{operation}_failure")

    # =====================================================
    # Service Metrics
    # =====================================================

    def record_service_runtime(self, service_name: str, elapsed: float) -> None:

        self.observe(f"{service_name}_runtime", elapsed)

    def record_exception(self, service_name: str) -> None:

        self.increment_counter(f"{service_name}_exceptions")

    def record_request(self, service_name: str) -> None:

        self.increment_counter(f"{service_name}_requests")

    # =====================================================
    # Export
    # =====================================================

    def snapshot(self) -> dict[str, Any]:
        """
        Export all telemetry.
        """

        return {
            "counters": {key: metric.value for key, metric in self._counters.items()},
            "gauges": {key: metric.value for key, metric in self._gauges.items()},
            "histograms": {
                key: {
                    "count": len(metric.values),
                    "min": min(metric.values) if metric.values else 0,
                    "max": max(metric.values) if metric.values else 0,
                    "mean": (
                        (sum(metric.values) / len(metric.values))
                        if metric.values
                        else 0
                    ),
                    "p95": self.p95(key) if metric.values else 0,
                }
                for key, metric in self._histograms.items()
            },
            "metadata": self.metadata(),
        }

    # =====================================================
    # Health
    # =====================================================

    def health(self) -> dict[str, Any]:
        """
        Telemetry health report.
        """

        return {
            "status": "HEALTHY",
            "enabled": self._enabled,
            "counters": len(self._counters),
            "gauges": len(self._gauges),
            "histograms": len(self._histograms),
            "timers": len(self._timers),
        }

    # =====================================================
    # Diagnostics
    # =====================================================

    def statistics(self) -> dict[str, Any]:
        """
        Telemetry statistics.
        """

        histogram_samples = sum(
            len(metric.values) for metric in self._histograms.values()
        )

        return {
            "enabled": self._enabled,
            "counter_count": len(self._counters),
            "gauge_count": len(self._gauges),
            "histogram_count": len(self._histograms),
            "timer_count": len(self._timers),
            "histogram_samples": histogram_samples,
            "metadata_entries": len(self._service_metadata),
        }

    # =====================================================
    # Prometheus Export
    # =====================================================

    def prometheus_export(self) -> str:
        """
        Export metrics using the Prometheus text exposition format.
        """

        lines = []

        # -------------------------------
        # Counters
        # -------------------------------

        for metric in self._counters.values():
            lines.append(f"# TYPE {metric.name} counter")

            lines.append(f"{metric.name} {metric.value}")

        # -------------------------------
        # Gauges
        # -------------------------------

        for metric in self._gauges.values():
            lines.append(f"# TYPE {metric.name} gauge")

            lines.append(f"{metric.name} {metric.value}")

        # -------------------------------
        # Histograms (summary)
        # -------------------------------

        for metric in self._histograms.values():
            if not metric.values:
                continue

            lines.append(f"# TYPE {metric.name} summary")

            lines.append(f"{metric.name}_count {len(metric.values)}")

            lines.append(f"{metric.name}_sum {sum(metric.values)}")

            lines.append(f"{metric.name}_p50 {self.p50(metric.name)}")

            lines.append(f"{metric.name}_p95 {self.p95(metric.name)}")

            lines.append(f"{metric.name}_p99 {self.p99(metric.name)}")

        return "\n".join(lines)

    # =====================================================
    # OpenTelemetry Hooks
    # =====================================================

    def begin_span(self, span_name: str) -> None:
        """
        Placeholder for future OpenTelemetry span support.
        """

        self.start_timer(span_name)

    def end_span(self, span_name: str) -> float:
        """
        Finish a telemetry span.
        """

        return self.stop_timer(span_name)

    # =====================================================
    # Maintenance
    # =====================================================

    def clear_histograms(self) -> None:

        for histogram in self._histograms.values():
            histogram.values.clear()

    def clear_timers(self) -> None:

        self._timers.clear()

    def cleanup(self) -> None:
        """
        Cleanup transient metrics.
        """

        self.clear_timers()

    # =====================================================
    # Lifecycle
    # =====================================================

    def startup(self) -> None:

        self.enable()

        self._logger.info("Telemetry service started.")

    def shutdown(self) -> None:

        self.cleanup()

        self.disable()

        self._logger.info("Telemetry service shutdown.")

    # =====================================================
    # Magic Methods
    # =====================================================

    def __contains__(self, metric: str) -> bool:

        return (
            metric in self._counters
            or metric in self._gauges
            or metric in self._histograms
        )

    def __len__(self) -> int:

        return len(self._counters) + len(self._gauges) + len(self._histograms)

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}(metrics={len(self)}, enabled={self._enabled})"
        )


# ============================================================
# Global Singleton
# ============================================================

telemetry_service = TelemetryService()
