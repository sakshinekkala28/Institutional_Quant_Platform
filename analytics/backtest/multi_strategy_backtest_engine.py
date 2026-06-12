"""
=========================================================
MULTI STRATEGY BACKTEST ENGINE
=========================================================

Purpose:
Institutional Multi-Strategy Research Engine

Input:
data/portfolios/*.csv
data/raw/prices/*.parquet

Outputs:
data/research/strategies/*
data/backtests/all_strategy_results.csv

=========================================================
"""

from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

import numpy as np
import pandas as pd

# =========================================================
# CONFIG
# =========================================================

INITIAL_CAPITAL = 1_000_000

RISK_FREE_RATE = 0.06

TRADING_DAYS = 252

MAX_WORKERS = 4

ENGINE_VERSION = "1.0.0"

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

PORTFOLIO_DIR = (
    ROOT
    / "data"
    / "portfolios"
)

PRICE_DIR = (
    ROOT
    / "data"
    / "raw"
    / "prices"
)

STRATEGY_DIR = (
    ROOT
    / "data"
    / "research"
    / "strategies"
)

BACKTEST_DIR = (
    ROOT
    / "data"
    / "backtests"
)

REPORT_FILE = (
    ROOT
    / "data"
    / "logs"
    / "multi_strategy_backtest_report.csv"
)

STRATEGY_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

BACKTEST_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

# =========================================================
# BACKTEST FUNCTION
# =========================================================

def run_strategy_backtest(
    portfolio_file,
):

    strategy_name = (
        Path(portfolio_file)
        .stem
    )

    try:

        portfolio = pd.read_csv(
            portfolio_file
        )

        required_cols = [
            "Symbol",
            "Weight",
        ]

        missing = [

            c

            for c in required_cols

            if c not in portfolio.columns
        ]

        if missing:

            return None

        returns_list = []

        for _, row in portfolio.iterrows():

            symbol = row["Symbol"]

            weight = row["Weight"]

            file = (
                PRICE_DIR
                / f"{symbol}.parquet"
            )

            if not file.exists():
                continue

            try:

                df = pd.read_parquet(
                    file
                )

                if (
                    "Date"
                    not in df.columns
                    or
                    "Close"
                    not in df.columns
                ):
                    continue

                tmp = pd.DataFrame({

                    "Date":
                    pd.to_datetime(
                        df["Date"]
                    ),

                    "Return":
                    pd.to_numeric(
                        df["Close"],
                        errors="coerce"
                    )
                    .pct_change(),

                    "Weight":
                    weight,
                })

                returns_list.append(
                    tmp
                )

            except Exception:

                continue

        if not returns_list:

            return None

        all_returns = pd.concat(
            returns_list,
            ignore_index=True,
        )

        all_returns = (
            all_returns
            .dropna()
        )

        portfolio_returns = (

            all_returns

            .groupby("Date")

            .apply(
                lambda x:
                (
                    x["Return"]
                    * x["Weight"]
                ).sum()
            )

            .reset_index(
                name="Portfolio_Return"
            )
        )

        portfolio_returns = (
            portfolio_returns
            .sort_values(
                "Date"
            )
        )

        if len(
            portfolio_returns
        ) < 30:

            return None

        portfolio_returns[
            "Portfolio_Value"
        ] = (

            INITIAL_CAPITAL

            * (

                1

                + portfolio_returns[
                    "Portfolio_Return"
                ]

            ).cumprod()
        )

        equity_curve = (
            portfolio_returns.copy()
        )

        rolling_max = (

            equity_curve[
                "Portfolio_Value"
            ]

            .cummax()
        )

        equity_curve[
            "Drawdown"
        ] = (

            equity_curve[
                "Portfolio_Value"
            ]

            / rolling_max

            - 1
        )

        returns = (
            portfolio_returns[
                "Portfolio_Return"
            ]
        )

        annual_return = (

            (
                1
                + returns.mean()
            )

            ** TRADING_DAYS

            - 1
        )

        annual_vol = (

            returns.std()

            * np.sqrt(
                TRADING_DAYS
            )
        )

        sharpe = (

            annual_return

            - RISK_FREE_RATE

        ) / max(
            annual_vol,
            1e-9,
        )

        downside = returns[
            returns < 0
        ]

        sortino = (

            annual_return

            - RISK_FREE_RATE

        ) / max(

            downside.std()

            * np.sqrt(
                TRADING_DAYS
            ),

            1e-9,
        )

        drawdown = (
            equity_curve[
                "Drawdown"
            ]
        )

        max_dd = (
            drawdown.min()
        )

        years = max(

            len(
                portfolio_returns
            )

            / TRADING_DAYS,

            1
            / TRADING_DAYS,
        )

        final_value = (
            equity_curve[
                "Portfolio_Value"
            ]
            .iloc[-1]
        )

        cagr = (

            (
                final_value

                / INITIAL_CAPITAL
            )

            ** (
                1 / years
            )

            - 1
        )

        calmar = (

            cagr

            / max(
                abs(
                    max_dd
                ),
                1e-9,
            )
        )

        win_rate = (
            returns > 0
        ).mean()

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
        # SAVE EQUITY CURVE
        # =====================================

        equity_curve.to_csv(

            STRATEGY_DIR

            / f"{strategy_name}_equity.csv",

            index=False,
        )

        metrics = {

            "Strategy":
            strategy_name,

            "Final_Capital":
            final_value,

            "CAGR":
            cagr,

            "Annual_Return":
            annual_return,

            "Annual_Volatility":
            annual_vol,

            "Sharpe":
            sharpe,

            "Sortino":
            sortino,

            "Calmar":
            calmar,

            "Max_Drawdown":
            max_dd,

            "Win_Rate":
            win_rate,

            "Profit_Factor":
            profit_factor,
        }

        pd.DataFrame(
            [metrics]
        ).to_csv(

            STRATEGY_DIR

            / f"{strategy_name}_metrics.csv",

            index=False,
        )

        return metrics

    except Exception as e:

        print(
            strategy_name,
            str(e)
        )

        return None

