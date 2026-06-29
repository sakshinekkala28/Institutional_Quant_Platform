"""
====================================================================
Institutional Quant Platform

Attribution Metrics

Author : Institutional Quant Platform

Purpose
-------
Institutional performance attribution
analytics.

Provides

• Allocation Effect
• Selection Effect
• Interaction Effect
• Brinson Attribution
• Active Return Attribution
• Factor Contribution

Used By

• Performance Engine
• Reporting
• Dashboard
• Portfolio Analytics

====================================================================
"""

from __future__ import annotations

import numpy as np


class AttributionMetrics:
    """
    Institutional performance attribution metrics.
    """

    # =====================================================
    # ALLOCATION EFFECT
    # =====================================================

    @staticmethod
    def allocation_effect(

        portfolio_weights: list[float] | np.ndarray,

        benchmark_weights: list[float] | np.ndarray,

        benchmark_returns: list[float] | np.ndarray,

    ) -> float:

        pw = np.asarray(

            portfolio_weights,

            dtype=np.float64,

        )

        bw = np.asarray(

            benchmark_weights,

            dtype=np.float64,

        )

        br = np.asarray(

            benchmark_returns,

            dtype=np.float64,

        )

        return float(

            np.sum(

                (

                    pw

                    -

                    bw

                )

                *

                br

            )

        )

    # =====================================================
    # SELECTION EFFECT
    # =====================================================

    @staticmethod
    def selection_effect(

        portfolio_weights: list[float] | np.ndarray,

        portfolio_returns: list[float] | np.ndarray,

        benchmark_returns: list[float] | np.ndarray,

    ) -> float:

        pw = np.asarray(

            portfolio_weights,

            dtype=np.float64,

        )

        pr = np.asarray(

            portfolio_returns,

            dtype=np.float64,

        )

        br = np.asarray(

            benchmark_returns,

            dtype=np.float64,

        )

        return float(

            np.sum(

                pw

                *

                (

                    pr

                    -

                    br

                )

            )

        )

    # =====================================================
    # INTERACTION EFFECT
    # =====================================================

    @staticmethod
    def interaction_effect(

        portfolio_weights: list[float] | np.ndarray,

        benchmark_weights: list[float] | np.ndarray,

        portfolio_returns: list[float] | np.ndarray,

        benchmark_returns: list[float] | np.ndarray,

    ) -> float:

        pw = np.asarray(

            portfolio_weights,

            dtype=np.float64,

        )

        bw = np.asarray(

            benchmark_weights,

            dtype=np.float64,

        )

        pr = np.asarray(

            portfolio_returns,

            dtype=np.float64,

        )

        br = np.asarray(

            benchmark_returns,

            dtype=np.float64,

        )

        return float(

            np.sum(

                (

                    pw

                    -

                    bw

                )

                *

                (

                    pr

                    -

                    br

                )

            )

        )

    # =====================================================
    # ACTIVE RETURN
    # =====================================================

    @classmethod
    def active_return(

        cls,

        portfolio_weights: list[float] | np.ndarray,

        benchmark_weights: list[float] | np.ndarray,

        portfolio_returns: list[float] | np.ndarray,

        benchmark_returns: list[float] | np.ndarray,

    ) -> float:

        return (

            cls.allocation_effect(

                portfolio_weights,

                benchmark_weights,

                benchmark_returns,

            )

            +

            cls.selection_effect(

                portfolio_weights,

                portfolio_returns,

                benchmark_returns,

            )

            +

            cls.interaction_effect(

                portfolio_weights,

                benchmark_weights,

                portfolio_returns,

                benchmark_returns,

            )

        )

    # =====================================================
    # BRINSON ATTRIBUTION
    # =====================================================

    @classmethod
    def brinson(

        cls,

        portfolio_weights: list[float] | np.ndarray,

        benchmark_weights: list[float] | np.ndarray,

        portfolio_returns: list[float] | np.ndarray,

        benchmark_returns: list[float] | np.ndarray,

    ) -> dict:

        allocation = cls.allocation_effect(

            portfolio_weights,

            benchmark_weights,

            benchmark_returns,

        )

        selection = cls.selection_effect(

            portfolio_weights,

            portfolio_returns,

            benchmark_returns,

        )

        interaction = cls.interaction_effect(

            portfolio_weights,

            benchmark_weights,

            portfolio_returns,

            benchmark_returns,

        )

        return {

            "Allocation":

                allocation,

            "Selection":

                selection,

            "Interaction":

                interaction,

            "Total":

                allocation

                +

                selection

                +

                interaction,

        }

    # =====================================================
    # FACTOR CONTRIBUTION
    # =====================================================

    @staticmethod
    def factor_contribution(

        factor_exposures: list[float] | np.ndarray,

        factor_returns: list[float] | np.ndarray,

    ) -> float:

        exposures = np.asarray(

            factor_exposures,

            dtype=np.float64,

        )

        returns = np.asarray(

            factor_returns,

            dtype=np.float64,

        )

        return float(

            np.dot(

                exposures,

                returns,

            )

        )

    # =====================================================
    # ASSET CONTRIBUTIONS
    # =====================================================

    @staticmethod
    def asset_contributions(

        weights: list[float] | np.ndarray,

        returns: list[float] | np.ndarray,

    ) -> np.ndarray:

        weights = np.asarray(

            weights,

            dtype=np.float64,

        )

        returns = np.asarray(

            returns,

            dtype=np.float64,

        )

        return (

            weights

            *

            returns

        )

    # =====================================================
    # SUMMARY
    # =====================================================

    @classmethod
    def summary(

        cls,

        portfolio_weights: list[float] | np.ndarray,

        benchmark_weights: list[float] | np.ndarray,

        portfolio_returns: list[float] | np.ndarray,

        benchmark_returns: list[float] | np.ndarray,

        factor_exposures: list[float] | np.ndarray,

        factor_returns: list[float] | np.ndarray,

    ) -> dict:

        attribution = cls.brinson(

            portfolio_weights,

            benchmark_weights,

            portfolio_returns,

            benchmark_returns,

        )

        return {

            **attribution,

            "ActiveReturn":

                cls.active_return(

                    portfolio_weights,

                    benchmark_weights,

                    portfolio_returns,

                    benchmark_returns,

                ),

            "FactorContribution":

                cls.factor_contribution(

                    factor_exposures,

                    factor_returns,

                ),

            "AssetContributions":

                cls.asset_contributions(

                    portfolio_weights,

                    portfolio_returns,

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