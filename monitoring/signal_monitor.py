"""
====================================================================
Institutional Quant Platform

Signal Monitor

Author : Institutional Quant Platform

Purpose
-------
Institutional signal quality monitoring.

Monitors

• Signal Coverage
• Signal Freshness
• Signal Strength
• Signal Confidence
• Signal Turnover
• Signal Distribution

Used By

• Dashboard
• Alert Engine
• Telemetry
• Scheduler

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import numpy as np
import pandas as pd


# ==========================================================
# SIGNAL MONITOR RESULT
# ==========================================================


@dataclass(slots=True)
class SignalMonitorResult:
    """
    Signal monitoring result.
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
# SIGNAL MONITOR
# ==========================================================


class SignalMonitor:
    """
    Institutional signal monitor.
    """

    # =====================================================
    # SIGNAL COVERAGE
    # =====================================================

    @staticmethod
    def coverage(

        signals: pd.DataFrame,

        universe_size: int,

    ) -> SignalMonitorResult:

        coverage = (

            len(signals)

            /

            max(

                universe_size,

                1,

            )

        ) * 100

        return SignalMonitorResult(

            metric="Signal Coverage",

            status=(

                "OK"

                if coverage >= 90

                else "WARNING"

            ),

            value=round(

                coverage,

                2,

            ),

            threshold=90,

            timestamp=datetime.utcnow(),

            metadata={

                "Signals":

                    len(signals),

            },

        )

    # =====================================================
    # SIGNAL FRESHNESS
    # =====================================================

    @staticmethod
    def freshness(

        generated_at: datetime,

        max_age_hours: int = 24,

    ) -> SignalMonitorResult:

        age = (

            datetime.utcnow()

            -

            generated_at

        ).total_seconds() / 3600

        return SignalMonitorResult(

            metric="Signal Freshness",

            status=(

                "OK"

                if age <= max_age_hours

                else "WARNING"

            ),

            value=round(

                age,

                2,

            ),

            threshold=max_age_hours,

            timestamp=datetime.utcnow(),

            metadata={

                "Unit":

                    "Hours",

            },

        )

    # =====================================================
    # SIGNAL STRENGTH
    # =====================================================

    @staticmethod
    def strength(

        scores,

    ) -> SignalMonitorResult:

        values = np.asarray(

            scores,

            dtype=float,

        )

        strength = float(

            np.mean(

                np.abs(

                    values

                )

            )

        )

        return SignalMonitorResult(

            metric="Signal Strength",

            status=(

                "OK"

                if strength > 0.50

                else "WARNING"

            ),

            value=round(

                strength,

                4,

            ),

            threshold=0.50,

            timestamp=datetime.utcnow(),

            metadata={},

        )

    # =====================================================
    # SIGNAL CONFIDENCE
    # =====================================================

    @staticmethod
    def confidence(

        confidence_scores,

    ) -> SignalMonitorResult:

        values = np.asarray(

            confidence_scores,

            dtype=float,

        )

        confidence = float(

            np.mean(

                values

            )

        )

        return SignalMonitorResult(

            metric="Signal Confidence",

            status=(

                "OK"

                if confidence >= 0.70

                else "WARNING"

            ),

            value=round(

                confidence,

                4,

            ),

            threshold=0.70,

            timestamp=datetime.utcnow(),

            metadata={},

        )

    # =====================================================
    # SIGNAL TURNOVER
    # =====================================================

    @staticmethod
    def turnover(

        previous_signals,

        current_signals,

    ) -> SignalMonitorResult:

        previous = set(

            previous_signals

        )

        current = set(

            current_signals

        )

        turnover = (

            len(

                previous

                ^

                current

            )

            /

            max(

                len(

                    previous

                    |

                    current

                ),

                1,

            )

        )

        return SignalMonitorResult(

            metric="Signal Turnover",

            status=(

                "OK"

                if turnover <= 0.40

                else "WARNING"

            ),

            value=round(

                turnover,

                4,

            ),

            threshold=0.40,

            timestamp=datetime.utcnow(),

            metadata={},

        )

    # =====================================================
    # SIGNAL DISTRIBUTION
    # =====================================================

    @staticmethod
    def distribution(

        scores,

    ) -> SignalMonitorResult:

        values = np.asarray(

            scores,

            dtype=float,

        )

        std = float(

            np.std(

                values

            )

        )

        return SignalMonitorResult(

            metric="Signal Distribution",

            status=(

                "OK"

                if std > 0.10

                else "WARNING"

            ),

            value=round(

                std,

                4,

            ),

            threshold=0.10,

            timestamp=datetime.utcnow(),

            metadata={

                "Minimum":

                    float(

                        np.min(values)

                    ),

                "Maximum":

                    float(

                        np.max(values)

                    ),

            },

        )

    # =====================================================
    # FULL REPORT
    # =====================================================

    @classmethod
    def report(

        cls,

        signals: pd.DataFrame,

        universe_size: int,

        generated_at: datetime,

        scores,

        confidence_scores,

        previous_symbols,

        current_symbols,

    ) -> dict:

        return {

            "Coverage":

                cls.coverage(

                    signals,

                    universe_size,

                ).summary(),

            "Freshness":

                cls.freshness(

                    generated_at,

                ).summary(),

            "Strength":

                cls.strength(

                    scores,

                ).summary(),

            "Confidence":

                cls.confidence(

                    confidence_scores,

                ).summary(),

            "Turnover":

                cls.turnover(

                    previous_symbols,

                    current_symbols,

                ).summary(),

            "Distribution":

                cls.distribution(

                    scores,

                ).summary(),

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