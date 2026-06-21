# ==========================================================
# REPORTING ENGINE
# Institutional Reporting Platform
# ==========================================================

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import pandas as pd


# ==========================================================
# REPORT CONFIG
# ==========================================================

@dataclass
class ReportConfig:

    REPORT_OWNER: str = "Institutional Quant Platform"

    REPORT_VERSION: str = "1.0"

    COMPANY_NAME: str = "Institutional Quant Research"


# ==========================================================
# REPORT REGISTRY
# ==========================================================

class ReportRegistry:

    def __init__(self):

        self.reports = {}

    def register(
        self,
        report_name,
        report_data
    ):

        self.reports[
            report_name
        ] = report_data

    def get(
        self,
        report_name
    ):

        return self.reports.get(
            report_name
        )

    def list_reports(self):

        return list(
            self.reports.keys()
        )
    
# ==========================================================
# PORTFOLIO REPORT
# ==========================================================

class PortfolioReport:

    @staticmethod
    def build(
        portfolio
    ):

        return {

            "Holdings":

            len(portfolio),

            "Weight_Sum":

            portfolio[
                "Target_Weight"
            ].sum(),

            "Max_Position":

            portfolio[
                "Target_Weight"
            ].max(),

            "Largest_Sector":

            portfolio.groupby(
                "Sector"
            )[
                "Target_Weight"
            ]

            .sum()

            .idxmax()

        }


# ==========================================================
# RISK REPORT
# ==========================================================

class RiskReport:

    @staticmethod
    def build(
        risk_report
    ):

        return {

            "Portfolio_Beta":

            risk_report.get(
                "Portfolio_Beta"
            ),

            "HHI":

            risk_report.get(
                "HHI"
            ),

            "Effective_Holdings":

            risk_report.get(
                "Effective_Holdings"
            )

        }
    
# ==========================================================
# PERFORMANCE REPORT
# ==========================================================

class PerformanceReport:

    @staticmethod
    def build(
        performance
    ):

        return {

            "Annual_Return":

            performance[
                "Performance"
            ][
                "Annual_Return"
            ],

            "Annual_Volatility":

            performance[
                "Performance"
            ][
                "Annual_Volatility"
            ]

        }


# ==========================================================
# EXECUTION REPORT
# ==========================================================

class ExecutionReport:

    @staticmethod
    def build(
        execution_df
    ):

        return {

            "Trades":

            len(execution_df),

            "Average_Slippage":

            execution_df[
                "Slippage_bps"
            ].mean(),

            "Average_Impact":

            execution_df[
                "Market_Impact_bps"
            ].mean()

        }
    
# ==========================================================
# CIO DASHBOARD
# ==========================================================

class CIODashboard:

    @staticmethod
    def build(
        portfolio_report,
        risk_report,
        performance_report
    ):

        return {

            "Date":

            datetime.now()

            .strftime(
                "%Y-%m-%d"
            ),

            "Holdings":

            portfolio_report[
                "Holdings"
            ],

            "Portfolio_Beta":

            risk_report[
                "Portfolio_Beta"
            ],

            "Annual_Return":

            performance_report[
                "Annual_Return"
            ],

            "Annual_Volatility":

            performance_report[
                "Annual_Volatility"
            ]

        }


# ==========================================================
# REPORTING ENGINE
# ==========================================================

class ReportingEngine:

    def __init__(self):

        self.registry = (
            ReportRegistry()
        )

    def generate(

        self,

        portfolio,

        risk,

        performance,

        execution=None

    ):

        portfolio_report = (

            PortfolioReport

            .build(
                portfolio
            )

        )

        risk_report = (

            RiskReport

            .build(
                risk
            )

        )

        performance_report = (

            PerformanceReport

            .build(
                performance
            )

        )

        dashboard = (

            CIODashboard

            .build(

                portfolio_report,

                risk_report,

                performance_report

            )

        )

        self.registry.register(
            "portfolio",
            portfolio_report
        )

        self.registry.register(
            "risk",
            risk_report
        )

        self.registry.register(
            "performance",
            performance_report
        )

        self.registry.register(
            "dashboard",
            dashboard
        )

        if execution is not None:

            execution_report = (

                ExecutionReport

                .build(
                    execution
                )

            )

            self.registry.register(
                "execution",
                execution_report
            )

        print(
            "\n✓ Reporting Complete"
        )

        return self.registry.reports