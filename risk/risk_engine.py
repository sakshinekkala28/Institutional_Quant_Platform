# ==========================================================
# RISK ENGINE
# Institutional Risk Platform
# ==========================================================

from __future__ import annotations

import numpy as np
import pandas as pd


# ==========================================================
# COVARIANCE ENGINE
# ==========================================================

class CovarianceEngine:

    @staticmethod
    def repair_psd(
        covariance_matrix
    ):

        eigvals, eigvecs = np.linalg.eigh(
            covariance_matrix
        )

        eigvals = np.maximum(
            eigvals,
            1e-5
        )

        repaired = (

            eigvecs

            @

            np.diag(eigvals)

            @

            eigvecs.T

        )

        return repaired

    @staticmethod
    def shrink_covariance(
        covariance_matrix,
        shrinkage=0.10
    ):

        diag = np.diag(
            np.diag(
                covariance_matrix
            )
        )

        return (

            (1 - shrinkage)

            *

            covariance_matrix

            +

            shrinkage

            *

            diag

        )


# ==========================================================
# VOLATILITY ENGINE
# ==========================================================

class VolatilityEngine:

    @staticmethod
    def portfolio_volatility(
        weights,
        covariance_matrix
    ):

        variance = (

            weights.T

            @

            covariance_matrix

            @

            weights

        )

        return np.sqrt(
            variance
        )
    
# ==========================================================
# BETA ENGINE
# ==========================================================

class BetaEngine:

    @staticmethod
    def portfolio_beta(
        portfolio
    ):

        return (

            portfolio[
                "Target_Weight"
            ]

            *

            portfolio[
                "Beta"
            ]

        ).sum()


# ==========================================================
# TRACKING ERROR ENGINE
# ==========================================================

class TrackingErrorEngine:

    @staticmethod
    def calculate(
        active_weights,
        covariance_matrix
    ):

        tracking_error = np.sqrt(

            active_weights.T

            @

            covariance_matrix

            @

            active_weights

        )

        return tracking_error
    
# ==========================================================
# RISK CONTRIBUTION ENGINE
# ==========================================================

class RiskContributionEngine:

    @staticmethod
    def calculate(
        weights,
        covariance_matrix
    ):

        portfolio_vol = np.sqrt(

            weights.T

            @

            covariance_matrix

            @

            weights

        )

        marginal_risk = (

            covariance_matrix

            @

            weights

        ) / portfolio_vol

        component_risk = (

            weights

            *

            marginal_risk

        )

        risk_pct = (

            component_risk

            /

            component_risk.sum()

        )

        return risk_pct


# ==========================================================
# FACTOR EXPOSURE ENGINE
# ==========================================================

class FactorExposureEngine:

    @staticmethod
    def calculate(
        portfolio
    ):

        factors = [

            "Signal_Factor",

            "Momentum_Factor",

            "Quality_Factor",

            "Value_Factor",

            "Growth_Factor",

            "Liquidity_Factor",

            "LowVol_Factor"

        ]

        exposures = []

        for factor in factors:

            if factor not in portfolio.columns:
                continue

            exposure = (

                portfolio[
                    factor
                ]

                *

                portfolio[
                    "Target_Weight"
                ]

            ).sum()

            exposures.append({

                "Factor": factor,

                "Exposure": exposure

            })

        return pd.DataFrame(
            exposures
        )
    
# ==========================================================
# TAIL RISK ENGINE
# ==========================================================

class TailRiskEngine:

    @staticmethod
    def calculate_var(
        returns,
        confidence=95
    ):

        return np.percentile(
            returns,
            100 - confidence
        )

    @staticmethod
    def calculate_cvar(
        returns,
        confidence=95
    ):

        var = (

            TailRiskEngine

            .calculate_var(
                returns,
                confidence
            )

        )

        return returns[
            returns <= var
        ].mean()


# ==========================================================
# GOVERNANCE ENGINE
# ==========================================================

class GovernanceEngine:

    @staticmethod
    def calculate_hhi(
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

            GovernanceEngine

            .calculate_hhi(
                weights
            )

        )

        return 1 / max(
            hhi,
            1e-9
        )


# ==========================================================
# MASTER RISK ENGINE
# ==========================================================

class RiskEngine:

    def evaluate(
        self,
        portfolio
    ):

        report = {}

        report["Portfolio_Beta"] = (

            BetaEngine

            .portfolio_beta(
                portfolio
            )

        )

        report["HHI"] = (

            GovernanceEngine

            .calculate_hhi(

                portfolio[
                    "Target_Weight"
                ]

            )

        )

        report["Effective_Holdings"] = (

            GovernanceEngine

            .effective_holdings(

                portfolio[
                    "Target_Weight"
                ]

            )

        )

        report["Factor_Exposure"] = (

            FactorExposureEngine

            .calculate(
                portfolio
            )

        )

        print(
            "\n✓ Risk Evaluation Complete"
        )

        print(
            f"Portfolio Beta: "
            f"{report['Portfolio_Beta']:.4f}"
        )

        print(
            f"HHI: "
            f"{report['HHI']:.4f}"
        )

        print(
            f"Effective Holdings: "
            f"{report['Effective_Holdings']:.2f}"
        )

        return report