"""
=========================================================
PIPELINE CONFIGURATION
=========================================================

Purpose:
Central registry for all platform pipelines.

This module defines:

• Platform execution order
• Stage grouping
• Pipeline registration
• Execution policies

=========================================================
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from config.settings import (
    STOP_ON_FAILURE,
)

# =========================================================
# PIPELINE DEFINITION
# =========================================================


@dataclass(frozen=True, slots=True)
class PipelineDefinition:
    """
    Immutable pipeline registration.
    """

    name: str

    stage: int

    enabled: bool

    entrypoint: Callable


# =========================================================
# IMPORT PIPELINES
# =========================================================

from orchestration.pipelines.data_pipeline import (
    main as data_pipeline,
)

#
# Uncomment as they become available.
#
# from orchestration.pipelines.factor_pipeline import (
#     main as factor_pipeline,
# )
#
# from orchestration.pipelines.alpha_pipeline import (
#     main as alpha_pipeline,
# )
#
# from orchestration.pipelines.risk_pipeline import (
#     main as risk_pipeline,
# )
#
# from orchestration.pipelines.portfolio_pipeline import (
#     main as portfolio_pipeline,
# )
#
# from orchestration.pipelines.execution_pipeline import (
#     main as execution_pipeline,
# )
#
# from orchestration.pipelines.reporting_pipeline import (
#     main as reporting_pipeline,
# )
#
# from orchestration.pipelines.monitoring_pipeline import (
#     main as monitoring_pipeline,
# )

# =========================================================
# PIPELINE REGISTRY
# =========================================================

PIPELINE_REGISTRY: tuple[PipelineDefinition, ...] = (
    PipelineDefinition(
        name="Data Pipeline",
        stage=1,
        enabled=True,
        entrypoint=data_pipeline,
    ),
    #
    # PipelineDefinition(
    #     name="Factor Pipeline",
    #     stage=2,
    #     enabled=True,
    #     entrypoint=factor_pipeline,
    # ),
    #
    # PipelineDefinition(
    #     name="Alpha Pipeline",
    #     stage=3,
    #     enabled=True,
    #     entrypoint=alpha_pipeline,
    # ),
    #
    # PipelineDefinition(
    #     name="Risk Pipeline",
    #     stage=4,
    #     enabled=True,
    #     entrypoint=risk_pipeline,
    # ),
    #
    # PipelineDefinition(
    #     name="Portfolio Pipeline",
    #     stage=5,
    #     enabled=True,
    #     entrypoint=portfolio_pipeline,
    # ),
    #
    # PipelineDefinition(
    #     name="Execution Pipeline",
    #     stage=6,
    #     enabled=True,
    #     entrypoint=execution_pipeline,
    # ),
    #
    # PipelineDefinition(
    #     name="Reporting Pipeline",
    #     stage=7,
    #     enabled=True,
    #     entrypoint=reporting_pipeline,
    # ),
    #
    # PipelineDefinition(
    #     name="Monitoring Pipeline",
    #     stage=8,
    #     enabled=True,
    #     entrypoint=monitoring_pipeline,
    # ),
)

# =========================================================
# EXECUTION SETTINGS
# =========================================================

PIPELINE_EXECUTION_ORDER = tuple(pipeline.name for pipeline in PIPELINE_REGISTRY)

TOTAL_PIPELINES = len(PIPELINE_REGISTRY)

STOP_PLATFORM_ON_FAILURE = STOP_ON_FAILURE

# =========================================================
# HELPERS
# =========================================================


def enabled_pipelines() -> list[PipelineDefinition]:
    """
    Return enabled pipelines
    in execution order.
    """

    return [pipeline for pipeline in PIPELINE_REGISTRY if pipeline.enabled]


def pipeline_names() -> list[str]:
    """
    Return pipeline names.
    """

    return [pipeline.name for pipeline in enabled_pipelines()]


def pipeline_count() -> int:
    """
    Number of enabled pipelines.
    """

    return len(enabled_pipelines())
