"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Executor Factory

Creates execution strategy instances.

Responsibilities
----------------
• Register executor implementations
• Create executors
• Support custom executors
• Provide default execution strategy

=========================================================
"""

from __future__ import annotations

from typing import ClassVar

from orchestration.executors.base_executor import BaseExecutor
from orchestration.executors.parallel_executor import ParallelExecutor
from orchestration.executors.retry_executor import RetryExecutor
from orchestration.executors.sequential_executor import SequentialExecutor

# from orchestration.executors.distributed_executor import (
# DistributedExecutor,
# )


class ExecutorFactory:
    """
    Factory for execution strategies.
    """

    _executors: ClassVar[
        dict[str, type[BaseExecutor]]
    ] = {
        "sequential": SequentialExecutor,
        "parallel": ParallelExecutor,
        "retry": RetryExecutor,
        # "distributed": DistributedExecutor,
    }

    # =====================================================
    # REGISTER
    # =====================================================

    @classmethod
    def register(
        cls,
        name: str,
        executor: type[BaseExecutor],
    ) -> None:
        """
        Register a custom executor.
        """

        cls._executors[name.lower()] = executor

    # =====================================================
    # CREATE
    # =====================================================

    @classmethod
    def create(
        cls,
        mode: str,
        registry,
        context,
        **kwargs,
    ) -> BaseExecutor:
        """
        Create an executor instance.
        """

        mode = mode.lower()

        if mode not in cls._executors:
            available = ", ".join(sorted(cls._executors))

            raise ValueError(f"Unknown executor '{mode}'. Available: {available}")

        executor_class = cls._executors[mode]

        return executor_class(
            registry=registry,
            context=context,
            **kwargs,
        )

    # =====================================================
    # HELPERS
    # =====================================================

    @classmethod
    def available(
        cls,
    ) -> list[str]:
        """
        Return registered executors.
        """

        return sorted(cls._executors.keys())

    @classmethod
    def exists(
        cls,
        name: str,
    ) -> bool:

        return name.lower() in cls._executors

    @classmethod
    def default(
        cls,
    ) -> str:
        """
        Default execution strategy.
        """

        return "sequential"

    # =====================================================
    # DUNDER
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return f"{self.__class__.__name__}(registered={len(self._executors)})"
