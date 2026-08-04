"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Pipeline Builder

Constructs executable pipelines from the
Engine Registry and Dependency Graph.

Responsibilities

• Build executable pipelines
• Resolve engine dependencies
• Generate execution order
• Generate parallel execution levels
• Validate pipeline integrity
• Produce pipeline metadata

=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field

from orchestration.base_engine import BaseEngine
from orchestration.dependency_graph import DependencyGraph
from orchestration.engine_registry import EngineRegistry

# =========================================================
# PIPELINE DEFINITION
# =========================================================


@dataclass(slots=True)
class PipelineDefinition:
    """
    Executable pipeline definition.
    """

    name: str

    engines: list[type[BaseEngine]] = field(default_factory=list)

    execution_order: list[str] = field(default_factory=list)

    execution_levels: list[list[str]] = field(default_factory=list)

    metadata: dict = field(default_factory=dict)

    # -----------------------------------------------------

    @property
    def engine_count(self) -> int:

        return len(self.engines)

    # -----------------------------------------------------

    @property
    def categories(self) -> list[str]:

        return sorted({engine.CATEGORY for engine in self.engines})

    # -----------------------------------------------------

    @property
    def stages(self) -> list[str]:

        return sorted({engine.STAGE for engine in self.engines})

    # -----------------------------------------------------

    @property
    def outputs(self) -> list[str]:

        outputs = []

        for engine in self.engines:
            outputs.extend(engine.OUTPUTS)

        return outputs

    # -----------------------------------------------------

    @property
    def dependencies(self) -> dict:

        return {engine.NAME: engine.DEPENDS_ON for engine in self.engines}


# =========================================================
# PIPELINE BUILDER
# =========================================================


