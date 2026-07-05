"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Orchestrator

Public facade for the orchestration framework.

Responsibilities
----------------
• Simplified public API
• Configure executor
• Execute platform
• Return execution results
• Expose execution report

Internally delegates all work to MasterOrchestrator.

=========================================================
"""

from __future__ import annotations

from typing import Optional

from orchestration.master_orchestrator import (
    MasterOrchestrator,
)

from orchestration.execution_context import (
    ExecutionContext,
)

from orchestration.execution_report import (
    ExecutionReport,
)

from orchestration.models.master_result import (
    MasterResult,
)


# =========================================================
# ORCHESTRATOR
# =========================================================

class Orchestrator:
    """
    Public orchestration facade.
    """

    DEFAULT_EXECUTOR = "sequential"

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(
        self,
        *,
        executor: str = DEFAULT_EXECUTOR,
    ) -> None:

        self._orchestrator = MasterOrchestrator(

            executor=executor,

        )

    # =====================================================
    # EXECUTION
    # =====================================================

    def run(
        self,
    ) -> MasterResult:
        """
        Execute the complete platform.
        """

        return self._orchestrator.run()

    # =====================================================
    # ACCESSORS
    # =====================================================

    @property
    def context(
        self,
    ) -> ExecutionContext:

        return self._orchestrator.context

    # -----------------------------------------------------

    @property
    def report(
        self,
    ) -> ExecutionReport:

        return self._orchestrator.report

    # -----------------------------------------------------

    @property
    def result(
        self,
    ) -> MasterResult:

        return self._orchestrator.result

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(
        self,
    ) -> dict:

        return {

            "executor":

                self._orchestrator.executor_mode,

            "status":

                self.result.status.value,

            "duration":

                round(

                    self.result.duration,

                    3,

                ),

            "pipelines":

                self.result.total_pipelines,

            "engines":

                self.result.total_engines,

        }

    # =====================================================
    # RESET
    # =====================================================

    def reset(
        self,
    ) -> None:
        """
        Reset orchestrator state.
        """

        executor = (

            self._orchestrator.executor_mode

        )

        self._orchestrator = MasterOrchestrator(

            executor=executor,

        )

    # =====================================================
    # DUNDER
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"executor='{self._orchestrator.executor_mode}')"

        )