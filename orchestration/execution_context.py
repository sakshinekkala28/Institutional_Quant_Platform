"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Execution Context

Shared runtime state for the orchestration framework.

Responsibilities
----------------
• Shared metadata
• Engine outputs
• Runtime variables
• Generated artifacts
• Execution cache
• Runtime statistics

The ExecutionContext is shared between every engine,
executor and orchestrator.

=========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import json
from pathlib import Path
from threading import RLock
from typing import Any

# =========================================================
# EXECUTION CONTEXT
# =========================================================


@dataclass(slots=True)
class ExecutionContext:
    """
    Shared execution context.
    """

    # -----------------------------------------------------
    # Runtime Metadata
    # -----------------------------------------------------

    metadata: dict[
        str,
        Any,
    ] = field(default_factory=dict)

    # -----------------------------------------------------
    # Engine Outputs
    # -----------------------------------------------------

    outputs: dict[
        str,
        Any,
    ] = field(default_factory=dict)

    # -----------------------------------------------------
    # Runtime Variables
    # -----------------------------------------------------

    variables: dict[
        str,
        Any,
    ] = field(default_factory=dict)

    # -----------------------------------------------------
    # Execution Cache
    # -----------------------------------------------------

    cache: dict[
        str,
        Any,
    ] = field(default_factory=dict)

    # -----------------------------------------------------
    # Artifacts
    # -----------------------------------------------------

    artifacts: set[str,] = field(default_factory=set)

    # -----------------------------------------------------
    # Generated Files
    # -----------------------------------------------------

    files: list[Path,] = field(default_factory=list)

    # -----------------------------------------------------
    # Warnings
    # -----------------------------------------------------

    warnings: list[str,] = field(default_factory=list)

    # -----------------------------------------------------
    # Errors
    # -----------------------------------------------------

    errors: list[str,] = field(default_factory=list)

    # -----------------------------------------------------
    # Runtime
    # -----------------------------------------------------

    started_at: datetime = field(default_factory=datetime.utcnow)

    finished_at: datetime | None = None

    # -----------------------------------------------------
    # Synchronization
    # -----------------------------------------------------

    _lock: RLock = field(
        default_factory=RLock,
        repr=False,
        compare=False,
    )

    # =====================================================
    # PROPERTIES
    # =====================================================

    @property
    def runtime_seconds(
        self,
    ) -> float:

        if self.finished_at is None:
            return (datetime.utcnow() - self.started_at).total_seconds()

        return (self.finished_at - self.started_at).total_seconds()

    # -----------------------------------------------------

    @property
    def artifact_count(
        self,
    ) -> int:

        return len(self.artifacts)

    # -----------------------------------------------------

    @property
    def output_count(
        self,
    ) -> int:

        return len(self.outputs)

    # -----------------------------------------------------

    @property
    def warning_count(
        self,
    ) -> int:

        return len(self.warnings)

    # -----------------------------------------------------

    @property
    def error_count(
        self,
    ) -> int:

        return len(self.errors)

    # =====================================================
    # RUNTIME
    # =====================================================

    @property
    def finished(
        self,
    ) -> bool:

        return self.finished_at is not None

    # -----------------------------------------------------

    def finish(
        self,
    ) -> None:

        self.finished_at = datetime.utcnow()

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(
        self,
    ) -> dict[str, Any]:

        return {
            "runtime": round(
                self.runtime_seconds,
                3,
            ),
            "outputs": self.output_count,
            "artifacts": self.artifact_count,
            "warnings": self.warning_count,
            "errors": self.error_count,
        }

    # =====================================================
    # DUNDER
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}("
            f"outputs={self.output_count}, "
            f"artifacts={self.artifact_count})"
        )

    # =====================================================
    # METADATA
    # =====================================================

    def set_metadata(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Store metadata.
        """

        with self._lock:
            self.metadata[key] = value

    # -----------------------------------------------------

    def get_metadata(
        self,
        key: str,
        default: Any | None = None,
    ) -> Any:
        """
        Retrieve metadata.
        """

        with self._lock:
            return self.metadata.get(
                key,
                default,
            )

    # -----------------------------------------------------

    def metadata_exists(
        self,
        key: str,
    ) -> bool:

        with self._lock:
            return key in self.metadata

    # =====================================================
    # VARIABLES
    # =====================================================

    def set_variable(
        self,
        key: str,
        value: Any,
    ) -> None:
        """
        Store runtime variable.
        """

        with self._lock:
            self.variables[key] = value

    # -----------------------------------------------------

    def get_variable(
        self,
        key: str,
        default: Any | None = None,
    ) -> Any:
        """
        Retrieve runtime variable.
        """

        with self._lock:
            return self.variables.get(
                key,
                default,
            )

    # -----------------------------------------------------

    def remove_variable(
        self,
        key: str,
    ) -> None:

        with self._lock:
            self.variables.pop(
                key,
                None,
            )

    # =====================================================
    # OUTPUTS
    # =====================================================

    def set_output(
        self,
        engine: str,
        output: Any,
    ) -> None:
        """
        Register engine output.
        """

        with self._lock:
            self.outputs[engine] = output

    # -----------------------------------------------------

    def get_output(
        self,
        engine: str,
        default: Any | None = None,
    ) -> Any:
        """
        Retrieve engine output.
        """

        with self._lock:
            return self.outputs.get(
                engine,
                default,
            )

    # -----------------------------------------------------

    def output_exists(
        self,
        engine: str,
    ) -> bool:

        with self._lock:
            return engine in self.outputs

    # =====================================================
    # CACHE
    # =====================================================

    def cache_set(
        self,
        key: str,
        value: Any,
    ) -> None:

        with self._lock:
            self.cache[key] = value

    # -----------------------------------------------------

    def cache_get(
        self,
        key: str,
        default: Any | None = None,
    ) -> Any:

        with self._lock:
            return self.cache.get(
                key,
                default,
            )

    # -----------------------------------------------------

    def cache_remove(
        self,
        key: str,
    ) -> None:

        with self._lock:
            self.cache.pop(
                key,
                None,
            )

    # -----------------------------------------------------

    def clear_cache(
        self,
    ) -> None:

        with self._lock:
            self.cache.clear()

    # =====================================================
    # ARTIFACTS
    # =====================================================

    def add_artifact(
        self,
        artifact: str,
    ) -> None:

        with self._lock:
            self.artifacts.add(artifact)

    # -----------------------------------------------------

    def has_artifact(
        self,
        artifact: str,
    ) -> bool:

        with self._lock:
            return artifact in self.artifacts

    # -----------------------------------------------------

    def remove_artifact(
        self,
        artifact: str,
    ) -> None:

        with self._lock:
            self.artifacts.discard(artifact)

    # =====================================================
    # FILES
    # =====================================================

    def add_file(
        self,
        path: Path,
    ) -> None:

        with self._lock:
            self.files.append(path)

    # -----------------------------------------------------

    def remove_file(
        self,
        path: Path,
    ) -> None:

        with self._lock:
            if path in self.files:
                self.files.remove(path)

    # =====================================================
    # WARNINGS
    # =====================================================

    def add_warning(
        self,
        warning: str,
    ) -> None:

        with self._lock:
            self.warnings.append(warning)

    # -----------------------------------------------------

    def add_error(
        self,
        error: str,
    ) -> None:

        with self._lock:
            self.errors.append(error)

    # -----------------------------------------------------

    def clear_messages(
        self,
    ) -> None:

        with self._lock:
            self.warnings.clear()

            self.errors.clear()

    # =====================================================
    # HELPERS
    # =====================================================

    def exists(
        self,
        key: str,
    ) -> bool:
        """
        Search every namespace.
        """

        with self._lock:
            return any(
                key in container
                for container in (
                    self.metadata,
                    self.outputs,
                    self.variables,
                    self.cache,
                )
            )

    # -----------------------------------------------------

    def remove(
        self,
        key: str,
    ) -> None:
        """
        Remove key everywhere.
        """

        with self._lock:
            self.metadata.pop(
                key,
                None,
            )

            self.outputs.pop(
                key,
                None,
            )

            self.variables.pop(
                key,
                None,
            )

            self.cache.pop(
                key,
                None,
            )

    # =====================================================
    # SNAPSHOT
    # =====================================================

    def snapshot(
        self,
    ) -> dict[str, Any]:
        """
        Create an immutable snapshot of the current
        execution context.

        Returns
        -------
        Dict[str, Any]
        """

        with self._lock:
            return {
                "metadata": dict(self.metadata),
                "outputs": dict(self.outputs),
                "variables": dict(self.variables),
                "cache": dict(self.cache),
                "artifacts": sorted(self.artifacts),
                "files": [str(path) for path in self.files],
                "warnings": list(self.warnings),
                "errors": list(self.errors),
                "started_at": self.started_at.isoformat(),
                "finished_at": (
                    self.finished_at.isoformat() if self.finished_at else None
                ),
            }

    # =====================================================
    # CLONE
    # =====================================================

    def clone(
        self,
    ) -> ExecutionContext:
        """
        Deep copy of the execution context.
        """

        clone = ExecutionContext()

        with self._lock:
            clone.metadata.update(self.metadata)

            clone.outputs.update(self.outputs)

            clone.variables.update(self.variables)

            clone.cache.update(self.cache)

            clone.artifacts.update(self.artifacts)

            clone.files.extend(self.files)

            clone.warnings.extend(self.warnings)

            clone.errors.extend(self.errors)

            clone.started_at = self.started_at

            clone.finished_at = self.finished_at

        return clone

    # =====================================================
    # MERGE
    # =====================================================

    def merge(
        self,
        other: ExecutionContext,
    ) -> None:
        """
        Merge another execution context.
        """

        with self._lock:
            self.metadata.update(other.metadata)

            self.outputs.update(other.outputs)

            self.variables.update(other.variables)

            self.cache.update(other.cache)

            self.artifacts.update(other.artifacts)

            self.files.extend(other.files)

            self.warnings.extend(other.warnings)

            self.errors.extend(other.errors)

    # =====================================================
    # EXPORT
    # =====================================================

    def to_dict(
        self,
    ) -> dict[str, Any]:
        """
        Export execution context.
        """

        return self.snapshot()

    # -----------------------------------------------------

    def to_json(
        self,
        *,
        indent: int = 4,
    ) -> str:
        """
        JSON serialization.
        """

        return json.dumps(
            self.to_dict(),
            indent=indent,
            default=str,
        )

    # =====================================================
    # RESTORE
    # =====================================================

    @classmethod
    def from_dict(
        cls,
        data: dict[str, Any],
    ) -> ExecutionContext:
        """
        Restore execution context.
        """

        context = cls()

        context.metadata.update(
            data.get(
                "metadata",
                {},
            )
        )

        context.outputs.update(
            data.get(
                "outputs",
                {},
            )
        )

        context.variables.update(
            data.get(
                "variables",
                {},
            )
        )

        context.cache.update(
            data.get(
                "cache",
                {},
            )
        )

        context.artifacts.update(
            data.get(
                "artifacts",
                [],
            )
        )

        context.files.extend(
            Path(path)
            for path in data.get(
                "files",
                [],
            )
        )

        context.warnings.extend(
            data.get(
                "warnings",
                [],
            )
        )

        context.errors.extend(
            data.get(
                "errors",
                [],
            )
        )

        return context

    # =====================================================
    # STATISTICS
    # =====================================================

    def statistics(
        self,
    ) -> dict[str, int]:
        """
        Execution statistics.
        """

        return {
            "metadata": len(self.metadata),
            "variables": len(self.variables),
            "outputs": len(self.outputs),
            "cache": len(self.cache),
            "artifacts": len(self.artifacts),
            "files": len(self.files),
            "warnings": len(self.warnings),
            "errors": len(self.errors),
        }

    # =====================================================
    # VALIDATION
    # =====================================================

    def validate(
        self,
    ) -> bool:
        """
        Validate execution context.
        """

        return self.started_at is not None

    # =====================================================
    # CHECKPOINT
    # =====================================================

    def checkpoint(
        self,
    ) -> dict[str, Any]:
        """
        Create a checkpoint of the current execution state.
        """

        return self.snapshot()

    # -----------------------------------------------------

    def restore(
        self,
        checkpoint: dict[str, Any],
    ) -> None:
        """
        Restore execution state from a checkpoint.
        """

        restored = self.from_dict(checkpoint)

        with self._lock:
            self.metadata = restored.metadata

            self.outputs = restored.outputs

            self.variables = restored.variables

            self.cache = restored.cache

            self.artifacts = restored.artifacts

            self.files = restored.files

            self.warnings = restored.warnings

            self.errors = restored.errors

            self.started_at = restored.started_at

            self.finished_at = restored.finished_at

    # =====================================================
    # PERSISTENCE
    # =====================================================

    def save(
        self,
        path: Path,
    ) -> None:
        """
        Save execution context to disk.
        """

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with path.open(
            "w",
            encoding="utf-8",
        ) as fp:
            json.dump(
                self.to_dict(),
                fp,
                indent=4,
                default=str,
            )

    # -----------------------------------------------------

    @classmethod
    def load(
        cls,
        path: Path,
    ) -> ExecutionContext:
        """
        Load execution context.
        """

        with path.open(
            "r",
            encoding="utf-8",
        ) as fp:
            data = json.load(fp)

        return cls.from_dict(data)

    # =====================================================
    # CLEANUP
    # =====================================================

    def cleanup(
        self,
    ) -> None:
        """
        Free temporary runtime memory.
        """

        with self._lock:
            self.cache.clear()

            self.variables.clear()

    # -----------------------------------------------------

    def clear_outputs(
        self,
    ) -> None:
        """
        Remove all outputs.
        """

        with self._lock:
            self.outputs.clear()

    # =====================================================
    # DIFF
    # =====================================================

    def diff(
        self,
        other: ExecutionContext,
    ) -> dict[str, Any]:
        """
        Compare two execution contexts.
        """

        return {
            "metadata": set(self.metadata) ^ set(other.metadata),
            "outputs": set(self.outputs) ^ set(other.outputs),
            "variables": set(self.variables) ^ set(other.variables),
            "artifacts": self.artifacts ^ other.artifacts,
        }

    # =====================================================
    # HASH
    # =====================================================

    def checksum(
        self,
    ) -> str:
        """
        Stable checksum of the execution state.
        """

        return hashlib.sha256(self.to_json().encode()).hexdigest()

    # =====================================================
    # REPORT
    # =====================================================

    def report(
        self,
    ) -> dict[str, Any]:
        """
        Comprehensive execution context report.
        """

        return {
            "summary": self.summary(),
            "statistics": self.statistics(),
            "runtime": round(
                self.runtime_seconds,
                3,
            ),
            "finished": self.finished,
            "checksum": self.checksum(),
        }

    # =====================================================
    # CONTAINER
    # =====================================================

    def __len__(
        self,
    ) -> int:

        return (
            len(self.metadata)
            + len(self.outputs)
            + len(self.variables)
            + len(self.cache)
        )

    # -----------------------------------------------------

    def __contains__(
        self,
        key: str,
    ) -> bool:

        return self.exists(key)

    # -----------------------------------------------------

    def __iter__(
        self,
    ):

        return iter(self.metadata.items())

    # -----------------------------------------------------

    def __str__(
        self,
    ) -> str:

        return (
            f"ExecutionContext("
            f"runtime={self.runtime_seconds:.2f}s, "
            f"outputs={self.output_count}, "
            f"artifacts={self.artifact_count})"
        )
