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

PERFORMANCE_DIR = (

    ROOT_DIR

    / "data"

    / "performance"

)

MONITORING_DIR = (

    ROOT_DIR

    / "data"

    / "monitoring"

)

FORECAST_FILE = (

    PERFORMANCE_DIR

    / "performance_forecast.csv"

)

GOVERNANCE_FILE = (

    PERFORMANCE_DIR

    / "governance_decision.csv"

)

ALERT_GOVERNANCE_FILE = (

    MONITORING_DIR

    / "alert_governance.csv"

)

SCENARIO_FILE = (

    PERFORMANCE_DIR

    / "scenario_analysis.csv"

)

STRESS_FILE = (

    PERFORMANCE_DIR

    / "stress_test_results.csv"

)

STRESS_IMPACT_FILE = (

    PERFORMANCE_DIR

    / "stress_committee_impact.csv"

)

SURVEILLANCE_FILE = (

    PERFORMANCE_DIR

    / "surveillance_dashboard.csv"

)

INVESTMENT_PACK_FILE = (

    PERFORMANCE_DIR

    / "investment_committee_pack.csv"

)

COMMITTEE_SUMMARY_FILE = (

    PERFORMANCE_DIR

    / "committee_summary.csv"

)

EXECUTIVE_DASHBOARD_FILE = (

    PERFORMANCE_DIR

    / "executive_dashboard.csv"

)

GOVERNANCE_COMMITTEE_DASHBOARD_FILE = (

    PERFORMANCE_DIR

    / "governance_committee_dashboard.csv"

)

# ==========================================================
# REPOSITORY
# ==========================================================

class CommitteePackRepository:

    @staticmethod
    def load_forecast():

        return pd.read_csv(

            FORECAST_FILE

        )

    @staticmethod
    def load_governance():

        return pd.read_csv(

            GOVERNANCE_FILE

        )

    @staticmethod
    def load_scenarios():

        return pd.read_csv(

            SCENARIO_FILE

        )

    @staticmethod
    def load_stress():

        return pd.read_csv(

            STRESS_FILE

        )

    @staticmethod
    def load_stress_impact():

        return pd.read_csv(

            STRESS_IMPACT_FILE

        )

    @staticmethod
    def load_surveillance():

        return pd.read_csv(

            SURVEILLANCE_FILE

        )
    
# ==========================================================
# VALIDATOR
# ==========================================================

class CommitteePackValidator:

    @staticmethod
    def validate(

        forecast,

        governance,

        scenarios,

        stress

    ):

        if forecast.empty:

            raise ValueError(

                "Forecast Empty"

            )

        if governance.empty:

            raise ValueError(

                "Governance Empty"

            )

        if scenarios.empty:

            raise ValueError(

                "Scenario Empty"

            )

        if stress.empty:

            raise ValueError(

                "Stress Empty"

            )
        
# ==========================================================
# EXECUTIVE RECOMMENDATION
# ==========================================================

class ExecutiveRecommendationEngine:

    @staticmethod
    def build(

        forecast,

        governance

    ):

        decision = (

            governance

            .iloc[0]

            ["Decision"]

        )

        recommendation = (

            forecast

            .iloc[0]

            [

                "Forecast_Recommendation"

            ]

        )

        if decision == "APPROVE":

            return recommendation

        if decision == "REVIEW":

            return (

                "REVIEW_REQUIRED"

            )

        return "REJECT"

# ==========================================================
# COMMITTEE SUMMARY ENGINE
# ==========================================================

