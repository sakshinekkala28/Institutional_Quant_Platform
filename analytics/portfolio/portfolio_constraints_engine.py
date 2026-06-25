from __future__ import annotations

import logging

from pathlib import Path

from datetime import UTC, datetime
import uuid

from typing import Dict
from dataclasses import dataclass, asdict

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

PORTFOLIO_DIR = (

    DATA_DIR

    / "portfolios"

)

INPUT_FILE = (

    PERFORMANCE_DIR

    / "cio_risk_budget_dashboard.csv"

)

OUTPUT_FILE = (

    PORTFOLIO_DIR

    / "portfolio_constraints_dashboard.csv"

)


@dataclass(slots=True)
class ConstraintContext:

    risk_budget_score: float

    risk_regime: str

    target_cash_level: float

    target_gross_exposure: float

    target_net_exposure: float

    position_size_scaler: float

    max_position_size: float

    sector_risk_budget: float

    turnover_budget: float

    portfolio_leverage_limit: float

    governance_status: str

class PortfolioConstraintValidator:

    REQUIRED_METRICS = [

        "Risk_Budget_Score",

        "Risk_Regime",

        "Target_Cash_Level",

        "Target_Gross_Exposure",

        "Target_Net_Exposure",

        "Position_Size_Scaler",

        "Max_Position_Size",

        "Sector_Risk_Budget",

        "Turnover_Budget",

        "Portfolio_Leverage_Limit"

    ]

    @staticmethod
    def validate():

        if not INPUT_FILE.exists():

            raise FileNotFoundError(

                INPUT_FILE

            )

        dashboard = pd.read_csv(

            INPUT_FILE

        )

        if dashboard.empty:

            raise ValueError(

                "Risk Budget Dashboard is empty."

            )

        available = set(

            dashboard["Metric"]

        )

        missing = [

            metric

            for metric

            in

            PortfolioConstraintValidator.REQUIRED_METRICS

            if metric not in available

        ]

        if missing:

            raise ValueError(

                f"Missing metrics: {missing}"

            )

        logger.info(

            "Portfolio Constraint Validation Passed"

        )

class PortfolioConstraintRepository:

    @staticmethod
    def load():

        logger.info(

            "Loading CIO Risk Budget Dashboard"

        )

        dashboard = pd.read_csv(

            INPUT_FILE

        )

        return dashboard
    
class ConstraintSignalEngine:

    @staticmethod
    def extract(

        dashboard

    ) -> Dict:

        metrics = dict(

            zip(

                dashboard["Metric"],

                dashboard["Value"]

            )

        )

        return ConstraintContext(

            risk_budget_score=float(

                metrics.get(

                    "Risk_Budget_Score",

                    0

                )

            ),

            risk_regime=str(

                metrics.get(

                    "Risk_Regime",

                    "BALANCED"

                )

            ),

            target_cash_level=float(

                metrics.get(

                    "Target_Cash_Level",

                    0

                )

            ),

            target_gross_exposure=float(

                metrics.get(

                    "Target_Gross_Exposure",

                    100

                )

            ),

            target_net_exposure=float(

                metrics.get(

                    "Target_Net_Exposure",

                    100

                )

            ),

            position_size_scaler=float(

                metrics.get(

                    "Position_Size_Scaler",

                    1.0

                )

            ),

            max_position_size=float(

                metrics.get(

                    "Max_Position_Size",

                    5

                )

            ),

            sector_risk_budget=float(

                metrics.get(

                    "Sector_Risk_Budget",

                    10

                )

            ),

            turnover_budget=float(

                metrics.get(

                    "Turnover_Budget",

                    25

                )

            ),

            portfolio_leverage_limit=float(

                metrics.get(

                    "Portfolio_Leverage_Limit",

                    1.0

                )

            ),

            governance_status=str(

                metrics.get(

                    "Governance_Status",

                    "UNKNOWN"

                )

            )

        )

class ConstraintBase:

    @staticmethod
    def build(

        signals

    ):

        return asdict(

            signals

        )
    
class ExposureConstraintEngine:

    @staticmethod
    def calculate(

        signals

    ):

        gross_exposure = float(

            signals.target_gross_exposure
        )

        net_exposure = float(

            signals.target_net_exposure

        )

        cash_buffer = float(

            signals.target_cash_level
        )

        leverage_limit = float(

            signals.portfolio_leverage_limit

        )

        long_exposure_limit = round(

            gross_exposure,

            2

        )

        short_exposure_limit = round(

            max(

                0,

                gross_exposure

                -

                net_exposure

            ),

            2

        )

        return {

            "Cash_Buffer":

                cash_buffer,

            "Target_Gross_Exposure":

                gross_exposure,

            "Target_Net_Exposure":

                net_exposure,

            "Long_Exposure_Limit":

                long_exposure_limit,

            "Short_Exposure_Limit":

                short_exposure_limit,

            "Portfolio_Leverage_Limit":

                leverage_limit

        }
    
