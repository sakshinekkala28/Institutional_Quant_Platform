"""
====================================================================
Institutional Quant Platform

Signals API Schemas

Author : Institutional Quant Platform

Purpose
-------
Signal request/response schemas.

Provides

• Alpha Signal
• Signal Summary
• Signal Ranking
• Confidence Score
• Factor Scores
• Signal History
• Universe
• Signal Generation

====================================================================
"""

from __future__ import annotations

from datetime import datetime

from pydantic import Field

from api.schemas.base import APIModel
from api.schemas.base import BaseResponse
from api.schemas.base import SuccessResponse


# ==========================================================
# SIGNAL
# ==========================================================


class Signal(
    APIModel,
):
    """
    Alpha signal.
    """

    symbol: str

    signal: str

    score: float

    confidence: float

    rank: int

    generated_at: datetime = Field(

        default_factory=datetime.utcnow,

    )


# ==========================================================
# FACTOR SCORE
# ==========================================================


class FactorScore(
    APIModel,
):
    """
    Factor score.
    """

    factor: str

    score: float


# ==========================================================
# SIGNAL DETAILS
# ==========================================================


class SignalDetails(
    Signal,
):
    """
    Complete signal.
    """

    sector: str | None = None

    industry: str | None = None

    market_cap: float | None = None

    factors: list[
        FactorScore
    ] = Field(

        default_factory=list,

    )


# ==========================================================
# SIGNAL SUMMARY
# ==========================================================


class SignalSummary(
    APIModel,
):
    """
    Signal summary.
    """

    total_signals: int

    buy: int

    hold: int

    sell: int

    average_confidence: float

    generated_at: datetime = Field(

        default_factory=datetime.utcnow,

    )


# ==========================================================
# SIGNAL HISTORY
# ==========================================================


class SignalHistory(
    APIModel,
):
    """
    Historical signal.
    """

    date: datetime

    signal: str

    score: float

    confidence: float


# ==========================================================
# SIGNAL GENERATION REQUEST
# ==========================================================


class SignalGenerationRequest(
    APIModel,
):
    """
    Signal generation request.
    """

    universe: str = "NSE"

    rebalance_date: datetime

    minimum_score: float = 0.0

    maximum_positions: int = 50


# ==========================================================
# SIGNAL GENERATION RESPONSE
# ==========================================================


class SignalGenerationResponse(
    BaseResponse,
):
    """
    Generation response.
    """

    job_id: str

    status: str


# ==========================================================
# UNIVERSE
# ==========================================================


class UniverseSummary(
    APIModel,
):
    """
    Universe summary.
    """

    name: str

    securities: int

    updated_at: datetime


# ==========================================================
# RESPONSES
# ==========================================================


class SignalResponse(
    SuccessResponse,
):
    """
    Signal response.
    """

    data: SignalDetails


class SignalListResponse(
    SuccessResponse,
):
    """
    Signal list.
    """

    data: list[Signal]


class SignalSummaryResponse(
    SuccessResponse,
):
    """
    Summary response.
    """

    data: SignalSummary


class SignalHistoryResponse(
    SuccessResponse,
):
    """
    History response.
    """

    data: list[
        SignalHistory
    ]


class UniverseResponse(
    SuccessResponse,
):
    """
    Universe response.
    """

    data: UniverseSummary


# ==========================================================
# EXPORTS
# ==========================================================


__all__ = [

    "Signal",

    "FactorScore",

    "SignalDetails",

    "SignalSummary",

    "SignalHistory",

    "SignalGenerationRequest",

    "SignalGenerationResponse",

    "UniverseSummary",

    "SignalResponse",

    "SignalListResponse",

    "SignalSummaryResponse",

    "SignalHistoryResponse",

    "UniverseResponse",

]