from __future__ import annotations

import logging

from pathlib import Path

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

MONITORING_DIR = (

    ROOT_DIR

    / "data"

    / "monitoring"

)

HISTORY_DIR = (

    MONITORING_DIR

    / "history"

)

TREND_FILE = (

    MONITORING_DIR

    / "monitor_trends.csv"

)

TREND_DASHBOARD_FILE = (

    MONITORING_DIR

    / "monitor_trend_dashboard.csv"

)

# ==========================================================
# REPOSITORY
# ==========================================================

class TrendRepository:

    @staticmethod
    def load_history():

        logger.info(

            "Loading Monitor History"

        )

        files = sorted(

            HISTORY_DIR.glob(

                "monitor_*.csv"

            )

        )

        if not files:

            return []

        return files
    
# ==========================================================
# VALIDATOR
# ==========================================================

class TrendValidator:

    @staticmethod
    def validate(

        files

    ):

        if not files:

            raise ValueError(

                "No Monitoring History Found"

            )

        logger.info(

            "Trend Validation Passed"

        )

# ==========================================================
# SEVERITY MAPPING
# ==========================================================

class SeverityMapper:

    MAP = {

        "NORMAL": 0,

        "WATCH": 1,

        "WARNING": 2,

        "CRITICAL": 3

    }

    @classmethod
    def score(

        cls,

        status

    ):

        return cls.MAP.get(

            str(status),

            0

        )

# ==========================================================
# HISTORY LOADER ENGINE
# ==========================================================

class HistoryLoaderEngine:

    @staticmethod
    def load(

        files

    ):

        logger.info(

            "Loading Historical Files"

        )

        records = []

        for file in files:

            df = pd.read_csv(

                file

            )

            row = df.iloc[0]

            records.append(

                {

                    "Date":

                        row["Date"],

                    "Status":

                        row["Overall_Status"]

                }

            )

        return pd.DataFrame(

            records

        )
    
# ==========================================================
# TREND CALCULATION ENGINE
# ==========================================================

class TrendCalculationEngine:

    @staticmethod
    def calculate(

        history

    ):

        logger.info(

            "Calculating Trend Scores"

        )

        history = (

            history

            .copy()

        )

        history[

            "Severity_Score"

        ] = (

            history[

                "Status"

            ]

            .apply(

                SeverityMapper.score

            )

        )

        return history

# ==========================================================
# SEVERITY TREND ENGINE
# ==========================================================

class SeverityTrendEngine:

    @staticmethod
    def build(

        history

    ):

        logger.info(

            "Building Severity Trend"

        )

        latest = (

            history

            .iloc[-1]

        )

        avg_score = (

            history[

                "Severity_Score"

            ]

            .mean()

        )

        worst_score = (

            history[

                "Severity_Score"

            ]

            .max()

        )

        return pd.DataFrame(

            [

                {

                    "Metric":

                        "Latest_Status",

                    "Value":

                        latest["Status"]

                },

                {

                    "Metric":

                        "Average_Severity",

                    "Value":

                        round(

                            avg_score,

                            2

                        )

                },

                {

                    "Metric":

                        "Worst_Severity",

                    "Value":

                        worst_score

                },

                {

                    "Metric":

                        "Observation_Count",

                    "Value":

                        len(

                            history

                        )

                }

            ]

        )
    
# ==========================================================
# TREND DIRECTION ENGINE
# ==========================================================

class TrendDirectionEngine:

    @staticmethod
    def determine(

        history

    ):

        logger.info(

            "Determining Trend Direction"

        )

        if len(history) < 2:

            return "INSUFFICIENT_HISTORY"

        first = (

            history

            .iloc[0][

                "Severity_Score"

            ]

        )

        last = (

            history

            .iloc[-1][

                "Severity_Score"

            ]

        )

        if last > first:

            return "DETERIORATING"

        if last < first:

            return "IMPROVING"

        return "STABLE"
    
# ==========================================================
# ALERT FREQUENCY ENGINE
# ==========================================================

class AlertFrequencyEngine:

    @staticmethod
    def build(

        history

    ):

        logger.info(

            "Calculating Alert Frequency"

        )

        counts = (

            history

            .groupby(

                "Status"

            )

            .size()

            .reset_index(

                name="Count"

            )

        )

        return counts
    
