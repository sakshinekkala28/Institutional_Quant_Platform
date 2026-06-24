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

GOVERNANCE_FILE = (
    MONITORING_DIR
    / "governance_command_center.csv"
)

OUTPUT_FILE = (
    PERFORMANCE_DIR
    / "cio_risk_budget_dashboard.csv"
)

class RiskBudgetValidator:

    REQUIRED_METRICS = [

        "Governance_Score",

        "Forecast_Confidence",

        "Stress_Severity_Score",

        "Macro_Risk_Level",

        "Governance_Status"

    ]

    @staticmethod
    def validate():

        if not GOVERNANCE_FILE.exists():

            raise FileNotFoundError(

                GOVERNANCE_FILE

            )

        governance = pd.read_csv(

            GOVERNANCE_FILE

        )

        available_metrics = set(

            governance["Metric"]

        )

        missing_metrics = [

            metric

            for metric

            in

            RiskBudgetValidator.REQUIRED_METRICS

            if metric not in available_metrics

        ]

        if missing_metrics:

            raise ValueError(

                f"Missing governance metrics: "

                f"{missing_metrics}"

            )

        logger.info(

            "Risk Budget Validation Passed"

        )

class RiskBudgetRepository:

    @staticmethod
    def load():

        logger.info(

            "Loading Governance Dashboard"

        )

        governance = pd.read_csv(

            GOVERNANCE_FILE

        )

        return governance
    
class RiskBudgetSignalEngine:

    @staticmethod
    def extract(

        governance

    ):

        metrics = dict(

            zip(

                governance["Metric"],

                governance["Value"]

            )

        )

        governance_score = float(

            metrics.get(

                "Governance_Score",

                0

            )

        )

        forecast_confidence = float(

            metrics.get(

                "Forecast_Confidence",

                0

            )

        )

        stress_severity = float(

            metrics.get(

                "Stress_Severity_Score",

                0

            )

        )

        macro_risk = str(

            metrics.get(

                "Macro_Risk_Level",

                "MODERATE"

            )

        )

        governance_status = str(

            metrics.get(

                "Governance_Status",

                "UNKNOWN"

            )

        )

        return {

            "Governance_Score":

                governance_score,

            "Forecast_Confidence":

                forecast_confidence,

            "Stress_Severity_Score":

                stress_severity,

            "Macro_Risk_Level":

                macro_risk,

            "Governance_Status":

                governance_status

        }
    
class RiskBudgetScoringEngine:

    MACRO_SCORE_MAP = {

        "LOW": 90,

        "MODERATE": 70,

        "HIGH": 40

    }

    @staticmethod
    def calculate(

        signals

    ):

        governance_score = float(

            signals[

                "Governance_Score"

            ]

        )

        forecast_confidence = float(

            signals[

                "Forecast_Confidence"

            ]

        )

        stress_severity = float(

            signals[

                "Stress_Severity_Score"

            ]

        )

        macro_risk = str(

            signals[

                "Macro_Risk_Level"

            ]

        )

        governance_status = str(

            signals[

                "Governance_Status"

            ]

        )

        stress_health = (

            100

            -

            stress_severity

        )

        macro_score = (

            RiskBudgetScoringEngine

            .MACRO_SCORE_MAP

            .get(

                macro_risk,

                50

            )

        )

        risk_budget_score = (

            governance_score * 0.35

            +

            forecast_confidence * 0.20

            +

            stress_health * 0.30

            +

            macro_score * 0.15

        )

        if governance_status == "HIGH_RISK":

            risk_budget_score -= 5

        elif governance_status == "ELEVATED_RISK":

            risk_budget_score -= 2

        risk_budget_score = max(

            0,

            min(

                100,

                risk_budget_score

            )

        )

        risk_budget_score = round(

            risk_budget_score,

            2

        )

        return {

            "Risk_Budget_Score":

                risk_budget_score,

            "Stress_Health":

                round(

                    stress_health,

                    2

                ),

            "Macro_Score":

                round(

                    macro_score,

                    2

                )

        }
    
class RiskBudgetRegimeEngine:

    @staticmethod
    def determine(

        risk_budget_score

    ):

        if risk_budget_score >= 80:

            return "AGGRESSIVE"

        elif risk_budget_score >= 65:

            return "OFFENSIVE"

        elif risk_budget_score >= 50:

            return "BALANCED"

        elif risk_budget_score >= 35:

            return "CAUTIOUS"

        return "DEFENSIVE"
    
