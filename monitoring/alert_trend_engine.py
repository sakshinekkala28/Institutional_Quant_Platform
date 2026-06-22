from pathlib import Path

import pandas as pd

import logging


logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s | %(levelname)s | %(message)s"

)

logger = logging.getLogger(__name__)


DATA_DIR = Path("data")

MONITORING_DIR = (

    DATA_DIR

    / "monitoring"

)

ALERT_HISTORY_FILE = (

    MONITORING_DIR

    / "alert_history.csv"

)


class AlertTrendValidator:

    @staticmethod
    def validate():

        if not ALERT_HISTORY_FILE.exists():

            raise FileNotFoundError(

                ALERT_HISTORY_FILE

            )

        logger.info(

            "Alert Trend Validation Passed"

        )

class AlertHistoryLoader:

    @staticmethod
    def load():

        logger.info(

            "Loading Alert History"

        )

        return pd.read_csv(

            ALERT_HISTORY_FILE

        )


class AlertSeverityEngine:

    SEVERITY_MAP = {

        "INFO": 0,

        "WATCH": 1,

        "MEDIUM": 1,

        "WARNING": 2,

        "HIGH": 3,

        "CRITICAL": 4

    }

    @classmethod
    def score(

        cls,

        alerts

    ):

        logger.info(

            "Calculating Severity Scores"

        )

        alerts = alerts.copy()

        alerts["Severity_Score"] = (

            alerts["Severity"]

            .map(

                cls.SEVERITY_MAP

            )

            .fillna(0)

        )

        return alerts
    
class AlertTrendEngine:

    @staticmethod
    def build(

        alerts

    ):

        logger.info(

            "Building Alert Trends"

        )

        trend = (

            alerts

            .groupby(

                "Date",

                as_index=False

            )

            .agg(

                {

                    "Severity_Score": "mean"

                }

            )

        )

        trend.rename(

            columns={

                "Severity_Score":

                    "Average_Severity"

            },

            inplace=True

        )

        return trend


class AlertDirectionEngine:

    @staticmethod
    def determine(

        trend

    ):

        logger.info(

            "Determining Alert Direction"

        )

        if len(

            trend

        ) < 2:

            return (

                "INSUFFICIENT_HISTORY"

            )

        first = (

            trend

            .iloc[0]

            [

                "Average_Severity"

            ]

        )

        last = (

            trend

            .iloc[-1]

            [

                "Average_Severity"

            ]

        )

        if last > first:

            return "DETERIORATING"

        if last < first:

            return "IMPROVING"

        return "STABLE"
    
class AlertTrendDashboard:

    @staticmethod
    def build(

        alerts,

        trend,

        direction

    ):

        return pd.DataFrame(

            [

                {

                    "Metric":

                        "Total_Alerts",

                    "Value":

                        len(

                            alerts

                        )

                },

                {

                    "Metric":

                        "Critical_Alerts",

                    "Value":

                        len(

                            alerts[

                                alerts["Severity"]

                                ==

                                "CRITICAL"

                            ]

                        )

                },

                {

                    "Metric":

                        "Trend_Direction",

                    "Value":

                        direction

                },

                {

                    "Metric":

                        "Observation_Count",

                    "Value":

                        len(

                            trend

                        )

                },

                {

                    "Metric":

                        "High_Alerts",

                    "Value":

                        len(

                            alerts[

                                alerts["Severity"]

                                ==

                                "HIGH"

                            ]

                        )

                },

                {
                    "Metric":

                        "Medium_Alerts",

                    "Value":

                        len(

                            alerts[

                                alerts["Severity"]

                                ==

                                "MEDIUM"

                            ]

                        )

                }

            ]

        )


class AlertTrendExporter:

    @staticmethod
    def export(

        trend,

        dashboard

    ):

        logger.info(

            "Exporting Alert Trends"

        )

        trend.to_csv(

            MONITORING_DIR

            / "alert_trends.csv",

            index=False

        )

        dashboard.to_csv(

            MONITORING_DIR

            / "alert_trend_dashboard.csv",

            index=False

        )


def run_example():

    logger.info(

        "Starting Alert Trend Analysis"

    )

    AlertTrendValidator.validate()

    alerts = (

        AlertHistoryLoader

        .load()

    )

    alerts = (

        AlertSeverityEngine

        .score(

            alerts

        )

    )

    trend = (

        AlertTrendEngine

        .build(

            alerts

        )

    )

    direction = (

        AlertDirectionEngine

        .determine(

            trend

        )

    )

    dashboard = (

        AlertTrendDashboard

        .build(

            alerts,

            trend,

            direction

        )

    )

    AlertTrendExporter.export(

        trend,

        dashboard

    )

    print()

    print(

        "=" * 80

    )

    print(

        "ALERT TREND ANALYSIS"

    )

    print(

        "=" * 80

    )

    print(

        dashboard

    )

    print()

    print(

        f"Trend Direction: "

        f"{direction}"

    )

    print(

        "=" * 80

    )


if __name__ == "__main__":

    run_example()