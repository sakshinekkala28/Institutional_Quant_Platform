"""
=========================================================
STRATEGY COMPARISON ENGINE
=========================================================

Purpose:
Institutional Multi-Strategy Evaluation Framework

Inputs:
data/research/strategies/*.csv

Outputs:
strategy_comparison.csv
strategy_rankings.csv
strategy_scorecard.csv

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

RISK_FREE_RATE = 0.06

TRADING_DAYS = 252

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

STRATEGY_DIR = (
    ROOT
    / "data"
    / "research"
    / "strategies"
)

OUTPUT_DIR = (
    ROOT
    / "data"
    / "research"
)

REPORT_FILE = (
    ROOT
    / "data"
    / "logs"
    / "strategy_comparison_report.csv"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

# =========================================================
# DISCOVER STRATEGIES
# =========================================================

print(
    "\n📥 Loading Strategies..."
)

strategy_files = sorted(
    STRATEGY_DIR.glob("*.csv")
)

if not strategy_files:

    raise ValueError(
        "No strategy files found"
    )

# =========================================================
# STORAGE
# =========================================================

results = []

# =========================================================
# PROCESS STRATEGIES
# =========================================================

for file in strategy_files:

    strategy_name = file.stem

    try:

        df = pd.read_csv(file)

        # =====================================
        # VALIDATION
        # =====================================

        if "Portfolio_Value" in df.columns:

            equity = pd.to_numeric(
                df["Portfolio_Value"],
                errors="coerce"
            )

            returns = (
                equity
                .pct_change()
                .dropna()
            )

        elif "Return" in df.columns:

            returns = pd.to_numeric(
                df["Return"],
                errors="coerce"
            ).dropna()

            equity = (
                1 + returns
            ).cumprod()

        else:

            print(
                f"Skipping {strategy_name}"
            )

            continue

        if len(returns) < 12:

            continue

        # =====================================
        # CAGR
        # =====================================

        years = max(
            len(returns)
            / TRADING_DAYS,
            0.1
        )

        cagr = (

            (
                equity.iloc[-1]
                / equity.iloc[0]
            )

            ** (1 / years)

            - 1
        )

        # =====================================
        # VOLATILITY
        # =====================================

        volatility = (

            returns.std()

            * np.sqrt(
                TRADING_DAYS
            )
        )

        # =====================================
        # SHARPE
        # =====================================

        sharpe = (

            cagr
            - RISK_FREE_RATE

        ) / max(
            volatility,
            1e-9,
        )

        # =====================================
        # SORTINO
        # =====================================

        downside = returns[
            returns < 0
        ]

        sortino = (

            cagr
            - RISK_FREE_RATE

        ) / max(

            downside.std()
            * np.sqrt(
                TRADING_DAYS
            ),

            1e-9,
        )

        # =====================================
        # DRAWDOWN
        # =====================================

        running_max = (
            equity.cummax()
        )

        drawdown = (
            equity
            / running_max
        ) - 1

        max_drawdown = (
            drawdown.min()
        )

        # =====================================
        # CALMAR
        # =====================================

        calmar = (

            cagr

            / max(
                abs(
                    max_drawdown
                ),
                1e-9,
            )
        )

        # =====================================
        # WIN RATE
        # =====================================

        win_rate = (
            returns > 0
        ).mean()

        # =====================================
        # PROFIT FACTOR
        # =====================================

        gross_profit = (
            returns[
                returns > 0
            ].sum()
        )

        gross_loss = abs(

            returns[
                returns < 0
            ].sum()
        )

        profit_factor = (

            gross_profit

            / max(
                gross_loss,
                1e-9,
            )
        )

        # =====================================
        # SCORE
        # =====================================

        results.append({

            "Strategy":
            strategy_name,

            "CAGR":
            cagr,

            "Volatility":
            volatility,

            "Sharpe":
            sharpe,

            "Sortino":
            sortino,

            "Max_Drawdown":
            max_drawdown,

            "Calmar":
            calmar,

            "Win_Rate":
            win_rate,

            "Profit_Factor":
            profit_factor,
        })

    except Exception as e:

        print(
            strategy_name,
            str(e)
        )

# =========================================================
# COMPARISON TABLE
# =========================================================

comparison = pd.DataFrame(
    results
)

if comparison.empty:

    raise ValueError(
        "No valid strategies"
    )

# =========================================================
# RANKS
# =========================================================

comparison["CAGR_Rank"] = (
    comparison["CAGR"]
    .rank(
        ascending=False
    )
)

comparison["Sharpe_Rank"] = (
    comparison["Sharpe"]
    .rank(
        ascending=False
    )
)

comparison["Calmar_Rank"] = (
    comparison["Calmar"]
    .rank(
        ascending=False
    )
)

comparison["Drawdown_Rank"] = (
    comparison[
        "Max_Drawdown"
    ].rank(
        ascending=False
    )
)

# =========================================================
# COMPOSITE SCORE
# =========================================================

comparison["Composite_Score"] = (

      0.30
    * comparison["CAGR"]
      .rank(pct=True)

    + 0.30
    * comparison["Sharpe"]
      .rank(pct=True)

    + 0.20
    * comparison["Calmar"]
      .rank(pct=True)

    + 0.20
    * (
        1
        -
        comparison[
            "Max_Drawdown"
        ].rank(pct=True)
      )
)

# =========================================================
# FINAL RANKING
# =========================================================

comparison = (

    comparison

    .sort_values(
        "Composite_Score",
        ascending=False,
    )

    .reset_index(
        drop=True
    )
)

comparison["Overall_Rank"] = (
    comparison.index + 1
)

# =========================================================
# SCORECARD
# =========================================================

scorecard = comparison[

    [

        "Overall_Rank",

        "Strategy",

        "Composite_Score",

        "CAGR",

        "Sharpe",

        "Sortino",

        "Calmar",

        "Max_Drawdown",

        "Win_Rate",

        "Profit_Factor",
    ]
]

# =========================================================
# SUMMARY
# =========================================================

best_strategy = (
    comparison.iloc[0]
)

summary = pd.DataFrame({

    "Metric": [

        "Strategies_Compared",

        "Best_Strategy",

        "Best_CAGR",

        "Best_Sharpe",

        "Run_Date",

        "Engine_Version",
    ],

    "Value": [

        len(comparison),

        best_strategy[
            "Strategy"
        ],

        best_strategy[
            "CAGR"
        ],

        best_strategy[
            "Sharpe"
        ],

        datetime.now()
        .strftime(
            "%Y-%m-%d"
        ),

        ENGINE_VERSION,
    ]
})

# =========================================================
# SAVE
# =========================================================

comparison.to_csv(

    OUTPUT_DIR
    / "strategy_comparison.csv",

    index=False,
)

scorecard.to_csv(

    OUTPUT_DIR
    / "strategy_scorecard.csv",

    index=False,
)

summary.to_csv(

    OUTPUT_DIR
    / "strategy_rankings.csv",

    index=False,
)

summary.to_csv(

    REPORT_FILE,

    index=False,
)

# =========================================================
# REPORT
# =========================================================

print("\n" + "=" * 70)

print(
    "🏁 STRATEGY COMPARISON COMPLETE"
)

print("=" * 70)

print(
    f"Strategies Compared : "
    f"{len(comparison)}"
)

print(
    f"Best Strategy       : "
    f"{best_strategy['Strategy']}"
)

print(
    f"Best CAGR           : "
    f"{best_strategy['CAGR']:.2%}"
)

print(
    f"Best Sharpe         : "
    f"{best_strategy['Sharpe']:.2f}"
)

print(
    f"\nOutput Directory:\n"
    f"{OUTPUT_DIR}"
)

print("=" * 70)