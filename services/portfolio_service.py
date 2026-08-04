"""
======================================================================

Institutional Quant Platform

Portfolio Service

Author
------
Institutional Quant Platform

Purpose
-------
Enterprise Portfolio Management Service.

Responsibilities
----------------
• Holdings
• Position Management
• Portfolio Weights
• Cash Management
• Portfolio Statistics

======================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from threading import Lock, RLock
from typing import Any

import pandas as pd

from core.services.base_service import BaseService

# ============================================================
# Exceptions
# ============================================================


class PortfolioError(Exception):
    """Base portfolio exception."""


class PortfolioNotFoundError(PortfolioError):
    """Portfolio does not exist."""


# ============================================================
# Portfolio Model
# ============================================================


@dataclass(slots=True)
class Portfolio:
    name: str

    holdings: pd.DataFrame

    benchmark: str = "NIFTY500"

    cash: float = 0.0

    nav: float = 0.0

    metadata: dict[str, Any] = field(default_factory=dict)


# ============================================================
# Portfolio Service
# ============================================================


class PortfolioService(BaseService):
    """
    Institutional Portfolio Manager.
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

        self._portfolios: dict[str, Portfolio] = {}

        self._enabled = True

        self._initialized = True

        self._logger.info("PortfolioService initialized.")

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
    # Registration
    # =====================================================

    def register(
        self,
        name: str,
        holdings: pd.DataFrame,
        benchmark: str = "NIFTY500",
        cash: float = 0.0,
        nav: float = 0.0,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """
        Register portfolio.
        """

        portfolio = Portfolio(
            name=name,
            holdings=holdings,
            benchmark=benchmark,
            cash=cash,
            nav=nav,
            metadata=metadata or {},
        )

        with self._lock:
            self._portfolios[name] = portfolio

    # =====================================================
    # Retrieval
    # =====================================================

    def get(self, name: str) -> Portfolio:

        if name not in self._portfolios:
            raise PortfolioNotFoundError(name)

        return self._portfolios[name]

    # =====================================================
    # Standard Accessors
    # =====================================================

    def holdings(self, portfolio: str) -> pd.DataFrame:

        return self.get(portfolio).holdings

    def benchmark(self, portfolio: str) -> str:

        return self.get(portfolio).benchmark

    def cash(self, portfolio: str) -> float:

        return self.get(portfolio).cash

    def nav(self, portfolio: str) -> float:

        return self.get(portfolio).nav

    # =====================================================
    # BaseService
    # =====================================================

    def run(self):

        return self.statistics()

    # =====================================================
    # Position Management
    # =====================================================

    def add_position(self, portfolio: str, position: dict[str, Any]) -> None:
        """
        Add a position.
        """

        instance = self.get(portfolio)

        dataframe = instance.holdings

        instance.holdings = pd.concat(
            [dataframe, pd.DataFrame([position])], ignore_index=True
        )

    # -----------------------------------------------------

    def remove_position(
        self, portfolio: str, symbol: str, symbol_column: str = "symbol"
    ) -> None:
        """
        Remove a position.
        """

        instance = self.get(portfolio)

        instance.holdings = instance.holdings.loc[
            instance.holdings[symbol_column] != symbol
        ].reset_index(drop=True)

    # -----------------------------------------------------

    def update_position(
        self,
        portfolio: str,
        symbol: str,
        updates: dict[str, Any],
        symbol_column: str = "symbol",
    ) -> None:
        """
        Update position.
        """

        instance = self.get(portfolio)

        dataframe = instance.holdings

        mask = dataframe[symbol_column] == symbol

        if not mask.any():
            raise PortfolioError(f"{symbol} not found.")

        for column, value in updates.items():
            dataframe.loc[mask, column] = value

    # =====================================================
    # Position Lookup
    # =====================================================

    def position(
        self, portfolio: str, symbol: str, symbol_column: str = "symbol"
    ) -> pd.Series:
        """
        Return a single position.
        """

        dataframe = self.holdings(portfolio)

        result = dataframe.loc[dataframe[symbol_column] == symbol]

        if result.empty:
            raise PortfolioError(symbol)

        return result.iloc[0]

    # =====================================================
    # Exposure
    # =====================================================

    def total_weight(self, portfolio: str, weight_column: str = "weight") -> float:
        """
        Total portfolio weight.
        """

        dataframe = self.holdings(portfolio)

        if weight_column not in dataframe.columns:
            return 0.0

        return float(dataframe[weight_column].sum())

    # -----------------------------------------------------

    def long_exposure(self, portfolio: str, weight_column: str = "weight") -> float:

        dataframe = self.holdings(portfolio)

        return float(dataframe.loc[dataframe[weight_column] > 0, weight_column].sum())

    # -----------------------------------------------------

    def short_exposure(self, portfolio: str, weight_column: str = "weight") -> float:

        dataframe = self.holdings(portfolio)

        return float(dataframe.loc[dataframe[weight_column] < 0, weight_column].sum())

    # =====================================================
    # Cash
    # =====================================================

    def update_cash(self, portfolio: str, amount: float) -> None:
        """
        Update available cash.
        """

        self.get(portfolio).cash = amount

    # -----------------------------------------------------

    def update_nav(self, portfolio: str, nav: float) -> None:
        """
        Update portfolio NAV.
        """

        self.get(portfolio).nav = nav

    # =====================================================
    # Validation
    # =====================================================

    def validate(self, portfolio: str, weight_column: str = "weight") -> bool:
        """
        Validate portfolio.
        """

        dataframe = self.holdings(portfolio)

        if dataframe.empty:
            raise PortfolioError("Portfolio is empty.")

        if weight_column in dataframe.columns:
            total = dataframe[weight_column].sum()

            if abs(total - 1.0) > 0.01:
                raise PortfolioError(f"Portfolio weights sum to {total:.4f}")

        return True

    # =====================================================
    # Statistics
    # =====================================================

    def statistics(self) -> dict[str, Any]:
        """
        Portfolio statistics.
        """

        portfolios = {}

        for name, portfolio in self._portfolios.items():
            portfolios[name] = {
                "holdings": len(portfolio.holdings),
                "cash": portfolio.cash,
                "nav": portfolio.nav,
                "benchmark": portfolio.benchmark,
            }

        return {"portfolio_count": len(self._portfolios), "portfolios": portfolios}

    # =====================================================
    # Portfolio Analytics
    # =====================================================

    def sector_exposure(
        self,
        portfolio: str,
        sector_column: str = "sector",
        weight_column: str = "weight",
    ) -> pd.Series:
        """
        Sector exposure.
        """

        dataframe = self.holdings(portfolio)

        self.validate(portfolio, weight_column)

        return dataframe.groupby(sector_column)[weight_column].sum()

    # -----------------------------------------------------

    def industry_exposure(
        self,
        portfolio: str,
        industry_column: str = "industry",
        weight_column: str = "weight",
    ) -> pd.Series:

        dataframe = self.holdings(portfolio)

        return dataframe.groupby(industry_column)[weight_column].sum()

    # -----------------------------------------------------

    def top_holdings(
        self, portfolio: str, n: int = 10, weight_column: str = "weight"
    ) -> pd.DataFrame:
        """
        Largest portfolio holdings.
        """

        dataframe = self.holdings(portfolio)

        return dataframe.sort_values(weight_column, ascending=False).head(n)

    # -----------------------------------------------------

    def concentration(self, portfolio: str, weight_column: str = "weight") -> float:
        """
        Herfindahl-Hirschman Index.
        """

        dataframe = self.holdings(portfolio)

        weights = dataframe[weight_column]

        return float((weights**2).sum())

    # =====================================================
    # Portfolio Metadata
    # =====================================================

    def metadata(self, portfolio: str) -> dict[str, Any]:

        return dict(self.get(portfolio).metadata)

    def update_metadata(self, portfolio: str, **kwargs) -> None:

        self.get(portfolio).metadata.update(kwargs)

    # =====================================================
    # Portfolio Registry
    # =====================================================

    def exists(self, portfolio: str) -> bool:

        return portfolio in self._portfolios

    def names(self) -> list[str]:

        return sorted(self._portfolios.keys())

    def remove(self, portfolio: str) -> None:

        if portfolio not in self._portfolios:
            raise PortfolioNotFoundError(portfolio)

        del self._portfolios[portfolio]

    def clear(self) -> None:

        self._portfolios.clear()

    # =====================================================
    # Snapshot
    # =====================================================

    def snapshot(self, portfolio: str) -> dict[str, Any]:
        """
        Portfolio snapshot.
        """

        instance = self.get(portfolio)

        return {
            "name": instance.name,
            "benchmark": instance.benchmark,
            "cash": instance.cash,
            "nav": instance.nav,
            "holdings": len(instance.holdings),
            "metadata": dict(instance.metadata),
        }

    # =====================================================
    # Health
    # =====================================================

    def health(self) -> dict[str, Any]:
        """
        Portfolio service health.
        """

        return {
            "status": "HEALTHY" if self._enabled else "DISABLED",
            "enabled": self._enabled,
            "portfolio_count": len(self._portfolios),
        }

    # =====================================================
    # Lifecycle
    # =====================================================

    def startup(self) -> None:

        self.enable()

        self._logger.info("PortfolioService started.")

    def shutdown(self) -> None:

        self.clear()

        self.disable()

        self._logger.info("PortfolioService shutdown.")

    # =====================================================
    # Magic Methods
    # =====================================================

    def __contains__(self, portfolio: str) -> bool:

        return self.exists(portfolio)

    def __len__(self) -> int:

        return len(self._portfolios)

    def __iter__(self):

        return iter(self._portfolios.items())

    def __repr__(self) -> str:

        return (
            f"{self.__class__.__name__}"
            f"(portfolios={len(self)}, "
            f"enabled={self._enabled})"
        )


# ============================================================
# Global Singleton
# ============================================================

portfolio_service = PortfolioService()