class PositionConstraintEngine:

    @staticmethod
    def calculate(

        signals

    ):

        policy = (

            ConstraintPolicyEngine

            .get(

                signals.risk_regime

            )

        )

        max_position = float(

            policy[

                "Max_Position"

            ]

        )

        scaler = float(

            signals.position_size_scaler

        )

        min_position = round(

            max_position

            * 0.10,

            2

        )

        target_position = round(

            max_position

            * 0.70,

            2

        )

        return {

            "Max_Position_Weight":

                max_position,

            "Target_Position_Weight":

                target_position,

            "Min_Position_Weight":

                min_position,

            "Position_Size_Scaler":

                scaler

        }
    
class SectorConstraintEngine:

    @staticmethod
    def calculate(

        signals

    ):

        sector_budget = float(

            signals.sector_risk_budget

        )

        max_sector = round(

            sector_budget,

            2

        )

        target_sector = round(

            sector_budget

            * 0.85,

            2

        )

        min_sector = round(

            sector_budget

            * 0.15,

            2

        )

        return {

            "Max_Sector_Weight":

                max_sector,

            "Target_Sector_Weight":

                target_sector,

            "Min_Sector_Weight":

                min_sector

        }
    
class HoldingsConstraintEngine:

    @staticmethod
    def calculate(

        signals

    ):

        regime = str(

            signals.risk_regime

        )

        policy = (

            ConstraintPolicyEngine

            .get(

                regime

            )

        )

        return {

            "Target_Number_of_Holdings":

                policy[

                    "Target_Holdings"

                ]

        }
    
class PortfolioConstraintScorecard:

    @staticmethod
    def build(

        signals

    ):

        exposure = (

            ExposureConstraintEngine

            .calculate(

                signals

            )

        )

        positions = (

            PositionConstraintEngine

            .calculate(

                signals

            )

        )

        sectors = (

            SectorConstraintEngine

            .calculate(

                signals

            )

        )

        holdings = (

            HoldingsConstraintEngine

            .calculate(

                signals

            )

        )

        return {

            **exposure,

            **positions,

            **sectors,

            **holdings

        }

class PortfolioRiskConstraintEngine:

    @staticmethod
    def calculate(

        signals

    ):

        regime = str(

            signals.risk_regime

        )

        score = float(

            signals.risk_budget_score

        )

        policy = (

            ConstraintPolicyEngine

            .get(

                regime

            )

        )

        return {

            "Max_Portfolio_Beta":

                policy[

                    "Max_Beta"

                ],

            "Volatility_Target":

                policy[

                    "Volatility_Target"

                ],

            "Tracking_Error_Budget":

                policy[

                    "Tracking_Error"

                ],

            "Risk_Budget_Score":

                score

        }
    
class DiversificationConstraintEngine:

    @staticmethod
    def calculate(

        signals,

        portfolio_constraints

    ):

        holdings = int(

            portfolio_constraints[

                "Target_Number_of_Holdings"

            ]

        )

        max_position = float(

            portfolio_constraints[

                "Max_Position_Weight"

            ]

        )

        minimum_names = max(

            holdings,

            int(

                100

                /

                max_position

            )

        )

        return {

            "Minimum_Diversification":

                minimum_names,

            "Maximum_Concentration":

                round(

                    max_position,

                    2

                )

        }
    
class CashConstraintEngine:

    @staticmethod
    def calculate(

        portfolio_constraints

    ):

        cash = float(

            portfolio_constraints[

                "Cash_Buffer"

            ]

        )

        investable_cash = round(

            100

            -

            cash,

            2

        )

        return {

            "Cash_Buffer":

                cash,

            "Investable_Capital":

                investable_cash

        }
    
class PortfolioGovernanceConstraintEngine:

    @staticmethod
    def calculate(

        signals

    ):

        regime = str(

            signals.risk_regime

        )

        governance = str(

            signals.governance_status

        )

        approval_required = (

            regime

            in

            [

                "AGGRESSIVE",

                "DEFENSIVE"

            ]

        )

        override_allowed = (

            governance

            !=

            "HIGH_RISK"

        )

        return {

            "Investment_Committee_Approval":

                approval_required,

            "Override_Allowed":

                override_allowed

        }
    
