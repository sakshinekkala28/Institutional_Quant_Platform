"""
====================================================================
Institutional Quant Platform

Base Loader

Author : Institutional Quant Platform
Purpose:
    Common Data Loading Framework

Responsibilities
----------------
• File Resolution
• File Validation
• Metadata Generation
• Logging
• Performance Timing
• Exception Translation
• Extension Hooks

All concrete loaders inherit from this class.

Examples

CSVLoader
ParquetLoader
ExcelLoader
JsonLoader
DuckDBLoader

====================================================================
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from dataclasses import dataclass
from dataclasses import field

from datetime import datetime
from datetime import UTC

from pathlib import Path

from time import perf_counter

from typing import Any
from typing import Generic
from typing import TypeVar
from typing import final

import hashlib

import pandas as pd

from core.settings import settings

from core.logging_manager import LoggingManager

from core.exceptions import DataLoadError
from core.exceptions import EmptyDatasetError
from core.exceptions import MissingColumnError

# ==========================================================
# GENERICS
# ==========================================================

T = TypeVar(
    "T"
)

# ==========================================================
# LOGGER
# ==========================================================

logger = LoggingManager.get_logger(
    __name__
)

# ==========================================================
# LOAD METADATA
# ==========================================================

@dataclass(slots=True)
class LoadMetadata:

    source: Path

    loader_name: str

    loaded_at: datetime

    elapsed_ms: float

    rows: int

    columns: int

    memory_usage_bytes: int

    file_size_bytes: int

    checksum: str

    dtypes: dict[str, str]

    column_names: list[str] = field(

        default_factory=list

    )

# ==========================================================
# LOAD RESULT
# ==========================================================


@dataclass(slots=True)
class LoadResult(Generic[T]):

    data: T

    metadata: LoadMetadata

# ==========================================================
# BASE LOADER
# ==========================================================


class BaseLoader(ABC):

    """
    Abstract Institutional Loader

    Every concrete loader inherits this class.

    Examples

        CSVLoader

        ParquetLoader

        ExcelLoader

        DuckDBLoader
    """

    def __init__(

        self,

        source: str | Path

    ) -> None:

        source_path = Path(
            source
        )

        if not source_path.is_absolute():

            source_path = (

                Path.cwd()

                / source_path

            )

        self.source = source_path.resolve()

        self.start_time: float = 0.0

    # ======================================================
    # PUBLIC
    # ======================================================

    @final
    def load(

        self

    ) -> LoadResult[pd.DataFrame]:

        """
        Standard loading pipeline.

        Validate

        Read

        Validate dataframe

        Generate metadata

        Return LoadResult
        """

        self.start_time = perf_counter()

        self.before_load()

        self._validate_source()

        logger.info(

            "Loading %s",

            self.source

        )

        try:

            dataframe = self._read()

        except Exception as exc:

            self.on_failure(

                exc

            )

            logger.exception(


                "Failed loading %s",

                self.source

            )

            raise DataLoadError(

                f"Unable to load "

                f"{self.source}: "

                f"{exc}"

            ) from exc

        self._validate_dataframe(
            dataframe
        )

        metadata = self._build_metadata(
            dataframe
        )

        result = LoadResult(

            data=dataframe,

            metadata=metadata

        )

        self.after_load(
            dataframe
        )

        result = self.cache(
            result
        )

        self.audit(
            result
        )

        logger.info(

            "Loaded %s (%d rows)",

            self.source.name,

            len(dataframe)

        )

        self.on_success(

            result

        )

        return result
    
    # ======================================================
    # SOURCE VALIDATION
    # ======================================================

    def _validate_source(

        self

    ) -> None:

        """
        Validate source file before loading.
        """

        if not self.source.exists():

            raise DataLoadError(

                f"File does not exist: {self.source}"

            )

        if not self.source.is_file():

            raise DataLoadError(

                f"Not a valid file: {self.source}"

            )

        if self.source.stat().st_size == 0:

            raise EmptyDatasetError(

                f"File is empty: {self.source}"

            )

    # ======================================================
    # DATAFRAME VALIDATION
    # ======================================================

    def _validate_dataframe(

        self,

        dataframe: pd.DataFrame

    ) -> None:

        """
        Validate dataframe after loading.
        """

        if dataframe is None:

            raise DataLoadError(

                "Loader returned None."

            )

        if dataframe.empty:

            raise EmptyDatasetError(

                f"{self.source.name} contains no records."

            )

        if dataframe.columns.has_duplicates:

            raise DataLoadError(

                "Duplicate column names detected."

            )

    # ======================================================
    # REQUIRED COLUMN VALIDATION
    # ======================================================

    def validate_columns(

        dataframe: pd.DataFrame,

        required_columns: list[str]

    ) -> None:

        """
        Validate required columns.
        """

        missing = [

            column

            for column in required_columns

            if column not in dataframe.columns

        ]

        if missing:

            raise MissingColumnError(

                f"Missing columns: {missing}"

            )

    # ======================================================
    # CHECKSUM
    # ======================================================

    def _generate_checksum(

        self

    ) -> str:

        """
        SHA256 checksum.
        """

        with self.source.open(

            "rb"

        ) as stream:

            return hashlib.file_digest(

                stream,

                "sha256"

            ).hexdigest()

    # ======================================================
    # METADATA
    # ======================================================

    def _build_metadata(

        self,

        dataframe: pd.DataFrame

    ) -> LoadMetadata:

        """
        Build institutional metadata.
        """

        elapsed = (

            perf_counter()

            - self.start_time

        ) * 1000

        return LoadMetadata(

            source=self.source,

            loader_name=self.__class__.__name__,

            loaded_at=datetime.now(

                UTC

            ),

            elapsed_ms=round(

                elapsed,

                2

            ),

            file_size_bytes=self.source.stat().st_size,

            checksum=self._generate_checksum(),

            rows=len(

                dataframe

            ),

            columns=len(

                dataframe.columns

            ),

            column_names=list(

                dataframe.columns

            ),

            memory_usage_bytes=int(

                dataframe

                .memory_usage(

                    deep=True

                )

                .sum()

            ),

            dtypes={

                column:

                str(dtype)

                for column, dtype

                in dataframe.dtypes.items()

            }

        )

    # ======================================================
    # ABSTRACT
    # ======================================================

    @abstractmethod

    def _read(

        self

    ) -> pd.DataFrame:

        """
        Concrete loaders implement this.

        Examples

        CSVLoader

        ParquetLoader

        ExcelLoader

        DuckDBLoader
        """

        raise NotImplementedError
    
    # ======================================================
    # DATA PROFILE
    # ======================================================

    def profile(

        self,

        dataframe: pd.DataFrame

    ) -> dict[str, Any]:

        """
        Build a lightweight statistical profile
        of the loaded dataset.

        Used by

        • Repositories

        • Validation

        • Diagnostics

        • Audit
        """

        memory_mb = (

            dataframe

            .memory_usage(

                deep=True

            )

            .sum()

            / 1024

            / 1024

        )

        duplicate_rows = int(

            dataframe

            .duplicated()

            .sum()

        )

        total_nulls = int(

            dataframe

            .isna()

            .sum()

            .sum()

        )

        total_cells = (

            dataframe.shape[0]

            * dataframe.shape[1]

        )

        null_percentage = (

            0.0

            if total_cells == 0

            else

            round(

                total_nulls

                / total_cells

                * 100,

                2

            )

        )

        return {

            "rows":

                len(

                    dataframe

                ),

            "columns":

                len(

                    dataframe.columns

                ),

            "memory_mb":

                round(

                    memory_mb,

                    3

                ),

            "duplicate_rows":

                duplicate_rows,

            "total_nulls":

                total_nulls,

            "null_percentage":

                null_percentage,

            "dtypes":

                {

                    column:

                    str(dtype)

                    for column, dtype

                    in dataframe.dtypes.items()

                }

        }

    # ======================================================
    # LOG DATASET
    # ======================================================

    def log_statistics(

        self,

        dataframe: pd.DataFrame

    ) -> None:

        """
        Log dataset statistics.
        """

        stats = self.profile(

            dataframe

        )

        logger.info(

            "Dataset Statistics | "

            "Rows=%d | "

            "Columns=%d | "

            "Memory=%.3f MB | "

            "Duplicates=%d | "

            "Nulls=%d (%.2f%%)",

            stats["rows"],

            stats["columns"],

            stats["memory_mb"],

            stats["duplicate_rows"],

            stats["total_nulls"],

            stats["null_percentage"]

        )

    # ======================================================
    # CALLBACKS
    # ======================================================

    def before_load(

        self

    ) -> None:

        """
        Hook executed before loading.

        Override in child classes
        if required.
        """

        return None

    def after_load(

        self,

        dataframe: pd.DataFrame

    ) -> None:

        """
        Hook executed after loading.

        Override if required.
        """

        self.log_statistics(

            dataframe

        )

    # ======================================================
    # CACHE HOOK
    # ======================================================

    def cache(

        self,

        result: LoadResult[pd.DataFrame]

    ) -> LoadResult[pd.DataFrame]:

        """
        Future cache integration.

        Reserved for

        • Memory Cache

        • Redis

        • DuckDB

        • Disk Cache

        Current implementation
        simply returns
        the original result.
        """

        return result

    # ======================================================
    # AUDIT HOOK
    # ======================================================

    def audit(

        self,

        result: LoadResult[pd.DataFrame]

    ) -> None:

        """
        Future audit integration.

        This method is intentionally
        lightweight so that
        audit_logger.py can later
        subscribe without modifying
        loaders.
        """

        logger.info(

            "Audit | "

            "Loader=%s | "

            "Source=%s | "

            "Rows=%d | "

            "Elapsed=%.2f ms",

            result.metadata.loader_name,

            result.metadata.source.name,

            result.metadata.rows,

            result.metadata.elapsed_ms

        )

    # ======================================================
    # SUCCESS CALLBACK
    # ======================================================

    def on_success(

        self,

        result: LoadResult[pd.DataFrame]

    ) -> None:

        """
        Called after a successful load.

        Reserved for

        • Metrics

        • Monitoring

        • Event Bus

        • Future Telemetry
        """

        logger.debug(

            "Load completed successfully: %s",

            result.metadata.source.name

        )

    # ======================================================
    # FAILURE CALLBACK
    # ======================================================

    def on_failure(

        self,

        exception: Exception

    ) -> None:

        """
        Called when loading fails.

        Reserved for

        • Alerting

        • Monitoring

        • Telemetry
        """

        logger.error(

            "Loader failed: %s",

            exception

        )

    # ======================================================
    # FILE INFORMATION
    # ======================================================

    @property
    def exists(

        self

    ) -> bool:

        """
        Returns whether
        the source exists.
        """

        return self.source.exists()
    

    @property
    def filename(

        self

    ) -> str:

        """
        Source filename.
        """

        return self.source.name
    
    @property
    def file_stem(

        self

    ) -> str:

        """
        Filename without extension.
        """

        return self.source.stem
    
    @property
    def extension(

        self

    ) -> str:

        """
        File extension.
        """

        return self.source.suffix.lower()

    @property
    def filesize(

        self

    ) -> int:

        """
        File size in bytes.
        """

        if not self.exists:

            return 0

        return self.source.stat().st_size

    # ======================================================
    # TIMER
    # ======================================================

    @property
    def elapsed_ms(

        self

    ) -> float:

        """
        Current elapsed time.
        """

        return round(

            (

                perf_counter()

                - self.start_time

            )

            * 1000,

            2

        )

    # ======================================================
    # RESOURCE MANAGEMENT
    # ======================================================

    def close(

        self

    ) -> None:

        """
        Resource cleanup hook.

        Override for

        • Database Connections

        • API Sessions

        • File Handles
        """

        return None

    # ======================================================
    # CONTEXT MANAGER
    # ======================================================

    def __enter__(

        self

    ) -> "BaseLoader":

        return self

    def __exit__(

        self,

        exc_type,

        exc_value,

        traceback

    ) -> None:

        self.close()

    # ======================================================
    # REPRESENTATION
    # ======================================================

    def __repr__(

        self

    ) -> str:

        return (

            f"{self.__class__.__name__}"

            "("

            f"source='{self.source}'"

            ")"

        )

    __str__ = __repr__