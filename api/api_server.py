# ==========================================================
# API SERVER
# Institutional Quant Platform API
# ==========================================================

from __future__ import annotations

from datetime import datetime

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(

    title="Institutional Quant Platform",

    version="1.0.0",

    docs_url="/docs",

    redoc_url="/redoc"

)


# ==========================================================
# HEALTH CHECK
# ==========================================================

@app.get("/health")

def health():

    return {

        "status": "healthy",

        "timestamp": datetime.utcnow()

    }


# ==========================================================
# ROOT
# ==========================================================

@app.get("/")

def root():

    return {

        "platform":

        "Institutional Quant Platform",

        "version":

        "1.0.0"

    }
# ==========================================================
# PORTFOLIO ENDPOINT
# ==========================================================

@app.get("/portfolio")

def portfolio():

    return {

        "message":

        "Portfolio endpoint"

    }


# ==========================================================
# RISK ENDPOINT
# ==========================================================

@app.get("/risk")

def risk():

    return {

        "message":

        "Risk endpoint"

    }


# ==========================================================
# GOVERNANCE ENDPOINT
# ==========================================================

@app.get("/governance")

def governance():

    return {

        "message":

        "Governance endpoint"

    }

# ==========================================================
# PERFORMANCE
# ==========================================================

@app.get("/performance")

def performance():

    return {

        "message":

        "Performance endpoint"

    }


# ==========================================================
# TRADE LIST
# ==========================================================

@app.get("/trades")

def trades():

    return {

        "message":

        "Trade endpoint"

    }


# ==========================================================
# SIGNALS
# ==========================================================

@app.get("/signals")

def signals():

    return {

        "message":

        "Signal endpoint"

    }

# ==========================================================
# DATABASE ROUTES
# ==========================================================

from ingestion.database_manager import (
    DatabaseManager
)

db = DatabaseManager()


@app.get("/portfolio/live")

def live_portfolio():

    try:

        df = db.load(
            "target_portfolio"
        )

        return JSONResponse(

            content=df.to_dict(
                orient="records"
            )

        )

    except Exception as e:

        return {

            "error":

            str(e)

        }


@app.get("/risk/latest")

def latest_risk():

    try:

        df = db.load(
            "risk_report"
        )

        return JSONResponse(

            content=df.to_dict(
                orient="records"
            )

        )

    except Exception as e:

        return {

            "error":

            str(e)

        }