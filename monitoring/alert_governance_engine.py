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

ALERT_DASHBOARD_FILE = (

    MONITORING_DIR

    / "alert_dashboard.csv"

)

ALERT_TREND_FILE = (

    MONITORING_DIR

    / "alert_trend_dashboard.csv"

)

GOVERNANCE_FILE = (

    MONITORING_DIR

    / "alert_governance.csv"

)

class AlertGovernanceValidator:

    @staticmethod
    def validate():

        if not ALERT_DASHBOARD_FILE.exists():

            raise FileNotFoundError(

                ALERT_DASHBOARD_FILE

            )

        if not ALERT_TREND_FILE.exists():

            raise FileNotFoundError(

                ALERT_TREND_FILE

            )

        logger.info(

            "Alert Governance Validation Passed"

        )


class AlertGovernanceLoader:

    @staticmethod
    def load():

        logger.info(

            "Loading Alert Dashboard"

        )

        dashboard = pd.read_csv(

            ALERT_DASHBOARD_FILE

        )

        logger.info(

            "Loading Alert Trends"

        )

        trend = pd.read_csv(

            ALERT_TREND_FILE

        )

        return (

            dashboard,

            trend

        )
    
class AlertGovernanceEngine:

    @staticmethod
    def calculate(

        dashboard,

        trend

    ):

        logger.info(

            "Calculating Alert Governance"

        )

        metrics = dict(

            zip(

                dashboard["Metric"],

                dashboard["Value"]

            )

        )

        total_alerts = int(

            metrics.get(

                "Total_Alerts",

                0

            )

        )

        critical_alerts = int(

            metrics.get(

                "Critical_Alerts",

                0

            )

        )

        high_alerts = int(

            metrics.get(

                "High_Alerts",

                0

            )

        )

        medium_alerts = int(

            metrics.get(

                "Medium_Alerts",

                0

            )

        )

        top_category = str(

            metrics.get(

                "Top_Category",

                "UNKNOWN"

            )

        )

        if total_alerts == 0:

            health_score = 100

        else:

            critical_ratio = (

                critical_alerts

                / total_alerts

            )

            high_ratio = (

                high_alerts

                / total_alerts

            )

            medium_ratio = (

                medium_alerts

                / total_alerts

            )

            health_score = (

                100

                -

                critical_ratio * 60

                -

                high_ratio * 25

                -

                medium_ratio * 10

            )

            health_score = round(

                max(

                    health_score,

                    0

                ),

                2

            )

        trend_direction = (

            trend.loc[

                trend["Metric"]

                ==

                "Trend_Direction",

                "Value"

            ]

            .iloc[0]

        )

        if trend_direction == "UP":

            escalation = (

                "ESCALATING"

            )

        elif trend_direction == "DOWN":

            escalation = (

                "IMPROVING"

            )

        else:

            escalation = (

                "STABLE"

            )

        if health_score >= 80:

            governance_view = (

                "HEALTHY"

            )

        elif health_score >= 60:

            governance_view = (

                "WATCH"

            )

        elif health_score >= 40:

            governance_view = (

                "WARNING"

            )

        else:

            governance_view = (

                "CRITICAL"

            )


        return pd.DataFrame(

            [

                {

                    "Metric":

                        "Alert_Health_Score",

                    "Value":

                        health_score

                },

                {

                    "Metric":

                        "Alert_Escalation",

                    "Value":

                        escalation

                },

                {

                    "Metric":

                        "Governance_View",

                    "Value":

                        governance_view

                },

                {

                    "Metric":

                        "Trend_Direction",

                    "Value":

                        trend_direction

                },

                {

                    "Metric":

                        "Top_Category",

                    "Value":

                        top_category

                },

                {

                    "Metric":

                        "Total_Alerts",

                    "Value":

                        total_alerts

                }

            ]

        )
    
class AlertGovernanceExporter:

    @staticmethod
    def export(

        governance

    ):

        logger.info(

            "Exporting Alert Governance"

        )

        governance.to_csv(

            GOVERNANCE_FILE,

            index=False

        )


def run_example():

    logger.info(

        "Starting Alert Governance"

    )

    AlertGovernanceValidator.validate()

    dashboard, trend = (

        AlertGovernanceLoader

        .load()

    )

    governance = (

        AlertGovernanceEngine

        .calculate(

            dashboard,

            trend

        )

    )

    AlertGovernanceExporter.export(

        governance

    )

    print()

    print(

        "=" * 80

    )

    print(

        "ALERT GOVERNANCE"

    )

    print(

        "=" * 80

    )

    print(

        governance

    )

    print(

        "=" * 80

    )


if __name__ == "__main__":

    run_example()