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

from pathlib import Path

from typing import Any

import pandas as pd

from core.data.loaders.base_loader import BaseLoader

from core.exceptions import DataLoadError


class ParquetLoader(

    BaseLoader

):

    """
    Institutional Parquet Loader.
    """

    def __init__(

        self,

        source: str | Path,

        engine: str = "auto",

        columns: list[str] | None = None,

        storage_options: dict[str, Any] | None = None,

        filesystem: Any | None = None,

        filters: list | None = None,

        use_nullable_dtypes: bool = False

    ) -> None:

        super().__init__(

            source

        )

        self.engine = engine

        self.columns = columns

        self.storage_options = storage_options

        self.filesystem = filesystem

        self.filters = filters

        self.use_nullable_dtypes = use_nullable_dtypes

    # =====================================================
    # PARQUET READER
    # =====================================================

    def _read(

        self

    ) -> pd.DataFrame:

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

            dataframe = pd.read_parquet(

                path=self.source,

                engine=self.engine,

                columns=self.columns,

                storage_options=self.storage_options,

                filesystem=self.filesystem,

                filters=self.filters,

                use_nullable_dtypes=self.use_nullable_dtypes

            )

            return dataframe

        except ImportError as exc:

            raise DataLoadError(

                "Parquet engine is not installed. "

                "Install pyarrow or fastparquet."

            ) from exc

        except FileNotFoundError as exc:

            raise DataLoadError(

                f"Parquet file not found: "

                f"{self.source}"

            ) from exc

        except PermissionError as exc:

            raise DataLoadError(

                f"Permission denied while reading "

                f"{self.source}: "

                f"{exc}"

            ) from exc

        except ValueError as exc:

            raise DataLoadError(

                f"Invalid parquet configuration "

                f"for {self.source}: "

                f"{exc}"

            ) from exc

        except OSError as exc:

            raise DataLoadError(

                f"Unable to access parquet file "

                f"{self.source}: "

                f"{exc}"

            ) from exc

        except Exception as exc:

            raise DataLoadError(

                f"Unexpected parquet loading error "

                f"for {self.source}: "

                f"{exc}"

            ) from exc