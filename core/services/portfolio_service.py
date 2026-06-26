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

        """
        BaseService execution entrypoint.
        """

        return self.load()

    # =====================================================
    # LOAD
    # =====================================================

    def load(

        self,

        reload: bool = False

    ) -> Portfolio:

        """
        Load portfolio from repository.
        """

        if (

            self._portfolio is None

            or reload

        ):

            self._portfolio = (

                self._repository.load()

            )

        return self._portfolio

    def reload(

        self

    ) -> Portfolio:

        """
        Force reload.
        """

        return self.load(

            reload=True

        )

    # =====================================================
    # ACCESS
    # =====================================================

    @property
    def portfolio(

        self

    ) -> Portfolio:

        """
        Loaded portfolio.
        """

        return self.load()

    @property
    def holdings(

        self

    ) -> int:

        """
        Portfolio holdings.
        """

        return self.portfolio.holdings

    @property
    def total_weight(

        self

    ) -> float:

        """
        Portfolio total weight.
        """

        return self.portfolio.total_weight
    
    # =====================================================
    # STATISTICS
    # =====================================================

    def statistics(

        self

    ) -> dict:

        """
        Portfolio statistics.
        """

        return PortfolioStatistics.summary(

            self.portfolio

        )

    # =====================================================
    # EXPOSURE
    # =====================================================

    def exposure(

        self

    ) -> dict:

        """
        Portfolio exposure.
        """

        return PortfolioExposure.summary(

            self.portfolio

        )

    # =====================================================
    # DIVERSIFICATION
    # =====================================================

    def diversification(

        self

    ) -> dict:

        """
        Portfolio diversification.
        """

        return PortfolioDiversification.summary(

            self.portfolio

        )

    # =====================================================
    # CONSTRAINTS
    # =====================================================

    def constraints(

        self

    ) -> dict[str, bool]:

        """
        Portfolio constraint checks.
        """

        return PortfolioConstraints.validate(

            self.portfolio

        )

    def is_valid(

        self

    ) -> bool:

        """
        Overall portfolio validation.
        """

        return PortfolioConstraints.passed(

            self.portfolio

        )

    # =====================================================
    # ALLOCATION
    # =====================================================

    def allocation(

        self

    ) -> dict:

        """
        Portfolio allocation.
        """

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

        """
        Portfolio turnover summary.
        """

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

        """
        Export portfolio as DataFrame.
        """

        return self.portfolio.to_dataframe()

    def symbols(

        self

    ) -> list[str]:

        """
        Portfolio symbols.
        """

        return self.portfolio.symbols()

    def positions(

        self

    ):

        """
        Portfolio positions.
        """

        return list(

            self.portfolio

        )

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self

    ) -> dict:

        """
        Complete portfolio summary.
        """

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

        """
        Save portfolio.
        """

        self._repository.save(

            self.portfolio,

            destination

        )