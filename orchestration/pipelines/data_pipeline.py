"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Analytics Data Pipeline

Responsibilities
----------------
1. Symbol Metadata
2. Market Cap Enrichment
3. Universe Construction
4. Incremental Price Update
5. Security Master
6. Stock Metadata

=========================================================
"""

from __future__ import annotations

from analytics.data.generate_metadata import (
    main as stock_metadata_engine,
)

from analytics.data.incremental_price_update import (
    main as price_update_engine,
)

from analytics.data.market_cap_enrichment import (
    main as market_cap_engine,
)

from analytics.data.security_master import (
    main as security_master_engine,
)

from analytics.data.symbol_metadata import (
    main as symbol_metadata_engine,
)

from analytics.data.updated_stocks import (
    main as universe_engine,
)

from orchestration.models.pipeline_result import (
    PipelineResult,
)

from orchestration.pipelines.base_pipeline import (
    BasePipeline,
)


# ==========================================================
# DATA PIPELINE
# ==========================================================

class DataPipeline(BasePipeline):
    """
    Institutional Analytics Data Pipeline.
    """

    NAME = "AnalyticsDataPipeline"

    EXECUTOR = "sequential"

    ENGINES = [

        (
            "Symbol Metadata",
            symbol_metadata_engine,
        ),

        (
            "Market Cap Enrichment",
            market_cap_engine,
        ),

        (
            "Universe Construction",
            universe_engine,
        ),

        (
            "Incremental Price Update",
            price_update_engine,
        ),

        (
            "Security Master",
            security_master_engine,
        ),

        (
            "Stock Metadata",
            stock_metadata_engine,
        ),

    ]

    # =====================================================
    # OPTIONAL HOOKS
    # =====================================================

    def before_run(self) -> None:

        print("\nStarting Analytics Data Pipeline...")

    # -----------------------------------------------------

    def after_run(
        self,
        result: PipelineResult,
    ) -> None:

        print(

            f"\nCompleted "

            f"{self.NAME}"

        )

        print(

            f"Status : "

            f"{result.status.value}"

        )

        print(

            f"Duration : "

            f"{result.duration:.2f}s"

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

    return DataPipeline.main()


# ==========================================================
# CLI
# ==========================================================

if __name__ == "__main__":

    result = main()

    print()

    print(result)