class PipelineBuilder:
    """
    Build executable pipelines from
    the Engine Registry.
    """

    # =====================================================
    # CONSTRUCTOR
    # =====================================================

    def __init__(
        self,
        registry: EngineRegistry,
        graph: DependencyGraph,
    ) -> None:

        self.registry = registry

        self.graph = graph

    # =====================================================
    # BUILD PIPELINE
    # =====================================================

    def build(
        self,
        pipeline_name: str = "Master Pipeline",
        stages: list[str] | None = None,
        categories: list[str] | None = None,
        engine_names: list[str] | None = None,
    ) -> PipelineDefinition:
        """
        Build an executable pipeline.
        """

        # ---------------------------------------------
        # Validate graph
        # ---------------------------------------------

        self._validate_graph()

        # ---------------------------------------------
        # Select engines
        # ---------------------------------------------

        engines = self._select_engines(
            stages=stages,
            categories=categories,
            engine_names=engine_names,
        )

        # ---------------------------------------------
        # Automatically include dependencies
        # ---------------------------------------------

        engines = self._expand_dependencies(engines)

        # ---------------------------------------------
        # Determine execution order
        # ---------------------------------------------

        execution_order = self._execution_order(engines)

        execution_levels = self._execution_levels(execution_order)

        # ---------------------------------------------
        # Metadata
        # ---------------------------------------------

        metadata = self._build_metadata(
            pipeline_name,
            engines,
            execution_levels,
        )

        return PipelineDefinition(
            name=pipeline_name,
            engines=engines,
            execution_order=execution_order,
            execution_levels=execution_levels,
            metadata=metadata,
        )

    # =====================================================
    # BUILD FROM STAGE
    # =====================================================

    def build_from_stage(
        self,
        stage: str,
    ) -> PipelineDefinition:
        """
        Convenience wrapper.
        """

        return self.build(
            pipeline_name=stage,
            stages=[stage],
        )

    # =====================================================
    # BUILD FROM CATEGORY
    # =====================================================

    def build_from_category(
        self,
        category: str,
    ) -> PipelineDefinition:
        """
        Convenience wrapper.
        """

        return self.build(
            pipeline_name=category,
            categories=[category],
        )

    # =====================================================
    # BUILD FROM ENGINE LIST
    # =====================================================

    def build_from_engines(
        self,
        pipeline_name: str,
        engines: list[str],
    ) -> PipelineDefinition:
        """
        Build pipeline from explicit engines.
        """

        return self.build(
            pipeline_name=pipeline_name,
            engine_names=engines,
        )

    # =====================================================
    # EXECUTION ORDER
    # =====================================================

    def _execution_order(
        self,
        engines: list[type[BaseEngine]],
    ) -> list[str]:
        """
        Build dependency-aware execution order.
        """

        selected = {engine.NAME for engine in engines}

        order = []

        for engine in self.graph.execution_order():
            if engine in selected:
                order.append(engine)

        return order

    # =====================================================
    # EXECUTION LEVELS
    # =====================================================

    def _execution_levels(
        self,
        execution_order: list[str],
    ) -> list[list[str]]:
        """
        Build parallel execution levels.
        """

        selected = set(execution_order)

        levels = []

        for level in self.graph.execution_levels():
            current = [engine for engine in level if engine in selected]

            if current:
                levels.append(current)

        return levels

    # =====================================================
    # GRAPH VALIDATION
    # =====================================================

    def _validate_graph(
        self,
    ) -> None:
        """
        Validate dependency graph.
        """

        report = self.graph.validate()

        if report["valid"]:
            return

        errors = []

        errors.extend(
            report.get(
                "dependency_errors",
                [],
            )
        )

        errors.extend(
            report.get(
                "node_errors",
                [],
            )
        )

        cycles = report.get(
            "cycles",
            [],
        )

        if cycles:
            errors.append(f"Dependency cycles detected: {cycles}")

        raise RuntimeError("\n".join(errors))

    # =====================================================
    # PIPELINE VALIDATION
    # =====================================================

    def _validate_pipeline(
        self,
        engines: list[type[BaseEngine]],
    ) -> None:
        """
        Validate selected pipeline.
        """

        if not engines:
            raise RuntimeError("Pipeline contains no engines.")

        names = [engine.NAME for engine in engines]

        if len(names) != len(set(names)):
            raise RuntimeError("Duplicate engines detected.")

        missing = []

        for engine in engines:
            for dependency in engine.DEPENDS_ON:
                if dependency not in names:
                    missing.append(
                        (
                            engine.NAME,
                            dependency,
                        )
                    )

        if missing:
            message = [
                f"{engine} requires {dependency}"
                for (
                    engine,
                    dependency,
                ) in missing
            ]

            raise RuntimeError("\n".join(message))

    # =====================================================
    # PIPELINE METRICS
    # =====================================================

    def pipeline_metrics(
        self,
        pipeline: PipelineDefinition,
    ) -> dict:
        """
        Return execution metrics for a pipeline.
        """

        parallel_width = max(
            (len(level) for level in pipeline.execution_levels),
            default=0,
        )

        outputs = sum(len(engine.OUTPUTS) for engine in pipeline.engines)

        inputs = sum(len(engine.INPUTS) for engine in pipeline.engines)

        dependencies = sum(len(engine.DEPENDS_ON) for engine in pipeline.engines)

        return {
            "pipeline": pipeline.name,
            "engine_count": pipeline.engine_count,
            "execution_levels": len(pipeline.execution_levels),
            "maximum_parallelism": parallel_width,
            "total_inputs": inputs,
            "total_outputs": outputs,
            "total_dependencies": dependencies,
        }

    # =====================================================
    # EXECUTION SUMMARY
    # =====================================================

    def execution_summary(
        self,
        pipeline: PipelineDefinition,
    ) -> dict:
        """
        Human-readable execution summary.
        """

        return {
            "pipeline": pipeline.name,
            "execution_order": pipeline.execution_order,
            "parallel_execution": pipeline.execution_levels,
            "metadata": pipeline.metadata,
            "metrics": self.pipeline_metrics(pipeline),
        }

    # =====================================================
    # CRITICAL ENGINES
    # =====================================================

    def critical_engines(
        self,
        pipeline: PipelineDefinition,
    ) -> list[str]:
        """
        Return critical engines.
        """

        return [engine.NAME for engine in pipeline.engines if engine.CRITICAL]

    # =====================================================
    # PARALLELIZABLE ENGINES
    # =====================================================

    def parallelizable_engines(
        self,
        pipeline: PipelineDefinition,
    ) -> list[str]:
        """
        Return engines that may
        execute concurrently.
        """

        return [engine.NAME for engine in pipeline.engines if engine.PARALLELIZABLE]

    # =====================================================
    # EXPORT
    # =====================================================

    def to_dict(
        self,
        pipeline: PipelineDefinition,
    ) -> dict:
        """
        Export pipeline.
        """

        return {
            "name": pipeline.name,
            "engines": [engine.metadata() for engine in pipeline.engines],
            "execution_order": pipeline.execution_order,
            "execution_levels": pipeline.execution_levels,
            "metadata": pipeline.metadata,
            "metrics": self.pipeline_metrics(pipeline),
        }

    # -----------------------------------------------------

    def to_json(
        self,
        pipeline: PipelineDefinition,
        indent: int = 4,
    ) -> str:
        """
        Export pipeline as JSON.
        """

        import json

        return json.dumps(
            self.to_dict(pipeline),
            indent=indent,
        )

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(
        self,
        pipeline: PipelineDefinition,
    ) -> dict:
        """
        Pipeline summary.
        """

        return {
            "pipeline": pipeline.name,
            "engines": pipeline.engine_count,
            "categories": pipeline.categories,
            "stages": pipeline.stages,
            "execution_levels": len(pipeline.execution_levels),
            "execution_order": pipeline.execution_order,
            "metrics": self.pipeline_metrics(pipeline),
        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}("
            f"registry={self.registry.engine_count}, "
            f"graph_nodes={self.graph.node_count})"
        )