# ==========================================================
# CATEGORY TREND ENGINE
# ==========================================================

class CategoryTrendEngine:

    @staticmethod
    def build(

        history

    ):

        logger.info(

            "Building Category Trends"

        )

        summary = []

        for status in [

            "NORMAL",

            "WATCH",

            "WARNING",

            "CRITICAL"

        ]:

            count = len(

                history[

                    history["Status"]

                    ==

                    status

                ]

            )

            summary.append(

                {

                    "Status":

                        status,

                    "Occurrences":

                        count

                }

            )

        return pd.DataFrame(

            summary

        )
    
# ==========================================================
# TREND DASHBOARD BUILDER
# ==========================================================

class TrendDashboardBuilder:

    @staticmethod
    def build(

        trend_summary,

        trend_direction

    ):

        logger.info(

            "Building Trend Dashboard"

        )

        dashboard = (

            trend_summary

            .copy()

        )

        dashboard.loc[

            len(dashboard)

        ] = [

            "TREND_DIRECTION",

            trend_direction

        ]

        return dashboard
    
# ==========================================================
# TREND EXPORTER
# ==========================================================

class TrendExporter:

    @staticmethod
    def export(

        trend_df

    ):

        logger.info(

            "Exporting Trends"

        )

        trend_df.to_csv(

            TREND_FILE,

            index=False

        )

        return TREND_FILE
    
# ==========================================================
# TREND DASHBOARD EXPORTER
# ==========================================================

class TrendDashboardExporter:

    @staticmethod
    def export(

        dashboard

    ):

        logger.info(

            "Exporting Trend Dashboard"

        )

        dashboard.to_csv(

            TREND_DASHBOARD_FILE,

            index=False

        )

        return TREND_DASHBOARD_FILE
    
# ==========================================================
# MONITOR TREND ENGINE
# ==========================================================

class MonitorTrendEngine:

    def run(

        self

    ):

        logger.info(

            "Starting Monitor Trend Analysis"

        )

        files = (

            TrendRepository

            .load_history()

        )

        TrendValidator.validate(

            files

        )

        history = (

            HistoryLoaderEngine

            .load(

                files

            )

        )

        history = (

            TrendCalculationEngine

            .calculate(

                history

            )

        )

        trend_summary = (

            SeverityTrendEngine

            .build(

                history

            )

        )

        trend_direction = (

            TrendDirectionEngine

            .determine(

                history

            )

        )

        frequency = (

            AlertFrequencyEngine

            .build(

                history

            )

        )

        category_trends = (

            CategoryTrendEngine

            .build(

                history

            )

        )

        dashboard = (

            TrendDashboardBuilder

            .build(

                category_trends,

                trend_direction

            )

        )

        return {

            "history":

                history,

            "trend_summary":

                trend_summary,

            "trend_direction":

                trend_direction,

            "frequency":

                frequency,

            "dashboard":

                dashboard

        }
    
# ==========================================================
# SUMMARY ENGINE
# ==========================================================

class TrendSummaryEngine:

    @staticmethod
    def display(

        result

    ):

        summary = (

            result[

                "trend_summary"

            ]

        )

        print()

        print(

            "=" * 80

        )

        print(

            "MONITOR TREND ANALYSIS"

        )

        print(

            "=" * 80

        )

        print(

            summary

        )

        print()

        print(

            f"Trend Direction: "

            f"{result['trend_direction']}"

        )

        print(

            "=" * 80

        )

# ==========================================================
# RUNNER
# ==========================================================

def run_example():

    result = (

        MonitorTrendEngine()

        .run()

    )

    TrendExporter.export(

        result[

            "frequency"

        ]

    )

    TrendDashboardExporter.export(

        result[

            "dashboard"

        ]

    )

    TrendSummaryEngine.display(

        result

    )

    print()

    print(

        "Generated Files"

    )

    print(

        "-" * 40

    )

    print(

        TREND_FILE

    )

    print(

        TREND_DASHBOARD_FILE

    )

    print(

        "-" * 40

    )

# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    run_example()