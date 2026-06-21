# ==========================================================
# GOVERNANCE ENGINE
# Institutional Compliance & Governance Layer
# ==========================================================

from __future__ import annotations

from dataclasses import dataclass
import pandas as pd
import numpy as np


# ==========================================================
# GOVERNANCE POLICY
# ==========================================================

@dataclass
class GovernancePolicy:

    MAX_POSITION_WEIGHT: float = 0.05

    MAX_SECTOR_WEIGHT: float = 0.30

    MAX_PORTFOLIO_BETA: float = 1.20

    MIN_PORTFOLIO_BETA: float = 0.80

    MAX_HHI: float = 0.05

    MIN_EFFECTIVE_HOLDINGS: int = 20

    MAX_TURNOVER: float = 0.30


# ==========================================================
# POSITION LIMIT ENGINE
# ==========================================================

class PositionLimitEngine:

    @staticmethod
    def validate(
        portfolio,
        policy
    ):

        max_position = (

            portfolio[
                "Target_Weight"
            ].max()

        )

        return {

            "Rule":
            "Position Limit",

            "Limit":
            policy.MAX_POSITION_WEIGHT,

            "Actual":
            max_position,

            "Pass":
            max_position
            <=
            policy.MAX_POSITION_WEIGHT

        }
    
# ==========================================================
# SECTOR LIMIT ENGINE
# ==========================================================

class SectorLimitEngine:

    @staticmethod
    def validate(
        portfolio,
        policy
    ):

        sector_weight = (

            portfolio

            .groupby("Sector")

            ["Target_Weight"]

            .sum()

            .max()

        )

        return {

            "Rule":
            "Sector Limit",

            "Limit":
            policy.MAX_SECTOR_WEIGHT,

            "Actual":
            sector_weight,

            "Pass":
            sector_weight
            <=
            policy.MAX_SECTOR_WEIGHT

        }


# ==========================================================
# BETA LIMIT ENGINE
# ==========================================================

class BetaLimitEngine:

    @staticmethod
    def validate(
        portfolio,
        policy
    ):

        beta = (

            portfolio[
                "Target_Weight"
            ]

            *

            portfolio[
                "Beta"
            ]

        ).sum()

        return {

            "Rule":
            "Portfolio Beta",

            "Lower":
            policy.MIN_PORTFOLIO_BETA,

            "Upper":
            policy.MAX_PORTFOLIO_BETA,

            "Actual":
            beta,

            "Pass":
            (
                policy.MIN_PORTFOLIO_BETA
                <= beta
                <= policy.MAX_PORTFOLIO_BETA
            )

        }
    
# ==========================================================
# CONCENTRATION ENGINE
# ==========================================================

class ConcentrationEngine:

    @staticmethod
    def hhi(
        weights
    ):

        return (

            weights ** 2

        ).sum()

    @staticmethod
    def effective_holdings(
        weights
    ):

        hhi = (

            ConcentrationEngine
            .hhi(weights)
        )

        return 1 / max(
            hhi,
            1e-9
        )

    @staticmethod
    def validate(
        portfolio,
        policy
    ):

        hhi = (

            ConcentrationEngine
            .hhi(
                portfolio[
                    "Target_Weight"
                ]
            )
        )

        effective = (

            ConcentrationEngine
            .effective_holdings(
                portfolio[
                    "Target_Weight"
                ]
            )
        )

        return {

            "Rule":
            "Concentration",

            "HHI":
            hhi,

            "Effective_Holdings":
            effective,

            "Pass":
            (
                hhi
                <=
                policy.MAX_HHI
            )
            and
            (
                effective
                >=
                policy.MIN_EFFECTIVE_HOLDINGS
            )

        }


# ==========================================================
# TURNOVER GOVERNANCE
# ==========================================================

class TurnoverGovernance:

    @staticmethod
    def validate(
        turnover,
        policy
    ):

        return {

            "Rule":
            "Turnover",

            "Limit":
            policy.MAX_TURNOVER,

            "Actual":
            turnover,

            "Pass":
            turnover
            <=
            policy.MAX_TURNOVER

        }
    
# ==========================================================
# AUDIT ENGINE
# ==========================================================

class AuditEngine:

    @staticmethod
    def build_report(
        checks
    ):

        return pd.DataFrame(
            checks
        )


# ==========================================================
# GOVERNANCE ENGINE
# ==========================================================

class GovernanceEngine:

    def __init__(self):

        self.policy = (
            GovernancePolicy()
        )

    def evaluate(
        self,
        portfolio,
        turnover=0.0
    ):

        checks = []

        checks.append(

            PositionLimitEngine
            .validate(
                portfolio,
                self.policy
            )

        )

        checks.append(

            SectorLimitEngine
            .validate(
                portfolio,
                self.policy
            )

        )

        checks.append(

            BetaLimitEngine
            .validate(
                portfolio,
                self.policy
            )

        )

        checks.append(

            ConcentrationEngine
            .validate(
                portfolio,
                self.policy
            )

        )

        checks.append(

            TurnoverGovernance
            .validate(
                turnover,
                self.policy
            )

        )

        report = (

            AuditEngine
            .build_report(
                checks
            )
        )

        overall_pass = (

            report["Pass"]

            .fillna(False)

            .all()

        )

        print(
            "\n✓ Governance Review Complete"
        )

        print(
            f"Overall Pass: "
            f"{overall_pass}"
        )

        return {

            "Governance_Report":
            report,

            "Approved":
            overall_pass

        }