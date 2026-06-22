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

DASHBOARD_FILE = (

    MONITORING_DIR

    / "alert_dashboard.csv"

)

class AlertDashboardBuilder:

    @staticmethod
    def build(

        alerts

    ):

        logger.info(

            "Building Alert Dashboard"

        )

        total_alerts = len(

            alerts

        )

        critical_alerts = len(

            alerts[

                alerts["Severity"]

                ==

                "CRITICAL"

            ]

        )

        high_alerts = len(

            alerts[

                alerts["Severity"]

                ==

                "HIGH"

            ]

        )

        medium_alerts = len(

            alerts[

                alerts["Severity"]

                ==

                "MEDIUM"

            ]

        )

        top_category = (

            alerts["Category"]

            .mode()

            .iloc[0]

        )

        return pd.DataFrame(

            [

                {

                    "Metric":

                        "Total_Alerts",

                    "Value":

                        total_alerts

                },

                {

                    "Metric":

                        "Critical_Alerts",

                    "Value":

                        critical_alerts

                },

                {

                    "Metric":

                        "High_Alerts",

                    "Value":

                        high_alerts

                },

                {

                    "Metric":

                        "Medium_Alerts",

                    "Value":

                        medium_alerts

                },

                {

                    "Metric":

                        "Top_Category",

                    "Value":

                        top_category

                }

            ]

        )
    
class AlertDashboardExporter:

    @staticmethod
    def export(

        dashboard

    ):

        logger.info(

            "Exporting Alert Dashboard"

        )

        dashboard.to_csv(

            DASHBOARD_FILE,

            index=False

        )

def run_example():

    logger.info(

        "Starting Alert Dashboard"

    )

    alerts = pd.read_csv(

        ALERT_HISTORY_FILE

    )

    dashboard = (

        AlertDashboardBuilder

        .build(

            alerts

        )

    )

    AlertDashboardExporter.export(

        dashboard

    )

    print()

    print(

        "=" * 80

    )

    print(

        "ALERT DASHBOARD"

    )

    print(

        "=" * 80

    )

    print(

        dashboard

    )

    print(

        "=" * 80

    )


if __name__ == "__main__":

    run_example()