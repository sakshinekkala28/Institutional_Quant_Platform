"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Portfolio Pipeline

Responsibilities
----------------
1. Portfolio Construction
2. Portfolio Optimization
3. Factor Optimization
4. Portfolio Constraints
5. Portfolio Rebalancing
6. Portfolio Monitoring
7. Portfolio History

=========================================================
"""

from __future__ import annotations

from analytics.portfolio.factor_optimizer import main as factor_optimizer_engine
from analytics.portfolio.optimizer_engine import main as optimizer_engine
from analytics.portfolio.portfolio_constraints_engine import (
    main as portfolio_constraints_engine,
)

# ==========================================================
# PORTFOLIO ENGINES
# ==========================================================
from analytics.portfolio.portfolio_engine import main as portfolio_engine
from analytics.portfolio.portfolio_history_engine import (
    main as portfolio_history_engine,
)
from analytics.portfolio.portfolio_monitor import main as portfolio_monitor_engine
from analytics.portfolio.portfolio_optimizer import main as portfolio_optimizer_engine
from analytics.portfolio.rebalancing_engine import main as rebalancing_engine
from orchestration.models.pipeline_result import PipelineResult
from orchestration.pipelines.base_pipeline import BasePipeline

# ==========================================================
# PORTFOLIO PIPELINE
# ==========================================================


class PortfolioPipeline(BasePipeline):
    """
    Institutional Portfolio Pipeline.
    """

    NAME = "PortfolioPipeline"

    #
    # Portfolio construction is dependency-driven.
    #
    EXECUTOR = "sequential"

    ENGINES = [
        (
            "Portfolio Engine",
            portfolio_engine,
        ),
        (
            "Optimizer Engine",
            optimizer_engine,
        ),
        (
            "Factor Optimizer",
            factor_optimizer_engine,
        ),
        (
            "Portfolio Optimizer",
            portfolio_optimizer_engine,
        ),
        (
            "Portfolio Constraints",
            portfolio_constraints_engine,
        ),
        (
            "Portfolio Rebalancing",
            rebalancing_engine,
        ),
        (
            "Portfolio Monitor",
            portfolio_monitor_engine,
        ),
        (
            "Portfolio History",
            portfolio_history_engine,
        ),
    ]

    # =====================================================
    # OPTIONAL HOOKS
    # =====================================================

    def before_run(self) -> None:

        print("\nStarting Portfolio Pipeline...")

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

    return PortfolioPipeline.main()


# ==========================================================
# CLI
# ==========================================================

if __name__ == "__main__":
    result = main()

    print(result)
