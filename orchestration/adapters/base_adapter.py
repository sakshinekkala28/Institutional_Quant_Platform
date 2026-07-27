"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Base Adapter

Abstract interface implemented by every platform adapter.

Responsibilities
----------------
• Connection lifecycle
• Read operations
• Write operations
• Health checks
• Transactions
• Resource cleanup

Implemented By
--------------
• CSVAdapter
• ParquetAdapter
• DuckDBAdapter
• SQLiteAdapter
• PostgreSQLAdapter
• APIAdapter
• Custom Adapters

=========================================================
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

# =========================================================
# BASE ADAPTER
# =========================================================


class BaseAdapter(ABC):
    """
    Abstract base class for all platform adapters.
    """

    NAME: str = "base"

    DESCRIPTION: str = ""

    VERSION: str = "1.0.0"

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __init__(
        self,
        **config: Any,
    ) -> None:

        self.config = config

        self.connected = False

    # =====================================================
    # CONNECTION
    # =====================================================

    @abstractmethod
    def connect(
        self,
    ) -> None:
        """
        Establish backend connection.
        """
        raise NotImplementedError

    # -----------------------------------------------------

    @abstractmethod
    def disconnect(
        self,
    ) -> None:
        """
        Close backend connection.
        """
        raise NotImplementedError

    # =====================================================
    # DATA ACCESS
    # =====================================================

    @abstractmethod
    def read(
        self,
        *args,
        **kwargs,
    ) -> Any:
        """
        Read data.
        """
        raise NotImplementedError

    # -----------------------------------------------------

    @abstractmethod
    def write(
        self,
        data: Any,
        *args,
        **kwargs,
    ) -> Any:
        """
        Write data.
        """
        raise NotImplementedError

    # =====================================================
    # OPTIONAL OPERATIONS
    # =====================================================

    def exists(
        self,
        *args,
        **kwargs,
    ) -> bool:
        """
        Check whether a resource exists.
        """

        raise NotImplementedError(f"{self.NAME} does not implement exists().")

    # -----------------------------------------------------

    def delete(
        self,
        *args,
        **kwargs,
    ) -> None:
        """
        Delete a resource.
        """

        raise NotImplementedError(f"{self.NAME} does not implement delete().")

    # -----------------------------------------------------

    def health_check(
        self,
    ) -> bool:
        """
        Validate backend availability.
        """

        return self.connected

    # =====================================================
    # METADATA
    # =====================================================

    @classmethod
    def metadata(
        cls,
    ) -> dict[str, Any]:

        return {
            "name": cls.NAME,
            "description": cls.DESCRIPTION,
            "version": cls.VERSION,
        }

    # =====================================================
    # CONTEXT MANAGER
    # =====================================================

    def __enter__(
        self,
    ) -> BaseAdapter:

        self.connect()

        return self

    # -----------------------------------------------------

    def __exit__(
        self,
        exc_type,
        exc,
        traceback,
    ) -> None:

        self.disconnect()

    # =====================================================
    # DUNDER
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return (
            f"{self.__class__.__name__}(name='{self.NAME}', connected={self.connected})"
        )
