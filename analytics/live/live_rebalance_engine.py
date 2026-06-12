"""
=========================================================
LIVE REBALANCE ENGINE
=========================================================

Purpose:
Institutional Production Orchestrator

Runs Entire Quant Platform

=========================================================
"""

from pathlib import Path
from datetime import datetime
import subprocess
import sys
import time
import pandas as pd

# =========================================================
# CONFIG
# =========================================================

ENGINE_VERSION = "1.0.0"

STOP_ON_FAILURE = True

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

LOG_DIR = (
    ROOT
    / "data"
    / "logs"
)

LOG_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

RUN_LOG = (
    LOG_DIR
    / "live_rebalance_log.csv"
)

# =========================================================
# PIPELINE
# =========================================================

PIPELINE = [

    (
        "Incremental Price Update",

        ROOT
        / "analytics"
        / "data"
        / "incremental_price_update.py"
    ),

    (
        "Factor Engine",

        ROOT
        / "analytics"
        / "factors"
        / "factor_engine.py"
    ),

    (
        "Factor Rank Engine",

        ROOT
        / "analytics"
        / "factors"
        / "factor_rank_engine.py"
    ),

    (
        "Portfolio Engine",

        ROOT
        / "analytics"
        / "portfolio"
        / "portfolio_engine.py"
    ),

    (
        "Portfolio Optimizer",

        ROOT
        / "analytics"
        / "portfolio"
        / "portfolio_optimizer.py"
    ),

    (
        "Risk Engine",

        ROOT
        / "analytics"
        / "risk"
        / "risk_engine.py"
    ),

    (
        "Execution Engine",

        ROOT
        / "analytics"
        / "execution"
        / "execution_engine.py"
    ),

    (
        "Performance Attribution",

        ROOT
        / "analytics"
        / "performance"
        / "performance_attribution_engine.py"
    ),
]

# =========================================================
# EXECUTOR
# =========================================================

def run_step(
    step_name,
    script_path
):

    start_time = datetime.now()

    print(
        "\n"
        + "=" * 70
    )

    print(
        f"🚀 {step_name}"
    )

    print(
        "=" * 70
    )

    try:

        result = subprocess.run(

            [
                sys.executable,
                str(script_path),
            ],

            capture_output=True,

            text=True,

            check=True,
        )

        duration = (

            datetime.now()
            -
            start_time
        ).total_seconds()

        print(
            result.stdout
        )

        return {

            "Step":
            step_name,

            "Status":
            "SUCCESS",

            "Duration_Seconds":
            round(
                duration,
                2
            ),

            "Timestamp":
            datetime.now()
            .strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        }

    except subprocess.CalledProcessError as e:

        duration = (

            datetime.now()
            -
            start_time
        ).total_seconds()

        print(
            e.stderr
        )

        return {

            "Step":
            step_name,

            "Status":
            "FAILED",

            "Duration_Seconds":
            round(
                duration,
                2
            ),

            "Timestamp":
            datetime.now()
            .strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        }

# =========================================================
# MAIN
# =========================================================

print(
    "\n🏦 LIVE REBALANCE ENGINE"
)

print(
    f"Version: "
    f"{ENGINE_VERSION}"
)

pipeline_results = []

overall_start = datetime.now()

for step_name, script in PIPELINE:

    if not script.exists():

        print(
            f"❌ Missing: {script}"
        )

        pipeline_results.append(

            {

                "Step":
                step_name,

                "Status":
                "MISSING",

                "Duration_Seconds":
                0,

                "Timestamp":
                datetime.now()
                .strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            }
        )

        if STOP_ON_FAILURE:
            break

        continue

    result = run_step(
        step_name,
        script
    )

    pipeline_results.append(
        result
    )

    if (
        result["Status"]
        != "SUCCESS"
        and STOP_ON_FAILURE
    ):

        print(
            "\n🛑 Pipeline Stopped"
        )

        break

# =========================================================
# SAVE LOG
# =========================================================

log_df = pd.DataFrame(
    pipeline_results
)

if RUN_LOG.exists():

    existing = pd.read_csv(
        RUN_LOG
    )

    log_df = pd.concat(

        [
            existing,
            log_df,
        ],

        ignore_index=True,
    )

log_df.to_csv(
    RUN_LOG,
    index=False,
)

# =========================================================
# SUMMARY
# =========================================================

total_runtime = (

    datetime.now()
    -
    overall_start
).total_seconds()

success_count = (

    pd.DataFrame(
        pipeline_results
    )["Status"]

    == "SUCCESS"
).sum()

failed_count = (

    pd.DataFrame(
        pipeline_results
    )["Status"]

    != "SUCCESS"
).sum()

# =========================================================
# REPORT
# =========================================================

print(
    "\n"
    + "=" * 70
)

print(
    "🏁 LIVE REBALANCE COMPLETE"
)

print(
    "=" * 70
)

print(
    f"Steps Run      : "
    f"{len(pipeline_results)}"
)

print(
    f"Successful     : "
    f"{success_count}"
)

print(
    f"Failed         : "
    f"{failed_count}"
)

print(
    f"Runtime (sec)  : "
    f"{total_runtime:,.2f}"
)

print(
    f"\nLog File:\n"
    f"{RUN_LOG}"
)

print(
    "=" * 70
)