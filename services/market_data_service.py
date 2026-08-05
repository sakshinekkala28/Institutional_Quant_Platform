"""
======================================================================

Institutional Quant Platform

Market Data Service

Author
------
Institutional Quant Platform

Purpose
-------
Enterprise market data service.

Responsibilities
----------------
• Security Master
• Price Data
• Fundamentals
• Factor Data
• Benchmark Data
• Universe Management

======================================================================
"""

from __future__ import annotations

from pathlib import Path
from threading import Lock, RLock
from typing import Any

import pandas as pd

from core.services.base_service import BaseService

# ============================================================
# Exceptions
# ============================================================


class MarketDataError(Exception):
    """Base market data exception."""


class DatasetNotLoadedError(MarketDataError):
    """Dataset not loaded."""


class DatasetAlreadyLoadedError(MarketDataError):
    """Dataset already loaded."""


# ============================================================
# Market Data Service
# ============================================================


class MarketDataService(BaseService):
    """
    Enterprise Market Data Manager.
    """

    _instance = None

    _instance_lock = Lock()

    def __new__(cls, *args, **kwargs):

        if cls._instance is None:
            with cls._instance_lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(self):

        if getattr(self, "_initialized", False):
            return

        super().__init__()

        self._lock = RLock()

        self._datasets: dict[str, pd.DataFrame] = {}

        self._metadata: dict[str, dict[str, Any]] = {}

        self._enabled = True

        self._initialized = True

        self._logger.info("MarketDataService initialized.")

    # =====================================================
    # Lifecycle
    # =====================================================

    def enable(self):

        self._enabled = True

    def disable(self):

        self._enabled = False

    def enabled(self):

        return self._enabled

    # =====================================================
    # Dataset Registration
    # =====================================================

    def register_dataset(
        self, name: str, dataframe: pd.DataFrame, metadata: dict[str, Any] | None = None
    ) -> None:
        """
        Register dataset.
        """

        with self._lock:
            if name in self._datasets:
                raise DatasetAlreadyLoadedError(name)

            self._datasets[name] = dataframe

            self._metadata[name] = metadata or {}

            self._logger.info("Loaded dataset '%s' (%d rows)", name, len(dataframe))

    # =====================================================
    # Load Dataset
    # =====================================================

    def load_csv(self, name: str, path: Path, **kwargs) -> pd.DataFrame:
        """
        Load CSV dataset.
        """

        dataframe = pd.read_csv(path, **kwargs)

        self.register_dataset(name, dataframe, {"source": str(path), "type": "csv"})

        return dataframe

    def load_parquet(self, name: str, path: Path, **kwargs) -> pd.DataFrame:
        """
        Load Parquet dataset.
        """

        dataframe = pd.read_parquet(path, **kwargs)

        self.register_dataset(name, dataframe, {"source": str(path), "type": "parquet"})

        return dataframe

    # =====================================================
    # BaseService
    # =====================================================

    def run(self):

        return self.statistics()

    # =====================================================
    # Dataset Retrieval
    # =====================================================

    def get_dataset(self, name: str) -> pd.DataFrame:
        """
        Retrieve a registered dataset.
        """

        with self._lock:
            if name not in self._datasets:
                raise DatasetNotLoadedError(name)

            return self._datasets[name]

    # -----------------------------------------------------

    def metadata(self, name: str) -> dict[str, Any]:
        """
        Dataset metadata.
        """

        if name not in self._metadata:
            raise DatasetNotLoadedError(name)

        return dict(self._metadata[name])

    # -----------------------------------------------------

    def exists(self, name: str) -> bool:

        return name in self._datasets

    # =====================================================
    # Dataset Removal
    # =====================================================

    def remove_dataset(self, name: str) -> None:
        """
        Remove dataset.
        """

        with self._lock:
            if name not in self._datasets:
                raise DatasetNotLoadedError(name)

            del self._datasets[name]

            self._metadata.pop(name, None)

    # -----------------------------------------------------

    def clear(self) -> None:
        """
        Remove every loaded dataset.
        """

        with self._lock:
            self._datasets.clear()

            self._metadata.clear()

    # =====================================================
    # Dataset Information
    # =====================================================

    def dataset_names(self) -> list[str]:

        return sorted(self._datasets.keys())

    def dataset_count(self) -> int:

        return len(self._datasets)

    # =====================================================
    # Standard Dataset Accessors
    # =====================================================

    def security_master(self) -> pd.DataFrame:

        return self.get_dataset("security_master")

    def price_data(self) -> pd.DataFrame:

        return self.get_dataset("price_data")

    def fundamentals(self) -> pd.DataFrame:

        return self.get_dataset("fundamentals")

    def benchmark(self) -> pd.DataFrame:

        return self.get_dataset("benchmark")

    def factor_data(self) -> pd.DataFrame:

        return self.get_dataset("factor_data")

    def universe(self) -> pd.DataFrame:

        return self.get_dataset("universe")

    # =====================================================
    # Validation
    # =====================================================

    def validate_dataset(self, name: str) -> bool:
        """
        Validate dataset.
        """

        dataframe = self.get_dataset(name)

        if dataframe.empty:
            raise MarketDataError(f"{name} is empty.")

        return True

    def validate_all(self) -> bool:
        """
        Validate every dataset.
        """

        for dataset in self.dataset_names():
            self.validate_dataset(dataset)

        return True

    # =====================================================
    # Statistics
    # =====================================================

    def statistics(self) -> dict[str, Any]:
        """
        Dataset statistics.
        """

        datasets = {}

        total_rows = 0

        for name, dataframe in self._datasets.items():
            rows = len(dataframe)

            cols = len(dataframe.columns)

            total_rows += rows

            datasets[name] = {
                "rows": rows,
                "columns": cols,
                "memory_mb": round(
                    dataframe.memory_usage(deep=True).sum() / 1024 / 1024, 2
                ),
            }

        return {
            "dataset_count": len(self._datasets),
            "total_rows": total_rows,
            "datasets": datasets,
        }

    # =====================================================
    # Snapshot
    # =====================================================

    def snapshot(self) -> dict[str, Any]:
        """
        Dataset summary.
        """

        return {"datasets": self.dataset_names(), "statistics": self.statistics()}

    # =====================================================
    # Symbol Queries
    # =====================================================

    def get_symbol(
        self, dataset: str, symbol: str, column: str = "symbol"
    ) -> pd.DataFrame:
        """
        Return rows for a specific symbol.
        """

        dataframe = self.get_dataset(dataset)

        if column not in dataframe.columns:
            raise MarketDataError(f"Column '{column}' not found.")

        return dataframe.loc[dataframe[column] == symbol]

    # -----------------------------------------------------

    def symbols(self, dataset: str, column: str = "symbol") -> list[str]:
        """
        Return unique symbols.
        """

        dataframe = self.get_dataset(dataset)

        if column not in dataframe.columns:
            raise MarketDataError(column)

        return sorted(dataframe[column].dropna().unique().tolist())

    # =====================================================
    # Generic Filters
    # =====================================================

    def filter(self, dataset: str, **filters) -> pd.DataFrame:
        """
        Filter dataset using equality conditions.
        """

        dataframe = self.get_dataset(dataset)

        result = dataframe

        for column, value in filters.items():
            if column not in dataframe.columns:
                raise MarketDataError(column)

            result = result.loc[result[column] == value]

        return result

    # =====================================================
    # Column Validation
    # =====================================================

    def require_columns(self, dataset: str, columns: list[str]) -> None:
        """
        Ensure required columns exist.
        """

        dataframe = self.get_dataset(dataset)

        missing = [column for column in columns if column not in dataframe.columns]

        if missing:
            raise MarketDataError(f"Missing columns: {missing}")

    # =====================================================
    # Duplicate Detection
    # =====================================================

    def duplicate_rows(
        self, dataset: str, subset: list[str] | None = None
    ) -> pd.DataFrame:
        """
        Return duplicate rows.
        """

        dataframe = self.get_dataset(dataset)

        return dataframe.loc[dataframe.duplicated(subset=subset, keep=False)]

    # =====================================================
    # Missing Data
    # =====================================================

    def missing_values(self, dataset: str) -> pd.Series:
        """
        Missing values per column.
        """

        dataframe = self.get_dataset(dataset)

        return dataframe.isna().sum()

    # =====================================================
    # Cache Integration
    # =====================================================

    def cache_dataset(self, name: str, cache_service) -> None:
        """
        Store dataset in CacheService.
        """

        cache_service.put(f"market_data:{name}", self.get_dataset(name))

    def load_from_cache(self, name: str, cache_service) -> pd.DataFrame:
        """
        Load dataset from CacheService.
        """

        dataframe = cache_service.get(f"market_data:{name}")

        if dataframe is None:
            raise DatasetNotLoadedError(name)

        return dataframe

    # =====================================================
    # Reload
    # =====================================================

    def reload_dataset(self, name: str, loader, *args, **kwargs) -> pd.DataFrame:
        """
        Reload a dataset using a loader function.
        """

        if self.exists(name):
            self.remove_dataset(name)

        dataframe = loader(*args, **kwargs)

        self.register_dataset(name, dataframe)

        return dataframe

    # =====================================================
    # Health
    # =====================================================

    def health(self) -> dict[str, Any]:
        """
        Health report.
        """

        healthy = all(not dataframe.empty for dataframe in self._datasets.values())

        return {
            "status": "HEALTHY" if healthy else "WARNING",
            "enabled": self._enabled,
            "datasets": len(self._datasets),
        }

    # =====================================================
    # Lifecycle
    # =====================================================

    def startup(self) -> None:

        self.enable()

        self._logger.info("MarketDataService started.")

    def shutdown(self) -> None:

        self.clear()

        self.disable()

        self._logger.info("MarketDataService shutdown.")

    # =====================================================
    # Magic Methods
    # =====================================================

    def __contains__(self, dataset: str) -> bool:

        return self.exists(dataset)

    def __len__(self) -> int:

        return len(self._datasets)

    def __iter__(self):

        return iter(self._datasets.items())

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}(datasets={len(self)}, enabled={self._enabled})"
        )


# ============================================================
# Global Singleton
# ============================================================

market_data_service = MarketDataService()
