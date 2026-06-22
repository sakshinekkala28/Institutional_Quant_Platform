from pathlib import Path

import pandas as pd

import logging


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


ROOT_DIR = (

    Path(__file__)

    .resolve()

    .parents[1]

)

DATA_DIR = (

    ROOT_DIR

    / "data"

)

PERFORMANCE_DIR = (

    DATA_DIR

    / "performance"

)

MONITORING_DIR = (

    DATA_DIR

    / "monitoring"

)


GOVERNANCE_COMMAND_CENTER_FILE = (

    MONITORING_DIR

    / "governance_command_center.csv"

)

COMMITTEE_PACK_FILE = (

    PERFORMANCE_DIR

    / "investment_committee_pack.csv"

)

EXECUTIVE_DASHBOARD_FILE = (

    PERFORMANCE_DIR

    / "executive_dashboard.csv"

)

OUTPUT_FILE = (

    PERFORMANCE_DIR

    / "governance_committee_dashboard.csv"

)

class GovernanceCommitteeValidator:

    @staticmethod
    def validate():

        logger.info(

            "Validating Inputs"

        )

        required_files = [

            GOVERNANCE_COMMAND_CENTER_FILE,

            COMMITTEE_PACK_FILE,

            EXECUTIVE_DASHBOARD_FILE

        ]

        for file_path in required_files:

            if not file_path.exists():

                raise FileNotFoundError(

                    file_path

                )

        logger.info(

            "Validation Passed"

        )


class GovernanceCommitteeRepository:

    @staticmethod
    def load():

        logger.info(

            "Loading Governance Command Center"

        )

        governance = pd.read_csv(

            GOVERNANCE_COMMAND_CENTER_FILE

        )

        logger.info(

            "Loading Committee Pack"

        )

        committee = pd.read_csv(

            COMMITTEE_PACK_FILE

        )

        logger.info(

            "Loading Executive Dashboard"

        )

        executive = pd.read_csv(

            EXECUTIVE_DASHBOARD_FILE

        )

        return (

            governance,

            committee,

            executive

        )
    
class GovernanceCommitteeMetrics:

    @staticmethod
    def build(

        governance,

        committee,

        executive

    ):

        governance_metrics = dict(

            zip(

                governance["Metric"],

                governance["Value"]

            )

        )

        executive_metrics = dict(

            zip(

                executive["Metric"],

                executive["Value"]

            )

        )

        return {

            "Governance_Score":

                governance_metrics.get(

                    "Governance_Score"

                ),

            "Risk_Level":

                governance_metrics.get(

                    "Risk_Level"

                ),

            "Executive_Action":

                governance_metrics.get(

                    "Executive_Action"

                ),

            "Overall_Status":

                governance_metrics.get(

                    "Overall_Status"

                ),

            "Pack_Score":

                executive_metrics.get(

                    "Pack_Score"

                ),

            "Recommendation":

                executive_metrics.get(

                    "Recommendation"

                ),

            "Forecast_Regime":

                executive_metrics.get(

                    "Forecast_Regime"

                )

        }
    
class GovernanceCommitteeDashboard:

    @staticmethod
    def build(

        metrics

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

                        "Executive_Action",

                    "Value":

                        metrics[

                            "Executive_Action"

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

                        "Pack_Score",

                    "Value":

                        metrics[

                            "Pack_Score"

                        ]

                },

                {

                    "Metric":

                        "Recommendation",

                    "Value":

                        metrics[

                            "Recommendation"

                        ]

                },

                {

                    "Metric":

                        "Forecast_Regime",

                    "Value":

                        metrics[

                            "Forecast_Regime"

                        ]

                }

            ]

        )

class GovernanceCommitteeExporter:

    @staticmethod
    def export(

        dashboard

    ):

        logger.info(

            "Exporting Governance Dashboard"

        )

        dashboard.to_csv(

            OUTPUT_FILE,

            index=False

        )


def run_example():

    logger.info(

        "Starting Governance Committee Integration"

    )

    GovernanceCommitteeValidator.validate()

    (

        governance,

        committee,

        executive

    ) = (

        GovernanceCommitteeRepository

        .load()

    )

    metrics = (

        GovernanceCommitteeMetrics

        .build(

            governance,

            committee,

            executive

        )

    )

    dashboard = (

        GovernanceCommitteeDashboard

        .build(

            metrics

        )

    )

    GovernanceCommitteeExporter.export(

        dashboard

    )

    print()

    print("=" * 80)

    print(

        "GOVERNANCE COMMITTEE DASHBOARD"

    )

    print("=" * 80)

    print(

        dashboard

    )

    print("=" * 80)

    print(

        f"Output: {OUTPUT_FILE}"

    )


if __name__ == "__main__":

    run_example()