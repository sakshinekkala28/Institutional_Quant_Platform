"""
====================================================================
Institutional Quant Platform

Turnover Model

Author : Institutional Quant Platform

Purpose
-------
Institutional portfolio turnover model.

Provides

• One-Way Turnover
• Two-Way Turnover
• Trade Notional
• Turnover Ratio

Used By

• TransactionCostModel
• Optimizers
• Execution Engine
• Rebalance Engine

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from core.models.portfolio import Portfolio


@dataclass(slots=True)
class TurnoverModel:
    """
    Institutional turnover model.
    """

    # =====================================================
    # INTERNAL
    # =====================================================

    @staticmethod
    def _weight_map(

        portfolio: Portfolio,

    ) -> dict[str, float]:

        return {

            position.symbol: position.weight

            for position

            in portfolio

        }

    # =====================================================
    # ONE-WAY TURNOVER
    # =====================================================

    def one_way_turnover(

        self,

        current: Portfolio,

        target: Portfolio,

    ) -> float:

        current_weights = self._weight_map(

            current

        )

        target_weights = self._weight_map(

            target

        )

        universe = (

            set(

                current_weights

            )

            |

            set(

                target_weights

            )

        )

        turnover = sum(

            abs(

                target_weights.get(

                    symbol,

                    0.0,

                )

                -

                current_weights.get(

                    symbol,

                    0.0,

                )

            )

            for symbol

            in universe

        )

        return 0.5 * turnover

    # =====================================================
    # TWO-WAY TURNOVER
    # =====================================================

    def two_way_turnover(

        self,

        current: Portfolio,

        target: Portfolio,

    ) -> float:

        current_weights = self._weight_map(

            current

        )

        target_weights = self._weight_map(

            target

        )

        universe = (

            set(

                current_weights

            )

            |

            set(

                target_weights

            )

        )

        return sum(

            abs(

                target_weights.get(

                    symbol,

                    0.0,

                )

                -

                current_weights.get(

                    symbol,

                    0.0,

                )

            )

            for symbol

            in universe

        )

    # =====================================================
    # TRADED NOTIONAL
    # =====================================================

    def traded_notional(

        self,

        current: Portfolio,

        target: Portfolio,

    ) -> float:

        return (

            self.one_way_turnover(

                current,

                target,

            )

            * current.nav

        )

    # =====================================================
    # TURNOVER RATIO
    # =====================================================

    def turnover_ratio(

        self,

        current: Portfolio,

        target: Portfolio,

    ) -> float:

        return self.one_way_turnover(

            current,

            target,

        )

    # =====================================================
    # ALIAS
    # =====================================================

    def calculate(

        self,

        current: Portfolio,

        target: Portfolio,

    ) -> float:

        return self.turnover_ratio(

            current,

            target,

        )

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self,

        current: Portfolio,

        target: Portfolio,

    ) -> dict:

        return {

            "One_Way_Turnover":

                self.one_way_turnover(

                    current,

                    target,

                ),

            "Two_Way_Turnover":

                self.two_way_turnover(

                    current,

                    target,

                ),

            "Traded_Notional":

                self.traded_notional(

                    current,

                    target,

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