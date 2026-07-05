"""
====================================================================
Institutional Quant Platform

Institutional Pipeline

Author : Institutional Quant Platform

Purpose
-------
Enterprise-grade workflow orchestration engine.

Responsibilities

• Platform Initialization
• Workflow Execution
• Stage Scheduling
• Dependency Resolution
• Artifact Management
• Runtime Metrics
• Checkpoint Management
• Reporting
• Graceful Shutdown

====================================================================
"""

from __future__ import annotations

# ==========================================================
# STANDARD LIBRARY
# ==========================================================

import logging
import os
import socket
import sys
import time
import traceback
import uuid

from collections import defaultdict
from collections import deque

from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import as_completed

from dataclasses import dataclass
from dataclasses import field

from datetime import UTC
from datetime import datetime

from enum import Enum
from enum import auto

from pathlib import Path

from typing import Any
from typing import Callable
from typing import Iterable

# ==========================================================
# PROJECT IMPORTS
# ==========================================================

from orchestration.context import PipelineContext

from orchestration.workflow import PIPELINE

# ==========================================================
# LOGGER
# ==========================================================

logger = logging.getLogger(__name__)

# ==========================================================
# PIPELINE CONSTANTS
# ==========================================================

PIPELINE_NAME = "Institutional Quant Platform"

PIPELINE_VERSION = "2.0.0"

DEFAULT_WORKERS = max(

    1,

    min(

        os.cpu_count() or 1,

        8,

    ),

)

DEFAULT_RETRIES = 3

DEFAULT_TIMEOUT = 3600

CHECKPOINT_DIRECTORY = Path(

    "data/checkpoints"

)

ARTIFACT_DIRECTORY = Path(

    "data/artifacts"

)

REPORT_DIRECTORY = Path(

    "reports"

)

LOG_DIRECTORY = Path(

    "logs"

)

# ==========================================================
# PIPELINE STATE
# ==========================================================


class PipelineState(Enum):
    """
    Pipeline lifecycle.
    """

    CREATED = auto()

    INITIALIZING = auto()

    READY = auto()

    RUNNING = auto()

    PAUSED = auto()

    COMPLETED = auto()

    FAILED = auto()

    CANCELLED = auto()

    SHUTDOWN = auto()


# ==========================================================
# STAGE STATUS
# ==========================================================


class StageStatus(Enum):
    """
    Stage execution state.
    """

    PENDING = auto()

    WAITING = auto()

    READY = auto()

    RUNNING = auto()

    SUCCESS = auto()

    FAILED = auto()

    SKIPPED = auto()

    RETRYING = auto()

    CANCELLED = auto()


# ==========================================================
# ARTIFACT TYPE
# ==========================================================


class ArtifactType(Enum):
    """
    Pipeline artifact category.
    """

    DATAFRAME = auto()

    PARQUET = auto()

    CSV = auto()

    JSON = auto()

    MODEL = auto()

    REPORT = auto()

    METRICS = auto()

    CACHE = auto()

    OTHER = auto()


# ==========================================================
# EXECUTION MODE
# ==========================================================


class ExecutionMode(Enum):
    """
    Pipeline execution mode.
    """

    SEQUENTIAL = auto()

    PARALLEL = auto()

    DAG = auto()


# ==========================================================
# PIPELINE EVENTS
# ==========================================================


class PipelineEvent(Enum):
    """
    Internal orchestration events.
    """

    PIPELINE_STARTED = auto()

    PIPELINE_FINISHED = auto()

    PIPELINE_FAILED = auto()

    STAGE_STARTED = auto()

    STAGE_FINISHED = auto()

    STAGE_FAILED = auto()

    STAGE_SKIPPED = auto()

    ARTIFACT_CREATED = auto()

    CHECKPOINT_CREATED = auto()


# ==========================================================
# EXECUTION ENVIRONMENT
# ==========================================================

HOSTNAME = socket.gethostname()

PROCESS_ID = os.getpid()

SESSION_ID = uuid.uuid4().hex

PIPELINE_STARTED_AT = datetime.now(UTC)

# ==========================================================
# STAGE RESULT
# ==========================================================


