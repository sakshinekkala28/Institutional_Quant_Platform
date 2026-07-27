"""
Institutional Quant Platform
Production Reference Repository

This file demonstrates the Repository Pattern used throughout
the platform.

Repositories abstract data persistence from business logic.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
import logging
from typing import Generic, TypeVar

logger = logging.getLogger(__name__)

# ======================================================================
# Domain Model
# ======================================================================


@dataclass(slots=True, frozen=True)
class Security:
    """Domain entity."""

    symbol: str
    company_name: str
    sector: str
    market_cap: float


# ======================================================================
# Generic Types
# ======================================================================

T = TypeVar("T")


# ======================================================================
# Repository Contract
# ======================================================================


class Repository(ABC, Generic[T]):
    """
    Base repository contract.

    Business logic depends on this interface,
    never on a concrete database.
    """

    @abstractmethod
    def get(self, identifier: str) -> T | None:
        """Retrieve a single entity."""

    @abstractmethod
    def list(self) -> list[T]:
        """Retrieve all entities."""

    @abstractmethod
    def save(self, entity: T) -> None:
        """Persist entity."""

    @abstractmethod
    def delete(self, identifier: str) -> None:
        """Delete entity."""


# ======================================================================
# DuckDB Implementation
# ======================================================================


class DuckDBRepository(Repository[Security]):
    """
    Example DuckDB repository.

    Replace in-memory storage with DuckDB SQL
    in production.
    """

    def __init__(self):

        self._storage: dict[str, Security] = {}

    def get(self, identifier: str) -> Security | None:

        logger.info(
            "Fetching %s from DuckDB.",
            identifier,
        )

        return self._storage.get(identifier)

    def list(self) -> list[Security]:

        logger.info("Listing securities.")

        return list(self._storage.values())

    def save(self, entity: Security) -> None:

        logger.info(
            "Saving %s",
            entity.symbol,
        )

        self._storage[entity.symbol] = entity

    def delete(self, identifier: str) -> None:

        logger.info(
            "Deleting %s",
            identifier,
        )

        self._storage.pop(identifier, None)


# ======================================================================
# PostgreSQL Implementation
# ======================================================================


class PostgreSQLRepository(Repository[Security]):
    """
    Future PostgreSQL implementation.

    The interface remains identical.
    """

    def get(self, identifier: str) -> Security | None:
        raise NotImplementedError

    def list(self) -> list[Security]:
        raise NotImplementedError

    def save(self, entity: Security) -> None:
        raise NotImplementedError

    def delete(self, identifier: str) -> None:
        raise NotImplementedError


# ======================================================================
# Repository Service
# ======================================================================


class SecurityService:
    """
    Business logic layer.

    Notice that it depends on Repository,
    not DuckDBRepository.
    """

    def __init__(
        self,
        repository: Repository[Security],
    ):
        self.repository = repository

    def register_security(
        self,
        security: Security,
    ) -> None:

        self.repository.save(security)

    def find(
        self,
        symbol: str,
    ) -> Security | None:

        return self.repository.get(symbol)

    def list_all(self) -> list[Security]:

        return self.repository.list()


# ======================================================================
# Example Usage
# ======================================================================


def main() -> None:

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )

    repository = DuckDBRepository()

    service = SecurityService(repository)

    service.register_security(
        Security(
            symbol="TCS",
            company_name="Tata Consultancy Services",
            sector="Information Technology",
            market_cap=15_000_000_000,
        )
    )

    security = service.find("TCS")

    logger.info(security)

    logger.info(service.list_all())


if __name__ == "__main__":
    main()
