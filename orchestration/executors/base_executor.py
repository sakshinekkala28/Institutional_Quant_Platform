"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Base Executor

Abstract execution strategy used by the Master
Orchestrator.

Responsibilities
----------------
• Execute one or more engines
• Manage engine lifecycle hooks
• Maintain shared execution context
• Produce EngineResult objects
• Support multiple execution strategies

Concrete Implementations
------------------------
• SequentialExecutor
• ParallelExecutor
• RetryExecutor
• DistributedExecutor

=========================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from orchestration.base_engine import BaseEngine
from orchestration.engine_registry import EngineRegistry
from orchestration.execution_context import ExecutionContext
from orchestration.models.engine_result import EngineResult


class BaseExecutor(ABC):
    """
    Abstract execution strategy.

    Concrete executors implement different execution
    models while exposing the same interface.
    """

    def __init__(
        self,
        registry: EngineRegistry,
        context: ExecutionContext,
    ) -> None:

        self.registry = registry

        self.context = context

        self._results: list[EngineResult] = []

    # =====================================================
    # ABSTRACT API
    # =====================================================

    @abstractmethod
    def execute(
        self,
        engine_names: list[str],
    ) -> list[EngineResult]:
        """
        Execute one or more engines.
        """

        raise NotImplementedError

    # =====================================================
    # ENGINE FACTORY
    # =====================================================

    def create_engine(
        self,
        engine_name: str,
    ) -> BaseEngine:
        """
        Instantiate an engine.
        """

        return self.registry.create(engine_name)

    # =====================================================
    # HOOKS
    # =====================================================

    def before_execution(
        self,
    ) -> None:
        """
        Hook executed before execution begins.
        """
        return

    def after_execution(
        self,
    ) -> None:
        """
        Hook executed after execution finishes.
        """
        return

    def before_engine(
        self,
        engine: BaseEngine,
    ) -> None:
        """
        Hook executed before an engine runs.
        """
        return

    def after_engine(
        self,
        engine: BaseEngine,
        result: EngineResult,
    ) -> None:
        """
        Hook executed after an engine runs.
        """
        return

    # =====================================================
    # RESULTS
    # =====================================================

    def add_result(
        self,
        result: EngineResult,
    ) -> None:

        self._results.append(result)

    @property
    def results(
        self,
    ) -> list[EngineResult]:

        return list(self._results)

    def clear_results(
        self,
    ) -> None:

        self._results.clear()

    # =====================================================
    # CONTEXT HELPERS
    # =====================================================

    def set_context(
        self,
        key: str,
        value: Any,
    ) -> None:

        self.context.metadata[key] = value

    def get_context(
        self,
        key: str,
        default: Any | None = None,
    ) -> Any:

        return self.context.metadata.get(
            key,
            default,
        )

    # =====================================================
    # OUTPUT HELPERS
    # =====================================================

    def register_output(
        self,
        engine_name: str,
        output: Any,
    ) -> None:

        self.context.outputs[engine_name] = output

    def register_artifact(
        self,
        path: str,
    ) -> None:

        self.context.artifacts.add(path)

    # =====================================================
    # INFORMATION
    # =====================================================

    @property
    def strategy(
        self,
    ) -> str:

        return self.__class__.__name__

    @property
    def engine_count(
        self,
    ) -> int:

        return len(self._results)

    # =====================================================
    # DUNDER
    # =====================================================

    def __len__(
        self,
    ) -> int:

        return len(self._results)

    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}("
            f"strategy='{self.strategy}', "
            f"executed={len(self)})"
        )
