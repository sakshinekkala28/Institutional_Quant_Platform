"""
====================================================================
Institutional Quant Platform

Risk API Schemas

Author : Institutional Quant Platform

Purpose
-------
Risk request/response schemas.

Provides

• Value at Risk (VaR)
• Expected Shortfall
• Volatility
• Beta
• Tracking Error
• Factor Exposure
• Sector Exposure
• Stress Test
• Scenario Analysis
• Risk Report

====================================================================
"""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from api.schemas.base import APIModel
from api.schemas.base import BaseResponse
from api.schemas.base import SuccessResponse


# ==========================================================
# VALUE AT RISK
# ==========================================================


class ValueAtRisk(
    APIModel,
):
    """
    Historical VaR.
    """

    confidence_level: float = 0.95

    value: float

    horizon_days: int = 1


# ==========================================================
# EXPECTED SHORTFALL
# ==========================================================


class ExpectedShortfall(
    APIModel,
):
    """
    Expected Shortfall (CVaR).
    """

    confidence_level: float = 0.95

    value: float

    horizon_days: int = 1


# ==========================================================
# VOLATILITY
# ==========================================================


class Volatility(
    APIModel,
):
    """
    Annualized volatility.
    """

    annualized_volatility: float


# ==========================================================
# BETA
# ==========================================================


class Beta(
    APIModel,
):
    """
    Portfolio beta.
    """

    benchmark: str

    beta: float


# ==========================================================
# TRACKING ERROR
# ==========================================================


class TrackingError(
    APIModel,
):
    """
    Tracking error.
    """

    benchmark: str

    tracking_error: float


# ==========================================================
# FACTOR EXPOSURE
# ==========================================================


class FactorExposure(
    APIModel,
):
    """
    Factor exposure.
    """

    factor: str

    exposure: float


# ==========================================================
# SECTOR EXPOSURE
# ==========================================================


class SectorExposure(
    APIModel,
):
    """
    Sector exposure.
    """

    sector: str

    weight: float


# ==========================================================
# RISK LIMIT
# ==========================================================


class RiskLimit(
    APIModel,
):
    """
    Risk limit.
    """

    name: str

    current: float

    limit: float

    breached: bool = False


# ==========================================================
# STRESS TEST
# ==========================================================


class StressTestResult(
    APIModel,
):
    """
    Stress test result.
    """

    scenario: str

    portfolio_return: float

    portfolio_loss: float


# ==========================================================
# SCENARIO ANALYSIS
# ==========================================================


class ScenarioAnalysis(
    APIModel,
):
    """
    Scenario analysis.
    """

    scenario: str

    expected_return: float

    expected_volatility: float

    probability: float


# ==========================================================
# RISK SUMMARY
# ==========================================================


class RiskSummary(
    APIModel,
):
    """
    Portfolio risk summary.
    """

    portfolio_volatility: float

    portfolio_beta: float

    value_at_risk: float

    expected_shortfall: float

    tracking_error: float

    max_drawdown: float

    leverage: float

    concentration: float

    updated_at: datetime = Field(

        default_factory=datetime.utcnow,

    )


# ==========================================================
# RISK REPORT
# ==========================================================


class RiskReport(
    APIModel,
):
    """
    Risk report.
    """

    report_id: str

    generated_at: datetime

    summary: RiskSummary

    factor_exposures: list[
        FactorExposure
    ]

    sector_exposures: list[
        SectorExposure
    ]

    limits: list[
        RiskLimit
    ]

    stress_tests: list[
        StressTestResult
    ]


# ==========================================================
# REQUEST
# ==========================================================


class RiskAnalysisRequest(
    APIModel,
):
    """
    Risk analysis request.
    """

    benchmark: str = "NIFTY 500"

    confidence_level: float = 0.95

    horizon_days: int = 1

    include_stress_test: bool = True

    include_factor_risk: bool = True


# ==========================================================
# RESPONSE
# ==========================================================


class RiskAnalysisResponse(
    BaseResponse,
):
    """
    Risk analysis response.
    """

    analysis_id: str

    status: str


class RiskSummaryResponse(
    SuccessResponse,
):
    """
    Risk summary response.
    """

    data: RiskSummary


class RiskReportResponse(
    SuccessResponse,
):
    """
    Risk report response.
    """

    data: RiskReport


class FactorExposureResponse(
    SuccessResponse,
):
    """
    Factor exposure response.
    """

    data: list[
        FactorExposure
    ]


class SectorExposureResponse(
    SuccessResponse,
):
    """
    Sector exposure response.
    """

    data: list[
        SectorExposure
    ]


class StressTestResponse(
    SuccessResponse,
):
    """
    Stress test response.
    """

    data: list[
        StressTestResult
    ]


class ScenarioAnalysisResponse(
    SuccessResponse,
):
    """
    Scenario analysis response.
    """

    data: list[
        ScenarioAnalysis
    ]


# ==========================================================
# EXPORTS
# ==========================================================


__all__ = [

    "ValueAtRisk",

    "ExpectedShortfall",

    "Volatility",

    "Beta",

    "TrackingError",

    "FactorExposure",

    "SectorExposure",

    "RiskLimit",

    "StressTestResult",

    "ScenarioAnalysis",

    "RiskSummary",

    "RiskReport",

    "RiskAnalysisRequest",

    "RiskAnalysisResponse",

    "RiskSummaryResponse",

    "RiskReportResponse",

    "FactorExposureResponse",

    "SectorExposureResponse",

    "StressTestResponse",

    "ScenarioAnalysisResponse",

]