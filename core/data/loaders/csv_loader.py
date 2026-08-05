"""
====================================================================
Institutional Quant Platform

CSV Loader

Author : Institutional Quant Platform

Purpose
-------
Production CSV Loader

Supports

• CSV
• GZIP CSV
• ZIP CSV
• UTF-8
• UTF-8-SIG
• Custom Separators
• Date Parsing
• Memory Optimization

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
class CSVLoaderConfig:
    source: str | Path
    separator: str = ","
    encoding: str = "utf-8"
    header: int | None = 0
    index_col: int | str | None = None
    dtype: dict[str, Any] | None = None
    parse_dates: list[str] | None = None
    na_values: list[str] | None = None
    low_memory: bool = False
    memory_map: bool = True
    compression: str | None = "infer"


class CSVLoader(BaseLoader):
    """
    Institutional CSV Loader.
    """

    def __init__(
        self,
        config: CSVLoaderConfig,
    ) -> None:

        super().__init__(config.source)

        self.separator = config.separator

        self.encoding = config.encoding

        self.header = config.header

        self.index_col = config.index_col

        self.dtype = config.dtype

        self.parse_dates = config.parse_dates

        self.na_values = config.na_values

        self.low_memory = config.low_memory

        self.memory_map = config.memory_map

        self.compression = config.compression

    # =====================================================
    # CSV READER
    # =====================================================

    def _read(self) -> pd.DataFrame:
        """
        Read CSV file.

        Returns
        -------
        pandas.DataFrame

        Raises
        ------
        DataLoadError
        """

        try:
            return pd.read_csv(
                filepath_or_buffer=self.source,
                sep=self.separator,
                encoding=self.encoding,
                header=self.header,
                index_col=self.index_col,
                dtype=self.dtype,
                parse_dates=self.parse_dates,
                na_values=self.na_values,
                low_memory=self.low_memory,
                memory_map=self.memory_map,
                compression=self.compression,
            )

        except UnicodeDecodeError as exc:
            raise DataLoadError(
                f"Encoding error while reading {self.source}: {exc}"
            ) from exc

        except pd.errors.EmptyDataError as exc:
            raise DataLoadError(f"CSV file is empty: {self.source}") from exc

        except pd.errors.ParserError as exc:
            raise DataLoadError(f"CSV parsing failed for {self.source}: {exc}") from exc

        except FileNotFoundError as exc:
            raise DataLoadError(f"CSV file not found: {self.source}") from exc

        except PermissionError as exc:
            raise DataLoadError(
                f"Permission denied while reading {self.source}: {exc}"
            ) from exc

        except Exception as exc:
            raise DataLoadError(
                f"Unexpected CSV loading error for {self.source}: {exc}"
            ) from exc
