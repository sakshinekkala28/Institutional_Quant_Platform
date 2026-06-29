"""
====================================================================
Institutional Quant Platform

Risk Metrics

Author : Institutional Quant Platform

Purpose
-------
Reusable institutional portfolio risk metrics.

Provides

• Volatility
• Downside Deviation
• Value at Risk (VaR)
• Expected Shortfall (CVaR)
• Maximum Drawdown
• Drawdown Duration
• Concentration Risk

Used By

• Performance Engine
• Risk Engine
• Reporting
• Dashboard

====================================================================
"""

from __future__ import annotations

import math

import numpy as np


class RiskMetrics:
    """
    Institutional portfolio risk metrics.
    """

    # =====================================================
    # VOLATILITY
    # =====================================================

    @staticmethod
    def volatility(

        returns: list[float] | np.ndarray,

        trading_days: int = 252,

    ) -> float:

        values = np.asarray(

            returns,

            dtype=np.float64,

        )

        if values.size < 2:

            return 0.0

        return float(

            np.std(

                values,

                ddof=1,

            )

            *

            math.sqrt(

                trading_days

            )

        )

    # =====================================================
    # DOWNSIDE DEVIATION
    # =====================================================

    @staticmethod
    def downside_deviation(

        returns: list[float] | np.ndarray,

        target_return: float = 0.0,

        trading_days: int = 252,

    ) -> float:

        values = np.asarray(

            returns,

            dtype=np.float64,

        )

        downside = values[

            values < target_return

        ]

        if downside.size < 2:

            return 0.0

        deviation = (

            downside

            -

            target_return

        )

        return float(

            np.std(

                deviation,

                ddof=1,

            )

            *

            math.sqrt(

                trading_days

            )

        )

    # =====================================================
    # VALUE AT RISK
    # =====================================================

    @staticmethod
    def value_at_risk(

        returns: list[float] | np.ndarray,

        confidence: float = 0.95,

    ) -> float:

        values = np.asarray(

            returns,

            dtype=np.float64,

        )

        if values.size == 0:

            return 0.0

        percentile = (

            100.0

            *

            (

                1.0

                -

                confidence

            )

        )

        return float(

            -np.percentile(

                values,

                percentile,

            )

        )

    # =====================================================
    # EXPECTED SHORTFALL
    # =====================================================

    @classmethod
    def expected_shortfall(

        cls,

        returns: list[float] | np.ndarray,

        confidence: float = 0.95,

    ) -> float:

        values = np.asarray(

            returns,

            dtype=np.float64,

        )

        if values.size == 0:

            return 0.0

        var = -cls.value_at_risk(

            values,

            confidence,

        )

        losses = values[

            values <= var

        ]

        if losses.size == 0:

            return 0.0

        return float(

            -losses.mean()

        )

    # =====================================================
    # MAXIMUM DRAWDOWN
    # =====================================================

    @staticmethod
    def maximum_drawdown(

        equity_curve: list[float] | np.ndarray,

    ) -> float:

        equity = np.asarray(

            equity_curve,

            dtype=np.float64,

        )

        if equity.size == 0:

            return 0.0

        running_max = np.maximum.accumulate(

            equity

        )

        drawdown = (

            equity

            -

            running_max

        ) / running_max

        return float(

            abs(

                np.min(

                    drawdown

                )

            )

        )

    # =====================================================
    # DRAWDOWN DURATION
    # =====================================================

    @staticmethod
    def drawdown_duration(

        equity_curve: list[float] | np.ndarray,

    ) -> int:

        equity = np.asarray(

            equity_curve,

            dtype=np.float64,

        )

        if equity.size == 0:

            return 0

        running_max = np.maximum.accumulate(

            equity

        )

        duration = 0

        maximum = 0

        for value, peak in zip(

            equity,

            running_max,

            strict=True,

        ):

            if value < peak:

                duration += 1

                maximum = max(

                    maximum,

                    duration,

                )

            else:

                duration = 0

        return maximum

    # =====================================================
    # CONCENTRATION RISK
    # =====================================================

    @staticmethod
    def concentration_risk(

        weights: list[float] | np.ndarray,

    ) -> float:

        weights = np.asarray(

            weights,

            dtype=np.float64,

        )

        if weights.size == 0:

            return 0.0

        return float(

            np.sum(

                weights ** 2

            )

        )

    # =====================================================
    # EFFECTIVE HOLDINGS
    # =====================================================

    @classmethod
    def effective_holdings(

        cls,

        weights: list[float] | np.ndarray,

    ) -> float:

        concentration = cls.concentration_risk(

            weights

        )

        if concentration <= 0:

            return 0.0

        return 1.0 / concentration

    # =====================================================
    # SUMMARY
    # =====================================================

    @classmethod
    def summary(

        cls,

        returns: list[float] | np.ndarray,

        equity_curve: list[float] | np.ndarray,

        weights: list[float] | np.ndarray,

        confidence: float = 0.95,

    ) -> dict:

        return {

            "Volatility":

                cls.volatility(

                    returns

                ),

            "DownsideDeviation":

                cls.downside_deviation(

                    returns

                ),

            "VaR":

                cls.value_at_risk(

                    returns,

                    confidence,

                ),

            "ExpectedShortfall":

                cls.expected_shortfall(

                    returns,

                    confidence,

                ),

            "MaximumDrawdown":

                cls.maximum_drawdown(

                    equity_curve

                ),

            "DrawdownDuration":

                cls.drawdown_duration(

                    equity_curve

                ),

            "ConcentrationRisk":

                cls.concentration_risk(

                    weights

                ),

            "EffectiveHoldings":

                cls.effective_holdings(

                    weights

                ),

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