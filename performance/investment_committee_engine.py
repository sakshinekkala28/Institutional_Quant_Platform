from __future__ import annotations

import logging

from dataclasses import dataclass

from pathlib import Path

import pandas as pd

from core.settings import settings

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

PERFORMANCE_SUMMARY_FILE = (

    PERFORMANCE_DIR

    / "performance_summary.csv"

)

PERFORMANCE_FORECAST_FILE = (

    PERFORMANCE_DIR

    / "performance_forecast.csv"

)

RISK_DASHBOARD_FILE = (

    PERFORMANCE_DIR

    / "risk_dashboard.csv"

)

SURVEILLANCE_DASHBOARD_FILE = (

    PERFORMANCE_DIR

    / "surveillance_dashboard.csv"

)

INVESTMENT_COMMITTEE_REPORT_FILE = (

    PERFORMANCE_DIR

    / "investment_committee_report.csv"

)

INVESTMENT_COMMITTEE_DASHBOARD_FILE = (

    PERFORMANCE_DIR

    / "investment_committee_dashboard.csv"

)

GOVERNANCE_DECISION_FILE = (

    PERFORMANCE_DIR

    / "governance_decision.csv"

)

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
# COMMITTEE MODEL
# ==========================================================

@dataclass

class CommitteeDecision:

    Committee_Score: float

    Governance_Score: float

    Risk_Score: float

    Decision: str

    Rationale: str

# ==========================================================
# REPOSITORY
# ==========================================================

class InvestmentCommitteeRepository:

    @staticmethod
    def load_summary() -> pd.DataFrame:

        logger.info(

            "Loading Performance Summary"

        )

        return pd.read_csv(

            PERFORMANCE_SUMMARY_FILE

        )

    @staticmethod
    def load_forecast() -> pd.DataFrame:

        logger.info(

            "Loading Forecast"

        )

        return pd.read_csv(

            PERFORMANCE_FORECAST_FILE

        )

    @staticmethod
    def load_risk_dashboard() -> pd.DataFrame:

        logger.info(

            "Loading Risk Dashboard"

        )

        return pd.read_csv(

            RISK_DASHBOARD_FILE

        )

    @staticmethod
    def load_surveillance_dashboard() -> pd.DataFrame:

        logger.info(

            "Loading Surveillance Dashboard"

        )

        return pd.read_csv(

            SURVEILLANCE_DASHBOARD_FILE

        )
    
# ==========================================================
# VALIDATOR
# ==========================================================

class CommitteeValidator:

    @staticmethod
    def validate(

        summary: pd.DataFrame,

        forecast: pd.DataFrame,

        risk_dashboard: pd.DataFrame,

        surveillance_dashboard: pd.DataFrame

    ):

        if summary.empty:

            raise ValueError(

                "Performance Summary Empty"

            )

        if forecast.empty:

            raise ValueError(

                "Forecast Empty"

            )

        if risk_dashboard.empty:

            raise ValueError(

                "Risk Dashboard Empty"

            )

        if surveillance_dashboard.empty:

            raise ValueError(

                "Surveillance Dashboard Empty"

            )

        logger.info(

            "Committee Validation Passed"

        )

# ==========================================================
# COMMITTEE SCORE ENGINE
# ==========================================================

class CommitteeScoreEngine:

    @staticmethod
    def calculate(

        forecast: pd.DataFrame

    ) -> float:

        logger.info(

            "Calculating Committee Score"

        )

        row = (

            forecast

            .iloc[0]

        )

        score = 0.0

        sharpe = float(

            row[

                "Expected_Sharpe"

            ]

        )

        expected_return = float(

            row[

                "Expected_Return_12M"

            ]

        )

        confidence = float(

            row[

                "Forecast_Confidence"

            ]

        )

        recommendation = str(

            row[

                "Forecast_Recommendation"

            ]

        )

        if sharpe >= 1.50:

            score += 30

        elif sharpe >= 1.00:

            score += 20

        elif sharpe >= 0.50:

            score += 10

        if expected_return >= 0.25:

            score += 25

        elif expected_return >= 0.15:

            score += 15

        elif expected_return >= 0.05:

            score += 5

        if confidence >= 80:

            score += 25

        elif confidence >= 60:

            score += 15

        elif confidence >= 40:

            score += 5

        recommendation_map = {

            "OVERWEIGHT": 20,

            "MARKET_WEIGHT": 10,

            "UNDERWEIGHT": 5,

            "REDUCE": 0

        }

        score += (

            recommendation_map

            .get(

                recommendation,

                0

            )

        )

        return float(

            min(

                score,

                100

            )

        )
    