class CommitteeSummaryEngine:

    @staticmethod
    def build(

        forecast: pd.DataFrame,

        governance: pd.DataFrame

    ) -> pd.DataFrame:

        logger.info(

            "Building Committee Summary"

        )

        forecast_row = (

            forecast

            .iloc[0]

        )

        governance_row = (

            governance

            .iloc[0]

        )

        return pd.DataFrame(

            [

                {

                    "Section":
                        "Forecast",

                    "Metric":

                        "Decision",

                    "Value":

                        governance_row[
                            "Decision"
                        ]

                },

                {

                    "Section":
                        "Forecast",
                        
                    "Metric":

                        "Forecast_Regime",

                    "Value":

                        forecast_row[
                            "Forecast_Regime"
                        ]

                },

                {

                    "Section":
                        "Forecast",
 
                    "Metric":

                        "Forecast_Recommendation",

                    "Value":

                        forecast_row[
                            "Forecast_Recommendation"
                        ]

                },

                {

                    "Section":
                        "Forecast",
 
                    "Metric":

                        "Forecast_Confidence",

                    "Value":

                        forecast_row[
                            "Forecast_Confidence"
                        ]

                },

                {

                    "Section":
                        "Forecast",
 
                    "Metric":

                        "Expected_Return_12M",

                    "Value":

                        forecast_row[
                            "Expected_Return_12M"
                        ]

                },

                {

                    "Section":
                        "Forecast",
 
                    "Metric":

                        "Committee_View",

                    "Value":

                        (
                            "STRONG_BUY"

                            if governance_row[
                                "Committee_Score"
                            ] >= 85

                            else

                            "BUY"

                            if governance_row[
                                "Committee_Score"
                            ] >= 70

                            else

                            "HOLD"

                            if governance_row[
                                "Committee_Score"
                            ] >= 50

                            else

                            "REDUCE"
                        )

                },
            
                {

                    "Section":
                        "Forecast",
 
                    "Metric":

                        "Investment_Decision",

                    "Value":

                        forecast_row[
                            "Forecast_Recommendation"
                        ]

                }

            ]

        )
        
# ==========================================================
# SCENARIO REVIEW ENGINE
# ==========================================================

class ScenarioReviewEngine:

    @staticmethod
    def build(

        scenarios: pd.DataFrame

    ) -> pd.DataFrame:

        logger.info(

            "Building Scenario Review"

        )

        best = (

            scenarios

            .sort_values(

                "Scenario_Score",

                ascending=False

            )

            .iloc[0]

        )

        worst = (

            scenarios

            .sort_values(

                "Scenario_Score",

                ascending=True

            )

            .iloc[0]

        )

        return pd.DataFrame(

            [

                {

                    "Section":
                        "Scenario",
 
                    "Metric":

                        "Best_Scenario",

                    "Value":

                        best[
                            "Scenario"
                        ]

                },

                {

                    "Section":
                        "Scenario",
 
                    "Metric":

                        "Best_Scenario_Score",

                    "Value":

                        best[
                            "Scenario_Score"
                        ]

                },

                {

                    "Section":
                        "Scenario",
 
                    "Metric":

                        "Worst_Scenario",

                    "Value":

                        worst[
                            "Scenario"
                        ]

                },

                {

                    "Section":
                        "Scenario",
 
                    "Metric":

                        "Worst_Scenario_Score",

                    "Value":

                        worst[
                            "Scenario_Score"
                        ]

                }

            ]

        )
    
# ==========================================================
# STRESS REVIEW ENGINE
# ==========================================================

class StressReviewEngine:

    @staticmethod
    def build(

        stress_df: pd.DataFrame,

        impact_df: pd.DataFrame

    ) -> pd.DataFrame:

        logger.info(

            "Building Stress Review"

        )

        best = (

            stress_df

            .sort_values(

                "Stress_Score",

                ascending=False

            )

            .iloc[0]

        )

        worst = (

            stress_df

            .sort_values(

                "Stress_Score",

                ascending=True

            )

            .iloc[0]

        )

        rejects = (

            impact_df[

                "Committee_Decision"

            ]

            ==

            "REJECT"

        ).sum()

        return pd.DataFrame(

            [

                {

                    "Section":
                        "Stress",
 
                    "Metric":

                        "Best_Stress",

                    "Value":

                        best[
                            "Scenario"
                        ]

                },

                {

                    "Section":
                        "Stress",
 
                    "Metric":

                        "Best_Stress_Score",

                    "Value":

                        best[
                            "Stress_Score"
                        ]

                },

                {

                    "Section":
                        "Stress",
 
                    "Metric":

                        "Worst_Stress",

                    "Value":

                        worst[
                            "Scenario"
                        ]

                },

                {

                    "Section":
                        "Stress",
 
                    "Metric":

                        "Worst_Stress_Score",

                    "Value":

                        worst[
                            "Stress_Score"
                        ]

                },

                {

                    "Section":
                        "Stress",
 
                    "Metric":

                        "Rejected_Stress_Scenarios",

                    "Value":

                        rejects

                }

            ]

        )
    
