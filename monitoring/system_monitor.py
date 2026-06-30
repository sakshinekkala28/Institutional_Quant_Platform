"""
====================================================================
Institutional Quant Platform

System Monitor

Author : Institutional Quant Platform

Purpose
-------
Institutional system monitoring.

Monitors

• CPU Usage
• Memory Usage
• Disk Usage
• Process Uptime
• Thread Count
• Load Average
• Platform Availability
• Network I/O

Used By

• Dashboard
• Health Monitor
• Alert Engine
• Telemetry

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import os
import platform
import time

import psutil


# ==========================================================
# SYSTEM MONITOR RESULT
# ==========================================================


@dataclass(slots=True)
class SystemMonitorResult:
    """
    System monitoring result.
    """

    metric: str

    status: str

    value: float | int | str

    threshold: float | int | None

    timestamp: datetime

    metadata: dict

    def summary(

        self,

    ) -> dict:

        return {

            "Metric":

                self.metric,

            "Status":

                self.status,

            "Value":

                self.value,

            "Threshold":

                self.threshold,

            "Timestamp":

                self.timestamp.isoformat(),

            "Metadata":

                self.metadata,

        }


# ==========================================================
# SYSTEM MONITOR
# ==========================================================


class SystemMonitor:
    """
    Institutional system monitor.
    """

    PROCESS = psutil.Process(

        os.getpid()

    )

    START_TIME = time.time()

    # =====================================================
    # CPU
    # =====================================================

    @staticmethod
    def cpu_usage(

        threshold: float = 85.0,

    ) -> SystemMonitorResult:

        cpu = psutil.cpu_percent(

            interval=0.25

        )

        return SystemMonitorResult(

            metric="CPU Usage",

            status=(

                "OK"

                if cpu <= threshold

                else "WARNING"

            ),

            value=round(

                cpu,

                2,

            ),

            threshold=threshold,

            timestamp=datetime.utcnow(),

            metadata={

                "LogicalCPUs":

                    psutil.cpu_count(),

            },

        )

    # =====================================================
    # MEMORY
    # =====================================================

    @staticmethod
    def memory_usage(

        threshold: float = 85.0,

    ) -> SystemMonitorResult:

        memory = psutil.virtual_memory()

        return SystemMonitorResult(

            metric="Memory Usage",

            status=(

                "OK"

                if memory.percent <= threshold

                else "WARNING"

            ),

            value=round(

                memory.percent,

                2,

            ),

            threshold=threshold,

            timestamp=datetime.utcnow(),

            metadata={

                "AvailableGB":

                    round(

                        memory.available

                        / 1024**3,

                        2,

                    ),

            },

        )

    # =====================================================
    # DISK
    # =====================================================

    @staticmethod
    def disk_usage(

        threshold: float = 90.0,

    ) -> SystemMonitorResult:

        disk = psutil.disk_usage(

            "/"

        )

        return SystemMonitorResult(

            metric="Disk Usage",

            status=(

                "OK"

                if disk.percent <= threshold

                else "WARNING"

            ),

            value=round(

                disk.percent,

                2,

            ),

            threshold=threshold,

            timestamp=datetime.utcnow(),

            metadata={

                "FreeGB":

                    round(

                        disk.free

                        / 1024**3,

                        2,

                    ),

            },

        )

    # =====================================================
    # PROCESS UPTIME
    # =====================================================

    @classmethod
    def uptime(

        cls,

    ) -> SystemMonitorResult:

        uptime = (

            time.time()

            -

            cls.START_TIME

        )

        return SystemMonitorResult(

            metric="Process Uptime",

            status="OK",

            value=round(

                uptime,

                2,

            ),

            threshold=None,

            timestamp=datetime.utcnow(),

            metadata={

                "Unit":

                    "Seconds",

            },

        )

    # =====================================================
    # THREAD COUNT
    # =====================================================

    @classmethod
    def threads(

        cls,

    ) -> SystemMonitorResult:

        count = cls.PROCESS.num_threads()

        return SystemMonitorResult(

            metric="Thread Count",

            status="OK",

            value=count,

            threshold=None,

            timestamp=datetime.utcnow(),

            metadata={},

        )

    # =====================================================
    # LOAD AVERAGE
    # =====================================================

    @staticmethod
    def load_average(

    ) -> SystemMonitorResult:

        try:

            load = os.getloadavg()[0]

        except (

            AttributeError,

            OSError,

        ):

            load = 0.0

        return SystemMonitorResult(

            metric="Load Average",

            status="OK",

            value=round(

                load,

                2,

            ),

            threshold=None,

            timestamp=datetime.utcnow(),

            metadata={},

        )

    # =====================================================
    # NETWORK
    # =====================================================

    @staticmethod
    def network_io(

    ) -> SystemMonitorResult:

        io = psutil.net_io_counters()

        return SystemMonitorResult(

            metric="Network I/O",

            status="OK",

            value=round(

                (

                    io.bytes_sent

                    +

                    io.bytes_recv

                )

                / 1024**2,

                2,

            ),

            threshold=None,

            timestamp=datetime.utcnow(),

            metadata={

                "SentMB":

                    round(

                        io.bytes_sent

                        / 1024**2,

                        2,

                    ),

                "ReceivedMB":

                    round(

                        io.bytes_recv

                        / 1024**2,

                        2,

                    ),

            },

        )

    # =====================================================
    # PLATFORM
    # =====================================================

    @staticmethod
    def platform_info(

    ) -> dict:

        return {

            "System":

                platform.system(),

            "Release":

                platform.release(),

            "Machine":

                platform.machine(),

            "Python":

                platform.python_version(),

        }

    # =====================================================
    # REPORT
    # =====================================================

    @classmethod
    def report(

        cls,

    ) -> dict:

        return {

            "CPU":

                cls.cpu_usage().summary(),

            "Memory":

                cls.memory_usage().summary(),

            "Disk":

                cls.disk_usage().summary(),

            "Uptime":

                cls.uptime().summary(),

            "Threads":

                cls.threads().summary(),

            "LoadAverage":

                cls.load_average().summary(),

            "Network":

                cls.network_io().summary(),

            "Platform":

                cls.platform_info(),

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}()"

        )

    __str__ = __repr__