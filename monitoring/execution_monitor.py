"""
====================================================================
Institutional Quant Platform

Execution Monitor

Author : Institutional Quant Platform

Purpose
-------
Institutional execution quality monitoring.

Monitors

• Fill Rate
• Slippage
• Market Impact
• Participation Rate
• Execution Latency
• Order Rejections
• Execution Cost
• VWAP Performance

Used By

• Execution Engine
• Dashboard
• Alert Engine
• Telemetry

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import numpy as np


# ==========================================================
# EXECUTION MONITOR RESULT
# ==========================================================


@dataclass(slots=True)
class ExecutionMonitorResult:
    """
    Execution monitoring result.
    """

    metric: str

    status: str

    value: float | int

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
# EXECUTION MONITOR
# ==========================================================


class ExecutionMonitor:
    """
    Institutional execution monitor.
    """

    # =====================================================
    # FILL RATE
    # =====================================================

    @staticmethod
    def fill_rate(

        executed_quantity: float,

        ordered_quantity: float,

        threshold: float = 0.95,

    ) -> ExecutionMonitorResult:

        rate = (

            executed_quantity

            /

            max(

                ordered_quantity,

                1,

            )

        )

        return ExecutionMonitorResult(

            metric="Fill Rate",

            status=(

                "OK"

                if rate >= threshold

                else "WARNING"

            ),

            value=round(

                rate,

                4,

            ),

            threshold=threshold,

            timestamp=datetime.utcnow(),

            metadata={},

        )

    # =====================================================
    # SLIPPAGE
    # =====================================================

    @staticmethod
    def slippage(

        slippage_bps: float,

        threshold: float = 25,

    ) -> ExecutionMonitorResult:

        return ExecutionMonitorResult(

            metric="Slippage",

            status=(

                "OK"

                if slippage_bps <= threshold

                else "WARNING"

            ),

            value=round(

                slippage_bps,

                2,

            ),

            threshold=threshold,

            timestamp=datetime.utcnow(),

            metadata={

                "Unit":

                    "bps",

            },

        )

    # =====================================================
    # MARKET IMPACT
    # =====================================================

    @staticmethod
    def market_impact(

        impact_bps: float,

        threshold: float = 30,

    ) -> ExecutionMonitorResult:

        return ExecutionMonitorResult(

            metric="Market Impact",

            status=(

                "OK"

                if impact_bps <= threshold

                else "WARNING"

            ),

            value=round(

                impact_bps,

                2,

            ),

            threshold=threshold,

            timestamp=datetime.utcnow(),

            metadata={

                "Unit":

                    "bps",

            },

        )

    # =====================================================
    # PARTICIPATION RATE
    # =====================================================

    @staticmethod
    def participation_rate(

        trade_value: float,

        adv: float,

        threshold: float = 0.10,

    ) -> ExecutionMonitorResult:

        rate = (

            trade_value

            /

            max(

                adv,

                1,

            )

        )

        return ExecutionMonitorResult(

            metric="Participation Rate",

            status=(

                "OK"

                if rate <= threshold

                else "WARNING"

            ),

            value=round(

                rate,

                4,

            ),

            threshold=threshold,

            timestamp=datetime.utcnow(),

            metadata={},

        )

    # =====================================================
    # EXECUTION LATENCY
    # =====================================================

    @staticmethod
    def latency(

        milliseconds: float,

        threshold: float = 500,

    ) -> ExecutionMonitorResult:

        return ExecutionMonitorResult(

            metric="Execution Latency",

            status=(

                "OK"

                if milliseconds <= threshold

                else "WARNING"

            ),

            value=round(

                milliseconds,

                2,

            ),

            threshold=threshold,

            timestamp=datetime.utcnow(),

            metadata={

                "Unit":

                    "ms",

            },

        )

    # =====================================================
    # REJECTION RATE
    # =====================================================

    @staticmethod
    def rejection_rate(

        rejected_orders: int,

        total_orders: int,

        threshold: float = 0.01,

    ) -> ExecutionMonitorResult:

        rate = (

            rejected_orders

            /

            max(

                total_orders,

                1,

            )

        )

        return ExecutionMonitorResult(

            metric="Order Rejection Rate",

            status=(

                "OK"

                if rate <= threshold

                else "CRITICAL"

            ),

            value=round(

                rate,

                4,

            ),

            threshold=threshold,

            timestamp=datetime.utcnow(),

            metadata={},

        )

    # =====================================================
    # EXECUTION COST
    # =====================================================

    @staticmethod
    def execution_cost(

        commissions: float,

        slippage_cost: float,

        impact_cost: float,

    ) -> ExecutionMonitorResult:

        total = (

            commissions

            +

            slippage_cost

            +

            impact_cost

        )

        return ExecutionMonitorResult(

            metric="Execution Cost",

            status="OK",

            value=round(

                total,

                2,

            ),

            threshold=None,

            timestamp=datetime.utcnow(),

            metadata={

                "Commission":

                    commissions,

                "Slippage":

                    slippage_cost,

                "MarketImpact":

                    impact_cost,

            },

        )

    # =====================================================
    # VWAP PERFORMANCE
    # =====================================================

    @staticmethod
    def vwap_performance(

        execution_price: float,

        vwap_price: float,

    ) -> ExecutionMonitorResult:

        difference = (

            execution_price

            -

            vwap_price

        )

        return ExecutionMonitorResult(

            metric="VWAP Performance",

            status=(

                "OK"

                if difference <= 0

                else "WARNING"

            ),

            value=round(

                difference,

                4,

            ),

            threshold=0,

            timestamp=datetime.utcnow(),

            metadata={},

        )

    # =====================================================
    # REPORT
    # =====================================================

    @classmethod
    def report(

        cls,

        executed_quantity: float,

        ordered_quantity: float,

        slippage_bps: float,

        impact_bps: float,

        trade_value: float,

        adv: float,

        latency_ms: float,

        rejected_orders: int,

        total_orders: int,

        commissions: float,

        slippage_cost: float,

        impact_cost: float,

        execution_price: float,

        vwap_price: float,

    ) -> dict:

        return {

            "FillRate":

                cls.fill_rate(

                    executed_quantity,

                    ordered_quantity,

                ).summary(),

            "Slippage":

                cls.slippage(

                                    slippage_bps,

                ).summary(),

            "MarketImpact":

                cls.market_impact(

                    impact_bps,

                ).summary(),

            "ParticipationRate":

                cls.participation_rate(

                    trade_value,

                    adv,

                ).summary(),

            "ExecutionLatency":

                cls.latency(

                    latency_ms,

                ).summary(),

            "OrderRejectionRate":

                cls.rejection_rate(

                    rejected_orders,

                    total_orders,

                ).summary(),

            "ExecutionCost":

                cls.execution_cost(

                    commissions,

                    slippage_cost,

                    impact_cost,

                ).summary(),

            "VWAPPerformance":

                cls.vwap_performance(

                    execution_price,

                    vwap_price,

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