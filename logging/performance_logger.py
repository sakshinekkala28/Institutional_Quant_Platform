"""
====================================================================
Institutional Quant Platform

Performance Logger

Author : Institutional Quant Platform

Purpose
-------
Institutional performance logger.

Tracks

• Function Execution Time
• Pipeline Runtime
• Memory Usage
• CPU Usage
• Throughput
• Latency
• Cache Performance

Used By

• Telemetry
• Dashboard
• Monitoring
• Performance Analytics

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from functools import wraps
import json
from pathlib import Path
import statistics
import time

import psutil


# ==========================================================
# PERFORMANCE RECORD
# ==========================================================


@dataclass(slots=True)
class PerformanceRecord:
    """
    Performance measurement.
    """

    timestamp: datetime

    component: str

    operation: str

    execution_time: float

    cpu_percent: float

    memory_mb: float

    metadata: dict

    def summary(

        self,

    ) -> dict:

        return {

            "Timestamp":

                self.timestamp.isoformat(),

            "Component":

                self.component,

            "Operation":

                self.operation,

            "ExecutionTime":

                self.execution_time,

            "CPUPercent":

                self.cpu_percent,

            "MemoryMB":

                self.memory_mb,

            "Metadata":

                self.metadata,

        }


# ==========================================================
# PERFORMANCE LOGGER
# ==========================================================


class PerformanceLogger:
    """
    Institutional performance logger.
    """

    def __init__(

        self,

    ) -> None:

        self._records: list[PerformanceRecord] = []

        self._process = psutil.Process()

    # =====================================================
    # LOG
    # =====================================================

    def log(

        self,

        component: str,

        operation: str,

        execution_time: float,

        **metadata,

    ) -> None:

        self._records.append(

            PerformanceRecord(

                timestamp=datetime.utcnow(),

                component=component,

                operation=operation,

                execution_time=execution_time,

                cpu_percent=psutil.cpu_percent(),

                memory_mb=(

                    self._process

                    .memory_info()

                    .rss

                    / 1024**2

                ),

                metadata=metadata,

            )

        )

    # =====================================================
    # DECORATOR
    # =====================================================

    def measure(

        self,

        component: str,

        operation: str,

    ):

        def decorator(

            function,

        ):

            @wraps(

                function

            )

            def wrapper(

                *args,

                **kwargs,

            ):

                start = (

                    time.perf_counter()

                )

                result = function(

                    *args,

                    **kwargs,

                )

                elapsed = (

                    time.perf_counter()

                    -

                    start

                )

                self.log(

                    component,

                    operation,

                    elapsed,

                )

                return result

            return wrapper

        return decorator

    # =====================================================
    # FILTER COMPONENT
    # =====================================================

    def by_component(

        self,

        component: str,

    ) -> list[PerformanceRecord]:

        return [

            record

            for record

            in self._records

            if record.component

            == component

        ]

    # =====================================================
    # FILTER OPERATION
    # =====================================================

    def by_operation(

        self,

        operation: str,

    ) -> list[PerformanceRecord]:

        return [

            record

            for record

            in self._records

            if record.operation

            == operation

        ]

    # =====================================================
    # STATISTICS
    # =====================================================

    def statistics(

        self,

    ) -> dict:

        if not self._records:

            return {}

        runtimes = [

            record.execution_time

            for record

            in self._records

        ]

        cpu = [

            record.cpu_percent

            for record

            in self._records

        ]

        memory = [

            record.memory_mb

            for record

            in self._records

        ]

        return {

            "Executions":

                len(

                    self._records

                ),

            "AverageRuntime":

                statistics.mean(

                    runtimes

                ),

            "MedianRuntime":

                statistics.median(

                    runtimes

                ),

            "MaximumRuntime":

                max(

                    runtimes

                ),

            "MinimumRuntime":

                min(

                    runtimes

                ),

            "AverageCPU":

                statistics.mean(

                    cpu

                ),

            "AverageMemory":

                statistics.mean(

                    memory

                ),

        }

    # =====================================================
    # EXPORT
    # =====================================================

    def export(

        self,

        filename: str | Path,

    ) -> None:

        payload = [

            record.summary()

            for record

            in self._records

        ]

        with Path(

            filename

        ).open(

            "w",

            encoding="utf-8",

        ) as file:

            json.dump(

                payload,

                file,

                indent=4,

            )

    # =====================================================
    # CLEAR
    # =====================================================

    def clear(

        self,

    ) -> None:

        self._records.clear()

    # =====================================================
    # PROPERTIES
    # =====================================================

    @property
    def records(

        self,

    ) -> list[PerformanceRecord]:

        return list(

            self._records

        )

    @property
    def count(

        self,

    ) -> int:

        return len(

            self._records

        )

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self,

    ) -> dict:

        return {

            "Records":

                self.count,

            **self.statistics(),

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Records={self.count})"

        )

    __str__ = __repr__