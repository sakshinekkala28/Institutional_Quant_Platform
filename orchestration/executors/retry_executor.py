"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Retry Executor

Execution strategy supporting retry policies.

Responsibilities
----------------
• Retry failed engines
• Exponential backoff
• Retry policy
• Failure reporting
• Execution statistics

=========================================================
"""

from __future__ import annotations

import time

from orchestration.executors.sequential_executor import SequentialExecutor
from orchestration.models.engine_result import EngineResult
from orchestration.models.engine_status import EngineStatus


class RetryExecutor(SequentialExecutor):
    """
    Sequential executor with retry support.
    """

    def __init__(
        self,
        registry,
        context,
        *,
        max_retries: int = 3,
        retry_delay: float = 1.0,
        exponential_backoff: bool = True,
    ) -> None:

        super().__init__(
            registry,
            context,
        )

        self.max_retries = max_retries

        self.retry_delay = retry_delay

        self.exponential_backoff = exponential_backoff

    # =====================================================
    # EXECUTE
    # =====================================================

    def execute(
        self,
        engine_names: list[str],
    ) -> list[EngineResult]:

        self.clear_results()

        self.before_execution()

        try:
            for engine_name in engine_names:
                result = self.execute_with_retry(engine_name)

                self.add_result(result)

        finally:
            self.after_execution()

        return self.results

    # =====================================================
    # RETRY
    # =====================================================

    def execute_with_retry(
        self,
        engine_name: str,
    ) -> EngineResult:
        """
        Execute engine with retry policy.
        """

        last_result: EngineResult | None = None

        for attempt in range(self.max_retries + 1):
            result = super().execute_engine(engine_name)

            if result.status == EngineStatus.SUCCESS:
                result.metadata["attempt"] = attempt + 1

                return result

            last_result = result

            self._wait(attempt)

        return last_result

    # =====================================================
    # BACKOFF
    # =====================================================

    def _wait(
        self,
        attempt: int,
    ) -> None:
        """
        Wait before retry.
        """

        delay = self.retry_delay

        if self.exponential_backoff:
            delay *= 2**attempt

        time.sleep(delay)

    # =====================================================
    # METADATA
    # =====================================================

    @property
    def retry_policy(
        self,
    ) -> dict:

        return {
            "max_retries": self.max_retries,
            "retry_delay": self.retry_delay,
            "exponential_backoff": self.exponential_backoff,
        }

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(
        self,
    ) -> dict:

        report = super().summary()

        report.update(
            {
                "retry_policy": self.retry_policy,
            }
        )

        return report
