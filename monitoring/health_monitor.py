"""
====================================================================
Institutional Quant Platform

Health Monitor

Author : Institutional Quant Platform

Purpose
-------
Monitors the health of the institutional
platform.

Checks

• Data Health
• Signal Health
• Portfolio Health
• Risk Health
• Execution Health
• System Health

Used By

• Dashboard
• Telemetry
• Alert Engine
• Scheduler

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from datetime import datetime


@dataclass(slots=True)
class HealthMonitor:
    """
    Institutional platform health monitor.
    """

    components: dict = field(

        default_factory=dict

    )

    timestamp: datetime = field(

        default_factory=datetime.utcnow

    )

    __hash__ = None

    # =====================================================
    # REGISTER
    # =====================================================

    def register(

        self,

        component: str,

        status: str,

        message: str = "",

    ) -> None:

        self.components[

            component

        ] = {

            "status": status.upper(),

            "message": message,

            "checked": datetime.utcnow(),

        }

    # =====================================================
    # UPDATE
    # =====================================================

    def update(

        self,

        component: str,

        status: str,

        message: str = "",

    ) -> None:

        self.register(

            component,

            status,

            message,

        )

    # =====================================================
    # HEALTH SCORE
    # =====================================================

    @property
    def score(

        self,

    ) -> float:

        if not self.components:

            return 0.0

        healthy = sum(

            value["status"] == "OK"

            for value

            in self.components.values()

        )

        return (

            healthy

            /

            len(

                self.components

            )

        ) * 100

    # =====================================================
    # FAILED COMPONENTS
    # =====================================================

    @property
    def failures(

        self,

    ) -> dict:

        return {

            key: value

            for key, value

            in self.components.items()

            if value["status"] != "OK"

        }

    # =====================================================
    # PLATFORM STATUS
    # =====================================================

    @property
    def platform_status(

        self,

    ) -> str:

        if not self.components:

            return "UNKNOWN"

        if len(

            self.failures

        ) == 0:

            return "HEALTHY"

        if len(

            self.failures

        ) < 3:

            return "WARNING"

        return "CRITICAL"

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self,

    ) -> dict:

        return {

            "PlatformStatus":

                self.platform_status,

            "HealthScore":

                round(

                    self.score,

                    2,

                ),

            "Components":

                len(

                    self.components

                ),

            "Failures":

                len(

                    self.failures

                ),

            "Timestamp":

                self.timestamp.isoformat(),

        }

    # =====================================================
    # RESET
    # =====================================================

    def clear(

        self,

    ) -> None:

        self.components.clear()

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ):

        return (

            f"{self.__class__.__name__}("

            f"Status={self.platform_status}, "

            f"Health={self.score:.1f}%)"

        )

    __str__ = __repr__