"""
====================================================================
Institutional Quant Platform

Risk Dependencies

Author : Institutional Quant Platform

Purpose
-------
FastAPI dependency providers for risk management services.

Provides

• Risk Engine
• Covariance Engine
• Volatility Engine
• Beta Engine
• Tracking Error Engine
• Risk Contribution Engine
• Factor Exposure Engine
• Tail Risk Engine
• Governance Engine
• Position Limit Engine
• Sector Limit Engine
• Concentration Engine
• Turnover Governance
• Audit Engine

Used By

• Risk Router
• Portfolio Router
• Optimization Router
• Execution Router
• Monitoring Router

====================================================================
"""

from __future__ import annotations

from functools import lru_cache

from risk.risk_engine import (
    RiskEngine,
    CovarianceEngine,
    VolatilityEngine,
    BetaEngine,
    TrackingErrorEngine,
    RiskContributionEngine,
    FactorExposureEngine,
    TailRiskEngine,
)

from risk.governance_engine import (
    GovernanceEngine,
    PositionLimitEngine,
    SectorLimitEngine,
    ConcentrationEngine,
    TurnoverGovernance,
    AuditEngine,
)


# ==========================================================
# RISK ENGINE
# ==========================================================


@lru_cache
def get_risk_engine() -> RiskEngine:
    """
    Primary portfolio risk engine.
    """
    return RiskEngine()


# ==========================================================
# COVARIANCE
# ==========================================================


@lru_cache
def get_covariance_engine() -> CovarianceEngine:
    """
    Covariance estimation engine.
    """
    return CovarianceEngine()


# ==========================================================
# VOLATILITY
# ==========================================================


@lru_cache
def get_volatility_engine() -> VolatilityEngine:
    """
    Volatility engine.
    """
    return VolatilityEngine()


# ==========================================================
# BETA
# ==========================================================


@lru_cache
def get_beta_engine() -> BetaEngine:
    """
    Beta calculation engine.
    """
    return BetaEngine()


# ==========================================================
# TRACKING ERROR
# ==========================================================


@lru_cache
def get_tracking_error_engine() -> TrackingErrorEngine:
    """
    Tracking error engine.
    """
    return TrackingErrorEngine()


# ==========================================================
# RISK CONTRIBUTION
# ==========================================================


@lru_cache
def get_risk_contribution_engine() -> RiskContributionEngine:
    """
    Marginal risk contribution engine.
    """
    return RiskContributionEngine()


# ==========================================================
# FACTOR EXPOSURE
# ==========================================================


@lru_cache
def get_factor_exposure_engine() -> FactorExposureEngine:
    """
    Factor exposure engine.
    """
    return FactorExposureEngine()


# ==========================================================
# TAIL RISK
# ==========================================================


@lru_cache
def get_tail_risk_engine() -> TailRiskEngine:
    """
    Tail risk engine.
    """
    return TailRiskEngine()


# ==========================================================
# GOVERNANCE
# ==========================================================


@lru_cache
def get_governance_engine() -> GovernanceEngine:
    """
    Governance engine.
    """
    return GovernanceEngine()


# ==========================================================
# POSITION LIMITS
# ==========================================================


@lru_cache
def get_position_limit_engine() -> PositionLimitEngine:
    """
    Position limit engine.
    """
    return PositionLimitEngine()


# ==========================================================
# SECTOR LIMITS
# ==========================================================


@lru_cache
def get_sector_limit_engine() -> SectorLimitEngine:
    """
    Sector limit engine.
    """
    return SectorLimitEngine()


# ==========================================================
# CONCENTRATION
# ==========================================================


@lru_cache
def get_concentration_engine() -> ConcentrationEngine:
    """
    Concentration engine.
    """
    return ConcentrationEngine()


# ==========================================================
# TURNOVER GOVERNANCE
# ==========================================================


@lru_cache
def get_turnover_governance() -> TurnoverGovernance:
    """
    Turnover governance engine.
    """
    return TurnoverGovernance()


# ==========================================================
# AUDIT
# ==========================================================


@lru_cache
def get_audit_engine() -> AuditEngine:
    """
    Risk audit engine.
    """
    return AuditEngine()


# ==========================================================
# HEALTH
# ==========================================================


def risk_health() -> dict:
    """
    Dependency health.
    """

    return {

        "engine": "RiskEngine",

        "status": "healthy",

        "singleton": True,

    }


# ==========================================================
# SUMMARY
# ==========================================================


def risk_summary() -> dict:
    """
    Registered services.
    """

    return {

        "services": [

            "RiskEngine",

            "CovarianceEngine",

            "VolatilityEngine",

            "BetaEngine",

            "TrackingErrorEngine",

            "RiskContributionEngine",

            "FactorExposureEngine",

            "TailRiskEngine",

            "GovernanceEngine",

            "PositionLimitEngine",

            "SectorLimitEngine",

            "ConcentrationEngine",

            "TurnoverGovernance",

            "AuditEngine",

        ],

        "count": 14,

    }


# ==========================================================
# EXPORTS
# ==========================================================


__all__ = [

    "get_risk_engine",

    "get_covariance_engine",

    "get_volatility_engine",

    "get_beta_engine",

    "get_tracking_error_engine",

    "get_risk_contribution_engine",

    "get_factor_exposure_engine",

    "get_tail_risk_engine",

    "get_governance_engine",

    "get_position_limit_engine",

    "get_sector_limit_engine",

    "get_concentration_engine",

    "get_turnover_governance",

    "get_audit_engine",

    "risk_health",

    "risk_summary",

]