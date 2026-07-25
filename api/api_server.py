# ==========================================================
# API SERVER
# Institutional Quant Platform API
# ==========================================================

from __future__ import annotations

from datetime import datetime
import numpy as np
import pandas as pd
from datetime import datetime, UTC

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from ingestion.database_manager import (
    DatabaseManager
)

db = DatabaseManager()

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

        "3.0.0"

    }

# ==========================================================
# PORTFOLIO ENDPOINT
# ==========================================================

def dataframe_to_records(
    df: pd.DataFrame,
):

    return (
        df
        .replace(
            [np.inf, -np.inf],
            np.nan,
        )
        .astype(object)
        .where(
            pd.notna(df),
            None,
        )
        .to_dict(
            orient="records"
        )
    )

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

    try:

        df = db.load(
            "trade_list"
        )

        return JSONResponse(
            content=dataframe_to_records(df)
        )

    except Exception as e:

        return {
            "error": str(e)
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

@app.get("/portfolio/live")

def live_portfolio():

    try:

        df = db.load(
            "target_portfolio"
        )

        return JSONResponse(
            content=dataframe_to_records(df)
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
            "rebalance_dashboard"
        )

        return JSONResponse(
            content=dataframe_to_records(df)
        )

    except Exception as e:

        return {
            "error": str(e)
        }
    

if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        "api.api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )