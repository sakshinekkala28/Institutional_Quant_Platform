"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Distributed Executor

Production-ready distributed execution framework.

Responsibilities
----------------
• Distributed engine execution
• Dependency-aware scheduling
• Worker abstraction
• Execution aggregation
• Failure handling
• Future integration with:
    - Ray
    - Dask
    - Celery
    - Kubernetes Jobs

=========================================================
"""

from __future__ import annotations

from collections.abc import Iterable
from concurrent.futures import FIRST_EXCEPTION, ThreadPoolExecutor, wait
import logging

from orchestration.executors.base_executor import BaseExecutor
from orchestration.models.engine_result import EngineResult

logger = logging.getLogger(__name__)


# ==========================================================
# DISTRIBUTED EXECUTOR
# ==========================================================


class DistributedExecutor(BaseExecutor):
    """
    Distributed execution engine.

    Currently executes using a local worker pool while
    preserving the distributed execution interface.
    """

    NAME = "distributed"

    def __init__(
        self,
        *,
        max_workers: int = 8,
    ) -> None:

        super().__init__()

        self.max_workers = max_workers

    # ======================================================
    # EXECUTION
    # ======================================================

    def execute(
        self,
        engines: Iterable,
    ) -> list[EngineResult]:
        """
        Execute engines concurrently.

        Returns
        -------
        list[EngineResult]
        """

        engines = list(engines)

        if not engines:
            return []

        logger.info(
            "DistributedExecutor starting %d engines.",
            len(engines),
        )

        results: list[EngineResult] = []

        with ThreadPoolExecutor(
            max_workers=self.max_workers,
            thread_name_prefix="distributed",
        ) as executor:
            futures = {
                executor.submit(
                    self._execute_engine,
                    engine,
                ): engine
                for engine in engines
            }

            completed, pending = wait(
                futures,
                return_when=FIRST_EXCEPTION,
            )

            # -------------------------------------------------
            # Completed Tasks
            # -------------------------------------------------

            for future in completed:
                try:
                    results.append(future.result())

                except Exception:
                    engine = futures[future]

                    logger.exception(
                        "Distributed execution failed: %s",
                        engine.name,
                    )

                    raise

            # -------------------------------------------------
            # Cancel Remaining Tasks
            # -------------------------------------------------

            for future in pending:
                future.cancel()

        logger.info("Distributed execution complete.")

        return results

    # ======================================================
    # ENGINE EXECUTION
    # ======================================================

    @staticmethod
    def _execute_engine(
        engine,
    ) -> EngineResult:
        """
        Execute a single engine.

        This method becomes the worker entry point
        when migrating to Ray, Dask, Celery, etc.
        """

        return engine.run()

    # ======================================================
    # CAPABILITIES
    # ======================================================

    @property
    def distributed(
        self,
    ) -> bool:

        return True

    @property
    def supports_dependencies(
        self,
    ) -> bool:

        return False

    @property
    def supports_retries(
        self,
    ) -> bool:

        return False

    # ======================================================
    # SUMMARY
    # ======================================================

    def summary(
        self,
    ) -> dict:

        return {
            "executor": self.NAME,
            "distributed": True,
            "max_workers": self.max_workers,
        }

    # ======================================================
    # DUNDER
    # ======================================================

    def __repr__(
        self,
    ) -> str:

        return f"{self.__class__.__name__}(workers={self.max_workers})"
