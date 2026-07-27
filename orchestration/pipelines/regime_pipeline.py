"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Regime Pipeline

Responsibilities
----------------
1. Benchmark Price Construction
2. Market Breadth Analysis
3. Macro Regime Analysis
4. Market Regime Classification
5. Composite Regime Detection

=========================================================
"""

from __future__ import annotations

# ==========================================================
# REGIME ENGINES
# ==========================================================
from analytics.regime.benchmark_prices import (
    main as benchmark_prices_engine,
)
from analytics.regime.macro_regime_engine import (
    main as macro_regime_engine,
)
from analytics.regime.market_breadth_engine import (
    main as market_breadth_engine,
)
from analytics.regime.market_regime_engine import (
    main as market_regime_engine,
)
from analytics.regime.regime_engine import (
    main as regime_engine,
)
from orchestration.models.pipeline_result import (
    PipelineResult,
)
from orchestration.pipelines.base_pipeline import (
    BasePipeline,
)

# ==========================================================
# REGIME PIPELINE
# ==========================================================


class RegimePipeline(BasePipeline):
    """
    Institutional Market Regime Pipeline.
    """

    NAME = "RegimePipeline"

    #
    # Regime detection has sequential dependencies.
    #
    EXECUTOR = "sequential"

    ENGINES = [
        (
            "Benchmark Prices",
            benchmark_prices_engine,
        ),
        (
            "Market Breadth",
            market_breadth_engine,
        ),
        (
            "Macro Regime",
            macro_regime_engine,
        ),
        (
            "Market Regime",
            market_regime_engine,
        ),
        (
            "Composite Regime",
            regime_engine,
        ),
    ]

    # =====================================================
    # OPTIONAL HOOKS
    # =====================================================

    def before_run(self) -> None:

        print("\nStarting Regime Pipeline...")

    # -----------------------------------------------------

    def after_run(
        self,
        result: PipelineResult,
    ) -> None:

        print(f"\nCompleted {self.NAME}")

        print(f"Status   : {result.status.value}")

        print(f"Duration : {result.duration:.2f}s")

    # =====================================================
    # ENTRY POINT
    # =====================================================

    @classmethod
    def main(
        cls,
    ) -> PipelineResult:

        return cls().run()


# ==========================================================
# MODULE ENTRY
# ==========================================================


def main() -> PipelineResult:

    return RegimePipeline.main()


# ==========================================================
# CLI
# ==========================================================

if __name__ == "__main__":
    result = main()

    print(result)
