"""
====================================================================
Institutional Quant Platform

Drawdown Metrics

Author : Institutional Quant Platform

Purpose
-------
Reusable institutional drawdown analytics.

Provides

• Drawdown Series
• Underwater Curve
• Maximum Drawdown
• Average Drawdown
• Drawdown Duration
• Recovery Duration
• Recovery Factor

Used By

• Performance Engine
• Reporting
• Dashboard

====================================================================
"""

from __future__ import annotations

import numpy as np


class DrawdownMetrics:
    """
    Institutional drawdown analytics.
    """

    # =====================================================
    # DRAWDOWN SERIES
    # =====================================================

    @staticmethod
    def drawdown_series(

        equity_curve: list[float] | np.ndarray,

    ) -> np.ndarray:

        equity = np.asarray(

            equity_curve,

            dtype=np.float64,

        )

        if equity.size == 0:

            return np.asarray([])

        running_max = np.maximum.accumulate(

            equity

        )

        return (

            equity

            -

            running_max

        ) / running_max

    # =====================================================
    # UNDERWATER CURVE
    # =====================================================

    @classmethod
    def underwater_curve(

        cls,

        equity_curve: list[float] | np.ndarray,

    ) -> np.ndarray:

        return cls.drawdown_series(

            equity_curve

        )

    # =====================================================
    # MAXIMUM DRAWDOWN
    # =====================================================

    @classmethod
    def maximum_drawdown(

        cls,

        equity_curve: list[float] | np.ndarray,

    ) -> float:

        drawdowns = cls.drawdown_series(

            equity_curve

        )

        if drawdowns.size == 0:

            return 0.0

        return float(

            abs(

                np.min(

                    drawdowns

                )

            )

        )

    # =====================================================
    # AVERAGE DRAWDOWN
    # =====================================================

    @classmethod
    def average_drawdown(

        cls,

        equity_curve: list[float] | np.ndarray,

    ) -> float:

        drawdowns = cls.drawdown_series(

            equity_curve

        )

        negative = drawdowns[

            drawdowns < 0

        ]

        if negative.size == 0:

            return 0.0

        return float(

            abs(

                negative.mean()

            )

        )

    # =====================================================
    # DRAWDOWN DURATION
    # =====================================================

    @classmethod
    def drawdown_duration(

        cls,

        equity_curve: list[float] | np.ndarray,

    ) -> int:

        drawdowns = cls.drawdown_series(

            equity_curve

        )

        duration = 0

        maximum = 0

        for value in drawdowns:

            if value < 0:

                duration += 1

                maximum = max(

                    maximum,

                    duration,

                )

            else:

                duration = 0

        return maximum

    # =====================================================
    # RECOVERY DURATION
    # =====================================================

    @staticmethod
    def recovery_duration(

        equity_curve: list[float] | np.ndarray,

    ) -> int:

        equity = np.asarray(

            equity_curve,

            dtype=np.float64,

        )

        if equity.size == 0:

            return 0

        peak = equity[0]

        duration = 0

        maximum = 0

        recovering = False

        for value in equity:

            if value >= peak:

                peak = value

                recovering = False

                duration = 0

            else:

                recovering = True

                duration += 1

                maximum = max(

                    maximum,

                    duration,

                )

        return maximum

    # =====================================================
    # RECOVERY FACTOR
    # =====================================================

    @classmethod
    def recovery_factor(

        cls,

        equity_curve: list[float] | np.ndarray,

    ) -> float:

        equity = np.asarray(

            equity_curve,

            dtype=np.float64,

        )

        if equity.size < 2:

            return 0.0

        total_return = (

            equity[-1]

            /

            equity[0]

        ) - 1.0

        max_dd = cls.maximum_drawdown(

            equity

        )

        if max_dd <= 0:

            return 0.0

        return float(

            total_return

            / max_dd

        )

    # =====================================================
    # SUMMARY
    # =====================================================

    @classmethod
    def summary(

        cls,

        equity_curve: list[float] | np.ndarray,

    ) -> dict:

        return {

            "MaximumDrawdown":

                cls.maximum_drawdown(

                    equity_curve

                ),

            "AverageDrawdown":

                cls.average_drawdown(

                    equity_curve

                ),

            "DrawdownDuration":

                cls.drawdown_duration(

                    equity_curve

                ),

            "RecoveryDuration":

                cls.recovery_duration(

                    equity_curve

                ),

            "RecoveryFactor":

                cls.recovery_factor(

                    equity_curve

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