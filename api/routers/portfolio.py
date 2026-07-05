"""
====================================================================
Institutional Quant Platform

Portfolio Router

Author : Institutional Quant Platform

Purpose
-------
Portfolio REST API.

Provides

• Portfolio Summary
• Holdings
• Weights
• Sector Exposure
• Risk Exposure
• Performance
• Rebalance
• Turnover

====================================================================
"""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter
from fastapi import HTTPException

from core.services.portfolio_service import PortfolioService

router = APIRouter()

# ==========================================================
# CONFIGURATION
# ==========================================================

PORTFOLIO_SOURCE = Path(
    "data/portfolios/live_portfolio.csv"
)

portfolio_service = PortfolioService(
    PORTFOLIO_SOURCE
)

# ==========================================================
# HEALTH
# ==========================================================

@router.get(
    "/health",
    summary="Portfolio Health",
)
async def health():

    return {

        "module": "Portfolio",

        "status": "Healthy",

        "holdings": portfolio_service.holdings,

        "fully_invested": portfolio_service.portfolio.fully_invested,

    }


# ==========================================================
# SUMMARY
# ==========================================================

@router.get(
    "/summary",
    summary="Portfolio Summary",
)
async def summary():

    return portfolio_service.summary()


# ==========================================================
# LIVE PORTFOLIO
# ==========================================================

@router.get(
    "/live",
    summary="Live Portfolio",
)
async def live():

    dataframe = portfolio_service.dataframe()

    return dataframe.to_dict(

        orient="records"

    )


# ==========================================================
# HOLDINGS
# ==========================================================

@router.get(
    "/holdings",
    summary="Current Holdings",
)
async def holdings():

    return {

        "holdings":

            portfolio_service.dataframe().to_dict(

                orient="records"

            )

    }


# ==========================================================
# POSITION
# ==========================================================

@router.get(
    "/position/{symbol}",
    summary="Single Position",
)
async def position(

    symbol: str,

):

    position = portfolio_service.portfolio.get(

        symbol.upper()

    )

    if position is None:

        raise HTTPException(

            status_code=404,

            detail=f"{symbol} not found."

        )

    return position.to_dict()


# ==========================================================
# WEIGHTS
# ==========================================================

@router.get(
    "/weights",
)
async def weights():

    return {

        "weights":

            [

                {

                    "Symbol": p.symbol,

                    "Weight": p.weight,

                }

                for p

                in portfolio_service.positions()

            ]

    }


# ==========================================================
# SECTOR EXPOSURE
# ==========================================================

@router.get(
    "/sector-exposure",
)
async def sector_exposure():

    return portfolio_service.sector_weights()


# ==========================================================
# FACTOR EXPOSURE
# ==========================================================

@router.get(
    "/factor-exposure",
)
async def factor_exposure():

    return {

        "message":

            "Factor exposure engine not connected."

    }


# ==========================================================
# PERFORMANCE
# ==========================================================

@router.get(
    "/performance",
)
async def performance():

    return {

        "message":

            "Performance engine not connected."

    }


# ==========================================================
# ATTRIBUTION
# ==========================================================

@router.get(
    "/attribution",
)
async def attribution():

    return {

        "message":

            "Attribution engine not connected."

    }


# ==========================================================
# REBALANCE
# ==========================================================

@router.post(
    "/rebalance",
)
async def rebalance():

    return {

        "status":

            "Rebalance request accepted."

    }


# ==========================================================
# OPTIMIZED PORTFOLIO
# ==========================================================

@router.get(
    "/optimized",
)
async def optimized():

    dataframe = portfolio_service.dataframe()

    return dataframe.to_dict(

        orient="records"

    )


# ==========================================================
# EXPORT
# ==========================================================

@router.get(
    "/export",
)
async def export():

    return {

        "rows":

            portfolio_service.holdings,

        "status":

            "Ready"

    }


# ==========================================================
# DELETE POSITION
# ==========================================================

@router.delete(
    "/position/{symbol}",
)
async def delete_position(

    symbol: str,

):

    raise HTTPException(

        status_code=501,

        detail=(

            "Delete operation "

            "not implemented."

        ),

    )