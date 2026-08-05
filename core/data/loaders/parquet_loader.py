"""
====================================================================
Institutional Quant Platform

Parquet Loader

Author : Institutional Quant Platform

Purpose
-------
Production Parquet Loader

Supports

• Apache Parquet
• PyArrow
• FastParquet
• Column Projection
• Nullable Types
• Partitioned Datasets

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from core.data.loaders.base_loader import BaseLoader
from core.exceptions import DataLoadError


@dataclass(slots=True)
class ParquetLoaderConfig:
    source: str | Path
    columns: list[str] | None = None
    engine: str = "pyarrow"
    filters: Any | None = None
    use_nullable_dtypes: bool = True
    dtype_backend: str = "numpy_nullable"

class ParquetLoader(BaseLoader):
    """
    Institutional Parquet Loader.
    """

    def __init__(
        self,
        config: ParquetLoaderConfig,
    ) -> None:

        super().__init__(config.source)

        self.engine = config.engine

        self.columns = config.columns

        self.storage_options = config.storage_options

        self.filesystem = config.filesystem

        self.filters = config.filters

        self.use_nullable_dtypes = config.use_nullable_dtypes

    # =====================================================
    # PARQUET READER
    # =====================================================

    def _read(self) -> pd.DataFrame:
        """
        Read Apache Parquet file.

        Returns
        -------
        pandas.DataFrame

        Raises
        ------
        DataLoadError
        """

        try:
            return pd.read_parquet(
                path=self.source,
                engine=self.engine,
                columns=self.columns,
                storage_options=self.storage_options,
                filesystem=self.filesystem,
                filters=self.filters,
                use_nullable_dtypes=self.use_nullable_dtypes,
            )

        except ImportError as exc:
            raise DataLoadError(
                "Parquet engine is not installed. Install pyarrow or fastparquet."
            ) from exc

        except FileNotFoundError as exc:
            raise DataLoadError(f"Parquet file not found: {self.source}") from exc

        except PermissionError as exc:
            raise DataLoadError(
                f"Permission denied while reading {self.source}: {exc}"
            ) from exc

        except ValueError as exc:
            raise DataLoadError(
                f"Invalid parquet configuration for {self.source}: {exc}"
            ) from exc

        except OSError as exc:
            raise DataLoadError(
                f"Unable to access parquet file {self.source}: {exc}"
            ) from exc

        except Exception as exc:
            raise DataLoadError(
                f"Unexpected parquet loading error for {self.source}: {exc}"
            ) from exc