# ==========================================================
# GOVERNANCE REVIEW ENGINE
# ==========================================================

class GovernanceReviewEngine:

    @staticmethod
    def build(

        governance: pd.DataFrame

    ) -> pd.DataFrame:

        logger.info(

            "Building Governance Review"

        )

        row = (

            governance

            .iloc[0]

        )

        return pd.DataFrame(

            [

                {

                    "Section":
                        "Governance",
 
                    "Metric":

                        "Committee_Score",

                    "Value":

                        row[
                            "Committee_Score"
                        ]

                },

                {

                    "Section":
                        "Governance",
 
                    "Metric":

                        "Governance_Score",

                    "Value":

                        row[
                            "Governance_Score"
                        ]

                },

                {

                    "Section":
                        "Governance",
 
                    "Metric":

                        "Risk_Score",

                    "Value":

                        row[
                            "Risk_Score"
                        ]

                }

            ]

        )

class AlertGovernanceReviewEngine:

    @staticmethod
    def build(

        alert_governance

    ):

        logger.info(

            "Building Alert Governance Review"

        )

        review_rows = []

        for _, row in alert_governance.iterrows():

            review_rows.append(

                {

                    "Section":

                        "Alert_Governance",

                    "Metric":

                        str(

                            row["Metric"]

                        ),

                    "Value":

                        str(

                            row["Value"]

                        )

                }

            )

        return pd.DataFrame(

            review_rows

        )
    

class GovernanceCommandCenterReview:

    @staticmethod
    def build(

        governance_committee

    ):

        logger.info(

            "Building Governance Command Center Review"

        )

        rows = []

        for _, row in governance_committee.iterrows():

            rows.append(

                {

                    "Section":

                        "Governance_Command_Center",

                    "Metric":

                        str(

                            row["Metric"]

                        ),

                    "Value":

                        str(

                            row["Value"]

                        )

                }

            )

        return pd.DataFrame(

            rows

        )
    
class AlertGovernanceLoader:

    @staticmethod
    def load():

        return pd.read_csv(

            ALERT_GOVERNANCE_FILE

        )
    
class GovernanceCommitteeDashboardLoader:

    @staticmethod
    def load():

        logger.info(

            "Loading Governance Committee Dashboard"

        )

        return pd.read_csv(

            GOVERNANCE_COMMITTEE_DASHBOARD_FILE

        )
    
# ==========================================================
# SURVEILLANCE REVIEW ENGINE
# ==========================================================

class SurveillanceReviewEngine:

    @staticmethod
    def build(

        surveillance: pd.DataFrame

    ) -> pd.DataFrame:

        logger.info(

            "Building Surveillance Review"

        )

        if surveillance.empty:

            return pd.DataFrame(

                [

                    {

                        "Section":
                            "Surveillance",
 
                        "Metric":

                            "Surveillance_Status",

                        "Value":

                            "UNKNOWN"

                    }

                ]

            )

        review_rows = []

        for _, row in surveillance.iterrows():

            review_rows.append(

                {

                    "Section":

                        "Surveillance",
                    
                    "Metric":

                        str(

                            row[
                                "Metric"
                            ]

                        ),

                    "Value":

                        str(

                            row[
                                "Value"
                            ]

                        )

                }

            )

        return pd.DataFrame(

            review_rows

        )
    
# ==========================================================
# PACK SCORE ENGINE
# ==========================================================

