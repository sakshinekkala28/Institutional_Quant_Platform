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

MONITORING_DIR = (

    DATA_DIR

    / "monitoring"

)

EXECUTIVE_DASHBOARD_FILE = (

    PERFORMANCE_DIR

    / "executive_dashboard.csv"

)

GOVERNANCE_COMMAND_CENTER_FILE = (

    MONITORING_DIR

    / "governance_command_center.csv"

)

OUTPUT_FILE = (

    PERFORMANCE_DIR

    / "final_decision_dashboard.csv"

)

class FinalDecisionRepository:

    @staticmethod
    def load():

        logger.info(

            "Loading Executive Dashboard"

        )

        executive = pd.read_csv(

            EXECUTIVE_DASHBOARD_FILE

        )

        logger.info(

            "Loading Governance Command Center"

        )

        governance = pd.read_csv(

            GOVERNANCE_COMMAND_CENTER_FILE

        )



        return (

            executive,

            governance

        )

            
class FinalDecisionValidator:

    @staticmethod
    def validate():

        required_files = [

            EXECUTIVE_DASHBOARD_FILE,

            GOVERNANCE_COMMAND_CENTER_FILE

        ]

        for file_path in required_files:

            if not file_path.exists():

                raise FileNotFoundError(

                    file_path

                )

        logger.info(

            "Decision Validation Passed"

        )

class DecisionScoringEngine:

    @staticmethod
    def calculate(

        executive,

        governance

    ):

        executive_metrics = dict(

            zip(

                executive["Metric"],

                executive["Value"]

            )

        )

        governance_metrics = dict(

            zip(

                governance["Metric"],

                governance["Value"]

            )

        )

        pack_score = float(

            executive_metrics.get(

                "Pack_Score",

                0

            )

        )

        governance_score = float(

            governance_metrics.get(

                "Governance_Score",

                0

            )

        )

        alert_score = float(

            executive_metrics.get(

                "Alert_Health_Score",

                0

            )

        )

        stress_severity = float(

            governance_metrics.get(

                "Stress_Severity_Score",

                0

            )

        )

        return {

            "Pack_Score":

                pack_score,

            "Governance_Score":

                governance_score,

            "Alert_Health":

                alert_score,

            "Stress_Severity_Score":

                stress_severity,

        }
    
class CIODecisionEngine:

    @staticmethod
    def build(

        executive,

        governance,

        scores

    ):

        executive_metrics = dict(

            zip(

                executive["Metric"],

                executive["Value"]

            )

        )

        governance_metrics = dict(

            zip(

                governance["Metric"],

                governance["Value"]

            )

        )

        forecast_bias = str(

            governance_metrics.get(

                "Forecast_Bias",

                ""

            )

        )

        governance_status = str(

            governance_metrics.get(

                "Governance_Status",

                ""

            )

        )
        
        stress_view = str(

            governance_metrics.get(

                "Stress_View",

                ""

            )

        )

        stress_severity = float(

            scores[

                "Stress_Severity_Score"

            ]

        )

        macro_risk = str(

            governance_metrics.get(

                "Macro_Risk_Level",

                ""

            )

        )

        executive_action = str(

            governance_metrics.get(

                "Executive_Action",

                ""

            )

        )

        forecast_regime = str(

            executive_metrics.get(

                "Forecast_Regime",

                "UNKNOWN"

            )

        )

        if executive_action == "ACTIVATE_DEFENSIVE_MODE":

            final_decision = "DEFENSIVE"

        elif governance_status in [

            "CRITICAL",

            "HIGH_RISK"

        ]:

            final_decision = "CAUTIOUS"

        elif stress_severity >= 80:

            final_decision = "DEFENSIVE"

        elif stress_severity >= 60:

            final_decision = "CAUTIOUS"

        elif macro_risk == "HIGH":

            final_decision = "CAUTIOUS"

        elif forecast_bias == "STRONGLY_BULLISH":

            final_decision = "AGGRESSIVE"

        elif forecast_bias == "BULLISH":

            final_decision = "OFFENSIVE"

        else:

            final_decision = "NEUTRAL"

        return {

            "Forecast_Regime":

                forecast_regime,

            "Forecast_Bias":

                forecast_bias,

            "Governance_Status":

                governance_status,

            "Stress_View":

                stress_view,
            
            "Stress_Severity_Score":

                stress_severity,

            "Macro_Risk_Level":

                macro_risk,

            "Risk_Level":

                governance_metrics.get(

                    "Risk_Level",

                    "UNKNOWN"

                ),

            "Executive_Action":

                executive_action,

            "Final_Decision":

                final_decision

        }
    
