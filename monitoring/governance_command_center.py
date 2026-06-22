from pathlib import Path

import pandas as pd

import logging


logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s | %(levelname)s | %(message)s"

)

logger = logging.getLogger(__name__)


DATA_DIR = Path("data")

PERFORMANCE_DIR = (

    DATA_DIR

    / "performance"

)

MONITORING_DIR = (

    DATA_DIR

    / "monitoring"

)


FORECAST_FILE = (

    PERFORMANCE_DIR

    / "performance_forecast.csv"

)

COMMITTEE_FILE = (

    PERFORMANCE_DIR

    / "investment_committee_pack.csv"

)

ALERT_GOVERNANCE_FILE = (

    MONITORING_DIR

    / "alert_governance.csv"

)

MONITOR_FILE = (

    MONITORING_DIR

    / "monitor_dashboard.csv"

)

OUTPUT_FILE = (

    MONITORING_DIR

    / "governance_command_center.csv"

)

class GovernanceRepository:

    @staticmethod
    def load():

        forecast = pd.read_csv(

            FORECAST_FILE

        )

        committee = pd.read_csv(

            COMMITTEE_FILE

        )

        alert_governance = pd.read_csv(

            ALERT_GOVERNANCE_FILE

        )

        monitor = pd.read_csv(

            MONITOR_FILE

        )

        return (

            forecast,

            committee,

            alert_governance,

            monitor

        )
    
class GovernanceScoringEngine:

    @staticmethod
    def calculate(

        forecast,

        committee,

        alert_governance,

        monitor

    ):

        forecast_confidence = float(

            forecast.iloc[0][

                "Forecast_Confidence"

            ]

        )

        alert_metrics = dict(

            zip(

                alert_governance["Metric"],

                alert_governance["Value"]

            )

        )

        alert_health = float(

            alert_metrics.get(

                "Alert_Health_Score",

                0

            )

        )

        escalation = str(

            alert_metrics.get(

                "Alert_Escalation",

                "UNKNOWN"

            )

        )

        governance_view = str(

            alert_metrics.get(

                "Governance_View",

                "UNKNOWN"

            )

        )

        overall_status = str(

            monitor.loc[

                monitor["Category"]

                ==

                "Overall",

                "Status"

            ]

            .iloc[0]

        )

        governance_score = (

            forecast_confidence * 0.40

            +

            alert_health * 0.60

        )

        if governance_score >= 85:

            risk_level = "LOW"

        elif governance_score >= 70:

            risk_level = "MODERATE"

        elif governance_score >= 50:

            risk_level = "HIGH"

        else:

            risk_level = "CRITICAL"

        return {

            "Governance_Score":

                round(

                    governance_score,

                    2

                ),

            "Risk_Level":

                risk_level,

            "Escalation":

                escalation,

            "Governance_View":

                governance_view,

            "Overall_Status":

                overall_status

        }
    
class ExecutiveRecommendationEngine:

    @staticmethod
    def recommend(

        metrics

    ):

        score = float(

            metrics[

                "Governance_Score"

            ]

        )

        escalation = str(

            metrics[

                "Escalation"

            ]

        )

        risk_level = str(

            metrics[

                "Risk_Level"

            ]

        )

        if escalation == "ESCALATING":

            return (

                "ACTIVATE_DEFENSIVE_MODE"

            )

        if risk_level == "CRITICAL":

            return (

                "REDUCE_EXPOSURE"

            )

        if risk_level == "HIGH":

            return (

                "REVIEW_POSITIONING"

            )

        if score >= 80:

            return (

                "MAINTAIN_OVERWEIGHT"

            )

        return (

            "MAINTAIN_NEUTRAL"

        )
    
class GovernanceCommandCenter:

    @staticmethod
    def build(

        metrics,

        recommendation

    ):

        return pd.DataFrame(

            [

                {

                    "Metric":

                        "Governance_Score",

                    "Value":

                        metrics[

                            "Governance_Score"

                        ]

                },

                {

                    "Metric":

                        "Risk_Level",

                    "Value":

                        metrics[

                            "Risk_Level"

                        ]

                },

                {

                    "Metric":

                        "Escalation",

                    "Value":

                        metrics[

                            "Escalation"

                        ]

                },

                {

                    "Metric":

                        "Governance_View",

                    "Value":

                        metrics[

                            "Governance_View"

                        ]

                },

                {

                    "Metric":

                        "Overall_Status",

                    "Value":

                        metrics[

                            "Overall_Status"

                        ]

                },

                {

                    "Metric":

                        "Executive_Action",

                    "Value":

                        recommendation

                }

            ]

        )
    
class GovernanceExporter:

    @staticmethod
    def export(

        dashboard

    ):

        dashboard.to_csv(

            OUTPUT_FILE,

            index=False

        )

def run_example():

    logger.info(

        "Starting Governance Command Center"

    )

    (
        forecast,
        committee,
        alert_governance,
        monitor

    ) = GovernanceRepository.load()

    metrics = (

        GovernanceScoringEngine

        .calculate(

            forecast,

            committee,

            alert_governance,

            monitor

        )

    )

    recommendation = (

        ExecutiveRecommendationEngine

        .recommend(

            metrics

        )

    )

    dashboard = (

        GovernanceCommandCenter

        .build(

            metrics,

            recommendation

        )

    )

    GovernanceExporter.export(

        dashboard

    )

    print()

    print(

        "=" * 80

    )

    print(

        "GOVERNANCE COMMAND CENTER"

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