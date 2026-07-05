"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Parallel Executor

Executes independent engines concurrently while
respecting dependency ordering determined by the
DependencyGraph.

Responsibilities
----------------
• Parallel engine execution
• Thread pool management
• Timeout handling
• Future aggregation
• Exception propagation
• Thread-safe result collection
• Execution statistics

=========================================================
"""

from __future__ import annotations

from concurrent.futures import (
    ThreadPoolExecutor,
    Future,
    as_completed,
)

from datetime import datetime

from threading import Lock

from typing import Dict
from typing import List
from typing import Optional

from orchestration.executors.base_executor import (
    BaseExecutor,
)

from orchestration.models.engine_result import (
    EngineResult,
)

from orchestration.models.engine_status import (
    EngineStatus,
)

class ParallelExecutor(BaseExecutor):
    """
    Parallel execution strategy.

    Executes engines belonging to the same dependency
    level concurrently.
    """

    def __init__(
        self,
        registry,
        context,
        *,
        max_workers: Optional[int] = None,
        timeout: Optional[float] = None,
        cancel_on_failure: bool = True,
    ) -> None:

        super().__init__(
            registry,
            context,
        )

        self.max_workers = max_workers

        self.timeout = timeout

        self.cancel_on_failure = (
            cancel_on_failure
        )

        self._lock = Lock()

        self._executor = ThreadPoolExecutor(

            max_workers=max_workers,

            thread_name_prefix="IQP",

        )

    # =====================================================
    # RUNTIME
    # =====================================================

    def reset(self) -> None:

        self.clear_results()

        self._submitted = 0

        self._completed = 0

        self._failed = 0

        self._futures: Dict[
            Future,
            str,
        ] = {}

    # =====================================================
    # PROPERTIES
    # =====================================================

    @property
    def submitted(self) -> int:

        return self._submitted

    # -----------------------------------------------------

    @property
    def completed(self) -> int:

        return self._completed

    # -----------------------------------------------------

    @property
    def failed(self) -> int:

        return self._failed
    
    # =====================================================
    # EXECUTE
    # =====================================================

    def execute(
        self,
        engine_names: List[str],
    ) -> List[EngineResult]:
        """
        Execute engines concurrently.
        """

        self.reset()

        self.before_execution()

        try:

            self._submit(
                engine_names
            )

            self._collect()

        finally:

            self.after_execution()

        return sorted(

            self.results,

            key=lambda r: engine_names.index(
                r.engine
            ),

        )
    
    # =====================================================
    # HOOKS
    # =====================================================

    def before_execution(self) -> None:

        self.set_context(

            "executor",

            self.strategy,

        )

        self.set_context(

            "parallel",

            True,

        )

        self.set_context(

            "started_at",

            datetime.utcnow().isoformat(),

        )

    # -----------------------------------------------------

    def after_execution(self) -> None:

        self.set_context(

            "finished_at",

            datetime.utcnow().isoformat(),

        )

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(self) -> dict:

        return {

            "strategy":

                self.strategy,

            "submitted":

                self.submitted,

            "completed":

                self.completed,

            "failed":

                self.failed,

            "workers":

                self.max_workers,

        }
    
    # =====================================================
    # DUNDER
    # =====================================================

    def __repr__(self) -> str:

        return (

            f"{self.__class__.__name__}("

            f"workers={self.max_workers}, "

            f"submitted={self.submitted})"

        )
    
    # =====================================================
    # SUBMIT TASKS
    # =====================================================

    def _submit(
        self,
        engine_names: List[str],
    ) -> None:
        """
        Submit all engines to the thread pool.
        """

        self._futures.clear()

        for engine_name in engine_names:

            future = self._executor.submit(

                self._execute_engine,

                engine_name,

            )

            self._submitted += 1

            self._futures[
                future
            ] = engine_name

    # =====================================================
    # EXECUTE ENGINE
    # =====================================================

    def _execute_engine(
        self,
        engine_name: str,
    ) -> EngineResult:
        """
        Execute a single engine.

        Runs inside a worker thread.
        """

        engine = self.create_engine(
            engine_name
        )

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

            with self._lock:

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

            result.metadata[
                "error"
            ] = str(exc)

        finally:

            self.after_engine(

                engine,

                result,

            )

        return result
    
    # =====================================================
    # COLLECT
    # =====================================================

    def _collect(
        self,
    ) -> None:
        """
        Collect completed futures.
        """

        for future in as_completed(

            self._futures,

            timeout=self.timeout,

        ):

            engine_name = self._futures[
                future
            ]

            try:

                result = future.result()

                self.add_result(
                    result
                )

                self._completed += 1

                if (

                    result.status

                    == EngineStatus.FAILED

                ):

                    self._failed += 1

                    if self.cancel_on_failure:

                        self._cancel_pending()

                        raise RuntimeError(

                            f"{engine_name} failed."

                        )

            except Exception:

                self._failed += 1

                self._cancel_pending()

                raise

    # =====================================================
    # CANCEL
    # =====================================================

    def _cancel_pending(
        self,
    ) -> None:
        """
        Cancel unfinished tasks.
        """

        for future in self._futures:

            if not future.done():

                future.cancel()

    # =====================================================
    # ENGINE HOOKS
    # =====================================================

    def before_engine(
        self,
        engine,
    ) -> None:

        with self._lock:

            self.context.metadata[
                "current_engine"
            ] = engine.NAME

    # -----------------------------------------------------

    def after_engine(
        self,
        engine,
        result,
    ) -> None:

        with self._lock:

            self.context.metadata[
                "last_engine"
            ] = engine.NAME

            self.context.metadata[
                "last_status"
            ] = result.status.value

    # =====================================================
    # CLEANUP
    # =====================================================

    def shutdown(
        self,
        wait: bool = True,
    ) -> None:
        """
        Shutdown the executor.
        """

        self._executor.shutdown(
            wait=wait,
        )