# ==========================================================
# MONITORING ENGINE
# Institutional Portfolio Monitoring
# ==========================================================

from __future__ import annotations

import pandas as pd
import numpy as np


# ==========================================================
# DRIFT MONITOR
# ==========================================================

class DriftMonitor:

    @staticmethod
    def weight_drift(
        current_portfolio,
        target_portfolio
    ):

        drift = current_portfolio.merge(

            target_portfolio,

            on="Symbol",

            how="outer",

            suffixes=(
                "_Current",
                "_Target"
            )

        )

        drift = drift.fillna(0)

        drift["Weight_Drift"] = (

            drift["Target_Weight"]

            -

            drift["Current_Weight"]

        )

        return drift

    @staticmethod
    def max_drift(
        drift_df
    ):

        return (

            drift_df[
                "Weight_Drift"
            ]

            .abs()

            .max()

        )
    
# ==========================================================
# SECTOR MONITOR
# ==========================================================

class SectorMonitor:

    @staticmethod
    def sector_exposure(
        portfolio
    ):

        return (

            portfolio

            .groupby("Sector")

            ["Target_Weight"]

            .sum()

            .sort_values(
                ascending=False
            )

        )

    @staticmethod
    def largest_sector(
        portfolio
    ):

        exposure = (

            SectorMonitor

            .sector_exposure(
                portfolio
            )

        )

        return exposure.index[0]


# ==========================================================
# EXPOSURE MONITOR
# ==========================================================

class ExposureMonitor:

    @staticmethod
    def factor_exposure(
        portfolio
    ):

        factors = [

            "Signal_Factor",

            "Momentum_Factor",

            "Quality_Factor",

            "Value_Factor",

            "Growth_Factor",

            "LowVol_Factor"

        ]

        exposures = {}

        for factor in factors:

            if factor not in portfolio.columns:
                continue

            exposures[factor] = (

                portfolio[factor]

                *

                portfolio[
                    "Target_Weight"
                ]

            ).sum()

        return exposures
    
# ==========================================================
# LIQUIDITY MONITOR
# ==========================================================

class LiquidityMonitor:

    @staticmethod
    def average_adv(
        portfolio
    ):

        if "ADV_20D" not in portfolio.columns:

            return np.nan

        return portfolio[
            "ADV_20D"
        ].mean()

    @staticmethod
    def lowest_liquidity(
        portfolio
    ):

        if "ADV_20D" not in portfolio.columns:

            return np.nan

        return portfolio[
            "ADV_20D"
        ].min()


# ==========================================================
# CAPACITY MONITOR
# ==========================================================

class CapacityMonitor:

    @staticmethod
    def participation_rate(
        portfolio
    ):

        if (

            "Trade_Value"

            not in portfolio.columns

        ):

            return np.nan

        return (

            portfolio[
                "Trade_Value"
            ]

            /

            portfolio[
                "ADV_20D"
            ]

        ).mean()

    @staticmethod
    def capacity_score(
        portfolio
    ):

        score = 100

        if "ADV_20D" not in portfolio.columns:

            return score

        avg_adv = (

            portfolio[
                "ADV_20D"
            ].median()

        )

        score -= min(

            avg_adv / 1_000_000,

            50

        )

        return round(
            score,
            2
        )
    
# ==========================================================
# ALERT ENGINE
# ==========================================================

class AlertEngine:

    @staticmethod
    def generate(
        portfolio
    ):

        alerts = []

        max_position = (

            portfolio[
                "Target_Weight"
            ].max()

        )

        if max_position > 0.05:

            alerts.append(

                f"Position Limit Breach "
                f"({max_position:.2%})"

            )

        sector_weights = (

            portfolio

            .groupby("Sector")

            ["Target_Weight"]

            .sum()

        )

        if sector_weights.max() > 0.30:

            alerts.append(

                "Sector Limit Breach"

            )

        return alerts


# ==========================================================
# MASTER MONITORING ENGINE
# ==========================================================

class MonitoringEngine:

    def run(
        self,
        portfolio
    ):

        report = {}

        report["Largest_Sector"] = (

            SectorMonitor

            .largest_sector(
                portfolio
            )

        )

        report["Factor_Exposure"] = (

            ExposureMonitor

            .factor_exposure(
                portfolio
            )

        )

        report["Capacity_Score"] = (

            CapacityMonitor

            .capacity_score(
                portfolio
            )

        )

        report["Alerts"] = (

            AlertEngine

            .generate(
                portfolio
            )

        )

        print(
            "\n✓ Monitoring Complete"
        )

        print(
            f"Largest Sector: "
            f"{report['Largest_Sector']}"
        )

        print(
            f"Capacity Score: "
            f"{report['Capacity_Score']}"
        )

        print(
            f"Alerts: "
            f"{len(report['Alerts'])}"
        )

        return report