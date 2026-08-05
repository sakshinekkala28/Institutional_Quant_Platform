"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Pipeline Analyzer

Provides analytical insights for executable pipelines.

Responsibilities

• Pipeline Metrics
• Execution Statistics
• Parallelism Analysis
• Dependency Analysis
• Critical Engine Detection
• Complexity Analysis

=========================================================
"""

from __future__ import annotations

import json

from orchestration.pipeline_builder import PipelineDefinition


class PipelineAnalyzer:
    """
    Analyze executable pipelines.
    """

    # =====================================================
    # BASIC METRICS
    # =====================================================

    def metrics(
        self,
        pipeline: PipelineDefinition,
    ) -> dict:
        """
        Return basic pipeline metrics.
        """

        return {
            "pipeline": pipeline.name,
            "engine_count": pipeline.engine_count,
            "execution_levels": len(pipeline.execution_levels),
            "categories": len(pipeline.categories),
            "stages": len(pipeline.stages),
            "inputs": len(
                pipeline.metadata.get(
                    "inputs",
                    [],
                )
            ),
            "outputs": len(
                pipeline.metadata.get(
                    "outputs",
                    [],
                )
            ),
        }

    # =====================================================
    # PARALLELISM
    # =====================================================

    def parallelism(
        self,
        pipeline: PipelineDefinition,
    ) -> dict:
        """
        Analyze execution parallelism.
        """

        widths = [len(level) for level in pipeline.execution_levels]

        return {
            "maximum_parallelism": max(
                widths,
                default=0,
            ),
            "minimum_parallelism": min(
                widths,
                default=0,
            ),
            "average_parallelism": round(
                sum(widths)
                / max(
                    len(widths),
                    1,
                ),
                2,
            ),
        }

    # =====================================================
    # DEPENDENCY ANALYSIS
    # =====================================================

    def dependency_metrics(
        self,
        pipeline: PipelineDefinition,
    ) -> dict:
        """
        Analyze dependency graph.
        """

        dependency_count = 0

        root_engines = 0

        leaf_engines = 0

        for engine in pipeline.engines:
            dependency_count += len(engine.DEPENDS_ON)

            if not engine.DEPENDS_ON:
                root_engines += 1

        dependents = set()

        for engine in pipeline.engines:
            dependents.update(engine.DEPENDS_ON)

        leaf_engines = pipeline.engine_count - len(dependents)

        return {
            "total_dependencies": dependency_count,
            "root_engines": root_engines,
            "leaf_engines": leaf_engines,
            "average_dependencies": round(
                dependency_count
                / max(
                    pipeline.engine_count,
                    1,
                ),
                2,
            ),
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
        Engines eligible for
        concurrent execution.
        """

        return [engine.NAME for engine in pipeline.engines if engine.PARALLELIZABLE]

    # =====================================================
    # STAGE UTILIZATION
    # =====================================================

    def stage_utilization(
        self,
        pipeline: PipelineDefinition,
    ) -> dict[str, int]:
        """
        Number of engines per stage.
        """

        utilization = {}

        for engine in pipeline.engines:
            utilization.setdefault(
                engine.STAGE,
                0,
            )

            utilization[engine.STAGE] += 1

        return dict(sorted(utilization.items()))

    # =====================================================
    # CATEGORY UTILIZATION
    # =====================================================

    def category_utilization(
        self,
        pipeline: PipelineDefinition,
    ) -> dict[str, int]:
        """
        Number of engines per category.
        """

        utilization = {}

        for engine in pipeline.engines:
            utilization.setdefault(
                engine.CATEGORY,
                0,
            )

            utilization[engine.CATEGORY] += 1

        return dict(sorted(utilization.items()))

    # =====================================================
    # PRIORITY DISTRIBUTION
    # =====================================================

    def priority_distribution(
        self,
        pipeline: PipelineDefinition,
    ) -> dict[int, int]:
        """
        Distribution of engine priorities.
        """

        priorities = {}

        for engine in pipeline.engines:
            priorities.setdefault(
                engine.PRIORITY,
                0,
            )

            priorities[engine.PRIORITY] += 1

        return dict(sorted(priorities.items()))

    # =====================================================
    # COMPLEXITY SCORE
    # =====================================================

    def complexity_score(
        self,
        pipeline: PipelineDefinition,
    ) -> float:
        """
        Estimate pipeline complexity.

        Score range:
            0 - 100
        """

        dependency_count = sum(len(engine.DEPENDS_ON) for engine in pipeline.engines)

        stage_count = len(pipeline.execution_levels)

        raw = pipeline.engine_count * 1.5 + dependency_count * 2 + stage_count * 4

        score = min(
            raw / 2.5,
            100,
        )

        return round(
            min(score, 100),
            2,
        )

    # =====================================================
    # ESTIMATED EXECUTION TIME
    # =====================================================

    def estimated_runtime(
        self,
        pipeline: PipelineDefinition,
        default_seconds: float = 10.0,
    ) -> dict:
        """
        Estimate runtime.

        Uses BaseEngine.RUNTIME_ESTIMATE
        if available.
        """

        total = 0.0

        by_engine = {}

        for engine in pipeline.engines:
            estimate = getattr(
                engine,
                "RUNTIME_ESTIMATE",
                default_seconds,
            )

            total += estimate

            by_engine[engine.NAME] = estimate

        return {
            "estimated_runtime_seconds": round(total, 2),
            "estimated_runtime_minutes": round(total / 60, 2),
            "engine_estimates": by_engine,
        }

    # =====================================================
    # BOTTLENECK DETECTION
    # =====================================================

    def bottlenecks(
        self,
        pipeline: PipelineDefinition,
    ) -> list[str]:
        """
        Identify potential bottleneck engines.

        Current heuristic:
            - Critical engines
            - Engines with many dependencies
        """

        bottlenecks = []

        for engine in pipeline.engines:
            if engine.CRITICAL:
                bottlenecks.append(engine.NAME)

                continue

            if len(engine.DEPENDS_ON) >= 3:
                bottlenecks.append(engine.NAME)

        return sorted(set(bottlenecks))

    # =====================================================
    # CRITICAL PATH ANALYSIS
    # =====================================================

    def critical_path(
        self,
        pipeline: PipelineDefinition,
    ) -> list[str]:
        """
        Approximate critical execution path.

        Uses the first engine from each execution
        level ordered by priority.
        """

        path = []

        for level in pipeline.execution_levels:
            if not level:
                continue

            path.append(level[0])

        return path

    # =====================================================
    # PARALLEL EFFICIENCY
    # =====================================================

    def parallel_efficiency(
        self,
        pipeline: PipelineDefinition,
    ) -> dict:
        """
        Estimate pipeline parallel efficiency.
        """

        levels = pipeline.execution_levels

        if not levels:
            return {
                "efficiency": 0.0,
                "serial_fraction": 1.0,
                "parallel_fraction": 0.0,
            }

        maximum_parallel = max(len(level) for level in levels)

        average_parallel = pipeline.engine_count / len(levels)

        efficiency = average_parallel / max(maximum_parallel, 1)

        return {
            "efficiency": round(efficiency, 3),
            "serial_fraction": round(
                1.0 - efficiency,
                3,
            ),
            "parallel_fraction": round(
                efficiency,
                3,
            ),
        }

    # =====================================================
    # RESOURCE UTILIZATION
    # =====================================================

    def resource_utilization(
        self,
        pipeline: PipelineDefinition,
    ) -> dict:
        """
        Estimate execution resource usage.
        """

        runtime = self.estimated_runtime(pipeline)

        return {
            "engines": pipeline.engine_count,
            "parallel_groups": len(pipeline.execution_levels),
            "estimated_runtime": runtime["estimated_runtime_seconds"],
            "critical_engines": len(self.critical_engines(pipeline)),
            "parallelizable": len(self.parallelizable_engines(pipeline)),
        }

    # =====================================================
    # EXECUTION STATISTICS
    # =====================================================

    def execution_statistics(
        self,
        pipeline: PipelineDefinition,
    ) -> dict:
        """
        Aggregate execution statistics.
        """

        return {
            "metrics": self.metrics(pipeline),
            "parallelism": self.parallelism(pipeline),
            "dependencies": self.dependency_metrics(pipeline),
            "runtime": self.estimated_runtime(pipeline),
            "complexity": self.complexity_score(pipeline),
        }

    # =====================================================
    # COMPLETE ANALYSIS
    # =====================================================

    def analysis_report(
        self,
        pipeline: PipelineDefinition,
    ) -> dict:
        """
        Complete pipeline analysis.
        """

        return {
            "pipeline": pipeline.name,
            "metrics": self.metrics(pipeline),
            "parallelism": self.parallelism(pipeline),
            "dependency_metrics": self.dependency_metrics(pipeline),
            "stage_utilization": self.stage_utilization(pipeline),
            "category_utilization": self.category_utilization(pipeline),
            "priority_distribution": self.priority_distribution(pipeline),
            "runtime": self.estimated_runtime(pipeline),
            "critical_path": self.critical_path(pipeline),
            "parallel_efficiency": self.parallel_efficiency(pipeline),
            "resource_utilization": self.resource_utilization(pipeline),
            "complexity_score": self.complexity_score(pipeline),
            "bottlenecks": self.bottlenecks(pipeline),
            "critical_engines": self.critical_engines(pipeline),
        }

    # =====================================================
    # EXPORT
    # =====================================================

    def to_dict(
        self,
        pipeline: PipelineDefinition,
    ) -> dict:
        """
        Export complete analysis.
        """

        return self.analysis_report(pipeline)

    # -----------------------------------------------------

    def to_json(
        self,
        pipeline: PipelineDefinition,
        indent: int = 4,
    ) -> str:
        """
        Export analysis as JSON.
        """

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
        Concise analysis summary.
        """

        runtime = self.estimated_runtime(pipeline)

        return {
            "pipeline": pipeline.name,
            "engines": pipeline.engine_count,
            "levels": len(pipeline.execution_levels),
            "complexity": self.complexity_score(pipeline),
            "parallel_efficiency": self.parallel_efficiency(pipeline)["efficiency"],
            "estimated_runtime": runtime["estimated_runtime_seconds"],
            "critical_engines": len(self.critical_engines(pipeline)),
        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return f"{self.__class__.__name__}()"