class InstitutionalPortfolioConstraintEngine:

    @staticmethod
    def build(

        signals

    ):

        portfolio_constraints = (

            PortfolioConstraintScorecard

            .build(

                signals

            )

        )

        risk_constraints = (

            PortfolioRiskConstraintEngine

            .calculate(

                signals

            )

        )

        diversification = (

            DiversificationConstraintEngine

            .calculate(

                signals,

                portfolio_constraints

            )

        )

        cash_constraints = (

            CashConstraintEngine

            .calculate(

                portfolio_constraints

            )

        )

        governance_constraints = (

            PortfolioGovernanceConstraintEngine

            .calculate(

                signals

            )

        )

        return {

            **portfolio_constraints,

            **risk_constraints,

            **diversification,

            **cash_constraints,

            **governance_constraints

        }

class ConstraintValidationEngine:

    @staticmethod
    def validate(

        constraints

    ):

        logger.info(

            "Validating Portfolio Constraints"

        )

        gross = float(

            constraints[

                "Target_Gross_Exposure"

            ]

        )

        net = float(

            constraints[

                "Target_Net_Exposure"

            ]

        )

        cash = float(

            constraints[

                "Cash_Buffer"

            ]

        )

        max_position = float(

            constraints[

                "Max_Position_Weight"

            ]

        )

        max_sector = float(

            constraints[

                "Max_Sector_Weight"

            ]

        )

        leverage = float(

            constraints[

                "Portfolio_Leverage_Limit"

            ]

        )

        if gross < net:

            raise ValueError(

                "Gross exposure cannot be less than net exposure."

            )

        if gross + cash > 100.5:

            raise ValueError(

                "Gross exposure + cash exceeds portfolio capacity."

            )

        if max_position > max_sector:

            raise ValueError(

                "Max position exceeds sector limit."

            )

        if leverage <= 0:

            raise ValueError(

                "Invalid leverage limit."

            )

        logger.info(

            "Portfolio Constraint Validation Passed"

        )

class ConstraintHealthEngine:

    @staticmethod
    def calculate(

        constraints

    ):

        logger.info(

            "Calculating Constraint Health"

        )

        score = 100.0

        gross = float(

            constraints[

                "Target_Gross_Exposure"

            ]

        )

        net = float(

            constraints[

                "Target_Net_Exposure"

            ]

        )

        cash = float(

            constraints[

                "Cash_Buffer"

            ]

        )

        leverage = float(

            constraints[

                "Portfolio_Leverage_Limit"

            ]

        )

        max_position = float(

            constraints[

                "Max_Position_Weight"

            ]

        )

        max_sector = float(

            constraints[

                "Max_Sector_Weight"

            ]

        )

        if gross < net:

            score -= 25

        if gross + cash > 100:

            score -= 20

        if leverage > 1.20:

            score -= 15

        if max_position > max_sector:

            score -= 20

        if cash < 0:

            score -= 20

        score = max(

            0,

            min(

                100,

                score

            )

        )

        if score >= 90:

            status = "EXCELLENT"

        elif score >= 75:

            status = "GOOD"

        elif score >= 60:

            status = "ACCEPTABLE"

        elif score >= 40:

            status = "WEAK"

        else:

            status = "FAILED"

        return {

            "Constraint_Health_Score":

                round(

                    score,

                    2

                ),

            "Constraint_Status":

                status

        }

class ConstraintMetadataEngine:

    ENGINE_NAME = (

        "PortfolioConstraintEngine"

    )

    ENGINE_VERSION = (

        "1.0.0"

    )

    POLICY_VERSION = (

        "InstitutionalPolicy-2026.1"

    )

    @staticmethod
    def build():

        timestamp = (

            datetime.now(

                UTC

            )

            .replace(

                microsecond=0

            )

            .isoformat()

            + "Z"

        )

        constraint_id = (

            uuid.uuid4()

            .hex[:12]

            .upper()

        )

        return {

            "Constraint_ID":

                constraint_id,

            "Generated_Timestamp":

                timestamp,

            "Constraint_Version":

                ConstraintMetadataEngine

                .ENGINE_VERSION,

            "Policy_Version":

                ConstraintMetadataEngine

                .POLICY_VERSION,

            "Source_Engine":

                ConstraintMetadataEngine

                .ENGINE_NAME

        }

