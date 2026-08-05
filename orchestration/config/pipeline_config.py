"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Pipeline Configuration

Purpose
-------
Central registry for all platform pipelines.

Responsibilities
----------------
• Pipeline registration
• Execution ordering
• Stage management
• Lazy pipeline loading
• Execution policies

=========================================================
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from importlib import import_module

from config.settings import STOP_ON_FAILURE

# =========================================================
# IMPORT HELPERS
# =========================================================


def load_pipeline(
    module_name: str,
    function_name: str = "main",
) -> Callable:
    """
    Lazily import a pipeline entrypoint.

    Prevents circular imports while keeping
    pipeline registration centralized.
    """

    module = import_module(module_name)

    return getattr(module, function_name)


# =========================================================
# PIPELINE DEFINITION
# =========================================================


@dataclass(
    frozen=True,
    slots=True,
)
class PipelineDefinition:
    """
    Immutable pipeline definition.
    """

    name: str

    stage: int

    enabled: bool

    entrypoint: Callable


# =========================================================
# PIPELINE REGISTRY
# =========================================================


PIPELINE_REGISTRY: tuple[PipelineDefinition, ...] = (

    PipelineDefinition(
        name="Data Pipeline",
        stage=1,
        enabled=True,
        entrypoint=load_pipeline(
            "orchestration.pipelines.data_pipeline",
        ),
    ),

    PipelineDefinition(
        name="Signal Pipeline",
        stage=2,
        enabled=True,
        entrypoint=load_pipeline(
            "orchestration.pipelines.signal_pipeline",
        ),
    ),

    PipelineDefinition(
        name="Factor Pipeline",
        stage=3,
        enabled=True,
        entrypoint=load_pipeline(
            "orchestration.pipelines.factor_pipeline",
        ),
    ),

    PipelineDefinition(
        name="Alpha Pipeline",
        stage=4,
        enabled=True,
        entrypoint=load_pipeline(
            "orchestration.pipelines.alpha_pipeline",
        ),
    ),

    PipelineDefinition(
        name="Regime Pipeline",
        stage=5,
        enabled=True,
        entrypoint=load_pipeline(
            "orchestration.pipelines.regime_pipeline",
        ),
    ),

    PipelineDefinition(
        name="Risk Model Pipeline",
        stage=6,
        enabled=True,
        entrypoint=load_pipeline(
            "orchestration.pipelines.risk_model_pipeline",
        ),
    ),

    PipelineDefinition(
        name="Risk Pipeline",
        stage=7,
        enabled=True,
        entrypoint=load_pipeline(
            "orchestration.pipelines.risk_pipeline",
        ),
    ),

    PipelineDefinition(
        name="Portfolio Pipeline",
        stage=8,
        enabled=True,
        entrypoint=load_pipeline(
            "orchestration.pipelines.portfolio_pipeline",
        ),
    ),

    PipelineDefinition(
        name="Execution Pipeline",
        stage=9,
        enabled=True,
        entrypoint=load_pipeline(
            "orchestration.pipelines.execution_pipeline",
        ),
    ),

    PipelineDefinition(
        name="Live Pipeline",
        stage=10,
        enabled=True,
        entrypoint=load_pipeline(
            "orchestration.pipelines.live_pipeline",
        ),
    ),

    PipelineDefinition(
        name="Performance Pipeline",
        stage=11,
        enabled=True,
        entrypoint=load_pipeline(
            "orchestration.pipelines.performance_pipeline",
        ),
    ),

    PipelineDefinition(
        name="Reporting Pipeline",
        stage=12,
        enabled=True,
        entrypoint=load_pipeline(
            "orchestration.pipelines.reporting_pipeline",
        ),
    ),

    PipelineDefinition(
        name="Monitoring Pipeline",
        stage=13,
        enabled=True,
        entrypoint=load_pipeline(
            "orchestration.pipelines.monitoring_pipeline",
        ),
    ),

)


# =========================================================
# EXECUTION SETTINGS
# =========================================================


PIPELINE_EXECUTION_ORDER: tuple[str, ...] = tuple(
    pipeline.name
    for pipeline in PIPELINE_REGISTRY
)

TOTAL_PIPELINES: int = len(PIPELINE_REGISTRY)

STOP_PLATFORM_ON_FAILURE: bool = STOP_ON_FAILURE


# =========================================================
# HELPERS
# =========================================================


def enabled_pipelines() -> list[PipelineDefinition]:
    """
    Return enabled pipelines.
    """

    return [
        pipeline
        for pipeline in PIPELINE_REGISTRY
        if pipeline.enabled
    ]


def disabled_pipelines() -> list[PipelineDefinition]:
    """
    Return disabled pipelines.
    """

    return [
        pipeline
        for pipeline in PIPELINE_REGISTRY
        if not pipeline.enabled
    ]


def pipeline_names() -> list[str]:
    """
    Return enabled pipeline names.
    """

    return [
        pipeline.name
        for pipeline in enabled_pipelines()
    ]


def pipeline_count() -> int:
    """
    Return number of enabled pipelines.
    """

    return len(enabled_pipelines())


def get_pipeline(
    name: str,
) -> PipelineDefinition:
    """
    Retrieve a pipeline by name.

    Raises
    ------
    KeyError
        If the pipeline is not registered.
    """

    normalized = name.casefold()

    for pipeline in PIPELINE_REGISTRY:
        if pipeline.name.casefold() == normalized:
            return pipeline

    raise KeyError(f"Unknown pipeline: {name}")


def pipeline_exists(
    name: str,
) -> bool:
    """
    Return whether a pipeline exists.
    """

    return any(
        pipeline.name.casefold() == name.casefold()
        for pipeline in PIPELINE_REGISTRY
    )


def execution_plan() -> list[PipelineDefinition]:
    """
    Return execution plan ordered by stage.
    """

    return sorted(
        enabled_pipelines(),
        key=lambda pipeline: pipeline.stage,
    )
