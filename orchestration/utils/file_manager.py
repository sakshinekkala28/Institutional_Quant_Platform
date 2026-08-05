"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Runtime Utilities

Platform runtime utilities.

Responsibilities
----------------
• Runtime information
• Process information
• Environment information
• Timing utilities
• Platform metadata

=========================================================
"""

from __future__ import annotations

import os
import platform
import socket
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from time import perf_counter
from typing import Any

# ==========================================================
# RUNTIME INFO
# ==========================================================


@dataclass(slots=True, frozen=True)
class RuntimeInfo:
    """
    Runtime environment information.
    """

    hostname: str

    platform: str

    python_version: str

    executable: str

    process_id: int

    working_directory: str

    cpu_count: int

    started_at: datetime


# ==========================================================
# TIMER
# ==========================================================


class Timer:
    """
    High precision timer.
    """

    def __init__(self) -> None:

        self._start = perf_counter()

    # -----------------------------------------------------

    def reset(self) -> None:

        self._start = perf_counter()

    # -----------------------------------------------------

    @property
    def elapsed(self) -> float:

        return perf_counter() - self._start

    # -----------------------------------------------------

    def __repr__(self) -> str:

        return f"{self.__class__.__name__}(elapsed={self.elapsed:.4f}s)"


# ==========================================================
# RUNTIME
# ==========================================================


class Runtime:
    """
    Platform runtime helper.
    """

    _START_TIME = datetime.utcnow()

    _TIMER = Timer()

    # =====================================================
    # INFORMATION
    # =====================================================

    @classmethod
    def info(cls) -> RuntimeInfo:

        return RuntimeInfo(
            hostname=socket.gethostname(),
            platform=platform.platform(),
            python_version=sys.version.split()[0],
            executable=sys.executable,
            process_id=os.getpid(),
            working_directory=str(Path.cwd()),
            cpu_count=os.cpu_count() or 1,
            started_at=cls._START_TIME,
        )

    # =====================================================
    # TIMING
    # =====================================================

    @classmethod
    def uptime(cls) -> float:

        return cls._TIMER.elapsed

    # -----------------------------------------------------

    @classmethod
    def timestamp(cls) -> datetime:

        return datetime.utcnow()

    # -----------------------------------------------------

    @classmethod
    def iso_timestamp(cls) -> str:

        return cls.timestamp().isoformat()

    # =====================================================
    # EXPORT
    # =====================================================

    @classmethod
    def metadata(cls) -> dict[str, Any]:

        info = cls.info()

        return {
            "hostname": info.hostname,
            "platform": info.platform,
            "python_version": info.python_version,
            "process_id": info.process_id,
            "working_directory": info.working_directory,
            "cpu_count": info.cpu_count,
            "started_at": info.started_at.isoformat(),
            "uptime_seconds": round(
                cls.uptime(),
                3,
            ),
        }

    # =====================================================
    # DUNDER
    # =====================================================

    def __repr__(self) -> str:

        return f"{self.__class__.__name__}(uptime={self.uptime():.2f}s)"