class PackScoreEngine:

    @staticmethod
    def build(

        governance: pd.DataFrame,

        forecast: pd.DataFrame,

        scenarios: pd.DataFrame,

        stress_df: pd.DataFrame

    ) -> float:

        logger.info(

            "Calculating Pack Score"

        )

        governance_score = float(

            governance

            .iloc[0]

            [

                "Committee_Score"

            ]

        )

        forecast_confidence = float(

            forecast

            .iloc[0]

            [

                "Forecast_Confidence"

            ]

        )

        scenario_score = float(

            scenarios

            [

                "Scenario_Score"

            ]

            .mean()

        )

        stress_score = float(

            stress_df

            [

                "Stress_Score"

            ]

            .mean()

        )

        pack_score = (

            governance_score * 0.40

            +

            forecast_confidence * 0.20

            +

            scenario_score * 0.20

            +

            stress_score * 0.20

        )

        return round(

            pack_score,

            2

        )
    
# ==========================================================
# EXECUTIVE DASHBOARD ENGINE
# ==========================================================

class ExecutiveDashboardEngine:

    @staticmethod
    def build(

        governance: pd.DataFrame,

        forecast: pd.DataFrame,

        scenarios: pd.DataFrame,

        stress_df: pd.DataFrame,

        governance_command_metrics: dict,

        alert_metrics: dict,

        pack_score: float,

        recommendation: str

    ) -> pd.DataFrame:

        logger.info(

            "Building Executive Dashboard"

        )

        return pd.DataFrame(

            [

                {
                    "Metric":
                        "Governance_Score",

                    "Value":
                        governance_command_metrics.get(
                            "Governance_Score",
                            "N/A"
                        )
                },

                {
                    "Metric":
                        "Risk_Level",

                    "Value":
                        governance_command_metrics.get(
                            "Risk_Level",
                            "N/A"
                        )
                },

                {
                    "Metric":
                        "Executive_Action",

                    "Value":
                        governance_command_metrics.get(
                            "Executive_Action",
                            "N/A"
                        )
                },

                {

                    "Metric":

                        "Pack_Score",

                    "Value":

                        pack_score

                },

                {

                    "Metric":

                        "Recommendation",

                    "Value":

                        recommendation

                },

                {

                    "Metric":

                        "Forecast_Regime",

                    "Value":

                        forecast

                        .iloc[0]

                        [

                            "Forecast_Regime"

                        ]

                },

                {

                    "Metric":

                        "Expected_Return_12M",

                    "Value":

                        forecast

                        .iloc[0]

                        [

                            "Expected_Return_12M"

                        ]

                },

                {

                    "Metric":

                        "Scenario_Average",

                    "Value":

                        round(

                            scenarios

                            [

                                "Scenario_Score"

                            ]

                            .mean(),

                            2

                        )

                },

                {

                    "Metric":

                        "Stress_Average",

                    "Value":

                        round(

                            stress_df

                            [

                                "Stress_Score"

                            ]

                            .mean(),

                            2

                        )

                },

                {
                    "Metric":
                        "Committee_View",

                    "Value":
                        (
                            "STRONG_BUY"
                            if pack_score >= 80
                            else
                            "BUY"
                            if pack_score >= 65
                            else
                            "HOLD"
                            if pack_score >= 50
                            else
                            "REDUCE"
                        )
                },

                {

                    "Metric":

                        "Alert_Health_Score",

                    "Value":

                        alert_metrics.get(

                            "Alert_Health_Score",

                            "N/A"

                        )

                },

                {

                    "Metric":

                        "Alert_Escalation",

                    "Value":

                        alert_metrics.get(

                            "Alert_Escalation",

                            "N/A"

                        )

                },

                {

                    "Metric":

                        "Pack_Grade",

                    "Value":

                        (
                            "A"

                            if pack_score >= 85

                            else

                            "B"

                            if pack_score >= 70

                            else

                            "C"

                            if pack_score >= 55

                            else

                            "D"
                        )

                }
            ]

        )
    
# ==========================================================
# INVESTMENT COMMITTEE PACK ENGINE
# ==========================================================