class RiskBudgetScorecardEngine:

    @staticmethod
    def build(

        signals

    ):

        score_metrics = (

            RiskBudgetScoringEngine

            .calculate(

                signals

            )

        )

        risk_regime = (

            RiskBudgetRegimeEngine

            .determine(

                score_metrics[

                    "Risk_Budget_Score"

                ]

            )

        )

        return {

            **score_metrics,

            "Risk_Regime":

                risk_regime

        }
    
class RiskBudgetAllocationEngine:

    @staticmethod
    def calculate(

        scorecard

    ):

        risk_budget_score = float(

            scorecard[

                "Risk_Budget_Score"

            ]

        )

        target_gross_exposure = (

            40

            +

            (

                risk_budget_score

                * 0.70

            )

        )

        target_gross_exposure = round(

            min(

                110,

                max(

                    40,

                    target_gross_exposure

                )

            ),

            2

        )

        target_cash_level = round(

            max(

                0,

                100

                -

                target_gross_exposure

            ),

            2

        )

        target_net_exposure = round(

            target_gross_exposure

            * 0.95,

            2

        )

        position_size_scaler = round(

            target_gross_exposure

            / 100,

            2

        )

        return {

            "Target_Cash_Level":

                target_cash_level,

            "Target_Gross_Exposure":

                target_gross_exposure,

            "Target_Net_Exposure":

                target_net_exposure,

            "Position_Size_Scaler":

                position_size_scaler

        }
    
class RiskCapacityEngine:

    @staticmethod
    def calculate(

        allocation_metrics

    ):

        gross_exposure = float(

            allocation_metrics[

                "Target_Gross_Exposure"

            ]

        )

        position_scaler = float(

            allocation_metrics[

                "Position_Size_Scaler"

            ]

        )

        max_position_size = round(

            position_scaler

            * 5,

            2

        )

        sector_risk_budget = round(

            gross_exposure

            / 10,

            2

        )

        turnover_budget = round(

            position_scaler

            * 25,

            2

        )

        return {

            "Max_Position_Size":

                max_position_size,

            "Sector_Risk_Budget":

                sector_risk_budget,

            "Turnover_Budget":

                turnover_budget

        }
    
class LeverageControlEngine:

    @staticmethod
    def calculate(

        risk_regime

    ):

        leverage_map = {

            "AGGRESSIVE": 1.20,

            "OFFENSIVE": 1.10,

            "BALANCED": 1.00,

            "CAUTIOUS": 0.85,

            "DEFENSIVE": 0.70

        }

        return {

            "Portfolio_Leverage_Limit":

                leverage_map.get(

                    risk_regime,

                    1.00

                )

        }
    
class PortfolioAllocationScorecard:

    @staticmethod
    def build(

        scorecard

    ):

        allocation_metrics = (

            RiskBudgetAllocationEngine

            .calculate(

                scorecard

            )

        )

        capacity_metrics = (

            RiskCapacityEngine

            .calculate(

                allocation_metrics

            )

        )

        leverage_metrics = (

            LeverageControlEngine

            .calculate(

                scorecard[

                    "Risk_Regime"

                ]

            )

        )

        return {

            **allocation_metrics,

            **capacity_metrics,

            **leverage_metrics

        }
    
class RiskBudgetEngine:

    @staticmethod
    def calculate(

        governance

    ):

        signals = (

            RiskBudgetSignalEngine

            .extract(

                governance

            )

        )

        scorecard = (

            RiskBudgetScorecardEngine

            .build(

                signals

            )

        )

        allocation = (

            PortfolioAllocationScorecard

            .build(

                scorecard

            )

        )

        return {

            **signals,

            **scorecard,

            **allocation

        }
    
