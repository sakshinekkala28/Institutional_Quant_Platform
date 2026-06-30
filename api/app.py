"""
====================================================================
Institutional Quant Platform

API Application

Author : Institutional Quant Platform

Purpose
-------
Main FastAPI application.

Provides

• REST API
• Health Check
• Metrics
• Version Info
• Router Registration

====================================================================
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from api.routers import (
    backtest,
    execution,
    monitoring,
    optimization,
    portfolio,
    risk,
    signals,
)

APP_NAME = "Institutional Quant Platform"

VERSION = "1.0.0"


# ==========================================================
# LIFECYCLE
# ==========================================================


@asynccontextmanager
async def lifespan(

    app: FastAPI,

):

    print(

        "\nStarting Institutional Quant Platform..."

    )

    yield

    print(

        "\nStopping Institutional Quant Platform..."

    )


# ==========================================================
# APPLICATION
# ==========================================================


app = FastAPI(

    title=APP_NAME,

    version=VERSION,

    lifespan=lifespan,

    docs_url="/docs",

    redoc_url="/redoc",

)

# ==========================================================
# ROUTERS
# ==========================================================

app.include_router(

    portfolio.router,

    prefix="/portfolio",

    tags=["Portfolio"],

)

app.include_router(

    signals.router,

    prefix="/signals",

    tags=["Signals"],

)

app.include_router(

    execution.router,

    prefix="/execution",

    tags=["Execution"],

)

app.include_router(

    optimization.router,

    prefix="/optimization",

    tags=["Optimization"],

)

app.include_router(

    risk.router,

    prefix="/risk",

    tags=["Risk"],

)

app.include_router(

    backtest.router,

    prefix="/backtest",

    tags=["Backtesting"],

)

app.include_router(

    monitoring.router,

    prefix="/monitoring",

    tags=["Monitoring"],

)

# ==========================================================
# ROOT
# ==========================================================


@app.get(

    "/",

)

async def root():

    return {

        "Application":

            APP_NAME,

        "Version":

            VERSION,

        "Status":

            "Running",

    }


# ==========================================================
# HEALTH
# ==========================================================


@app.get(

    "/health",

)

async def health():

    return {

        "Status":

            "Healthy",

    }


# ==========================================================
# VERSION
# ==========================================================


@app.get(

    "/version",

)

async def version():

    return {

        "Version":

            VERSION,

    }


# ==========================================================
# METRICS
# ==========================================================


@app.get(

    "/metrics",

)

async def metrics():

    return JSONResponse(

        {

            "Application":

                APP_NAME,

            "Version":

                VERSION,

            "Status":

                "Healthy",

        }

    )