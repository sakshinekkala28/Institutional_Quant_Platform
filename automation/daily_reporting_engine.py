from __future__ import annotations

import logging

from pathlib import Path

from datetime import datetime

import pandas as pd

from core.settings import settings

# ==========================================================
# LOGGING
# ==========================================================

logging.basicConfig(

    level=logging.INFO,

    format=(

        "%(asctime)s | "

        "%(levelname)s | "

        "%(message)s"

    )

)

logger = logging.getLogger(

    __name__

)

# ==========================================================
# PATHS
# ==========================================================

ROOT_DIR = (

    settings
    .environment
    .ROOT_DIR

)

PERFORMANCE_DIR = (

    ROOT_DIR

    / "data"

    / "performance"

)

REPORT_DIR = (

    ROOT_DIR

    / "data"

    / "reports"

)

DAILY_REPORT_FILE = (

    REPORT_DIR

    / "daily_report_summary.csv"

)

EXECUTIVE_FILE = (

    PERFORMANCE_DIR

    / "executive_dashboard.csv"

)

FORECAST_FILE = (

    PERFORMANCE_DIR

    / "performance_forecast.csv"

)

COMMITTEE_FILE = (

    PERFORMANCE_DIR

    / "investment_committee_pack.csv"

)

# ==========================================================
# REPOSITORY
# ==========================================================

class DailyReportingRepository:

    @staticmethod
    def load_executive():

        return pd.read_csv(

            EXECUTIVE_FILE

        )

    @staticmethod
    def load_forecast():

        return pd.read_csv(

            FORECAST_FILE

        )

    @staticmethod
    def load_committee():

        return pd.read_csv(

            COMMITTEE_FILE

        )
    
# ==========================================================
# VALIDATOR
# ==========================================================

class DailyReportingValidator:

    @staticmethod
    def validate(

        executive,

        forecast,

        committee

    ):

        if executive.empty:

            raise ValueError(

                "Executive Dashboard Empty"

            )

        if forecast.empty:

            raise ValueError(

                "Forecast Empty"

            )

        if committee.empty:

            raise ValueError(

                "Committee Pack Empty"

            )
        
# ==========================================================
# DAILY SUMMARY BUILDER
# ==========================================================

class DailySummaryBuilder:

    @staticmethod
    def build(

        executive,

        forecast,

        committee

    ):

        logger.info(

            "Building Daily Summary"

        )

        metrics = {}

        for _, row in executive.iterrows():

            metrics[

                row["Metric"]

            ] = row["Value"]

        forecast_row = (

            forecast

            .iloc[0]

        )

        return pd.DataFrame(

            [

                {

                    "Date":

                        datetime.now()

                        .strftime(

                            "%Y-%m-%d"

                        ),

                    "Pack_Score":

                        metrics.get(

                            "Pack_Score"

                        ),

                    "Committee_View":

                        metrics.get(

                            "Committee_View"

                        ),

                    "Recommendation":

                        metrics.get(

                            "Recommendation"

                        ),

                    "Forecast_Regime":

                        forecast_row[

                            "Forecast_Regime"

                        ],

                    "Forecast_Confidence":

                        forecast_row[

                            "Forecast_Confidence"

                        ],

                    "Expected_Return_12M":

                        forecast_row[

                            "Expected_Return_12M"

                        ]

                }

            ]

        )
    
# ==========================================================
# DAILY REPORT EXPORTER
# ==========================================================

class DailyReportExporter:

    @staticmethod
    def export(

        summary_df

    ):

        logger.info(

            "Exporting Daily Summary"

        )

        summary_df.to_csv(

            DAILY_REPORT_FILE,

            index=False

        )

        logger.info(

            "Daily Summary Exported"

        )

        return DAILY_REPORT_FILE
    
# ==========================================================
# REPORT HEALTH ENGINE
# ==========================================================

class ReportHealthEngine:

    @staticmethod
    def evaluate(

        forecast

    ):

        logger.info(

            "Evaluating Report Health"

        )

        row = (

            forecast

            .iloc[0]

        )

        confidence = (

            row[

                "Forecast_Confidence"

            ]

        )

        sharpe = (

            row[

                "Expected_Sharpe"

            ]

        )

        if (

            confidence >= 80

            and

            sharpe >= 1.50

        ):

            return "EXCELLENT"

        elif (

            confidence >= 70

            and

            sharpe >= 1.00

        ):

            return "GOOD"

        elif (

            confidence >= 60

        ):

            return "MODERATE"

        return "WEAK"
    
# ==========================================================
# SUMMARY FORMATTER
# ==========================================================

class SummaryFormatter:

    @staticmethod
    def display(

        summary_df,

        health

    ):

        row = (

            summary_df

            .iloc[0]

        )

        print()

        print(

            "=" * 80

        )

        print(

            "DAILY EXECUTIVE REPORT"

        )

        print(

            "=" * 80

        )

        print(

            f"Date: "

            f"{row['Date']}"

        )

        print(

            f"Pack Score: "

            f"{row['Pack_Score']}"

        )

        print(

            f"Committee View: "

            f"{row['Committee_View']}"

        )

        print(

            f"Recommendation: "

            f"{row['Recommendation']}"

        )

        print(

            f"Forecast Regime: "

            f"{row['Forecast_Regime']}"

        )

        print(

            f"Forecast Confidence: "

            f"{row['Forecast_Confidence']:.2f}"

        )

        print(

            f"Expected Return (12M): "

            f"{float(row['Expected_Return_12M']):.2%}"

        )

        print(

            f"Portfolio Health: "

            f"{health}"

        )

        print(

            "=" * 80

        )

# ==========================================================
# DAILY METRICS ENGINE
# ==========================================================