@dataclass(slots=True)
class StageResult:
    """
    Result returned by every pipeline stage.
    """

    name: str

    status: StageStatus

    success: bool

    started_at: datetime

    finished_at: datetime

    duration_seconds: float

    retries: int = 0

    artifacts: list[str] = field(

        default_factory=list

    )

    warnings: list[str] = field(

        default_factory=list

    )

    errors: list[str] = field(

        default_factory=list

    )

    metadata: dict[str, Any] = field(

        default_factory=dict

    )

    @property
    def failed(

        self

    ) -> bool:

        return not self.success

    @property
    def artifact_count(

        self

    ) -> int:

        return len(

            self.artifacts

        )

    def add_warning(

        self,

        message: str,

    ) -> None:

        self.warnings.append(

            message

        )

    def add_error(

        self,

        message: str,

    ) -> None:

        self.errors.append(

            message

        )

    def add_artifact(

        self,

        artifact: str,

    ) -> None:

        self.artifacts.append(

            artifact

        )

    def summary(

        self

    ) -> dict[str, Any]:

        return {

            "stage":

                self.name,

            "status":

                self.status.name,

            "success":

                self.success,

            "duration":

                self.duration_seconds,

            "retries":

                self.retries,

            "artifacts":

                self.artifact_count,

            "warnings":

                len(

                    self.warnings

                ),

            "errors":

                len(

                    self.errors

                ),

        }


# ==========================================================
# STAGE METRICS
# ==========================================================


@dataclass(slots=True)
class StageMetrics:
    """
    Runtime metrics collected for a stage.
    """

    stage_name: str

    rows_processed: int = 0

    input_rows: int = 0

    output_rows: int = 0

    input_columns: int = 0

    output_columns: int = 0

    files_read: int = 0

    files_written: int = 0

    cpu_seconds: float = 0.0

    wall_time_seconds: float = 0.0

    memory_before_mb: float = 0.0

    memory_after_mb: float = 0.0

    peak_memory_mb: float = 0.0

    start_time: datetime | None = None

    end_time: datetime | None = None

    metadata: dict[str, Any] = field(

        default_factory=dict

    )

    @property
    def elapsed(

        self

    ) -> float:

        if (

            self.start_time is None

            or

            self.end_time is None

        ):

            return 0.0

        return (

            self.end_time

            -

            self.start_time

        ).total_seconds()

    def summary(

        self

    ) -> dict[str, Any]:

        return {

            "stage":

                self.stage_name,

            "rows":

                self.rows_processed,

            "files_read":

                self.files_read,

            "files_written":

                self.files_written,

            "wall_time":

                self.wall_time_seconds,

            "memory_peak":

                self.peak_memory_mb,

        }


# ==========================================================
# PIPELINE ARTIFACT
# ==========================================================


@dataclass(slots=True)
class PipelineArtifact:
    """
    Artifact generated by a pipeline stage.
    """

    name: str

    artifact_type: ArtifactType

    path: Path

    producer: str

    created_at: datetime

    version: str = "1.0"

    checksum: str | None = None

    rows: int | None = None

    columns: int | None = None

    size_bytes: int | None = None

    metadata: dict[str, Any] = field(

        default_factory=dict

    )

    @property
    def exists(

        self

    ) -> bool:

        return self.path.exists()

    @property
    def size_mb(

        self

    ) -> float:

        if (

            self.size_bytes is None

        ):

            return 0.0

        return (

            self.size_bytes

            /

            1024

            /

            1024

        )

    def summary(

        self

    ) -> dict[str, Any]:

        return {

            "artifact":

                self.name,

            "type":

                self.artifact_type.name,

            "producer":

                self.producer,

            "path":

                str(

                    self.path

                ),

            "rows":

                self.rows,

            "columns":

                self.columns,

            "size_mb":

                round(

                    self.size_mb,

                    2,

                ),

        }
    
# ==========================================================
# PIPELINE METRICS
# ==========================================================


