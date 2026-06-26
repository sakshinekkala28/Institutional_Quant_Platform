"""
====================================================================
Institutional Quant Platform

Optimizer Factory

Author : Institutional Quant Platform

Purpose
-------
Factory for creating institutional
portfolio optimizers.

Supports

• Equal Weight
• Minimum Variance
• Maximum Sharpe
• Mean Variance
• Risk Parity
• HRP
• Black-Litterman

====================================================================
"""

from __future__ import annotations

from optimization.base_optimizer import BaseOptimizer

from optimization.optimizers.equal_weight import (
    EqualWeightOptimizer
)

from optimization.optimizers.minimum_variance import (
    MinimumVarianceOptimizer
)

from optimization.optimizers.max_sharpe import (
    MaximumSharpeOptimizer
)

from optimization.optimizers.mean_variance import (
    MeanVarianceOptimizer
)

from optimization.optimizers.risk_parity import (
    RiskParityOptimizer
)

from optimization.optimizers.hrp import (
    HRPOptimizer
)

from optimization.optimizers.black_litterman import (
    BlackLittermanOptimizer
)


class OptimizerFactory:
    """
    Institutional optimizer factory.
    """

    _OPTIMIZERS = {

        "equal_weight":
            EqualWeightOptimizer,

        "minimum_variance":
            MinimumVarianceOptimizer,

        "max_sharpe":
            MaximumSharpeOptimizer,

        "mean_variance":
            MeanVarianceOptimizer,

        "risk_parity":
            RiskParityOptimizer,

        "hrp":
            HRPOptimizer,

        "black_litterman":
            BlackLittermanOptimizer,

    }

    # =====================================================
    # CREATE
    # =====================================================

    @classmethod
    def create(

        cls,

        optimizer: str,

        **kwargs

    ) -> BaseOptimizer:

        optimizer = (

            optimizer

            .strip()

            .lower()

        )

        if optimizer not in cls._OPTIMIZERS:

            supported = ", ".join(

                sorted(

                    cls._OPTIMIZERS

                )

            )

            raise ValueError(

                f"Unknown optimizer "

                f"'{optimizer}'. "

                f"Supported: {supported}"

            )

        return cls._OPTIMIZERS[

            optimizer

        ](

            **kwargs

        )

    # =====================================================
    # AVAILABLE
    # =====================================================

    @classmethod
    def available(

        cls

    ) -> list[str]:

        return sorted(

            cls._OPTIMIZERS.keys()

        )