class DailyMetricsEngine:

    @staticmethod
    def build(

        forecast

    ):

        row = (

            forecast

            .iloc[0]

        )

        return {

            "Forecast_Regime":

                row[

                    "Forecast_Regime"

                ],

            "Forecast_Confidence":

                row[

                    "Forecast_Confidence"

                ],

            "Forecast_Risk_Grade":

                row[

                    "Forecast_Risk_Grade"

                ],

            "Recommendation":

                row[

                    "Forecast_Recommendation"

                ]

        }
    
# ==========================================================
# DASHBOARD SNAPSHOT ENGINE
# ==========================================================

class DashboardSnapshotEngine:

    @staticmethod
    def build(

        summary_df,

        health

    ):

        logger.info(

            "Building Dashboard Snapshot"

        )

        row = (

            summary_df

            .iloc[0]

        )

        return {

            "Date":

                row["Date"],

            "Pack_Score":

                row["Pack_Score"],

            "Committee_View":

                row["Committee_View"],

            "Recommendation":

                row["Recommendation"],

            "Forecast_Regime":

                row["Forecast_Regime"],

            "Portfolio_Health":

                health

        }
    
# ==========================================================
# REPORT ARCHIVE ENGINE
# ==========================================================

class ReportArchiveEngine:

    @staticmethod
    def archive(

        summary_df

    ):

        logger.info(

            "Archiving Daily Report"

        )

        archive_dir = (

            REPORT_DIR

            / "archive"

        )

        archive_dir.mkdir(

            parents=True,

            exist_ok=True

        )

        archive_file = (

            archive_dir

            /

            f"daily_report_"

            f"{datetime.now().strftime('%Y%m%d')}"

            f".csv"

        )

        summary_df.to_csv(

            archive_file,

            index=False

        )

        return archive_file
    
# ==========================================================
# DAILY REPORTING ENGINE
# ==========================================================

class DailyReportingEngine:

    def run(

        self

    ):

        logger.info(

            "Starting Daily Reporting"

        )

        executive = (

            DailyReportingRepository

            .load_executive()

        )

        forecast = (

            DailyReportingRepository

            .load_forecast()

        )

        committee = (

            DailyReportingRepository

            .load_committee()

        )

        DailyReportingValidator.validate(

            executive,

            forecast,

            committee

        )

        summary_df = (

            DailySummaryBuilder

            .build(

                executive,

                forecast,

                committee

            )

        )

        health = (

            ReportHealthEngine

            .evaluate(

                forecast

            )

        )

        snapshot = (

            DashboardSnapshotEngine

            .build(

                summary_df,

                health

            )

        )

        archive_file = (

            ReportArchiveEngine

            .archive(

                summary_df

            )

        )

        report_file = (

            DailyReportExporter

            .export(

                summary_df

            )

        )

        metrics = (

            DailyMetricsEngine

            .build(

                forecast

            )

        )

        return {

            "summary":

                summary_df,

            "health":

                health,

            "snapshot":

                snapshot,

            "archive":

                archive_file,

            "report":

                report_file,

            "metrics":

                metrics

        }
    
# ==========================================================
# DAILY DASHBOARD ENGINE
# ==========================================================

class DailyDashboardEngine:

    @staticmethod
    def build(

        result

    ):

        return pd.DataFrame(

            [

                {

                    "Metric":

                        "Portfolio_Health",

                    "Value":

                        result["health"]

                },

                {

                    "Metric":

                        "Forecast_Regime",

                    "Value":

                        result["metrics"]["Forecast_Regime"]

                },

                {

                    "Metric":

                        "Recommendation",

                    "Value":

                        result["metrics"]["Recommendation"]

                },

                {

                    "Metric":

                        "Forecast_Confidence",

                    "Value":

                        result["metrics"]["Forecast_Confidence"]

                }

            ]

        )

# ==========================================================
# DAILY DASHBOARD EXPORTER
# ==========================================================

DAILY_DASHBOARD_FILE = (

    REPORT_DIR

    / "daily_dashboard.csv"

)

class DailyDashboardExporter:

    @staticmethod
    def export(

        dashboard_df

    ):

        logger.info(

            "Exporting Daily Dashboard"

        )

        dashboard_df.to_csv(

            DAILY_DASHBOARD_FILE,

            index=False

        )

        logger.info(

            "Daily Dashboard Exported"

        )

        return DAILY_DASHBOARD_FILE

# ==========================================================
# REPORT STATUS ENGINE
# ==========================================================

class ReportStatusEngine:

    @staticmethod
    def build(

        result

    ):

        return {

            "Health":

                result["health"],

            "Report_File":

                str(

                    result["report"]

                ),

            "Archive_File":

                str(

                    result["archive"]

                ),

            "Forecast_Regime":

                result["metrics"][

                    "Forecast_Regime"

                ],

            "Recommendation":

                result["metrics"][

                    "Recommendation"

                ]

        }

# ==========================================================
# RUNNER
# ==========================================================

def run_example():

    result = (

        DailyReportingEngine()

        .run()

    )

    dashboard_df = (

        DailyDashboardEngine

        .build(

            result

        )

    )

    dashboard_file = (

        DailyDashboardExporter

        .export(

            dashboard_df

        )

    )

    SummaryFormatter.display(

        result["summary"],

        result["health"]

    )

    status = (

        ReportStatusEngine

        .build(

            result

        )

    )

    print()

    print(

        "Generated Files"

    )

    print(

        "-" * 40

    )

    print(

        f"Daily Report: "

        f"{status['Report_File']}"

    )

    print(

        f"Archive: "

        f"{status['Archive_File']}"

    )

    print(

        f"Dashboard: "

        f"{dashboard_file}"

    )

    print(

        "-" * 40

    )

# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    run_example()