"""
====================================================================
Institutional Quant Platform

Portfolio Monitor

Author : Institutional Quant Platform

Purpose
-------
Institutional portfolio health monitoring.

Monitors

• Portfolio Value
• Cash Utilization
• Concentration Risk
• Position Limits
• Leverage
• Sector Exposure
• Portfolio Turnover
• Constraint Violations

Used By

• Dashboard
• Alert Engine
• Health Monitor
• Risk Engine

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import numpy as np


# ==========================================================
# PORTFOLIO MONITOR RESULT
# ==========================================================


@dataclass(slots=True)
class PortfolioMonitorResult:
    """
    Portfolio monitoring result.
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
# PORTFOLIO MONITOR
# ==========================================================


class PortfolioMonitor:
    """
    Institutional portfolio monitor.
    """

    # =====================================================
    # PORTFOLIO VALUE
    # =====================================================

    @staticmethod
    def portfolio_value(

        value: float,

    ) -> PortfolioMonitorResult:

        return PortfolioMonitorResult(

            metric="Portfolio Value",

            status="OK",

            value=round(

                value,

                2,

            ),

            threshold=None,

            timestamp=datetime.utcnow(),

            metadata={

                "Currency":

                    "Base",

            },

        )

    # =====================================================
    # CASH UTILIZATION
    # =====================================================

    @staticmethod
    def cash_utilization(

        cash: float,

        portfolio_value: float,

    ) -> PortfolioMonitorResult:

        utilization = (

            100

            *

            (

                1

                -

                cash

                /

                max(

                    portfolio_value,

                    1,

                )

            )

        )

        return PortfolioMonitorResult(

            metric="Cash Utilization",

            status=(

                "OK"

                if utilization <= 95

                else "WARNING"

            ),

            value=round(

                utilization,

                2,

            ),

            threshold=95,

            timestamp=datetime.utcnow(),

            metadata={

                "Cash":

                    cash,

            },

        )

    # =====================================================
    # CONCENTRATION
    # =====================================================

    @staticmethod
    def concentration(

        weights,

    ) -> PortfolioMonitorResult:

        weights = np.asarray(

            weights,

            dtype=float,

        )

        hhi = np.sum(

            weights ** 2

        )

        return PortfolioMonitorResult(

            metric="Concentration Risk",

            status=(

                "OK"

                if hhi < 0.15

                else "WARNING"

            ),

            value=round(

                float(

                    hhi

                ),

                4,

            ),

            threshold=0.15,

            timestamp=datetime.utcnow(),

            metadata={

                "EffectiveHoldings":

                    round(

                        1

                        /

                        max(

                            hhi,

                            1e-8,

                        ),

                        2,

                    ),

            },

        )

    # =====================================================
    # POSITION LIMIT
    # =====================================================

    @staticmethod
    def position_limit(

        weights,

        maximum: float = 0.10,

    ) -> PortfolioMonitorResult:

        maximum_weight = float(

            np.max(

                weights

            )

        )

        return PortfolioMonitorResult(

            metric="Position Limit",

            status=(

                "OK"

                if maximum_weight <= maximum

                else "CRITICAL"

            ),

            value=round(

                maximum_weight,

                4,

            ),

            threshold=maximum,

            timestamp=datetime.utcnow(),

            metadata={},

        )

    # =====================================================
    # LEVERAGE
    # =====================================================

    @staticmethod
    def leverage(

        gross_exposure: float,

        net_asset_value: float,

    ) -> PortfolioMonitorResult:

        leverage = (

            gross_exposure

            /

            max(

                net_asset_value,

                1,

            )

        )

        return PortfolioMonitorResult(

            metric="Leverage",

            status=(

                "OK"

                if leverage <= 1.0

                else "WARNING"

            ),

            value=round(

                leverage,

                4,

            ),

            threshold=1.0,

            timestamp=datetime.utcnow(),

            metadata={},

        )

    # =====================================================
    # SECTOR EXPOSURE
    # =====================================================

    @staticmethod
    def sector_exposure(

        sector_weights: dict,

        limit: float = 0.30,

    ) -> PortfolioMonitorResult:

        maximum = max(

            sector_weights.values(),

            default=0,

        )

        sector = max(

            sector_weights,

            key=sector_weights.get,

            default="",

        )

        return PortfolioMonitorResult(

            metric="Sector Exposure",

            status=(

                "OK"

                if maximum <= limit

                else "WARNING"

            ),

            value=round(

                maximum,

                4,

            ),

            threshold=limit,

            timestamp=datetime.utcnow(),

            metadata={

                "Sector":

                    sector,

            },

        )

    # =====================================================
    # TURNOVER
    # =====================================================

    @staticmethod
    def turnover(

        turnover: float,

        limit: float = 0.50,

    ) -> PortfolioMonitorResult:

        return PortfolioMonitorResult(

            metric="Portfolio Turnover",

            status=(

                "OK"

                if turnover <= limit

                else "WARNING"

            ),

            value=round(

                turnover,

                4,

            ),

            threshold=limit,

            timestamp=datetime.utcnow(),

            metadata={},

        )

    # =====================================================
    # CONSTRAINTS
    # =====================================================

    @staticmethod
    def constraint_violations(

        violations: int,

    ) -> PortfolioMonitorResult:

        return PortfolioMonitorResult(

            metric="Constraint Violations",

            status=(

                "OK"

                if violations == 0

                else "CRITICAL"

            ),

            value=violations,

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

        portfolio_value: float,

        cash: float,

        weights,

        gross_exposure: float,

        sector_weights: dict,

        turnover: float,

        constraint_violations: int,

    ) -> dict:

        return {

            "PortfolioValue":

                cls.portfolio_value(

                    portfolio_value,

                ).summary(),

            "CashUtilization":

                cls.cash_utilization(

                    cash,

                    portfolio_value,

                ).summary(),

            "Concentration":

                cls.concentration(

                    weights,

                ).summary(),

            "PositionLimit":

                cls.position_limit(

                    weights,

                ).summary(),

            "Leverage":

                cls.leverage(

                    gross_exposure,

                    portfolio_value,

                ).summary(),

            "SectorExposure":

                cls.sector_exposure(

                    sector_weights,

                ).summary(),

            "Turnover":

                cls.turnover(

                    turnover,

                ).summary(),

            "ConstraintViolations":

                cls.constraint_violations(

                    constraint_violations,

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