class RiskBudgetDashboard:

    @staticmethod
    def build(

        metrics

    ):

        dashboard_rows = [

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

                    "Forecast_Confidence",

                "Value":

                    metrics[

                        "Forecast_Confidence"

                    ]

            },

            {

                "Metric":

                    "Stress_Severity_Score",

                "Value":

                    metrics[

                        "Stress_Severity_Score"

                    ]

            },

            {

                "Metric":

                    "Macro_Risk_Level",

                "Value":

                    metrics[

                        "Macro_Risk_Level"

                    ]

            },

            {

                "Metric":

                    "Governance_Status",

                "Value":

                    metrics[

                        "Governance_Status"

                    ]

            },

            {

                "Metric":

                    "Stress_Health",

                "Value":

                    metrics[

                        "Stress_Health"

                    ]

            },

            {

                "Metric":

                    "Macro_Score",

                "Value":

                    metrics[

                        "Macro_Score"

                    ]

            },

            {

                "Metric":

                    "Risk_Budget_Score",

                "Value":

                    metrics[

                        "Risk_Budget_Score"

                    ]

            },

            {

                "Metric":

                    "Risk_Regime",

                "Value":

                    metrics[

                        "Risk_Regime"

                    ]

            },

            {

                "Metric":

                    "Target_Cash_Level",

                "Value":

                    metrics[

                        "Target_Cash_Level"

                    ]

            },

            {

                "Metric":

                    "Target_Gross_Exposure",

                "Value":

                    metrics[

                        "Target_Gross_Exposure"

                    ]

            },

            {

                "Metric":

                    "Target_Net_Exposure",

                "Value":

                    metrics[

                        "Target_Net_Exposure"

                    ]

            },

            {

                "Metric":

                    "Position_Size_Scaler",

                "Value":

                    metrics[

                        "Position_Size_Scaler"

                    ]

            },

            {

                "Metric":

                    "Max_Position_Size",

                "Value":

                    metrics[

                        "Max_Position_Size"

                    ]

            },

            {

                "Metric":

                    "Sector_Risk_Budget",

                "Value":

                    metrics[

                        "Sector_Risk_Budget"

                    ]

            },

            {

                "Metric":

                    "Turnover_Budget",

                "Value":

                    metrics[

                        "Turnover_Budget"

                    ]

            },

            {

                "Metric":

                    "Portfolio_Leverage_Limit",

                "Value":

                    metrics[

                        "Portfolio_Leverage_Limit"

                    ]

            }

        ]

        return pd.DataFrame(

            dashboard_rows

        )
    
class RiskBudgetExporter:

    @staticmethod
    def export(

        dashboard

    ):

        logger.info(

            "Exporting CIO Risk Budget"

        )

        dashboard.to_csv(

            OUTPUT_FILE,

            index=False

        )

        logger.info(

            f"Saved: {OUTPUT_FILE}"

        )

class RiskBudgetReporter:

    @staticmethod
    def report(

        metrics

    ):

        print()

        print(

            "=" * 80

        )

        print(

            "CIO RISK BUDGET"

        )

        print(

            "=" * 80

        )

        print(

            f"Risk Budget Score       : "

            f"{metrics['Risk_Budget_Score']}"

        )

        print(

            f"Risk Regime             : "

            f"{metrics['Risk_Regime']}"

        )

        print(

            f"Cash Target             : "

            f"{metrics['Target_Cash_Level']}%"

        )

        print(

            f"Gross Exposure Target   : "

            f"{metrics['Target_Gross_Exposure']}%"

        )

        print(

            f"Net Exposure Target     : "

            f"{metrics['Target_Net_Exposure']}%"

        )

        print(

            f"Position Scaler         : "

            f"{metrics['Position_Size_Scaler']}"

        )

        print(

            f"Max Position Size       : "

            f"{metrics['Max_Position_Size']}%"

        )

        print(

            f"Sector Risk Budget      : "

            f"{metrics['Sector_Risk_Budget']}%"

        )

        print(

            f"Turnover Budget         : "

            f"{metrics['Turnover_Budget']}%"

        )

        print(

            f"Leverage Limit          : "

            f"{metrics['Portfolio_Leverage_Limit']}x"

        )

        print(

            "=" * 80

        )

def run_example():

    logger.info(

        "Starting CIO Risk Budget Engine"

    )

    RiskBudgetValidator.validate()

    governance = (

        RiskBudgetRepository

        .load()

    )

    metrics = (

        RiskBudgetEngine

        .calculate(

            governance

        )

    )

    dashboard = (

        RiskBudgetDashboard

        .build(

            metrics

        )

    )

    RiskBudgetExporter.export(

        dashboard

    )

    RiskBudgetReporter.report(

        metrics

    )
    

if __name__ == "__main__":

    run_example()