@dataclass(slots=True)
class PipelineMetrics:
    """
    Pipeline execution statistics.
    """

    pipeline_name: str = PIPELINE_NAME

    pipeline_version: str = PIPELINE_VERSION

    started_at: datetime | None = None

    finished_at: datetime | None = None

    total_stages: int = 0

    completed_stages: int = 0

    failed_stages: int = 0

    skipped_stages: int = 0

    total_artifacts: int = 0

    total_rows_processed: int = 0

    total_files_read: int = 0

    total_files_written: int = 0

    cpu_seconds: float = 0.0

    wall_seconds: float = 0.0

    metadata: dict[str, Any] = field(

        default_factory=dict

    )

    stage_metrics: dict[str, StageMetrics] = field(

        default_factory=dict

    )

    @property
    def duration(

        self

    ) -> float:

        if (

            self.started_at is None

            or

            self.finished_at is None

        ):

            return 0.0

        return (

            self.finished_at

            -

            self.started_at

        ).total_seconds()

    @property
    def success_rate(

        self

    ) -> float:

        if self.total_stages == 0:

            return 0.0

        return (

            self.completed_stages

            /

            self.total_stages

        ) * 100.0

    def add_stage_metrics(

        self,

        metrics: StageMetrics,

    ) -> None:

        self.stage_metrics[

            metrics.stage_name

        ] = metrics

        self.total_rows_processed += (

            metrics.rows_processed

        )

        self.total_files_read += (

            metrics.files_read

        )

        self.total_files_written += (

            metrics.files_written

        )

    def summary(

        self

    ) -> dict[str, Any]:

        return {

            "pipeline":

                self.pipeline_name,

            "version":

                self.pipeline_version,

            "duration_seconds":

                round(

                    self.duration,

                    2,

                ),

            "stages":

                self.total_stages,

            "completed":

                self.completed_stages,

            "failed":

                self.failed_stages,

            "skipped":

                self.skipped_stages,

            "success_rate":

                round(

                    self.success_rate,

                    2,

                ),

            "rows_processed":

                self.total_rows_processed,

            "artifacts":

                self.total_artifacts,

        }


# ==========================================================
# PIPELINE SUMMARY
# ==========================================================


@dataclass(slots=True)
class PipelineSummary:
    """
    Final pipeline execution summary.
    """

    state: PipelineState

    metrics: PipelineMetrics

    results: dict[str, StageResult]

    artifacts: dict[str, PipelineArtifact]

    metadata: dict[str, Any] = field(

        default_factory=dict

    )

    @property
    def successful(

        self

    ) -> bool:

        return (

            self.state

            ==

            PipelineState.COMPLETED

        )

    def summary(

        self

    ) -> dict[str, Any]:

        return {

            "state":

                self.state.name,

            "successful":

                self.successful,

            "metrics":

                self.metrics.summary(),

            "stages":

                len(

                    self.results

                ),

            "artifacts":

                len(

                    self.artifacts

                ),

        }


# ==========================================================
# RETRY POLICY
# ==========================================================


@dataclass(slots=True)
class RetryPolicy:
    """
    Retry configuration.
    """

    enabled: bool = True

    retries: int = DEFAULT_RETRIES

    delay_seconds: float = 3.0

    exponential_backoff: bool = True

    maximum_delay: float = 60.0

    retry_exceptions: tuple[type[Exception], ...] = (

        Exception,

    )

    def delay(

        self,

        attempt: int,

    ) -> float:

        if not self.exponential_backoff:

            return self.delay_seconds

        return min(

            self.delay_seconds

            *

            (

                2

                **

                max(

                    attempt - 1,

                    0,

                )

            ),

            self.maximum_delay,

        )


# ==========================================================
# PIPELINE CONFIGURATION
# ==========================================================


@dataclass(slots=True)
class PipelineConfiguration:
    """
    Runtime configuration.
    """

    workers: int = DEFAULT_WORKERS

    timeout_seconds: int = DEFAULT_TIMEOUT

    execution_mode: ExecutionMode = (

        ExecutionMode.DAG

    )

    retry_policy: RetryPolicy = field(

        default_factory=RetryPolicy

    )

    checkpoint_directory: Path = (

        CHECKPOINT_DIRECTORY

    )

    artifact_directory: Path = (

        ARTIFACT_DIRECTORY

    )

    report_directory: Path = (

        REPORT_DIRECTORY

    )

    logging_directory: Path = (

        LOG_DIRECTORY

    )

    validate_outputs: bool = True

    publish_reports: bool = True

    enable_checkpoints: bool = True

    enable_metrics: bool = True

    enable_parallel_execution: bool = True

    fail_fast: bool = False


# ==========================================================
# PIPELINE EXCEPTION
# ==========================================================


class PipelineException(

    RuntimeError

):
    """
    Base pipeline exception.
    """

    def __init__(

        self,

        message: str,

        stage: str | None = None,

    ) -> None:

        super().__init__(

            message

        )

        self.stage = stage

        self.timestamp = datetime.now(

            UTC

        )

    def __repr__(

        self

    ) -> str:

        return (

            f"{self.__class__.__name__}"

            "("

            f"stage={self.stage}, "

            f"message={self.args[0]!r}"

            ")"

        )

    __str__ = __repr__

