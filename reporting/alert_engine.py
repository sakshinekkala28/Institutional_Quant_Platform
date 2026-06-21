# ==========================================================
# ALERT ENGINE
# Institutional Alerting Framework
# ==========================================================

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import pandas as pd


# ==========================================================
# ALERT CONFIGURATION
# ==========================================================

@dataclass
class AlertConfig:

    MAX_POSITION_WEIGHT: float = 0.05

    MAX_SECTOR_WEIGHT: float = 0.30

    MAX_BETA: float = 1.20

    MIN_BETA: float = 0.80

    MAX_TURNOVER: float = 0.30

    MAX_TRACKING_ERROR: float = 0.08

    MIN_CAPACITY_SCORE: float = 50


# ==========================================================
# ALERT REGISTRY
# ==========================================================

class AlertRegistry:

    def __init__(self):

        self.alerts = []

    def add(

        self,

        severity,

        category,

        message

    ):

        self.alerts.append({

            "Timestamp":

            datetime.now(),

            "Severity":

            severity,

            "Category":

            category,

            "Message":

            message

        })

    def get_alerts(self):

        return pd.DataFrame(
            self.alerts
        )
    
# ==========================================================
# PORTFOLIO ALERTS
# ==========================================================

class PortfolioAlertEngine:

    @staticmethod
    def evaluate(

        portfolio,

        registry,

        config

    ):

        max_position = (

            portfolio[
                "Target_Weight"
            ].max()

        )

        if max_position > config.MAX_POSITION_WEIGHT:

            registry.add(

                "HIGH",

                "POSITION",

                f"Position Limit Breach: "
                f"{max_position:.2%}"

            )

        sector_weights = (

            portfolio

            .groupby("Sector")

            ["Target_Weight"]

            .sum()

        )

        if sector_weights.max() > config.MAX_SECTOR_WEIGHT:

            registry.add(

                "HIGH",

                "SECTOR",

                "Sector Limit Breach"

            )

        # ==========================================================
# RISK ALERTS
# ==========================================================

class RiskAlertEngine:

    @staticmethod
    def evaluate(

        risk_report,

        registry,

        config

    ):

        beta = risk_report.get(
            "Portfolio_Beta",
            1.0
        )

        if beta > config.MAX_BETA:

            registry.add(

                "MEDIUM",

                "BETA",

                f"High Beta: {beta:.2f}"

            )

        if beta < config.MIN_BETA:

            registry.add(

                "MEDIUM",

                "BETA",

                f"Low Beta: {beta:.2f}"

            )

        tracking_error = (

            risk_report.get(
                "Tracking_Error",
                0
            )

        )

        if tracking_error > config.MAX_TRACKING_ERROR:

            registry.add(

                "HIGH",

                "TRACKING_ERROR",

                f"Tracking Error: "
                f"{tracking_error:.2%}"

            )

        # ==========================================================
# ALERT ENGINE
# ==========================================================

class AlertEngine:

    def __init__(self):

        self.config = AlertConfig()

        self.registry = AlertRegistry()

    def run(

        self,

        portfolio,

        risk_report,

        monitoring_report=None

    ):

        PortfolioAlertEngine.evaluate(

            portfolio,

            self.registry,

            self.config

        )

        RiskAlertEngine.evaluate(

            risk_report,

            self.registry,

            self.config

        )

        if monitoring_report:

            capacity_score = (

                monitoring_report.get(
                    "Capacity_Score",
                    100
                )

            )

            if (

                capacity_score

                <

                self.config.MIN_CAPACITY_SCORE

            ):

                self.registry.add(

                    "HIGH",

                    "CAPACITY",

                    f"Capacity Score: "
                    f"{capacity_score}"

                )

        alerts = (

            self.registry

            .get_alerts()

        )

        print(

            f"\n✓ Alerts Generated: "

            f"{len(alerts)}"

        )

        return alerts