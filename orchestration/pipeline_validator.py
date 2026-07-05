"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Pipeline Validator

Validates executable pipelines before execution.

Responsibilities

• Graph Validation
• Pipeline Validation
• Dependency Validation
• Duplicate Detection
• Input Validation
• Output Validation

=========================================================
"""

from __future__ import annotations

from typing import Dict
from typing import List

from orchestration.pipeline_builder import (
    PipelineDefinition,
)

from orchestration.dependency_graph import (
    DependencyGraph,
)

from orchestration.engine_registry import (
    EngineRegistry,
)


class PipelineValidator:
    """
    Validate executable pipelines.
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
    # GRAPH VALIDATION
    # =====================================================

    def validate_graph(self) -> Dict:
        """
        Validate dependency graph.
        """

        return self.graph.validate()
    
    # =====================================================
    # PIPELINE VALIDATION
    # =====================================================

    def validate_pipeline(
        self,
        pipeline: PipelineDefinition,
    ) -> Dict:
        """
        Validate complete pipeline.
        """

        report = {

            "valid": True,

            "errors": [],

            "warnings": [],

        }

        report["errors"].extend(

            self.validate_duplicates(
                pipeline
            )

        )

        report["errors"].extend(

            self.validate_dependencies(
                pipeline
            )

        )

        report["errors"].extend(

            self.validate_inputs(
                pipeline
            )

        )

        report["errors"].extend(

            self.validate_outputs(
                pipeline
            )

        )

        report["valid"] = (

            len(report["errors"]) == 0

        )

        return report
    
    # =====================================================
    # DUPLICATE ENGINES
    # =====================================================

    def validate_duplicates(
        self,
        pipeline: PipelineDefinition,
    ) -> List[str]:
        """
        Detect duplicate engines.
        """

        names = [

            engine.NAME

            for engine

            in pipeline.engines

        ]

        duplicates = []

        seen = set()

        for name in names:

            if name in seen:

                duplicates.append(

                    f"Duplicate engine: {name}"

                )

            seen.add(name)

        return duplicates
    
    # =====================================================
    # DEPENDENCY VALIDATION
    # =====================================================

    def validate_dependencies(
        self,
        pipeline: PipelineDefinition,
    ) -> List[str]:
        """
        Validate pipeline dependencies.
        """

        available = {

            engine.NAME

            for engine

            in pipeline.engines

        }

        errors = []

        for engine in pipeline.engines:

            for dependency in engine.DEPENDS_ON:

                if dependency not in available:

                    errors.append(

                        f"{engine.NAME} "

                        f"requires "

                        f"{dependency}"

                    )

        return errors
    
    # =====================================================
    # INPUT VALIDATION
    # =====================================================

    def validate_inputs(
        self,
        pipeline: PipelineDefinition,
    ) -> List[str]:
        """
        Validate declared input resources.
        """

        errors: List[str] = []

        for engine in pipeline.engines:

            if not isinstance(
                engine.INPUTS,
                list,
            ):

                errors.append(

                    f"{engine.NAME}: "

                    "INPUTS must be a list."

                )

                continue

            for resource in engine.INPUTS:

                if not isinstance(
                    resource,
                    str,
                ):

                    errors.append(

                        f"{engine.NAME}: "

                        f"Invalid input "

                        f"'{resource}'."

                    )

        return errors

    # =====================================================
    # OUTPUT VALIDATION
    # =====================================================

    def validate_outputs(
        self,
        pipeline: PipelineDefinition,
    ) -> List[str]:
        """
        Validate declared outputs.
        """

        errors: List[str] = []

        produced = {}

        for engine in pipeline.engines:

            if not isinstance(
                engine.OUTPUTS,
                list,
            ):

                errors.append(

                    f"{engine.NAME}: "

                    "OUTPUTS must be a list."

                )

                continue

            for output in engine.OUTPUTS:

                if output in produced:

                    errors.append(

                        f"Duplicate output "

                        f"'{output}' "

                        f"generated by "

                        f"{produced[output]} "

                        f"and "

                        f"{engine.NAME}"

                    )

                else:

                    produced[
                        output
                    ] = engine.NAME

        return errors

    # =====================================================
    # CATEGORY VALIDATION
    # =====================================================

    def validate_categories(
        self,
        pipeline: PipelineDefinition,
    ) -> List[str]:
        """
        Validate engine categories.
        """

        errors: List[str] = []

        for engine in pipeline.engines:

            if not engine.CATEGORY:

                errors.append(

                    f"{engine.NAME}: "

                    "CATEGORY not defined."

                )

        return errors

    # =====================================================
    # STAGE VALIDATION
    # =====================================================

    def validate_stages(
        self,
        pipeline: PipelineDefinition,
    ) -> List[str]:
        """
        Validate stage assignments.
        """

        errors: List[str] = []

        for engine in pipeline.engines:

            if not engine.STAGE:

                errors.append(

                    f"{engine.NAME}: "

                    "STAGE not defined."

                )

        return errors

    # =====================================================
    # EXECUTION ORDER
    # =====================================================

    def validate_execution_order(
        self,
        pipeline: PipelineDefinition,
    ) -> List[str]:
        """
        Validate dependency order.
        """

        errors: List[str] = []

        order = {

            engine: index

            for index, engine

            in enumerate(

                pipeline.execution_order

            )

        }

        for engine in pipeline.engines:

            current = order.get(
                engine.NAME
            )

            if current is None:

                errors.append(

                    f"{engine.NAME} "

                    "missing from "

                    "execution order."

                )

                continue

            for dependency in engine.DEPENDS_ON:

                parent = order.get(
                    dependency
                )

                if parent is None:

                    continue

                if parent > current:

                    errors.append(

                        f"{dependency} "

                        f"must execute "

                        f"before "

                        f"{engine.NAME}"

                    )

        return errors

    # =====================================================
    # EXECUTION LEVELS
    # =====================================================

    def validate_execution_levels(
        self,
        pipeline: PipelineDefinition,
    ) -> List[str]:
        """
        Validate execution levels.
        """

        errors: List[str] = []

        assigned = set()

        for level in pipeline.execution_levels:

            for engine in level:

                if engine in assigned:

                    errors.append(

                        f"{engine} "

                        "appears in "

                        "multiple levels."

                    )

                assigned.add(engine)

        expected = {

            engine.NAME

            for engine

            in pipeline.engines

        }

        missing = expected - assigned

        if missing:

            errors.append(

                "Missing execution "

                f"levels: "

                f"{sorted(missing)}"

            )

        return errors
    
    # =====================================================
    # PIPELINE WARNINGS
    # =====================================================

    def warnings(
        self,
        pipeline: PipelineDefinition,
    ) -> List[str]:
        """
        Generate non-fatal pipeline warnings.
        """

        warnings: List[str] = []

        # ---------------------------------------------
        # Single engine pipeline
        # ---------------------------------------------

        if pipeline.engine_count == 1:

            warnings.append(

                "Pipeline contains "
                "only one engine."

            )

        # ---------------------------------------------
        # No outputs
        # ---------------------------------------------

        if not pipeline.outputs:

            warnings.append(

                "Pipeline produces "
                "no declared outputs."

            )

        # ---------------------------------------------
        # Multiple roots
        # ---------------------------------------------

        roots = [

            engine.NAME

            for engine in pipeline.engines

            if not engine.DEPENDS_ON

        ]

        if len(roots) > 5:

            warnings.append(

                f"Pipeline contains "
                f"{len(roots)} "
                f"root engines."

            )

        # ---------------------------------------------
        # Long execution chain
        # ---------------------------------------------

        if len(

            pipeline.execution_levels

        ) > 10:

            warnings.append(

                "Deep dependency chain "

                "may reduce "

                "parallel execution."

            )

        return warnings

    # =====================================================
    # PIPELINE COMPLETENESS
    # =====================================================

    def completeness_score(
        self,
        pipeline: PipelineDefinition,
    ) -> float:
        """
        Simple completeness score.
        """

        score = 100.0

        for engine in pipeline.engines:

            if not engine.INPUTS:

                score -= 1

            if not engine.OUTPUTS:

                score -= 1

            if not engine.CATEGORY:

                score -= 2

            if not engine.STAGE:

                score -= 2

            if not engine.DESCRIPTION:

                score -= 1

        return max(

            round(score, 2),

            0.0,

        )

    # =====================================================
    # VALIDATION SUMMARY
    # =====================================================

    def validation_summary(
        self,
        pipeline: PipelineDefinition,
    ) -> Dict:
        """
        Complete validation report.
        """

        report = self.validate_pipeline(
            pipeline
        )

        return {

            "pipeline":

                pipeline.name,

            "valid":

                report["valid"],

            "engine_count":

                pipeline.engine_count,

            "error_count":

                len(

                    report["errors"]

                ),

            "warning_count":

                len(

                    self.warnings(
                        pipeline
                    )

                ),

            "warnings":

                self.warnings(
                    pipeline
                ),

            "errors":

                report["errors"],

            "quality_score":

                self.completeness_score(
                    pipeline
                ),

        }

    # =====================================================
    # PIPELINE HEALTH
    # =====================================================

    def health(
        self,
        pipeline: PipelineDefinition,
    ) -> str:
        """
        Human-readable health status.
        """

        report = self.validation_summary(
            pipeline
        )

        if not report["valid"]:

            return "FAILED"

        if report["quality_score"] >= 95:

            return "EXCELLENT"

        if report["quality_score"] >= 85:

            return "GOOD"

        if report["quality_score"] >= 70:

            return "FAIR"

        return "POOR"

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(
        self,
        pipeline: PipelineDefinition,
    ) -> Dict:
        """
        Validator summary.
        """

        validation = self.validation_summary(
            pipeline
        )

        return {

            "pipeline":

                pipeline.name,

            "health":

                self.health(
                    pipeline
                ),

            "quality_score":

                validation[
                    "quality_score"
                ],

            "valid":

                validation["valid"],

            "errors":

                validation[
                    "error_count"
                ],

            "warnings":

                validation[
                    "warning_count"
                ],

        }

    # =====================================================
    # DUNDER
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"registry={self.registry.engine_count}, "

            f"graph_nodes={self.graph.node_count})"

        )