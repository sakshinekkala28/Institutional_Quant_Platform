from __future__ import annotations

import time
from contextlib import contextmanager

from opentelemetry import trace
from prometheus_client import Counter
from prometheus_client import Histogram

PIPELINE_RUNS = Counter(
    "pipeline_runs_total",
    "Total Pipeline Runs",
    ["engine"]
)

PIPELINE_FAILURES = Counter(
    "pipeline_failures_total",
    "Pipeline Failures",
    ["engine"]
)

PIPELINE_DURATION = Histogram(
    "pipeline_duration_seconds",
    "Pipeline Runtime",
    ["engine"]
)

tracer = trace.get_tracer(
    "institutional_quant_platform"
)


class TelemetryManager:

    @staticmethod
    @contextmanager
    def monitor(engine_name: str):

        start = time.time()

        PIPELINE_RUNS.labels(
            engine=engine_name
        ).inc()

        with tracer.start_as_current_span(
            engine_name
        ):

            try:

                yield

            except Exception:

                PIPELINE_FAILURES.labels(
                    engine=engine_name
                ).inc()

                raise

            finally:

                duration = (
                    time.time() - start
                )

                PIPELINE_DURATION.labels(
                    engine=engine_name
                ).observe(duration)