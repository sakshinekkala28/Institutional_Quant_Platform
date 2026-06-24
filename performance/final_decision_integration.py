from __future__ import annotations

import logging

from pathlib import Path

import pandas as pd

from core.settings import settings


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

    settings
    .environment
    .ROOT_DIR

)

DATA_DIR = (

    ROOT_DIR

    / "data"

)

PERFORMANCE_DIR = (

    DATA_DIR

    / "performance"

)


FINAL_DECISION_FILE = (

    PERFORMANCE_DIR

    / "final_decision.csv"

)

EXECUTIVE_DASHBOARD_FILE = (

    PERFORMANCE_DIR

    / "executive_dashboard.csv"

)

COMMITTEE_PACK_FILE = (

    PERFORMANCE_DIR

    / "investment_committee_pack.csv"

)

class FinalDecisionIntegrationRepository:

    @staticmethod
    def load():

        logger.info(

            "Loading Final Decision"

        )

        final_decision = pd.read_csv(

            FINAL_DECISION_FILE

        )

        logger.info(

            "Loading Executive Dashboard"

        )

        executive = pd.read_csv(

            EXECUTIVE_DASHBOARD_FILE

        )

        logger.info(

            "Loading Committee Pack"

        )

        committee = pd.read_csv(

            COMMITTEE_PACK_FILE

        )

        return (

            final_decision,

            executive,

            committee

        )
    
class ExecutiveDashboardIntegrator:

    @staticmethod
    def build(

        executive,

        final_decision

    ):

        return pd.concat(

            [

                executive,

                final_decision

            ],

            ignore_index=True

        )

class CommitteePackIntegrator:

    @staticmethod
    def build(

        committee,

        final_decision

    ):

        rows = []

        for _, row in final_decision.iterrows():

            rows.append(

                {

                    "Section":

                        "Final_Decision",

                    "Metric":

                        row["Metric"],

                    "Value":

                        row["Value"]

                }

            )

        return pd.concat(

            [

                committee,

                pd.DataFrame(

                    rows

                )

            ],

            ignore_index=True

        )
    
class FinalDecisionIntegrationExporter:

    @staticmethod
    def export(

        executive,

        committee

    ):

        logger.info(

            "Exporting Integrated Files"

        )

        executive.to_csv(

            EXECUTIVE_DASHBOARD_FILE,

            index=False

        )

        committee.to_csv(

            COMMITTEE_PACK_FILE,

            index=False

        )

def run_example():

    logger.info(

        "Starting Final Decision Integration"

    )

    (

        final_decision,

        executive,

        committee

    ) = (

        FinalDecisionIntegrationRepository

        .load()

    )

    executive = (

        ExecutiveDashboardIntegrator

        .build(

            executive,

            final_decision

        )

    )

    committee = (

        CommitteePackIntegrator

        .build(

            committee,

            final_decision

        )

    )

    FinalDecisionIntegrationExporter.export(

        executive,

        committee

    )

    print()

    print("=" * 80)

    print(

        "FINAL DECISION INTEGRATION"

    )

    print("=" * 80)

    print(

        "Executive Dashboard Updated"

    )

    print(

        "Committee Pack Updated"

    )

    print("=" * 80)


if __name__ == "__main__":

    run_example()