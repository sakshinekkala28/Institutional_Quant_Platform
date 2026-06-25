"""
====================================================================
Institutional Quant Platform

Portfolio Repository

Author : Institutional Quant Platform

Purpose
-------
Repository responsible for loading and
transforming institutional portfolios.

Returns

Portfolio

instead of

DataFrame

====================================================================
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from core.data.loaders.csv_loader import CSVLoader

from core.data.repositories.base_repository import (

    BaseRepository

)

from core.data.validators.dataframe_validator import (

    DataFrameValidator

)

from core.models.portfolio import Portfolio

from core.models.portfolio_position import (

    PortfolioPosition

)


class PortfolioRepository(

    BaseRepository[Portfolio]

):

    """
    Institutional Portfolio Repository.
    """

    REQUIRED_COLUMNS = [

        "Security_ID",

        "Symbol",

        "Company_Name",

        "Sector",

        "Rank",

        "Alpha_Adjusted",

        "Weight",

        "Last_Close",

        "Market_Cap",

        "ADV_20D",

        "Portfolio_Date",

        "Engine_Version"

    ]

    def __init__(

        self,

        source: str | Path

    ) -> None:

        loader = CSVLoader(

            source

        )

        validator = DataFrameValidator(

            required_columns=

            self.REQUIRED_COLUMNS,

            allow_empty=False,

            allow_duplicate_rows=False,

            allow_duplicate_columns=False,

            max_null_percentage=5.0

        )

        super().__init__(

            loader=loader,

            validator=validator

        )

    # =====================================================
    # TRANSFORM
    # =====================================================

    def _transform(

        self,

        dataframe: pd.DataFrame

    ) -> Portfolio:
        
        """
        Convert DataFrame into
        Portfolio domain object.
        """

        positions: list[PortfolioPosition] = []

        for row in dataframe.itertuples(

            index=False

        ):

            positions.append(

                PortfolioPosition(

                    security_id=str(

                        row.Security_ID

                    ),

                    symbol=str(

                        row.Symbol

                    ),

                    company_name=str(

                        row.Company_Name

                    ),

                    sector=str(

                        row.Sector

                    ),

                    rank=int(

                        row.Rank

                    ),

                    alpha_adjusted=float(

                        row.Alpha_Adjusted

                    ),

                    weight=float(

                        row.Weight

                    ),

                    last_close=float(

                        row.Last_Close

                    ),

                    market_cap=float(

                        row.Market_Cap

                    ),

                    adv_20d=float(

                        row.ADV_20D

                    ),

                    portfolio_date=str(

                        row.Portfolio_Date

                    ),

                    engine_version=str(

                        row.Engine_Version

                    )

                )

            )

        return Portfolio(

            positions=positions

        )

    # =====================================================
    # SAVE
    # =====================================================

    def save(

        self,

        portfolio: Portfolio,

        destination: str | Path

    ) -> None:

        """
        Save portfolio.
        """

        dataframe = portfolio.to_dataframe()

        Path(

            destination

        ).parent.mkdir(

            parents=True,

            exist_ok=True

        )

        dataframe.to_csv(

            destination,

            index=False

        )

    # =====================================================
    # PORTFOLIO HELPERS
    # =====================================================

    def holdings(

        self

    ) -> int:

        """
        Number of holdings.
        """

        return self.load().holdings

    def total_weight(

        self

    ) -> float:

        """
        Total portfolio weight.
        """

        return self.load().total_weight

    def top_holdings(

        self,

        n: int = 10

    ) -> list[PortfolioPosition]:

        """
        Largest positions.
        """

        return self.load().top_holdings(

            n

        )

    def get_position(

        self,

        symbol: str

    ) -> PortfolioPosition | None:

        """
        Lookup by symbol.
        """

        return self.load().get(

            symbol

        )

    def sector_weights(

        self

    ) -> dict[str, float]:

        """
        Sector allocation.
        """

        return self.load().sector_weights()

    def portfolio_summary(

        self

    ) -> dict:

        """
        Portfolio statistics.
        """

        return self.load().summary()