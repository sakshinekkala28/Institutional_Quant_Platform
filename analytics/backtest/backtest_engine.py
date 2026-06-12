"""
=========================================================
BACKTEST ENGINE
=========================================================

Purpose:
Institutional Portfolio Backtest Engine

Input:
data/portfolios/live_portfolio.csv
data/raw/prices/*.parquet

Outputs:
data/backtests/equity_curve.csv
data/backtests/monthly_returns.csv
data/backtests/backtest_results.csv
data/logs/backtest_report.csv

=========================================================
"""

from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd

# =========================================================
# CONFIG
# =========================================================

INITIAL_CAPITAL = 1_000_000

RISK_FREE_RATE = 0.06

TRADING_DAYS = 252

ENGINE_VERSION = "1.0.0"

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

PRICE_DIR = (
    ROOT
    / "data"
    / "raw"
    / "prices"
)

BACKTEST_DIR = (
    ROOT
    / "data"
    / "backtests"
)

RESULTS_FILE = (
    BACKTEST_DIR
    / "backtest_results.csv"
)

EQUITY_FILE = (
    BACKTEST_DIR
    / "equity_curve.csv"
)

MONTHLY_FILE = (
    BACKTEST_DIR
    / "monthly_returns.csv"
)

REPORT_FILE = (
    ROOT
    / "data"
    / "logs"
    / "backtest_report.csv"
)

# =========================================================
# LOAD PORTFOLIO
# =========================================================

print("\n📥 Loading Portfolio...")

portfolio = pd.read_csv(
    PORTFOLIO_FILE
)

if portfolio.empty:

    raise ValueError(
        "Portfolio is empty"
    )

required_cols = [
    "Symbol",
    "Weight",
]

for col in required_cols:

    if col not in portfolio.columns:

        raise ValueError(
            f"Missing column: {col}"
        )

# =========================================================
# LOAD PRICE HISTORY
# =========================================================

print("\n📊 Building Return Matrix...")

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

        if "Close" not in df.columns:
            continue

        prices = pd.to_numeric(
            df["Close"],
            errors="coerce"
        )

        returns = (
            prices
            .pct_change()
        )

        tmp = pd.DataFrame({

            "Date":
            pd.to_datetime(
                df["Date"]
            ),

            "Return":
            returns,

            "Weight":
            weight,

            "Symbol":
            symbol,
        })

        returns_list.append(
            tmp
        )

    except Exception:

        continue

if not returns_list:

    raise ValueError(
        "No usable price history"
    )

# =========================================================
# PORTFOLIO RETURNS
# =========================================================

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
    .sort_values("Date")
)

# =========================================================
# EQUITY CURVE
# =========================================================

portfolio_returns[
    "Portfolio_Value"
] = (

    INITIAL_CAPITAL

    * (

        1
        +
        portfolio_returns[
            "Portfolio_Return"
        ]

    ).cumprod()

)

portfolio_returns[
    "Cumulative_Return"
] = (

    portfolio_returns[
        "Portfolio_Value"
    ]

    / INITIAL_CAPITAL

    - 1
)

equity_curve = (

    portfolio_returns[

        [
            "Date",
            "Portfolio_Return",
            "Portfolio_Value",
            "Cumulative_Return",
        ]

    ]

    .copy()
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

equity_curve[
    "High_Water_Mark"
] = rolling_max

# =========================================================
# MONTHLY RETURNS
# =========================================================

monthly_returns = (

    portfolio_returns

    .set_index("Date")

    ["Portfolio_Return"]

    .resample("ME")

    .apply(
        lambda x:
        (1 + x).prod() - 1
    )

    .reset_index()
)

# =========================================================
# PERFORMANCE METRICS
# =========================================================

daily_returns = (
    portfolio_returns[
        "Portfolio_Return"
    ]
)

annual_return = (

    (1 + daily_returns.mean())

    ** TRADING_DAYS

    - 1

)

annual_volatility = (

    daily_returns.std()

    * np.sqrt(
        TRADING_DAYS
    )
)

sharpe_ratio = (

    annual_return
    - RISK_FREE_RATE

) / max(
    annual_volatility,
    1e-9,
)

downside = daily_returns[
    daily_returns < 0
]

sortino_ratio = (

    annual_return
    - RISK_FREE_RATE

) / max(

    downside.std()
    * np.sqrt(
        TRADING_DAYS
    ),

    1e-9,
)

equity = equity_curve[
    "Portfolio_Value"
]

rolling_max = (
    equity.cummax()
)

drawdown = (
    equity
    / rolling_max
) - 1

max_drawdown = (
    drawdown.min()
)

years = (

    len(
        portfolio_returns
    )

    / TRADING_DAYS
)

cagr = (

    (
        equity.iloc[-1]
        / equity.iloc[0]
    )

    ** (1 / years)

    - 1
)

calmar_ratio = (

    cagr

    / max(
        abs(
            max_drawdown
        ),
        1e-9,
    )
)

win_rate = (

    (
        daily_returns > 0
    ).mean()
)

gross_profit = (
    daily_returns[
        daily_returns > 0
    ].sum()
)

gross_loss = abs(
    daily_returns[
        daily_returns < 0
    ].sum()
)

profit_factor = (

    gross_profit

    / max(
        gross_loss,
        1e-9,
    )
)

# =========================================================
# RESULTS
# =========================================================

results = pd.DataFrame({

    "Metric": [

        "Initial_Capital",
        "Final_Capital",

        "CAGR",

        "Annual_Return",

        "Annual_Volatility",

        "Sharpe_Ratio",

        "Sortino_Ratio",

        "Max_Drawdown",

        "Calmar_Ratio",

        "Win_Rate",

        "Profit_Factor",

        "Run_Date",

        "Engine_Version",
    ],

    "Value": [

        INITIAL_CAPITAL,

        equity.iloc[-1],

        cagr,

        annual_return,

        annual_volatility,

        sharpe_ratio,

        sortino_ratio,

        max_drawdown,

        calmar_ratio,

        win_rate,

        profit_factor,

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

BACKTEST_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

equity_curve.to_csv(
    EQUITY_FILE,
    index=False,
)

monthly_returns.to_csv(
    MONTHLY_FILE,
    index=False,
)

results.to_csv(
    RESULTS_FILE,
    index=False,
)

results.to_csv(
    REPORT_FILE,
    index=False,
)

# =========================================================
# REPORT
# =========================================================

print("\n" + "=" * 70)

print(
    "🏁 BACKTEST COMPLETE"
)

print("=" * 70)

print(
    f"CAGR           : {cagr:.2%}"
)

print(
    f"Sharpe Ratio   : {sharpe_ratio:.2f}"
)

print(
    f"Max Drawdown   : {max_drawdown:.2%}"
)

print(
    f"Win Rate       : {win_rate:.2%}"
)

print(
    f"Final Capital  : "
    f"{equity.iloc[-1]:,.0f}"
)

print("=" * 70)