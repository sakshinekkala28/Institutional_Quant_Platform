"""
====================================================================
Institutional Quant Platform

Portfolio Service

Author : Institutional Quant Platform

Purpose
-------
Portfolio orchestration service.

Coordinates

• PortfolioRepository
• PortfolioStatistics
• PortfolioExposure
• PortfolioDiversification
• PortfolioConstraints
• PortfolioAllocation
• PortfolioTurnover

====================================================================
"""

from __future__ import annotations

from pathlib import Path

from core.data.repositories.portfolio_repository import (
    PortfolioRepository
)

from core.models.portfolio import Portfolio
from core.models.portfolio_position import PortfolioPosition

from core.portfolio.statistics import (
    PortfolioStatistics
)

from core.portfolio.exposure import (
    PortfolioExposure
)

from core.portfolio.diversification import (
    PortfolioDiversification
)

from core.portfolio.constraints import (
    PortfolioConstraints
)

from core.portfolio.allocation import (
    PortfolioAllocation
)

from core.portfolio.turnover import (
    PortfolioTurnover
)

from core.services.base_service import (
    BaseService
)


class PortfolioService(

    BaseService

):
    """
    Portfolio orchestration service.
    """

    def __init__(

        self,

        source: str | Path

    ) -> None:

        super().__init__()

        self._repository = PortfolioRepository(

            source

        )

        self._portfolio: Portfolio | None = None

    # =====================================================
    # EXECUTION
    # =====================================================

    def run(

        self

    ) -> Portfolio:

        return self.load()

    # =====================================================
    # LOAD
    # =====================================================

    def load(

        self,

        reload: bool = False

    ) -> Portfolio:

        if self._portfolio is None or reload:

            self._portfolio = self._repository.load()

        return self._portfolio

    def reload(

        self

    ) -> Portfolio:

        return self.load(

            reload=True

        )

    # =====================================================
    # PROPERTIES
    # =====================================================

    @property
    def portfolio(

        self

    ) -> Portfolio:

        return self.load()

    @property
    def holdings(

        self

    ) -> int:

        return self.portfolio.holdings

    @property
    def total_weight(

        self

    ) -> float:

        return self.portfolio.total_weight

    # =====================================================
    # API HELPERS
    # =====================================================

    def get_portfolio(

        self

    ) -> Portfolio:

        return self.portfolio

    def get_holdings(

        self

    ) -> list[PortfolioPosition]:

        return list(

            self.portfolio

        )

    def get_position(

        self,

        symbol: str

    ) -> PortfolioPosition | None:

        return self.portfolio.get(

            symbol

        )

    def get_top_holdings(

        self,

        n: int = 10

    ) -> list[PortfolioPosition]:

        return self.portfolio.top_holdings(

            n

        )

    def get_sector_weights(

        self

    ) -> dict[str, float]:

        return self.portfolio.sector_weights()

    # =====================================================
    # STATISTICS
    # =====================================================

    def statistics(

        self

    ) -> dict:

        return PortfolioStatistics.summary(

            self.portfolio

        )

    # =====================================================
    # EXPOSURE
    # =====================================================

    def exposure(

        self

    ) -> dict:

        return PortfolioExposure.summary(

            self.portfolio

        )

    # =====================================================
    # DIVERSIFICATION
    # =====================================================

    def diversification(

        self

    ) -> dict:

        return PortfolioDiversification.summary(

            self.portfolio

        )

    # =====================================================
    # CONSTRAINTS
    # =====================================================

    def constraints(

        self

    ) -> dict[str, bool]:

        return PortfolioConstraints.validate(

            self.portfolio

        )

    def is_valid(

        self

    ) -> bool:

        return PortfolioConstraints.passed(

            self.portfolio

        )

    # =====================================================
    # ALLOCATION
    # =====================================================

    def allocation(

        self

    ) -> dict:

        return PortfolioAllocation.summary(

            self.portfolio

        )

    # =====================================================
    # TURNOVER
    # =====================================================

    def turnover(

        self,

        target: Portfolio

    ) -> dict:

        return PortfolioTurnover.summary(

            self.portfolio,

            target

        )

    # =====================================================
    # EXPORT
    # =====================================================

    def dataframe(

        self

    ):

        return self.portfolio.to_dataframe()

    def to_dataframe(

        self

    ):

        return self.portfolio.to_dataframe()

    def to_dict(

        self

    ) -> list[dict]:

        return self.portfolio.to_dataframe().to_dict(

            orient="records"

        )

    def symbols(

        self

    ) -> list[str]:

        return self.portfolio.symbols()

    def positions(

        self

    ) -> list[PortfolioPosition]:

        return list(

            self.portfolio

        )

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self

    ) -> dict:

        return {

            "statistics":

                self.statistics(),

            "exposure":

                self.exposure(),

            "diversification":

                self.diversification(),

            "constraints":

                self.constraints(),

            "allocation":

                self.allocation()

        }

    # =====================================================
    # SAVE
    # =====================================================

    def save(

        self,

        destination: str | Path

    ) -> None:

        self._repository.save(

            self.portfolio,

            destination

        )