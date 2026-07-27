"""
=========================================================
TIMER UTILITY
=========================================================

Purpose:
Reusable execution timer for engines, pipelines,
and orchestration.

=========================================================
"""

from __future__ import annotations

from time import perf_counter


class Timer:
    """
    High-resolution execution timer.

    Example
    -------
    with Timer() as timer:
        run_engine()

    print(timer.elapsed)
    """

    def __init__(self) -> None:

        self._start = 0.0

        self._end = 0.0

    # =====================================================
    # CONTEXT MANAGER
    # =====================================================

    def __enter__(self) -> Timer:

        self.start()

        return self

    def __exit__(
        self,
        exc_type,
        exc_val,
        exc_tb,
    ) -> None:

        self.stop()

    # =====================================================
    # CONTROL
    # =====================================================

    def start(self) -> None:

        self._start = perf_counter()

    def stop(self) -> None:

        self._end = perf_counter()

    # =====================================================
    # METRICS
    # =====================================================

    @property
    def elapsed(self) -> float:

        if self._end == 0:
            return perf_counter() - self._start

        return self._end - self._start

    @property
    def elapsed_ms(self) -> float:

        return round(
            self.elapsed * 1000,
            2,
        )

    @property
    def elapsed_seconds(self) -> float:

        return round(
            self.elapsed,
            2,
        )

    # =====================================================
    # STRING
    # =====================================================

    def __str__(
        self,
    ) -> str:

        return f"{self.elapsed:.2f}s"