# =========================================================
# DISCOVER PORTFOLIOS
# =========================================================

print(
    "\n📥 Loading Portfolios..."
)

portfolio_files = sorted(
    PORTFOLIO_DIR.glob(
        "*.csv"
    )
)

if not portfolio_files:

    raise ValueError(
        "No portfolios found"
    )

print(
    f"Strategies Found: "
    f"{len(portfolio_files)}"
)

# =========================================================
# EXECUTE
# =========================================================

print(
    "\n🚀 Running Backtests..."
)

results = []

with ThreadPoolExecutor(
    max_workers=MAX_WORKERS
) as executor:

    futures = [

        executor.submit(
            run_strategy_backtest,
            str(f),
        )

        for f in portfolio_files
    ]

    for future in futures:

        result = future.result()

        if result:

            results.append(
                result
            )

# =========================================================
# MASTER RESULTS
# =========================================================

master = pd.DataFrame(
    results
)

if master.empty:

    raise ValueError(
        "No successful backtests"
    )

master = (

    master

    .sort_values(
        "Sharpe",
        ascending=False,
    )

    .reset_index(
        drop=True
    )
)

master["Rank"] = (
    master.index + 1
)

master["Run_Date"] = (
    datetime.now()
    .strftime(
        "%Y-%m-%d"
    )
)

master["Engine_Version"] = (
    ENGINE_VERSION
)

master.to_csv(

    BACKTEST_DIR

    / "all_strategy_results.csv",

    index=False,
)

master.to_csv(
    REPORT_FILE,
    index=False,
)

# =========================================================
# REPORT
# =========================================================

best = master.iloc[0]

print("\n" + "=" * 70)

print(
    "🏁 MULTI STRATEGY BACKTEST COMPLETE"
)

print("=" * 70)

print(
    f"Strategies Tested : "
    f"{len(master)}"
)

print(
    f"Best Strategy     : "
    f"{best['Strategy']}"
)

print(
    f"Best Sharpe       : "
    f"{best['Sharpe']:.2f}"
)

print(
    f"Best CAGR         : "
    f"{best['CAGR']:.2%}"
)

print(
    f"\nOutput Directory:\n"
    f"{STRATEGY_DIR}"
)

print("=" * 70)