# ==========================================================
# INSTITUTIONAL PIPELINE
# ==========================================================


class InstitutionalPipeline:
    """
    Enterprise workflow orchestrator.

    Coordinates every stage of the institutional
    investment workflow.
    """

    # ======================================================
    # INITIALIZATION
    # ======================================================

    def __init__(

        self,

        workflow: Iterable[str] | None = None,

        context: PipelineContext | None = None,

        configuration: PipelineConfiguration | None = None,

    ) -> None:

        logger.info(

            "Initializing Institutional Pipeline..."

        )

        self.configuration = (

            configuration

            or

            PipelineConfiguration()

        )

        self.context = (

            context

            or

            PipelineContext()

        )

        self.workflow = list(

            workflow

            or

            PIPELINE

        )

        self.state = PipelineState.CREATED

        self.metrics = PipelineMetrics(

            pipeline_name=PIPELINE_NAME,

            pipeline_version=PIPELINE_VERSION,

        )

        self.results: dict[

            str,

            StageResult

        ] = {}

        self.artifacts: dict[

            str,

            PipelineArtifact

        ] = {}

        self.stage_dependencies: dict[

            str,

            set[str]

        ] = defaultdict(

            set

        )

        self.reverse_dependencies: dict[

            str,

            set[str]

        ] = defaultdict(

            set

        )

        self.execution_queue: deque[str] = deque()

        self.completed: set[str] = set()

        self.failed: set[str] = set()

        self.running: set[str] = set()

        self.stage_registry: dict[

            str,

            Callable[..., Any]

        ] = {}

        self.metadata: dict[

            str,

            Any

        ] = {

            "pipeline_id": SESSION_ID,

            "hostname": HOSTNAME,

            "pid": PROCESS_ID,

            "version": PIPELINE_VERSION,

            "created_at": datetime.now(

                UTC

            ),

        }

        self._executor: ThreadPoolExecutor | None = None

        self._shutdown_requested = False

        logger.info(

            "Pipeline initialized."

        )

    # ======================================================
    # PROPERTIES
    # ======================================================

    @property
    def initialized(

        self

    ) -> bool:

        return (

            self.state

            !=

            PipelineState.CREATED

        )

    @property
    def completed_successfully(

        self

    ) -> bool:

        return (

            self.state

            ==

            PipelineState.COMPLETED

        )

    @property
    def total_stages(

        self

    ) -> int:

        return len(

            self.workflow

        )

    @property
    def completed_stages(

        self

    ) -> int:

        return len(

            self.completed

        )

    @property
    def failed_stages(

        self

    ) -> int:

        return len(

            self.failed

        )

    @property
    def pending_stages(

        self

    ) -> list[str]:

        return [

            stage

            for stage

            in self.workflow

            if stage

            not in self.completed

            and stage

            not in self.failed

        ]

    # ======================================================
    # REGISTRATION
    # ======================================================

    def register_stage(

        self,

        name: str,

        runner: Callable[..., Any],

    ) -> None:

        logger.info(

            "Registering stage %s",

            name,

        )

        self.stage_registry[

            name

        ] = runner

    def register_artifact(

        self,

        artifact: PipelineArtifact,

    ) -> None:

        self.artifacts[

            artifact.name

        ] = artifact

        self.metrics.total_artifacts += 1

    # ======================================================
    # LOOKUPS
    # ======================================================

    def has_stage(

        self,

        stage: str,

    ) -> bool:

        return (

            stage

            in self.stage_registry

        )

    def has_artifact(

        self,

        artifact: str,

    ) -> bool:

        return (

            artifact

            in self.artifacts

        )

    def artifact(

        self,

        name: str,

    ) -> PipelineArtifact | None:

        return self.artifacts.get(

            name

        )

    def result(

        self,

        stage: str,

    ) -> StageResult | None:

        return self.results.get(

            stage

        )

    # ======================================================
    # RESET
    # ======================================================

    def reset(

        self

    ) -> None:

        logger.info(

            "Resetting pipeline."

        )

        self.results.clear()

        self.artifacts.clear()

        self.completed.clear()

        self.failed.clear()

        self.running.clear()

        self.execution_queue.clear()

        self.metrics = PipelineMetrics(

            pipeline_name=PIPELINE_NAME,

            pipeline_version=PIPELINE_VERSION,

        )

        self.state = PipelineState.CREATED

    # ======================================================
    # INITIALIZATION
    # ======================================================

    def initialize(

        self,

    ) -> None:
        """
        Initialize the pipeline.
        """

        logger.info(

            "Initializing workflow."

        )

        self.state = PipelineState.INITIALIZING

        self.metrics.started_at = datetime.now(

            UTC

        )

        self._create_directories()

        self._register_workflow()

        self._build_dependency_graph()

        self._validate_workflow()

        self._prepare_execution_queue()

        self.state = PipelineState.READY

        logger.info(

            "Pipeline ready."

        )

    # ======================================================
    # DIRECTORY INITIALIZATION
    # ======================================================

    def _create_directories(

        self,

    ) -> None:

        directories = [

            self.configuration.artifact_directory,

            self.configuration.report_directory,

            self.configuration.checkpoint_directory,

            self.configuration.logging_directory,

        ]

        for directory in directories:

            directory.mkdir(

                parents=True,

                exist_ok=True,

            )

    # ======================================================
    # WORKFLOW REGISTRATION
    # ======================================================

    def _register_workflow(

        self,

    ) -> None:

        logger.info(

            "Registering workflow."

        )

        self.metrics.total_stages = len(

            self.workflow

        )

        for stage in self.workflow:

            if stage not in self.stage_registry:

                logger.debug(

                    "Workflow stage detected: %s",

                    stage,

                )

    # ======================================================
    # DEPENDENCY GRAPH
    # ======================================================

    def _build_dependency_graph(

        self,

    ) -> None:
        """
        Override in subclasses if
        explicit dependencies exist.
        """

        self.stage_dependencies.clear()

        self.reverse_dependencies.clear()

        previous = None

        for stage in self.workflow:

            if previous is not None:

                self.stage_dependencies[

                    stage

                ].add(

                    previous

                )

                self.reverse_dependencies[

                    previous

                ].add(

                    stage

                )

            previous = stage

    # ======================================================
    # WORKFLOW VALIDATION
    # ======================================================

    def _validate_workflow(

        self,

    ) -> None:

        if not self.workflow:

            raise PipelineException(

                "Workflow is empty."

            )

        duplicates = {

            stage

            for stage in self.workflow

            if self.workflow.count(

                stage

            ) > 1

        }

        if duplicates:

            raise PipelineException(

                "Duplicate stages detected: "

                + ", ".join(

                    sorted(

                        duplicates

                    )

                )

            )

    # ======================================================
    # EXECUTION QUEUE
    # ======================================================

    def _prepare_execution_queue(

        self,

    ) -> None:

        self.execution_queue.clear()

        for stage in self.workflow:

            self.execution_queue.append(

                stage

            )

        logger.info(

            "Execution queue prepared with %d stages.",

            len(

                self.execution_queue

            ),

        )

