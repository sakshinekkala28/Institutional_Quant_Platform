"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Risk Model Pipeline

Responsibilities
----------------
1. Daily Returns Construction
2. Beta Model Construction
3. Volatility Model
4. Factor Returns
5. Factor Covariance
6. Specific Risk
7. Factor Exposure Matrix
8. Factor Risk Model
9. Covariance Matrix
10. Risk Model Validation

=========================================================
"""

from __future__ import annotations

from orchestration.models.pipeline_result import (
    PipelineResult,
)

from orchestration.pipelines.base_pipeline import (
    BasePipeline,
)

# ==========================================================
# RISK MODEL ENGINES
# ==========================================================

from analytics.risk.build_daily_returns import (
    main as daily_returns_engine,
)

from analytics.risk.build_beta_master import (
    main as beta_master_engine,
)

from analytics.risk.build_beta_model import (
    main as beta_model_engine,
)

from analytics.risk.build_volatility_model import (
    main as volatility_model_engine,
)

from analytics.risk.build_factor_returns import (
    main as factor_returns_engine,
)

from analytics.risk.build_factor_covariance import (
    main as factor_covariance_engine,
)

from analytics.risk.build_specific_risk import (
    main as specific_risk_engine,
)

from analytics.risk.build_factor_exposure_matrix import (
    main as exposure_matrix_engine,
)

from analytics.risk.build_factor_risk_model import (
    main as factor_risk_model_builder,
)

from analytics.risk.factor_risk_model import (
    main as factor_risk_model_engine,
)

from analytics.risk.covariance_matrix_engine import (
    main as covariance_matrix_engine,
)


# ==========================================================
# RISK MODEL PIPELINE
# ==========================================================

class RiskModelPipeline(BasePipeline):
    """
    Institutional Multi-Factor Risk Model Pipeline.
    """

    NAME = "RiskModelPipeline"

    #
    # Every stage depends on the previous one.
    #
    EXECUTOR = "sequential"

    ENGINES = [

        (
            "Daily Returns",
            daily_returns_engine,
        ),

        (
            "Beta Master",
            beta_master_engine,
        ),

        (
            "Beta Model",
            beta_model_engine,
        ),

        (
            "Volatility Model",
            volatility_model_engine,
        ),

        (
            "Factor Returns",
            factor_returns_engine,
        ),

        (
            "Factor Covariance",
            factor_covariance_engine,
        ),

        (
            "Specific Risk",
            specific_risk_engine,
        ),

        (
            "Factor Exposure Matrix",
            exposure_matrix_engine,
        ),

        (
            "Factor Risk Model Builder",
            factor_risk_model_builder,
        ),

        (
            "Factor Risk Model",
            factor_risk_model_engine,
        ),

        (
            "Covariance Matrix",
            covariance_matrix_engine,
        ),

    ]

    # =====================================================
    # OPTIONAL HOOKS
    # =====================================================

    def before_run(self) -> None:

        print(
            "\nStarting Risk Model Pipeline..."
        )

    # -----------------------------------------------------

    def after_run(
        self,
        result: PipelineResult,
    ) -> None:

        print(
            f"\nCompleted {self.NAME}"
        )

        print(
            f"Status   : {result.status.value}"
        )

        print(
            f"Duration : {result.duration:.2f}s"
        )

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

    return RiskModelPipeline.main()


# ==========================================================
# CLI
# ==========================================================

if __name__ == "__main__":

    result = main()

    print(result)