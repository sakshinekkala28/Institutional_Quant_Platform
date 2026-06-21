# ==========================================================
# PERFORMANCE ENGINE
# Institutional Performance Attribution
# ==========================================================

from __future__ import annotations

import numpy as np
import pandas as pd


# ==========================================================
# PERFORMANCE ANALYTICS
# ==========================================================

class PerformanceAnalytics:

    @staticmethod
    def cumulative_return(
        returns
    ):

        return (

            (1 + returns)

            .cumprod()

            - 1

        )

    @staticmethod
    def annualized_return(
        returns
    ):

        cumulative = (

            (1 + returns)

            .prod()

        )

        years = (

            len(returns)

            / 252

        )

        return (

            cumulative

            ** (1 / years)

            - 1

        )

    @staticmethod
    def annualized_volatility(
        returns
    ):

        return (

            returns.std()

            * np.sqrt(252)

        )
    
# ==========================================================
# SECTOR ATTRIBUTION
# ==========================================================

class SectorAttributionEngine:

    @staticmethod
    def calculate(
        portfolio
    ):

        attribution = (

            portfolio

            .groupby("Sector")

            .agg({

                "Target_Weight":"sum",

                "Expected_Return":"mean"

            })

            .reset_index()

        )

        attribution[
            "Contribution"
        ] = (

            attribution[
                "Target_Weight"
            ]

            *

            attribution[
                "Expected_Return"
            ]

        )

        return attribution

    @staticmethod
    def top_contributors(
        attribution,
        n=5
    ):

        return (

            attribution

            .sort_values(

                "Contribution",

                ascending=False

            )

            .head(n)

        )
    
# ==========================================================
# FACTOR ATTRIBUTION
# ==========================================================

class FactorAttributionEngine:

    FACTORS = [

        "Signal_Factor",

        "Momentum_Factor",

        "Quality_Factor",

        "Value_Factor",

        "Growth_Factor",

        "Liquidity_Factor",

        "LowVol_Factor"

    ]

    @classmethod
    def calculate(
        cls,
        portfolio
    ):

        exposures = []

        for factor in cls.FACTORS:

            if factor not in portfolio.columns:
                continue

            exposure = (

                portfolio[factor]

                *

                portfolio[
                    "Target_Weight"
                ]

            ).sum()

            exposures.append({

                "Factor":
                factor,

                "Exposure":
                exposure

            })

        return pd.DataFrame(
            exposures
        )

    @staticmethod
    def strongest_factor(
        factor_report
    ):

        idx = (

            factor_report[
                "Exposure"
            ]

            .idxmax()

        )

        return factor_report.loc[idx]
    
# ==========================================================
# CIO DASHBOARD
# ==========================================================

class CIODashboard:

    @staticmethod
    def build(
        portfolio,
        performance_report,
        factor_report,
        sector_report
    ):

        dashboard = {

            "Portfolio_Value":

            portfolio.get(
                "Portfolio_Value",
                pd.Series([0])
            ).sum(),

            "Annual_Return":

            performance_report[
                "Annual_Return"
            ],

            "Annual_Volatility":

            performance_report[
                "Annual_Volatility"
            ],

            "Top_Factor":

            factor_report.sort_values(

                "Exposure",

                ascending=False

            )

            .iloc[0]["Factor"],

            "Top_Sector":

            sector_report.sort_values(

                "Contribution",

                ascending=False

            )

            .iloc[0]["Sector"]

        }

        return dashboard


# ==========================================================
# PERFORMANCE ENGINE
# ==========================================================

class PerformanceEngine:

    def evaluate(
        self,
        portfolio,
        returns
    ):

        performance_report = {

            "Annual_Return":

            PerformanceAnalytics
            .annualized_return(
                returns
            ),

            "Annual_Volatility":

            PerformanceAnalytics
            .annualized_volatility(
                returns
            )

        }

        factor_report = (

            FactorAttributionEngine

            .calculate(
                portfolio
            )

        )

        sector_report = (

            SectorAttributionEngine

            .calculate(
                portfolio
            )

        )

        dashboard = (

            CIODashboard

            .build(

                portfolio,

                performance_report,

                factor_report,

                sector_report

            )

        )

        print(
            "\n✓ Performance Evaluation Complete"
        )

        return {

            "Performance":
            performance_report,

            "Factor_Report":
            factor_report,

            "Sector_Report":
            sector_report,

            "Dashboard":
            dashboard

        }