class InvestmentCommitteePackEngine:

    def run(

        self

    ):

        logger.info(

            "Starting Investment Committee Pack"

        )

        forecast = (

            CommitteePackRepository

            .load_forecast()

        )

        governance = (

            CommitteePackRepository

            .load_governance()

        )

        alert_governance = (

            AlertGovernanceLoader

            .load()

        )

        governance_committee = (

            GovernanceCommitteeDashboardLoader
        
            .load()

        )

        alert_metrics = dict(

            zip(

                alert_governance["Metric"],

                alert_governance["Value"]

            )

        )

        scenarios = (

            CommitteePackRepository

            .load_scenarios()

        )

        stress_df = (

            CommitteePackRepository

            .load_stress()

        )

        stress_impact = (

            CommitteePackRepository

            .load_stress_impact()

        )

        surveillance = (

            CommitteePackRepository

            .load_surveillance()

        )

        CommitteePackValidator.validate(

            forecast,

            governance,

            scenarios,

            stress_df

        )

        committee_summary = (

            CommitteeSummaryEngine

            .build(

                forecast,

                governance

            )

        )

        scenario_review = (

            ScenarioReviewEngine

            .build(

                scenarios

            )

        )

        stress_review = (

            StressReviewEngine

            .build(

                stress_df,

                stress_impact

            )

        )

        governance_review = (

            GovernanceReviewEngine

            .build(

                governance

            )

        )

        alert_governance_review = (

            AlertGovernanceReviewEngine

            .build(

                alert_governance

            )

        )

        governance_command_center_review = (

            GovernanceCommandCenterReview

            .build(

                governance_committee

            )

        )

        governance_command_metrics = dict(

            zip(

                governance_committee["Metric"],

                governance_committee["Value"]
                
            )

        )

        surveillance_review = (

            SurveillanceReviewEngine

            .build(

                surveillance

            )

        )

        recommendation = (

            ExecutiveRecommendationEngine

            .build(

                forecast,

                governance

            )

        )

        pack_score = (

            PackScoreEngine

            .build(

                governance,

                forecast,

                scenarios,

                stress_df

            )

        )

        executive_dashboard = (

            ExecutiveDashboardEngine

            .build(

                governance,

                forecast,

                scenarios,

                stress_df,

                governance_command_metrics,

                alert_metrics,

                pack_score,

                recommendation

            )

        )

        committee_pack = pd.concat(

            [

                committee_summary,

                scenario_review,

                stress_review,

                governance_review,

                alert_governance_review,

                governance_command_center_review,

                surveillance_review

            ],

            ignore_index=True

        )

        return (

            committee_pack,

            executive_dashboard,

            pack_score

        )
    
# ==========================================================
# EXPORT ENGINE
# ==========================================================

class ExportEngine:

    @staticmethod
    def export(

        committee_pack: pd.DataFrame,

        executive_dashboard: pd.DataFrame

    ):

        logger.info(

            "Exporting Committee Pack"

        )

        committee_pack.to_csv(

            INVESTMENT_PACK_FILE,

            index=False

        )

        committee_pack.to_csv(

            COMMITTEE_SUMMARY_FILE,

            index=False

        )

        executive_dashboard.to_csv(

            EXECUTIVE_DASHBOARD_FILE,

            index=False

        )

        logger.info(

            "Committee Pack Exported"

        )

# ==========================================================
# RUNNER
# ==========================================================

def run_example():

    (

        committee_pack,

        executive_dashboard,

        pack_score

    ) = (

        InvestmentCommitteePackEngine()

        .run()

    )

    ExportEngine.export(

        committee_pack,

        executive_dashboard

    )

    recommendation = (

        executive_dashboard

        .loc[

            executive_dashboard[
                "Metric"
            ]
            ==
            "Recommendation",

            "Value"

        ]

        .iloc[0]

    )

    print()

    print(

        "=" * 80

    )

    print(

        "INVESTMENT COMMITTEE PACK"

    )

    print(

        "=" * 80

    )

    print(

        f"Pack Score: {pack_score:.2f}"

    )

    print(

        f"Recommendation: {recommendation}"

    )

    print(

        "=" * 80

    )


# ==========================================================
# MAIN
# ==========================================================

if __name__ == "__main__":

    run_example()