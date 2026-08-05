"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Scheduler

Coordinates scheduled execution of the platform.

Responsibilities
----------------
• Job registration
• Job management
• One-time execution
• Scheduled execution
• Job enable / disable
• Orchestrator integration

The Scheduler NEVER executes engines directly.
It delegates execution to MasterOrchestrator.

=========================================================
"""

from __future__ import annotations

from contextlib import suppress
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import threading
import time

from orchestration.master_orchestrator import MasterOrchestrator
from orchestration.models.master_result import MasterResult

# =========================================================
# SCHEDULED JOB
# =========================================================


@dataclass(slots=True)
class ScheduledJob:
    """
    Scheduled platform execution.
    """

    name: str

    frequency: str

    enabled: bool = True

    executor: str = "sequential"

    interval_seconds: int = 0

    pipeline: str = "default"

    metadata: dict[str, str] = field(default_factory=dict)

    created_at: datetime = field(default_factory=datetime.utcnow)

    last_run: datetime | None = None

    next_run: datetime | None = None

    run_count: int = 0

    failure_count: int = 0

    def mark_executed(self) -> None:

        self.last_run = datetime.utcnow()

        self.run_count += 1

        if self.interval_seconds > 0:
            self.next_run = self.last_run + timedelta(seconds=self.interval_seconds)

    def mark_failed(self) -> None:

        self.failure_count += 1


# =========================================================
# JOB REGISTRY
# =========================================================


class JobRegistry:
    """
    Stores scheduled jobs.
    """

    def __init__(self) -> None:

        self._jobs: dict[
            str,
            ScheduledJob,
        ] = {}

    # -----------------------------------------------------

    def register(
        self,
        job: ScheduledJob,
    ) -> None:

        if job.name in self._jobs:
            raise ValueError(f"Job '{job.name}' already exists.")

        self._jobs[job.name] = job

    # -----------------------------------------------------

    def unregister(
        self,
        name: str,
    ) -> None:

        self._jobs.pop(
            name,
            None,
        )

    # -----------------------------------------------------

    def get(
        self,
        name: str,
    ) -> ScheduledJob:

        return self._jobs[name]

    # -----------------------------------------------------

    def jobs(
        self,
    ) -> list[ScheduledJob]:

        return list(self._jobs.values())

    # -----------------------------------------------------

    def active_jobs(
        self,
    ) -> list[ScheduledJob]:

        return [job for job in self._jobs.values() if job.enabled]

    # -----------------------------------------------------

    def enable(
        self,
        name: str,
    ) -> None:

        self.get(name).enabled = True

    # -----------------------------------------------------

    def disable(
        self,
        name: str,
    ) -> None:

        self.get(name).enabled = False

    # -----------------------------------------------------

    def __len__(
        self,
    ) -> int:

        return len(self._jobs)

    # -----------------------------------------------------

    def __contains__(
        self,
        name: str,
    ) -> bool:

        return name in self._jobs


# =========================================================
# SCHEDULER
# =========================================================


class Scheduler:
    """
    Institutional platform scheduler.
    """

    def __init__(self) -> None:

        self.registry = JobRegistry()

        self._thread = None

        self._running = False

        self._last_result: MasterResult | None = None

        self._last_run: datetime | None = None

    # =====================================================
    # DEFAULT JOBS
    # =====================================================

    def register_default_jobs(
        self,
    ) -> None:

        self.registry.register(
            ScheduledJob(
                name="daily",
                frequency="DAILY",
                interval_seconds=86400,
            )
        )

        self.registry.register(
            ScheduledJob(
                name="weekly",
                frequency="WEEKLY",
                interval_seconds=604800,
            )
        )

        self.registry.register(
            ScheduledJob(
                name="monthly",
                frequency="MONTHLY",
            )
        )

    # =====================================================
    # JOB EXECUTION
    # =====================================================

    def run_job(
        self,
        name: str,
    ) -> MasterResult:
        """
        Execute a single scheduled job.
        """

        job = self.registry.get(name)

        if not job.enabled:
            raise RuntimeError(f"Job '{name}' is disabled.")

        orchestrator = MasterOrchestrator(
            executor=job.executor,
        )

        try:
            result = orchestrator.run()

            job.mark_executed()

            self._last_run = job.last_run

            self._last_result = result

            return result

        except Exception:
            job.mark_failed()

            raise

    # =====================================================
    # RUN ALL JOBS
    # =====================================================

    def run_all(
        self,
    ) -> list[MasterResult]:
        """
        Execute all enabled jobs.
        """

        results: list[MasterResult] = []

        for job in self.registry.active_jobs():
            results.append(
                self.run_job(
                    job.name,
                )
            )

        return results

    # =====================================================
    # BACKGROUND LOOP
    # =====================================================

    def _worker(
        self,
    ) -> None:
        """
        Background scheduler loop.
        """

        while self._running:
            now = datetime.utcnow()

            for job in self.registry.active_jobs():
                if job.next_run is None or now >= job.next_run:
                    with suppress(Exception):
                        self.run_job(job.name)

            time.sleep(1)

    # =====================================================
    # START
    # =====================================================

    def start(
        self,
    ) -> None:
        """
        Start background scheduling.
        """

        if self._running:
            return

        self._running = True

        self._thread = threading.Thread(
            target=self._worker,
            daemon=True,
            name="PlatformScheduler",
        )

        self._thread.start()

    # =====================================================
    # STOP
    # =====================================================

    def stop(
        self,
    ) -> None:
        """
        Stop scheduler.
        """

        self._running = False

        if self._thread is not None:
            self._thread.join()

            self._thread = None

    # =====================================================
    # STATUS
    # =====================================================

    @property
    def running(
        self,
    ) -> bool:

        return self._running

    # -----------------------------------------------------

    @property
    def last_result(
        self,
    ) -> MasterResult | None:

        return self._last_result

    # -----------------------------------------------------

    @property
    def last_run(
        self,
    ) -> datetime | None:

        return self._last_run

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(
        self,
    ) -> dict:
        """
        Scheduler summary.
        """

        return {
            "running": self.running,
            "registered_jobs": len(
                self.registry,
            ),
            "active_jobs": len(
                self.registry.active_jobs(),
            ),
            "last_run": (self.last_run.isoformat() if self.last_run else None),
            "last_status": (
                self.last_result.status.value if self.last_result else "NOT_RUN"
            ),
        }

    # =====================================================
    # DUNDER
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}("
            f"jobs={len(self.registry)}, "
            f"running={self.running})"
        )
