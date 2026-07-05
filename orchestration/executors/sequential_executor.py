"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Sequential Executor

Default execution strategy.

Responsibilities
----------------
• Execute engines sequentially
• Maintain execution lifecycle
• Produce EngineResult objects
• Update ExecutionContext

=========================================================
"""

from __future__ import annotations

from datetime import datetime
from time import perf_counter
from typing import Any
from typing import List

from orchestration.base_engine import (
    BaseEngine,
)

from orchestration.executors.base_executor import (
    BaseExecutor,
)

from orchestration.models.engine_result import (
    EngineResult,
)

from orchestration.models.engine_status import (
    EngineStatus,
)

class SequentialExecutor(BaseExecutor):
    """
    Sequential execution strategy.
    """

    def __init__(
        self,
        registry,
        context,
    ) -> None:

        super().__init__(

            registry,

            context,

        )

    # =====================================================
    # EXECUTE
    # =====================================================

    def execute(
        self,
        engine_names: List[str],
    ) -> List[EngineResult]:
        """
        Execute engines sequentially.
        """

        self.clear_results()

        self.before_execution()

        try:

            for engine_name in engine_names:

                result = self.execute_engine(

                    engine_name

                )

                self.add_result(

                    result

                )

        finally:

            self.after_execution()

        return self.results
    
    # =====================================================
    # ENGINE
    # =====================================================

    def execute_engine(
        self,
        engine_name: str,
    ) -> EngineResult:
        """
        Execute one engine.
        """

        engine = self.create_engine(

            engine_name

        )

        timer = perf_counter()

        result = EngineResult(

            engine=engine.NAME,

            status=EngineStatus.RUNNING,

            duration=0.0,

        )

        self.before_engine(

            engine

        )

        try:

            output = engine.run(

                self.context

            )

            result.status = (

                EngineStatus.SUCCESS

            )

            result.output = output

            self.register_output(

                engine.NAME,

                output,

            )

            for path in engine.OUTPUTS:

                self.register_artifact(

                    path

                )

        except Exception as exc:

            result.status = (

                EngineStatus.FAILED

            )

            result.metadata["error"] = str(

                exc

            )

            raise

        finally:

            result.duration = (

                perf_counter()

                - timer

            )

            self.after_engine(

                engine,

                result,

            )

        return result
    
    # =====================================================
    # HOOKS
    # =====================================================

    def before_execution(
        self,
    ) -> None:

        self.set_context(

            "executor",

            self.strategy,

        )

        self.set_context(

            "execution_started",

            datetime.utcnow().isoformat(),

        )

    # -----------------------------------------------------

    def after_execution(
        self,
    ) -> None:

        self.set_context(

            "execution_finished",

            datetime.utcnow().isoformat(),

        )

    # =====================================================
    # ENGINE HOOKS
    # =====================================================

    def before_engine(
        self,
        engine: BaseEngine,
    ) -> None:

        self.set_context(

            "current_engine",

            engine.NAME,

        )

    # -----------------------------------------------------

    def after_engine(
        self,
        engine: BaseEngine,
        result: EngineResult,
    ) -> None:

        self.context.metadata[

            "last_engine"

        ] = engine.NAME

        self.context.metadata[

            "last_status"

        ] = result.status.value

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(
        self,
    ) -> dict:

        success = sum(

            1

            for result

            in self.results

            if (

                result.status

                == EngineStatus.SUCCESS

            )

        )

        failed = len(

            self.results

        ) - success

        return {

            "strategy":

                self.strategy,

            "executed":

                len(

                    self.results

                ),

            "successful":

                success,

            "failed":

                failed,

        }

    # =====================================================
    # DUNDER
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"executed={len(self.results)})"

        )