class ConstraintPolicyEngine:

    POLICY = {

        "AGGRESSIVE": {

            "Target_Holdings": 35,

            "Max_Beta": 1.30,

            "Volatility_Target": 24,

            "Tracking_Error": 12,

            "Max_Position": 5.0

        },

        "OFFENSIVE": {

            "Target_Holdings": 45,

            "Max_Beta": 1.15,

            "Volatility_Target": 20,

            "Tracking_Error": 10,

            "Max_Position": 4.5

        },

        "BALANCED": {

            "Target_Holdings": 50,

            "Max_Beta": 1.00,

            "Volatility_Target": 16,

            "Tracking_Error": 8,

            "Max_Position": 4.0

        },

        "CAUTIOUS": {

            "Target_Holdings": 60,

            "Max_Beta": 0.85,

            "Volatility_Target": 12,

            "Tracking_Error": 6,

            "Max_Position": 3.5

        },

        "DEFENSIVE": {

            "Target_Holdings": 75,

            "Max_Beta": 0.70,

            "Volatility_Target": 8,

            "Tracking_Error": 4,

            "Max_Position": 3.0

        }

    }

    @classmethod
    def get(

        cls,

        regime

    ):

        return cls.POLICY.get(

            regime,

            cls.POLICY[

                "BALANCED"

            ]

        )

class PortfolioConstraintEngine:

    @staticmethod
    def calculate():

        signals = (

            ConstraintSignalEngine
            .extract(

                PortfolioConstraintRepository
                .load()

            )

        )

        constraints = (

            InstitutionalPortfolioConstraintEngine
            .build(

                signals

            )

        )

        ConstraintValidationEngine.validate(

            constraints

        )

        health = (

            ConstraintHealthEngine

            .calculate(

                constraints

            )

        )

        metadata = (

            ConstraintMetadataEngine

            .build()

        )

        return {

            **asdict(

                signals

            ),

            **constraints,

            **health,

            **metadata

        }
    
class PortfolioConstraintDashboard:

    @staticmethod
    def build(

        metrics

    ):

        dashboard = [

            {

                "Metric": key,

                "Value": value

            }

            for key, value

            in

            metrics.items()

        ]

        return pd.DataFrame(

            dashboard

        )

class PortfolioConstraintExporter:

    @staticmethod
    def export(

        dashboard

    ):

        OUTPUT_FILE.parent.mkdir(

            parents=True,

            exist_ok=True

        )

        dashboard.to_csv(

            OUTPUT_FILE,

            index=False

        )

        logger.info(

            f"Saved: {OUTPUT_FILE}"

        )

class PortfolioConstraintReporter:

    @staticmethod
    def report(

        metrics

    ):

        print()

        print(

            "=" * 100

        )

        print(

            "INSTITUTIONAL PORTFOLIO CONSTRAINTS"

        )

        print(

            "=" * 100

        )

        print(

            f"Risk Regime                 : {metrics['risk_regime']}"

        )

        print(

            f"Risk Budget Score           : {metrics['risk_budget_score']}"

        )

        print(

            f"Cash Buffer                 : {metrics['Cash_Buffer']}%"

        )

        print(

            f"Gross Exposure              : {metrics['Target_Gross_Exposure']}%"

        )

        print(

            f"Net Exposure                : {metrics['Target_Net_Exposure']}%"

        )

        print(

            f"Maximum Position            : {metrics['Max_Position_Weight']}%"

        )

        print(

            f"Target Position             : {metrics['Target_Position_Weight']}%"

        )

        print(

            f"Maximum Sector              : {metrics['Max_Sector_Weight']}%"

        )

        print(

            f"Target Holdings             : {metrics['Target_Number_of_Holdings']}"

        )

        print(

            f"Portfolio Beta Limit        : {metrics['Max_Portfolio_Beta']}"

        )

        print(

            f"Volatility Target           : {metrics['Volatility_Target']}%"

        )

        print(

            f"Tracking Error Budget       : {metrics['Tracking_Error_Budget']}%"

        )

        print(

            f"Leverage Limit              : {metrics['Portfolio_Leverage_Limit']}x"

        )

        print(

            f"Investment Committee Review : {metrics['Investment_Committee_Approval']}"

        )

        print(

            "=" * 100
        )

def run_example():

    logger.info(

        "Starting Portfolio Constraints Engine"

    )

    PortfolioConstraintValidator.validate()

    metrics = (

        PortfolioConstraintEngine

        .calculate()

    )

    dashboard = (

        PortfolioConstraintDashboard

        .build(

            metrics

        )

    )

    PortfolioConstraintExporter.export(

        dashboard

    )

    PortfolioConstraintReporter.report(

        metrics

    )


if __name__ == "__main__":

    run_example()