# ======================================================
# EXECUTION
# ======================================================

def execute(self) -> PipelineSummary:
    """
    Execute the configured workflow.
    """

    if self.state == PipelineState.CREATED:
        self.initialize()

    logger.info("Starting pipeline execution.")

    self.state = PipelineState.RUNNING

    executor = PipelineExecutor(
        pipeline=self,
    )

    executor.execute()

    self.metrics.finished_at = datetime.now(UTC)

    if self.failed:
        self.state = PipelineState.FAILED
    else:
        self.state = PipelineState.COMPLETED

    publisher = PipelinePublisher(
        pipeline=self,
    )

    publisher.publish()

    return PipelineSummary(
        state=self.state,
        metrics=self.metrics,
        results=self.results,
        artifacts=self.artifacts,
        metadata=self.metadata,
    )


# ======================================================
# SHUTDOWN
# ======================================================

def shutdown(self) -> None:
    """
    Gracefully shutdown the pipeline.
    """

    logger.info("Pipeline shutdown requested.")

    self._shutdown_requested = True

    if self._executor is not None:
        self._executor.shutdown(
            wait=True,
            cancel_futures=False,
        )

    self.state = PipelineState.SHUTDOWN


# ======================================================
# CONTEXT MANAGER
# ======================================================

def __enter__(self):

    self.initialize()

    return self


def __exit__(
    self,
    exc_type,
    exc,
    traceback,
):

    self.shutdown()