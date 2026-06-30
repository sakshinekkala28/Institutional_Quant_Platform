"""
====================================================================
Institutional Quant Platform

Risk Monitor

Author : Institutional Quant Platform

Purpose
-------
Institutional portfolio risk monitoring.

Monitors

• Portfolio Volatility
• Value at Risk (VaR)
• Expected Shortfall (CVaR)
• Beta
• Tracking Error
• Concentration
• Leverage
• Risk Limit Breaches

Used By

• Risk Engine
• Dashboard
• Alert Engine
• Health Monitor

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import numpy as np


# ==========================================================
# RISK MONITOR RESULT
# ==========================================================


@dataclass(slots=True)
class RiskMonitorResult:
    """
    Risk monitoring result.
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
# RISK MONITOR
# ==========================================================


class RiskMonitor:
    """
    Institutional risk monitor.
    """

    # =====================================================
    # VOLATILITY
    # =====================================================

    @staticmethod
    def volatility(

        returns,

        threshold: float = 0.30,

    ) -> RiskMonitorResult:

        returns = np.asarray(

            returns,

            dtype=float,

        )

        volatility = (

            np.std(

                returns,

                ddof=1,

            )

            *

            np.sqrt(

                252

            )

        )

        return RiskMonitorResult(

            metric="Portfolio Volatility",

            status=(

                "OK"

                if volatility <= threshold

                else "WARNING"

            ),

            value=round(

                float(

                    volatility

                ),

                4,

            ),

            threshold=threshold,

            timestamp=datetime.utcnow(),

            metadata={

                "Annualized":

                    True,

            },

        )

    # =====================================================
    # VALUE AT RISK
    # =====================================================

    @staticmethod
    def value_at_risk(

        returns,

        confidence: float = 0.95,

        threshold: float = 0.03,

    ) -> RiskMonitorResult:

        returns = np.asarray(

            returns,

            dtype=float,

        )

        var = -np.percentile(

            returns,

            (1 - confidence) * 100,

        )

        return RiskMonitorResult(

            metric="Value at Risk",

            status=(

                "OK"

                if var <= threshold

                else "WARNING"

            ),

            value=round(

                float(

                    var

                ),

                4,

            ),

            threshold=threshold,

            timestamp=datetime.utcnow(),

            metadata={

                "Confidence":

                    confidence,

            },

        )

    # =====================================================
    # EXPECTED SHORTFALL
    # =====================================================

    @staticmethod
    def expected_shortfall(

        returns,

        confidence: float = 0.95,

        threshold: float = 0.05,

    ) -> RiskMonitorResult:

        returns = np.asarray(

            returns,

            dtype=float,

        )

        cutoff = np.percentile(

            returns,

            (1 - confidence) * 100,

        )

        losses = returns[

            returns <= cutoff

        ]

        es = (

            -losses.mean()

            if losses.size

            else 0.0

        )

        return RiskMonitorResult(

            metric="Expected Shortfall",

            status=(

                "OK"

                if es <= threshold

                else "WARNING"

            ),

            value=round(

                float(

                    es

                ),

                4,

            ),

            threshold=threshold,

            timestamp=datetime.utcnow(),

            metadata={

                "Confidence":

                    confidence,

            },

        )

    # =====================================================
    # BETA
    # =====================================================

    @staticmethod
    def beta(

        portfolio_returns,

        benchmark_returns,

        threshold: float = 1.20,

    ) -> RiskMonitorResult:

        portfolio = np.asarray(

            portfolio_returns,

            dtype=float,

        )

        benchmark = np.asarray(

            benchmark_returns,

            dtype=float,

        )

        covariance = np.cov(

            portfolio,

            benchmark,

        )[0, 1]

        variance = np.var(

            benchmark,

        )

        beta = (

            covariance

            / variance

            if variance > 0

            else 0

        )

        return RiskMonitorResult(

            metric="Portfolio Beta",

            status=(

                "OK"

                if beta <= threshold

                else "WARNING"

            ),

            value=round(

                float(

                    beta

                ),

                4,

            ),

            threshold=threshold,

            timestamp=datetime.utcnow(),

            metadata={},

        )

    # =====================================================
    # TRACKING ERROR
    # =====================================================

    @staticmethod
    def tracking_error(

        portfolio_returns,

        benchmark_returns,

        threshold: float = 0.10,

    ) -> RiskMonitorResult:

        active = (

            np.asarray(

                portfolio_returns,

                dtype=float,

            )

            -

            np.asarray(

                benchmark_returns,

                dtype=float,

            )

        )

        tracking = (

            np.std(

                active,

                ddof=1,

            )

            *

            np.sqrt(

                252

            )

        )

        return RiskMonitorResult(

            metric="Tracking Error",

            status=(

                "OK"

                if tracking <= threshold

                else "WARNING"

            ),

            value=round(

                float(

                    tracking

                ),

                4,

            ),

            threshold=threshold,

            timestamp=datetime.utcnow(),

            metadata={

                "Annualized":

                    True,

            },

        )

    # =====================================================
    # CONCENTRATION
    # =====================================================

    @staticmethod
    def concentration(

        weights,

        threshold: float = 0.15,

    ) -> RiskMonitorResult:

        weights = np.asarray(

            weights,

            dtype=float,

        )

        hhi = np.sum(

            weights ** 2

        )

        return RiskMonitorResult(

            metric="Concentration Risk",

            status=(

                "OK"

                if hhi <= threshold

                else "WARNING"

            ),

            value=round(

                float(

                    hhi

                ),

                4,

            ),

            threshold=threshold,

            timestamp=datetime.utcnow(),

            metadata={

                "EffectiveHoldings":

                    round(

                        1 / hhi,

                        2,

                    )

                    if hhi > 0

                    else 0,

            },

        )

    # =====================================================
    # LEVERAGE
    # =====================================================

    @staticmethod
    def leverage(

        gross_exposure: float,

        nav: float,

        threshold: float = 1.0,

    ) -> RiskMonitorResult:

        leverage = (

            gross_exposure

            /

            max(

                nav,

                1,

            )

        )

        return RiskMonitorResult(

            metric="Leverage",

            status=(

                "OK"

                if leverage <= threshold

                else "CRITICAL"

            ),

            value=round(

                leverage,

                4,

            ),

            threshold=threshold,

            timestamp=datetime.utcnow(),

            metadata={},

        )

    # =====================================================
    # RISK LIMIT BREACHES
    # =====================================================

    @staticmethod
    def limit_breaches(

        breaches: int,

    ) -> RiskMonitorResult:

        return RiskMonitorResult(

            metric="Risk Limit Breaches",

            status=(

                "OK"

                if breaches == 0

                else "CRITICAL"

            ),

            value=breaches,

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

        portfolio_returns,

        benchmark_returns,

        weights,

        gross_exposure: float,

        nav: float,

        breaches: int,

    ) -> dict:

        return {

            "Volatility":

                cls.volatility(

                    portfolio_returns,

                ).summary(),

            "VaR":

                cls.value_at_risk(

                    portfolio_returns,

                ).summary(),

            "ExpectedShortfall":

                cls.expected_shortfall(

                    portfolio_returns,

                ).summary(),

            "Beta":

                cls.beta(

                    portfolio_returns,

                    benchmark_returns,

                ).summary(),

            "TrackingError":

                cls.tracking_error(

                    portfolio_returns,

                    benchmark_returns,

                ).summary(),

            "Concentration":

                cls.concentration(

                    weights,

                ).summary(),

            "Leverage":

                cls.leverage(

                    gross_exposure,

                    nav,

                ).summary(),

            "RiskLimitBreaches":

                cls.limit_breaches(

                    breaches,

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