# ==========================================================
# PORTFOLIO ENGINE
# Institutional Portfolio Construction Engine
# ==========================================================

from __future__ import annotations

import numpy as np
import pandas as pd

# ==========================================================
# DATA VALIDATION
# ==========================================================

class PortfolioDataValidator:

    REQUIRED_COLUMNS = {

        "ADV_20D": 1_000_000,

        "Beta": 1.0,

        "Volatility_252D": 0.25,

        "Market_Cap": 1_000_000_000,

        "Sector": "UNKNOWN"

    }

    @classmethod
    def ensure_required_columns(
        cls,
        df: pd.DataFrame
    ) -> pd.DataFrame:

        df = df.copy()

        for col, default in cls.REQUIRED_COLUMNS.items():

            if col not in df.columns:

                df[col] = default

        return df

# ==========================================================
# PORTFOLIO CONSTRUCTOR
# ==========================================================

class PortfolioConstructor:

    def __init__(
        self,
        target_holdings=40
    ):

        self.target_holdings = target_holdings

    def select_holdings(
        self,
        universe
    ):

        universe = (

            universe

            .sort_values(

                "Selection_Score",

                ascending=False

            )

            .head(
                self.target_holdings
            )

            .copy()

        )

        universe["Rank"] = np.arange(

            1,

            len(universe) + 1

        )

        return universe


# ==========================================================
# PORTFOLIO HEALTH CHECK
# ==========================================================

class PortfolioHealthCheck:

    @staticmethod
    def validate(universe):

        if len(universe) == 0:

            raise ValueError(
                "Universe Empty"
            )
        
        if "Selection_Score" not in universe.columns:

            raise ValueError(
                "Selection_Score column missing"
            )


        if universe[
            "Selection_Score"
        ].isna().all():

            raise ValueError(
                "Selection Score Missing"
            )

        return True
    
# ==========================================================
# RISK PARITY ALLOCATOR
# ==========================================================

class RiskParityAllocator:

    @staticmethod
    def allocate(
        portfolio
    ):

        portfolio[
            "Risk_Adjusted_Score"
        ] = (

            portfolio[
                "Selection_Score"
            ]

            /

            np.sqrt(

                portfolio[
                    "Volatility_252D"
                ]

            )

        )

        portfolio[
            "Liquidity_Capacity"
        ] = (

            portfolio[
                "ADV_20D"
            ]

            /

            portfolio[
                "ADV_20D"
            ].median()

        )

        portfolio[
            "Liquidity_Capacity"
        ] = (

            portfolio[
                "Liquidity_Capacity"
            ]

            .clip(
                lower=0.50,
                upper=2.00
            )

        )

        portfolio[
            "Risk_Adjusted_Score"
        ] *= (

            portfolio[
                "Liquidity_Capacity"
            ] ** 0.25

        )

        portfolio[
            "Risk_Parity_Score"
        ] = (

            portfolio[
                "Risk_Adjusted_Score"
            ]

            /

            portfolio[
                "Volatility_252D"
            ]

        )

        portfolio[
            "Target_Weight"
        ] = (

            portfolio[
                "Risk_Parity_Score"
            ]

            /

            portfolio[
                "Risk_Parity_Score"
            ].sum()

        )

        return portfolio
    
# ==========================================================
# CONSTRAINT ENGINE
# ==========================================================

class ConstraintEngine:

    @staticmethod
    def normalize_weights(
        portfolio
    ):

        total = portfolio[
            "Target_Weight"
        ].sum()

        if total > 0:

            portfolio[
                "Target_Weight"
            ] /= total

        return portfolio

    @staticmethod
    def position_cap(
        portfolio,
        max_position=0.05
    ):

        for _ in range(20):

            capped = (

                portfolio[
                    "Target_Weight"
                ]

                >

                max_position

            )

            if not capped.any():
                break

            excess = (

                portfolio.loc[
                    capped,
                    "Target_Weight"
                ]

                -

                max_position

            ).sum()

            portfolio.loc[
                capped,
                "Target_Weight"
            ] = max_position

            remaining = ~capped

            portfolio.loc[
                remaining,
                "Target_Weight"
            ] += (

                excess

                *

                portfolio.loc[
                    remaining,
                    "Target_Weight"
                ]

                /

                portfolio.loc[
                    remaining,
                    "Target_Weight"
                ].sum()

            )

        return ConstraintEngine.normalize_weights(
            portfolio
        )

    @staticmethod
    def sector_cap(
        portfolio,
        max_sector_weight=0.30
    ):

        sector_weights = (

            portfolio

            .groupby(
                "Sector"
            )

            ["Target_Weight"]

            .sum()

        )

        for sector in sector_weights.index:

            weight = sector_weights[
                sector
            ]

            if weight > max_sector_weight:

                scale = (

                    max_sector_weight

                    /

                    weight

                )

                portfolio.loc[

                    portfolio[
                        "Sector"
                    ] == sector,

                    "Target_Weight"

                ] *= scale

        return ConstraintEngine.normalize_weights(
            portfolio
        )

# ==========================================================
# BLACK LITTERMAN
# ==========================================================

class BlackLittermanOverlay:

    @staticmethod
    def apply(
        portfolio,
        alpha_weight=0.90,
        market_weight=0.10
    ):

        portfolio[
            "Market_Weight"
        ] = (

            portfolio[
                "Market_Cap"
            ]

            /

            portfolio[
                "Market_Cap"
            ].sum()

        )

        portfolio[
            "Target_Weight"
        ] = (

            alpha_weight

            *

            portfolio[
                "Target_Weight"
            ]

            +

            market_weight

            *

            portfolio[
                "Market_Weight"
            ]

        )

        portfolio[
            "Target_Weight"
        ] /= (

            portfolio[
                "Target_Weight"
            ].sum()

        )

        return portfolio


# ==========================================================
# PORTFOLIO ENGINE
# ==========================================================

class PortfolioEngine:

    def __init__(

        self,

        target_holdings=40

    ):

        self.target_holdings = target_holdings

    def construct(
        self,
        alpha_universe
    ):

        PortfolioHealthCheck.validate(
            alpha_universe
        )

        alpha_universe = (
            PortfolioDataValidator
            .ensure_required_columns(
                alpha_universe
            )
        )

        portfolio = (

            PortfolioConstructor(

                self.target_holdings

            )

            .select_holdings(
                alpha_universe
            )

        )

        portfolio = (

            RiskParityAllocator

            .allocate(
                portfolio
            )

        )

        portfolio = (

            ConstraintEngine

            .position_cap(
                portfolio,
                max_position=0.05
            )

        )

        portfolio = (

            ConstraintEngine

            .sector_cap(
                portfolio,
                max_sector_weight=0.30
            )

        )

        portfolio = (

            BlackLittermanOverlay

            .apply(
                portfolio
            )

        )

        print(
            "\n✓ Portfolio Constructed"
        )

        print(
            f"Holdings: {len(portfolio)}"
        )

        print(
            "Weight Sum:",
            round(
                portfolio[
                    "Target_Weight"
                ].sum(),
                4
            )
        )

        return portfolio