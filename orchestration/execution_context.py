"""
Institutional Quant Platform
============================

Execution Context

Shared runtime context passed to every engine.

Responsibilities
----------------
- Pipeline metadata
- Runtime configuration
- Shared logger
- Data paths
- Runtime cache
- Shared objects

Author: Institutional Quant Platform
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict
import logging
import uuid


@dataclass
class ExecutionContext:
    """
    Shared runtime object passed to every engine.
    """

    # ------------------------------------------------------------------
    # Pipeline Information
    # ------------------------------------------------------------------

    pipeline_name: str = "full"

    pipeline_id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    started_at: datetime = field(
        default_factory=datetime.utcnow
    )

    market_date: str = ""

    # ------------------------------------------------------------------
    # Paths
    # ------------------------------------------------------------------

    project_root: Path = field(
        default_factory=lambda: Path.cwd()
    )

    data_dir: Path = field(init=False)

    raw_dir: Path = field(init=False)

    processed_dir: Path = field(init=False)

    logs_dir: Path = field(init=False)

    live_dir: Path = field(init=False)

    performance_dir: Path = field(init=False)

    risk_dir: Path = field(init=False)

    portfolio_dir: Path = field(init=False)

    execution_dir: Path = field(init=False)

    monitoring_dir: Path = field(init=False)

    # ------------------------------------------------------------------
    # Runtime
    # ------------------------------------------------------------------

    logger: logging.Logger = field(init=False)

    configuration: Dict[str, Any] = field(
        default_factory=dict
    )

    cache: Dict[str, Any] = field(
        default_factory=dict
    )

    shared: Dict[str, Any] = field(
        default_factory=dict
    )

    metrics: Dict[str, Any] = field(
        default_factory=dict
    )

    # ------------------------------------------------------------------

    def __post_init__(self):

        data_root = self.project_root / "data"

        self.data_dir = data_root

        self.raw_dir = data_root / "raw"

        self.processed_dir = data_root / "processed"

        self.logs_dir = data_root / "logs"

        self.live_dir = data_root / "live"

        self.performance_dir = data_root / "performance"

        self.risk_dir = data_root / "risk"

        self.portfolio_dir = data_root / "portfolios"

        self.execution_dir = data_root / "execution"

        self.monitoring_dir = data_root / "monitoring"

        self.logger = logging.getLogger("Pipeline")

    # ------------------------------------------------------------------

    def ensure_directories(self):

        directories = [

            self.data_dir,

            self.raw_dir,

            self.processed_dir,

            self.logs_dir,

            self.live_dir,

            self.performance_dir,

            self.risk_dir,

            self.portfolio_dir,

            self.execution_dir,

            self.monitoring_dir,

        ]

        for directory in directories:

            directory.mkdir(
                parents=True,
                exist_ok=True,
            )

    # ------------------------------------------------------------------

    def set(self, key: str, value: Any):

        self.shared[key] = value

    # ------------------------------------------------------------------

    def get(self, key: str, default=None):

        return self.shared.get(key, default)

    # ------------------------------------------------------------------

    def cache_set(self, key: str, value: Any):

        self.cache[key] = value

    # ------------------------------------------------------------------

    def cache_get(self, key: str, default=None):

        return self.cache.get(key, default)

    # ------------------------------------------------------------------

    def add_metric(
        self,
        key: str,
        value: Any,
    ):

        self.metrics[key] = value

    # ------------------------------------------------------------------

    def summary(self):

        return {

            "pipeline_name": self.pipeline_name,

            "pipeline_id": self.pipeline_id,

            "started_at": self.started_at.isoformat(),

            "project_root": str(self.project_root),

            "data_directory": str(self.data_dir),

            "cache_objects": len(self.cache),

            "shared_objects": len(self.shared),

            "metrics": len(self.metrics),

        }

    # ------------------------------------------------------------------

    def __repr__(self):

        return (

            f"ExecutionContext("

            f"pipeline='{self.pipeline_name}', "

            f"id='{self.pipeline_id[:8]}')"

        )