class PortfolioMandateEngine:

    @staticmethod
    def build(

        final_decision

    ):

        mapping = {

            "AGGRESSIVE":

                "MAXIMIZE_ALPHA",

            "OFFENSIVE":

                "GROWTH",

            "NEUTRAL":

                "BALANCED",

            "CAUTIOUS":

                "RISK_CONTROL",

            "DEFENSIVE":

                "CAPITAL_PRESERVATION"

        }

        return mapping.get(

            final_decision,

            "MAINTAIN"

        )
class FinalDecisionDashboard:

    @staticmethod
    def build(

        decision_metrics,

        mandate

    ):

        return pd.DataFrame(

            [

                {

                    "Metric":

                        "Forecast_Regime",

                    "Value":

                        decision_metrics[
                            "Forecast_Regime"
                        ]

                },

                {

                    "Metric":

                        "Risk_Level",

                    "Value":

                        decision_metrics[
                            "Risk_Level"
                        ]

                },

                {

                    "Metric":

                        "Executive_Action",

                    "Value":

                        decision_metrics[
                            "Executive_Action"
                        ]

                },

                {

                    "Metric":

                        "Forecast_Bias",

                    "Value":

                        decision_metrics[

                            "Forecast_Bias"

                        ]

                },

                {

                    "Metric":

                        "Stress_View",

                    "Value":

                        decision_metrics[

                            "Stress_View"

                        ]

                },

                {

                    "Metric":

                        "Stress_Severity_Score",

                    "Value":

                        decision_metrics[

                            "Stress_Severity_Score"

                        ]

                },

                {

                    "Metric":

                        "Governance_Status",

                    "Value":

                        decision_metrics[

                            "Governance_Status"

                        ]

                },

                {

                    "Metric":

                        "Macro_Risk_Level",

                    "Value":

                        decision_metrics[

                            "Macro_Risk_Level"

                        ]

                },
                
                {

                    "Metric":

                        "Final_Decision",

                    "Value":

                        decision_metrics[
                            "Final_Decision"
                        ]

                },

                {

                    "Metric":

                        "Portfolio_Mandate",

                    "Value":

                        mandate

                }

            ]

        )
    
class FinalDecisionExporter:

    @staticmethod
    def export(

        dashboard

    ):

        logger.info(

            "Exporting Final Decision"

        )

        dashboard.to_csv(

            OUTPUT_FILE,

            index=False

        )

def run_example():

    logger.info(

        "Starting Final Decision Engine"

    )

    FinalDecisionValidator.validate()

    (

        executive,

        governance

    ) = (

        FinalDecisionRepository

        .load()

    )

    scores = (

        DecisionScoringEngine

        .calculate(

            executive,

            governance

        )

    )

    decision_metrics = (

        CIODecisionEngine

        .build(

            executive,

            governance,

            scores

        )

    )

    mandate = (

        PortfolioMandateEngine

        .build(

            decision_metrics[

                "Final_Decision"

            ]

        )

    )

    dashboard = (

        FinalDecisionDashboard

        .build(

            decision_metrics,

            mandate

        )

    )

    FinalDecisionExporter.export(

        dashboard

    )

    print()

    print("=" * 80)

    print(

        "FINAL CIO DECISION"

    )

    print("=" * 80)

    print(dashboard)

    print("=" * 80)


if __name__ == "__main__":

    run_example()