# ==========================================================
# GOVERNANCE SCORE ENGINE
# ==========================================================

class GovernanceScoreEngine:

    @staticmethod
    def calculate(

        forecast: pd.DataFrame,

        surveillance_dashboard: pd.DataFrame

    ) -> float:

        logger.info(

            "Calculating Governance Score"

        )

        score = 100.0

        row = (

            forecast

            .iloc[0]

        )

        confidence = float(

            row[

                "Forecast_Confidence"

            ]

        )

        if confidence < 60:

            score -= 20

        elif confidence < 75:

            score -= 10

        if (

            "Value"

            in surveillance_dashboard.columns

        ):

            score -= min(

                len(

                    surveillance_dashboard

                ),

                10

            )

        return float(

            max(

                score,

                0

            )

        )
    
# ==========================================================
# RISK SCORE ENGINE
# ==========================================================

class RiskScoreEngine:

    @staticmethod
    def calculate(

        forecast: pd.DataFrame

    ) -> float:

        logger.info(

            "Calculating Risk Score"

        )

        row = (

            forecast

            .iloc[0]

        )

        score = 100.0

        volatility = float(

            row[

                "Expected_Volatility"

            ]

        )

        drawdown = float(

            row[

                "Expected_Max_Drawdown"

            ]

        )

        risk_grade = str(

            row[

                "Forecast_Risk_Grade"

            ]

        )

        if volatility > 0.25:

            score -= 30

        elif volatility > 0.20:

            score -= 15

        elif volatility > 0.15:

            score -= 5

        if drawdown > 0.35:

            score -= 30

        elif drawdown > 0.25:

            score -= 15

        elif drawdown > 0.15:

            score -= 5

        risk_grade_penalty = {

            "LOW": 0,

            "MODERATE": 10,

            "HIGH": 25,

            "VERY_HIGH": 40

        }

        score -= (

            risk_grade_penalty

            .get(

                risk_grade,

                0

            )

        )

        return float(

            max(

                score,

                0

            )

        )
    
# ==========================================================
# COMMITTEE SCORECARD ENGINE
# ==========================================================

class CommitteeScorecardEngine:

    @staticmethod
    def build(

        committee_score: float,

        governance_score: float,

        risk_score: float

    ) -> pd.DataFrame:

        return pd.DataFrame(

            [

                {

                    "Metric":

                        "Committee_Score",

                    "Value":

                        committee_score

                },

                {

                    "Metric":

                        "Governance_Score",

                    "Value":

                        governance_score

                },

                {

                    "Metric":

                        "Risk_Score",

                    "Value":

                        risk_score

                }

            ]

        )

# ==========================================================
# APPROVAL DECISION ENGINE
# ==========================================================

class ApprovalDecisionEngine:

    @staticmethod
    def calculate(

        committee_score: float,

        governance_score: float,

        risk_score: float

    ) -> str:

        logger.info(

            "Calculating Approval Decision"

        )

        overall_score = (

            committee_score

            * 0.40

            +

            governance_score

            * 0.30

            +

            risk_score

            * 0.30

        )

        if overall_score >= 85:

            return "APPROVE"

        elif overall_score >= 70:

            return "APPROVE_WITH_CAUTION"

        elif overall_score >= 55:

            return "REVIEW_REQUIRED"

        return "REJECT"
    
# ==========================================================
# GOVERNANCE RULE ENGINE
# ==========================================================

class GovernanceRuleEngine:

    @staticmethod
    def apply(

        decision: str,

        forecast: pd.DataFrame

    ) -> str:

        logger.info(

            "Applying Governance Rules"

        )

        row = (

            forecast

            .iloc[0]

        )

        confidence = float(

            row[

                "Forecast_Confidence"

            ]

        )

        drawdown = float(

            row[

                "Expected_Max_Drawdown"

            ]

        )

        sharpe = float(

            row[

                "Expected_Sharpe"

            ]

        )

        if confidence < 50:

            return "REVIEW_REQUIRED"

        if drawdown > 0.40:

            return "REVIEW_REQUIRED"

        if sharpe < 0.50:

            return "REJECT"

        return decision

# ==========================================================
# RISK REVIEW ENGINE
# ==========================================================

class RiskReviewEngine:

    @staticmethod
    def build(

        forecast: pd.DataFrame

    ) -> list[str]:

        logger.info(

            "Building Risk Review"

        )

        row = (

            forecast

            .iloc[0]

        )

        comments = []

        if (

            row[

                "Expected_Volatility"

            ]

            > 0.20

        ):

            comments.append(

                "Elevated forecast volatility"

            )

        if (

            row[

                "Expected_Max_Drawdown"

            ]

            > 0.25

        ):

            comments.append(

                "Elevated forecast drawdown"

            )

        if (

            row[

                "Forecast_Confidence"

            ]

            < 60

        ):

            comments.append(

                "Low forecast confidence"

            )

        if not comments:

            comments.append(

                "Risk profile acceptable"

            )

        return comments
    
# ==========================================================
# COMMITTEE RATIONALE ENGINE
# ==========================================================

class CommitteeRationaleEngine:

    @staticmethod
    def build(

        forecast: pd.DataFrame,

        decision: str

    ) -> str:

        logger.info(

            "Building Committee Rationale"

        )

        row = (

            forecast

            .iloc[0]

        )

        rationale = [

            f"Decision: {decision}",

            f"Forecast Regime: {row['Forecast_Regime']}",

            f"Recommendation: {row['Forecast_Recommendation']}",

            f"Expected Sharpe: {row['Expected_Sharpe']:.2f}",

            f"Expected Return: {row['Expected_Return_12M']:.2%}",

            f"Forecast Confidence: {row['Forecast_Confidence']:.1f}"

        ]

        return " | ".join(

            rationale

        )

# ==========================================================
# GOVERNANCE DECISION ENGINE
# ==========================================================

class GovernanceDecisionEngine:

    @staticmethod
    def build(

        committee_score: float,

        governance_score: float,

        risk_score: float,

        decision: str,

        rationale: str

    ) -> pd.DataFrame:

        return pd.DataFrame(

            [

                {

                    "Committee_Score":

                        committee_score,

                    "Governance_Score":

                        governance_score,

                    "Risk_Score":

                        risk_score,

                    "Decision":

                        decision,

                    "Rationale":

                        rationale

                }

            ]

        )

# ==========================================================
# INVESTMENT COMMITTEE DASHBOARD ENGINE
# ==========================================================

class InvestmentCommitteeDashboardEngine:

    @staticmethod
    def build(

        decision_model: CommitteeDecision

    ) -> pd.DataFrame:

        logger.info(

            "Building Committee Dashboard"

        )

        return pd.DataFrame(

            [

                {

                    "Metric":

                        "Committee_Score",

                    "Value":

                        decision_model
                        .Committee_Score

                },

                {

                    "Metric":

                        "Governance_Score",

                    "Value":

                        decision_model
                        .Governance_Score

                },

                {

                    "Metric":

                        "Risk_Score",

                    "Value":

                        decision_model
                        .Risk_Score

                },

                {

                    "Metric":

                        "Decision",

                    "Value":

                        decision_model
                        .Decision

                },

                {

                    "Metric":

                        "Rationale",

                    "Value":

                        decision_model
                        .Rationale

                }

            ]

        )
        
# ==========================================================
# EXPORT ENGINE
# ==========================================================

class ExportEngine:

    @staticmethod
    def save(

        committee_report: pd.DataFrame,

        committee_dashboard: pd.DataFrame,

        governance_decision: pd.DataFrame

    ):

        logger.info(

            "Exporting Committee Reports"

        )

        committee_report.to_csv(

            INVESTMENT_COMMITTEE_REPORT_FILE,

            index=False

        )

        committee_dashboard.to_csv(

            INVESTMENT_COMMITTEE_DASHBOARD_FILE,

            index=False

        )

        governance_decision.to_csv(

            GOVERNANCE_DECISION_FILE,

            index=False

        )

        logger.info(

            "Committee Reports Exported"

        )

# ==========================================================
# INVESTMENT COMMITTEE ENGINE
# ==========================================================

class InvestmentCommitteeEngine:

    def run(

        self

    ) -> CommitteeDecision:

        logger.info(

            "Starting Investment Committee"

        )

        summary = (

            InvestmentCommitteeRepository

            .load_summary()

        )

        forecast = (

            InvestmentCommitteeRepository

            .load_forecast()

        )

        risk_dashboard = (

            InvestmentCommitteeRepository

            .load_risk_dashboard()

        )

        surveillance_dashboard = (

            InvestmentCommitteeRepository

            .load_surveillance_dashboard()

        )

        CommitteeValidator.validate(

            summary,

            forecast,

            risk_dashboard,

            surveillance_dashboard

        )

        committee_score = (

            CommitteeScoreEngine

            .calculate(

                forecast

            )

        )

        governance_score = (

            GovernanceScoreEngine

            .calculate(

                forecast,

                surveillance_dashboard

            )

        )

        risk_score = (

            RiskScoreEngine

            .calculate(

                forecast

            )

        )

        decision = (

            ApprovalDecisionEngine

            .calculate(

                committee_score,

                governance_score,

                risk_score

            )

        )

        decision = (

            GovernanceRuleEngine

            .apply(

                decision,

                forecast

            )

        )

        
        rationale = (

            CommitteeRationaleEngine

            .build(

                forecast,

                decision

            )

        )
        
        risk_comments = (

            RiskReviewEngine

            .build(

                forecast

            )

        )

        rationale = (

            rationale

            +

            " | "

            +

            "; ".join(

                risk_comments

            )

        )

        decision_model = (

            CommitteeDecision(

                Committee_Score=

                    committee_score,

                Governance_Score=

                    governance_score,

                Risk_Score=

                    risk_score,

                Decision=

                    decision,

                Rationale=

                    rationale

            )

        )

        committee_report = pd.DataFrame(

            [

                decision_model

                .__dict__

            ]

        )

        governance_decision = (

            GovernanceDecisionEngine

            .build(

                committee_score,

                governance_score,

                risk_score,

                decision,

                rationale

            )

        )

        committee_dashboard = (

            InvestmentCommitteeDashboardEngine

            .build(

                decision_model

            )

        )

        ExportEngine.save(

            committee_report,

            committee_dashboard,

            governance_decision

        )

        logger.info(

            "Investment Committee Complete"

        )

        return decision_model

# ==========================================================
# RUNNER
# ==========================================================

def run_example():

    result = (

        InvestmentCommitteeEngine()

        .run()

    )

    print()

    print(

        "=" * 80

    )

    print(

        "INVESTMENT COMMITTEE DECISION"

    )

    print(

        "=" * 80

    )

    print(

        f"Committee Score: "

        f"{result.Committee_Score:.2f}"

    )

    print(

        f"Governance Score: "

        f"{result.Governance_Score:.2f}"

    )

    print(

        f"Risk Score: "

        f"{result.Risk_Score:.2f}"

    )

    print(

        f"Decision: "

        f"{result.Decision}"

    )

    print(

        f"Rationale: "

        f"{result.Rationale}"

    )

    print(

        "=" * 80

    )


if __name__ == "__main__":

    run_example()