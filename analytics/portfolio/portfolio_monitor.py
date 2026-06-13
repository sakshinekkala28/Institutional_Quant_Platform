"""
=========================================================
PORTFOLIO MONITOR ENGINE
=========================================================

Purpose:
Institutional Portfolio Monitoring & Health Assessment

Outputs:
portfolio_health.csv
portfolio_drift.csv
rebalance_recommendations.csv
portfolio_dashboard.csv

=========================================================
"""

from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd

# =========================================================
# CONFIG
# =========================================================

ENGINE_VERSION = "1.0.0"

MAX_POSITION_WEIGHT = 0.05

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

PORTFOLIO_FILE = (
    ROOT
    / "data"
    / "portfolios"
    / "live_portfolio.csv"
)

SIGNAL_FILE = (
    ROOT
    / "data"
    / "signals"
    / "signal_master.csv"
)

REGIME_FILE = (
    ROOT
    / "data"
    / "regime"
    / "market_regime.csv"
)

RISK_FILE = (
    ROOT
    / "data"
    / "risk"
    / "risk_budget_dashboard.csv"
)

EXPOSURE_FILE = (
    ROOT
    / "data"
    / "risk"
    / "exposure_dashboard.csv"
)

CAPACITY_FILE = (
    ROOT
    / "data"
    / "execution"
    / "capacity_summary.csv"
)

TCOST_FILE = (
    ROOT
    / "data"
    / "execution"
    / "transaction_cost_summary.csv"
)

OUTPUT_DIR = (
    ROOT
    / "data"
    / "portfolios"
)

REPORT_FILE = (
    ROOT
    / "data"
    / "logs"
    / "portfolio_monitor_report.csv"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

# =========================================================
# SAFE LOAD
# =========================================================

def safe_load(path):

    if path.exists():

        try:
            return pd.read_csv(path)

        except Exception:
            return pd.DataFrame()

    return pd.DataFrame()

# =========================================================
# LOAD
# =========================================================

print(
    "\n📥 Loading Portfolio Inputs..."
)

portfolio = safe_load(
    PORTFOLIO_FILE
)

signals = safe_load(
    SIGNAL_FILE
)

regime = safe_load(
    REGIME_FILE
)

risk = safe_load(
    RISK_FILE
)

exposure = safe_load(
    EXPOSURE_FILE
)

capacity = safe_load(
    CAPACITY_FILE
)

tcost = safe_load(
    TCOST_FILE
)

if portfolio.empty:

    raise ValueError(
        "Portfolio empty"
    )

# =========================================================
# CURRENT REGIME
# =========================================================

current_regime = "UNKNOWN"

if (
    not regime.empty
    and "Regime" in regime.columns
):

    current_regime = (
        regime.iloc[-1]["Regime"]
    )

# =========================================================
# POSITION HEALTH
# =========================================================

portfolio_health = portfolio.copy()

portfolio_health["Health_Flag"] = "OK"

if "Weight" in portfolio_health.columns:

    portfolio_health.loc[
        portfolio_health["Weight"]
        > MAX_POSITION_WEIGHT,

        "Health_Flag"

    ] = "OVERWEIGHT"

# =========================================================
# SIGNAL MONITORING
# =========================================================

rebalance_records = []

sell_count = 0

if (
    not signals.empty
    and "Symbol" in signals.columns
):

    merged = portfolio.merge(

        signals[
            [
                "Symbol",
                "Signal",
                "Signal_Score",
            ]
        ],

        on="Symbol",

        how="left",
    )

    for _, row in merged.iterrows():

        signal = str(
            row.get(
                "Signal",
                ""
            )
        )

        if signal in [

            "SELL",

            "REDUCE",
        ]:

            sell_count += 1

            rebalance_records.append({

                "Symbol":
                row["Symbol"],

                "Action":
                signal,

                "Reason":
                "Signal deterioration",
            })

# =========================================================
# DRIFT ANALYSIS
# =========================================================

portfolio_drift = portfolio.copy()

if "Weight" in portfolio.columns:

    target = (
        1 / len(portfolio)
    )

    portfolio_drift[
        "Target_Weight"
    ] = target

    portfolio_drift[
        "Drift"
    ] = (

        portfolio_drift[
            "Weight"
        ]

        - target

    )

# =========================================================
# HEALTH SCORE
# =========================================================

health_score = 100

# Signal penalty

health_score -= (
    sell_count * 2
)

# Risk penalty

if not risk.empty:

    try:

        breaches = int(

            risk.loc[
                risk["Metric"]
                ==
                "Risk_Breaches",

                "Value"
            ].iloc[0]
        )

        health_score -= (
            breaches * 5
        )

    except Exception:

        pass

# Regime penalty

if "BEAR" in current_regime:

    health_score -= 10

if "HIGH_VOL" in current_regime:

    health_score -= 5

health_score = max(
    0,
    min(
        100,
        health_score
    )
)

# =========================================================
# HEALTH CLASSIFICATION
# =========================================================

if health_score >= 90:

    health_status = (
        "EXCELLENT"
    )

elif health_score >= 75:

    health_status = (
        "HEALTHY"
    )

elif health_score >= 60:

    health_status = (
        "WATCH"
    )

else:

    health_status = (
        "ACTION_REQUIRED"
    )

# =========================================================
# DASHBOARD
# =========================================================

dashboard = pd.DataFrame({

    "Metric": [

        "Current_Regime",

        "Holdings",

        "Health_Score",

        "Health_Status",

        "Sell_Signals",

        "Rebalance_Items",

        "Run_Date",

        "Engine_Version",
    ],

    "Value": [

        current_regime,

        len(portfolio),

        health_score,

        health_status,

        sell_count,

        len(
            rebalance_records
        ),

        datetime.now()
        .strftime(
            "%Y-%m-%d"
        ),

        ENGINE_VERSION,
    ]
})

# =========================================================
# REBALANCE FILE
# =========================================================

rebalance = pd.DataFrame(
    rebalance_records
)

# =========================================================
# SAVE
# =========================================================

portfolio_health.to_csv(

    OUTPUT_DIR
    / "portfolio_health.csv",

    index=False,
)

portfolio_drift.to_csv(

    OUTPUT_DIR
    / "portfolio_drift.csv",

    index=False,
)

rebalance.to_csv(

    OUTPUT_DIR
    / "rebalance_recommendations.csv",

    index=False,
)

dashboard.to_csv(

    OUTPUT_DIR
    / "portfolio_dashboard.csv",

    index=False,
)

dashboard.to_csv(

    REPORT_FILE,

    index=False,
)

# =========================================================
# REPORT
# =========================================================

print("\n" + "=" * 70)

print(
    "🏁 PORTFOLIO MONITOR COMPLETE"
)

print("=" * 70)

print(
    f"Regime         : "
    f"{current_regime}"
)

print(
    f"Health Score   : "
    f"{health_score}"
)

print(
    f"Health Status  : "
    f"{health_status}"
)

print(
    f"Sell Signals   : "
    f"{sell_count}"
)

print(
    f"Rebalance Items: "
    f"{len(rebalance_records)}"
)

print(
    f"\nOutput Directory:\n"
    f"{OUTPUT_DIR}"
)

print("=" * 70)