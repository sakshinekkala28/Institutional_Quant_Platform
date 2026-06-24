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

ALERT_GOVERNANCE_FILE = (

    MONITORING_DIR

    / "alert_governance.csv"

)

MONITOR_FILE = (

    MONITORING_DIR

    / "monitor_dashboard.csv"

)

STRESS_DASHBOARD_FILE = (

    MONITORING_DIR

    / "stress_dashboard.csv"

)

OUTPUT_FILE = (

    MONITORING_DIR

    / "governance_command_center.csv"

)

GOVERNANCE_FORECAST_FILE = (

    PERFORMANCE_DIR

    / "forecast_dashboard.csv"

)

MULTI_HORIZON_FILE = (

    PERFORMANCE_DIR

    / "multi_horizon_forecast_dashboard.csv"

)

FINAL_DECISION_FILE = (

    PERFORMANCE_DIR

    / "final_decision_dashboard.csv"

)

class GovernanceStatusEngine:

    @staticmethod
    def classify(

        score

    ):

        if score >= 80:

            return "NORMAL"

        if score >= 60:

            return "ELEVATED_RISK"

        if score >= 40:

            return "HIGH_RISK"

        return "CRITICAL"
    

class GovernanceRepository:

    @staticmethod
    def load():

        forecast = pd.read_csv(

            FORECAST_FILE

        )

        alert_governance = pd.read_csv(

            ALERT_GOVERNANCE_FILE

        )

        monitor = pd.read_csv(

            MONITOR_FILE

        )

        stress_dashboard = pd.read_csv(

            STRESS_DASHBOARD_FILE

        )

        return (

            forecast,

            alert_governance,

            monitor,

            stress_dashboard

        )

class GovernanceForecastLoader:

    @staticmethod
    def load():

        logger.info(

            "Loading Governance Forecast Inputs"

        )

        forecast = pd.read_csv(

            GOVERNANCE_FORECAST_FILE

        )

        horizon = pd.read_csv(

            MULTI_HORIZON_FILE

        )

        decision = pd.read_csv(

            FINAL_DECISION_FILE

        )

        return (

            forecast,

            horizon,

            decision

        )


class GovernanceSignalEngine:

    @staticmethod
    def build(

        forecast_df,

        horizon_df,

        decision_df,

        stress_dashboard

    ):

        forecast_metrics = dict(

            zip(

                forecast_df["Metric"],

                forecast_df["Value"]

            )

        )

        horizon_metrics = dict(

            zip(

                horizon_df["Metric"],

                horizon_df["Value"]

            )

        )

        decision_metrics = dict(

            zip(

                decision_df["Metric"],

                decision_df["Value"]

            )

        )

        stress_metrics = dict(

            zip(

                stress_dashboard["Metric"],

                stress_dashboard["Value"]

            )

        )

        return {

            "Forecast_Bias":

                horizon_metrics.get(

                    "Forecast_Bias"

                ),

            "Forecast_Confidence":

                float(

                    horizon_metrics.get(

                        "Forecast_Confidence",

                        0

                    )

                ),

            "Stress_Severity_Score":

                float(

                    stress_metrics.get(

                        "Stress_Severity_Score",

                        0

                    )

                ),

            "Stress_View":

                stress_metrics.get(
            
                    "Stress_View",

                    "UNKNOWN"

                ),

            "Stress_Average":

                float(

                    stress_metrics.get(

                        "Stress_Average",

                        0

                    )

                ),

            "Worst_Stress_Score":

                float(

                    stress_metrics.get(

                        "Worst_Stress_Score",

                        0

                    )

                ),

            "Rejected_Scenarios":

                int(

                    stress_metrics.get(

                        "Rejected_Scenarios",

                        0
            
                    )
            
                ),

            "Macro_Regime":

                horizon_metrics.get(

                    "Macro_Regime"

                ),

            "Macro_Risk_Level":

                horizon_metrics.get(

                    "Macro_Risk_Level"

                ),

            "Final_Decision":

                decision_metrics.get(

                    "Final_Decision"

                ),

            "Portfolio_Mandate":

                decision_metrics.get(

                    "Portfolio_Mandate"

                )

        }
    

class GovernanceScoringEngine:

    @staticmethod
    def calculate(

        forecast,

        alert_governance,

        monitor,

        signals

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

            forecast_confidence * 0.45

            +

            alert_health * 0.55

        )

        if (

            signals["Forecast_Bias"]

            ==

            "STRONGLY_BULLISH"

        ):

            governance_score += 15

        elif (

            signals["Forecast_Bias"]

            ==

            "BULLISH"

        ):

            governance_score += 10

        elif (

            signals["Forecast_Bias"]

            ==

            "CAUTIOUS_BULLISH"

        ):

            governance_score += 5


        if (

            signals["Macro_Risk_Level"]

            ==

            "HIGH"

        ):

            governance_score -= 5
        
        governance_score -= (

            signals[

                "Stress_Severity_Score"

            ]

            * 0.10

        )
        
        if (

            signals["Macro_Regime"]

            ==

            "CRISIS"

        ):

            governance_score -= 20

        elif (

            signals["Macro_Regime"]

            ==
        
            "RISK_OFF"

        ):

            governance_score -= 5

        if (

            signals["Forecast_Bias"]

            ==

            "BEARISH"

        ):

            governance_score -= 10

        governance_score = max(

            governance_score,

            0

        )

        if governance_score >= 85:

            risk_level = "LOW"

        elif governance_score >= 70:

            risk_level = "MODERATE"

        elif governance_score >= 55:

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

        if (

            escalation == "ESCALATING"

            and

            risk_level == "CRITICAL"

        ):

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

        recommendation,

        signals,

        governance_status

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

                        "Forecast_Bias",

                    "Value":

                        signals[

                            "Forecast_Bias"

                        ]

                },

                {

                    "Metric":

                        "Forecast_Confidence",

                    "Value":

                        signals[

                            "Forecast_Confidence"

                        ]

                },

                {

                    "Metric":
                        "Stress_View",
                
                    "Value":
                        signals[
                            "Stress_View"
                        ]

                },

                {
                    "Metric":
                        "Stress_Average",

                    "Value":
                        signals[
                            "Stress_Average"
                        ]
                },


                {

                    "Metric":

                        "Stress_Severity_Score",

                    "Value":

                        signals[

                            "Stress_Severity_Score"

                        ]
                
                },
                
                {
                    "Metric":
                        "Worst_Stress_Score",

                    "Value":
                        signals[
                            "Worst_Stress_Score"
                        ]
                },

                {
                    "Metric":
                        "Rejected_Scenarios",
                
                    "Value":
                        signals[
                            "Rejected_Scenarios"
                        ]
                },

                {

                    "Metric":
                        "Macro_Risk_Level",

                    "Value":
                        signals[
                            "Macro_Risk_Level"
                        ]

                },

                {

                    "Metric":
                        "Macro_Regime",

                    "Value":
                        signals[
                            "Macro_Regime"
                        ]

                },

                {

                    "Metric":

                        "Final_Decision",

                    "Value":

                        signals[

                            "Final_Decision"

                        ]

                },

                {

                    "Metric":

                        "Portfolio_Mandate",

                    "Value":

                        signals[

                            "Portfolio_Mandate"

                        ]

                },

                {

                    "Metric":

                        "Governance_Status",

                    "Value":

                        governance_status

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
        alert_governance,
        monitor,
        stress_dashboard

    ) = GovernanceRepository.load()

    (

        forecast_dashboard,

        horizon_dashboard,

        decision_dashboard

    ) = (

        GovernanceForecastLoader

        .load()

    )

    signals = (

        GovernanceSignalEngine

        .build(

            forecast_dashboard,

            horizon_dashboard,

            decision_dashboard,

            stress_dashboard

        )

    )

    metrics = (

        GovernanceScoringEngine

        .calculate(

            forecast,

            alert_governance,

            monitor,

            signals

        )

    )

    recommendation = (

        ExecutiveRecommendationEngine

        .recommend(

            metrics

        )

    )

    governance_status = (

        GovernanceStatusEngine

        .classify(

            metrics[

                "Governance_Score"

            ]

        )

    )

    dashboard = (

        GovernanceCommandCenter

        .build(

            metrics,

            recommendation,

            signals,

            governance_status

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