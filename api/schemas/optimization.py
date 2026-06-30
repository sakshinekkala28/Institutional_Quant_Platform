"""
====================================================================
Institutional Quant Platform

Optimization API Schemas

Author : Institutional Quant Platform

Purpose
-------
Portfolio optimization request/response schemas.

Provides

• Optimization Request
• Constraints
• Objective Function
• Efficient Frontier
• Optimized Portfolio
• Risk Contribution
• Optimization Report

====================================================================
"""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import Field

from api.schemas.base import APIModel
from api.schemas.base import BaseResponse
from api.schemas.base import SuccessResponse


# ==========================================================
# OPTIMIZATION CONSTRAINT
# ==========================================================


class OptimizationConstraint(
    APIModel,
):
    """
    Portfolio optimization constraint.
    """

    max_weight: float = 0.10

    min_weight: float = 0.00

    max_sector_weight: float = 0.30

    max_turnover: float = 0.25

    max_leverage: float = 1.00

    cash_weight: float = 0.00


# ==========================================================
# OBJECTIVE FUNCTION
# ==========================================================


class ObjectiveFunction(
    APIModel,
):
    """
    Optimization objective.
    """

    objective: Literal[

        "MaxSharpe",

        "MinVariance",

        "RiskParity",

        "MaxDiversification",

        "MinCVaR",

    ] = "MaxSharpe"


# ==========================================================
# OPTIMIZATION REQUEST
# ==========================================================


class OptimizationRequest(
    APIModel,
):
    """
    Optimization request.
    """

    rebalance_date: datetime

    benchmark: str = "NIFTY 500"

    risk_free_rate: float = 0.06

    constraints: OptimizationConstraint = Field(

        default_factory=OptimizationConstraint,

    )

    objective: ObjectiveFunction = Field(

        default_factory=ObjectiveFunction,

    )


# ==========================================================
# OPTIMIZED POSITION
# ==========================================================


class OptimizedPosition(
    APIModel,
):
    """
    Optimized portfolio position.
    """

    symbol: str

    weight: float

    expected_return: float

    expected_risk: float


# ==========================================================
# RISK CONTRIBUTION
# ==========================================================


class RiskContribution(
    APIModel,
):
    """
    Risk contribution.
    """

    symbol: str

    contribution: float


# ==========================================================
# EFFICIENT FRONTIER
# ==========================================================


class EfficientFrontierPoint(
    APIModel,
):
    """
    Efficient frontier point.
    """

    expected_return: float

    volatility: float

    sharpe_ratio: float


# ==========================================================
# OPTIMIZATION RESULT
# ==========================================================


class OptimizationResult(
    APIModel,
):
    """
    Optimization result.
    """

    optimization_id: str

    generated_at: datetime

    expected_return: float

    expected_volatility: float

    sharpe_ratio: float

    turnover: float

    positions: list[
        OptimizedPosition
    ]


# ==========================================================
# OPTIMIZATION REPORT
# ==========================================================


class OptimizationReport(
    APIModel,
):
    """
    Optimization report.
    """

    report_id: str

    optimization: OptimizationResult

    risk_contribution: list[
        RiskContribution
    ]

    efficient_frontier: list[
        EfficientFrontierPoint
    ]


# ==========================================================
# RESPONSE
# ==========================================================


class OptimizationResponse(
    BaseResponse,
):
    """
    Optimization response.
    """

    optimization_id: str

    status: str


class OptimizationResultResponse(
    SuccessResponse,
):
    """
    Optimization result response.
    """

    data: OptimizationResult


class OptimizationReportResponse(
    SuccessResponse,
):
    """
    Optimization report response.
    """

    data: OptimizationReport


class EfficientFrontierResponse(
    SuccessResponse,
):
    """
    Efficient frontier response.
    """

    data: list[
        EfficientFrontierPoint
    ]


class RiskContributionResponse(
    SuccessResponse,
):
    """
    Risk contribution response.
    """

    data: list[
        RiskContribution
    ]


# ==========================================================
# EXPORTS
# ==========================================================


__all__ = [

    "OptimizationConstraint",

    "ObjectiveFunction",

    "OptimizationRequest",

    "OptimizedPosition",

    "RiskContribution",

    "EfficientFrontierPoint",

    "OptimizationResult",

    "OptimizationReport",

    "OptimizationResponse",

    "OptimizationResultResponse",

    "OptimizationReportResponse",

    "EfficientFrontierResponse",

    "RiskContributionResponse",

]