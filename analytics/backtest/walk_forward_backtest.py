"""
=========================================================
WALK FORWARD BACKTEST ENGINE
=========================================================

Purpose:
Institutional Bias-Free Backtesting

Methodology:
Monthly Rebalance

Outputs:
walk_forward_equity_curve.csv
walk_forward_results.csv
rebalance_history.csv

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

TOP_N = 50

REBALANCE_FREQ = "ME"

TRADING_DAYS = 252

ENGINE_VERSION = "1.0.0"

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

SECURITY_MASTER = (
    ROOT
    / "data"
    / "raw"
    / "security_master.csv"
)

PRICE_DIR = (
    ROOT
    / "data"
    / "raw"
    / "prices"
)

OUTPUT_DIR = (
    ROOT
    / "data"
    / "backtests"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

# =========================================================
# LOAD UNIVERSE
# =========================================================

print(
    "\n📥 Loading Securities..."
)

universe = pd.read_csv(
    SECURITY_MASTER
)

symbols = (
    universe["Symbol"]
    .dropna()
    .unique()
    .tolist()
)

# =========================================================
# LOAD PRICES
# =========================================================

price_matrix = []

for symbol in symbols:

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

        tmp = pd.DataFrame({

            "Date":
            pd.to_datetime(
                df["Date"]
            ),

            "Symbol":
            symbol,

            "Close":
            pd.to_numeric(
                df["Close"],
                errors="coerce"
            )
        })

        price_matrix.append(
            tmp
        )

    except Exception:

        continue

prices = pd.concat(
    price_matrix,
    ignore_index=True
)

prices = prices.dropna()

print(
    f"Price Rows: "
    f"{len(prices):,}"
)

print(
    f"Symbols: "
    f"{prices['Symbol'].nunique():,}"
)

prices["Date"] = pd.to_datetime(
    prices["Date"],
    errors="coerce"
)

prices = prices.dropna(
    subset=["Date"]
)

# =========================================================
# REBALANCE DATES
# =========================================================

prices["Date"] = pd.to_datetime(
    prices["Date"]
)

rebalance_dates = (

    prices

    .groupby(
        prices["Date"]
        .dt.to_period("M")
    )["Date"]

    .max()

    .sort_values()

    .tolist()
)

print(
    f"Rebalance Dates: "
    f"{len(rebalance_dates)}"
)

print(
    "First:",
    rebalance_dates[0]
)

print(
    "Last:",
    rebalance_dates[-1]
)

# =========================================================
# STORAGE
# =========================================================

capital = INITIAL_CAPITAL

equity_curve = []

rebalance_history = []

# =========================================================
# MAIN LOOP
# =========================================================

print(
    "\n🚀 Running Walk Forward..."
)

for idx in range(
    12,
    len(rebalance_dates) - 1
):

    rebalance_date = (
        rebalance_dates[idx]
    )

    next_date = (
        rebalance_dates[idx + 1]
    )

    # =====================================
    # Historical Data Only
    # =====================================

    hist = prices[
        prices["Date"]
        <= rebalance_date
    ]

    factor_records = []

    # =====================================
    # Factor Calculation
    # =====================================

    for symbol in symbols:

        tmp = hist[
            hist["Symbol"]
            == symbol
        ]

        if len(tmp) < 252:
            continue

        close = (
            tmp["Close"]
            .dropna()
        )

        momentum = (

            close.iloc[-1]

            / close.iloc[-252]

            - 1
        )

        volatility = (

            close
            .pct_change()
            .std()

            * np.sqrt(252)
        )

        factor_records.append({

            "Symbol":
            symbol,

            "Momentum":
            momentum,

            "Volatility":
            volatility,
        })

    factors = pd.DataFrame(
        factor_records
    )

    if factors.empty:
        continue

    # =====================================
    # Ranking
    # =====================================

    factors["Momentum_Rank"] = (

        factors[
            "Momentum"
        ]

        .rank(
            pct=True
        )
    )

    factors["Vol_Rank"] = (

        1

        -

        factors[
            "Volatility"
        ]

        .rank(
            pct=True
        )
    )

    factors["Alpha"] = (

        0.7
        * factors[
            "Momentum_Rank"
        ]

        +

        0.3
        * factors[
            "Vol_Rank"
        ]
    )

    portfolio = (

        factors

        .sort_values(
            "Alpha",
            ascending=False
        )

        .head(TOP_N)
    )

    portfolio["Weight"] = (
        1 / len(portfolio)
    )

    # =====================================
    # Forward Returns
    # =====================================

    future = prices[

        (prices["Date"] > rebalance_date)

        &

        (prices["Date"] <= next_date)
    ]

    if future.empty:
        continue

    returns = []

    for _, row in portfolio.iterrows():

        symbol = row["Symbol"]

        weight = row["Weight"]

        tmp = future[
            future["Symbol"]
            == symbol
        ]

        if len(tmp) < 2:
            continue

        ret = (

            tmp["Close"]
            .iloc[-1]

            / tmp["Close"]
            .iloc[0]

            - 1
        )

        returns.append(
            ret * weight
        )

    period_return = np.sum(
        returns
    )

    capital *= (
        1 + period_return
    )

    equity_curve.append({

        "Date":
        next_date,

        "Portfolio_Value":
        capital,

        "Period_Return":
        period_return,
    })

    rebalance_history.append({

        "Rebalance_Date":
        rebalance_date,

        "Portfolio_Size":
        len(portfolio),

        "Portfolio_Return":
        period_return,
    })

# =========================================================
# EQUITY CURVE
# =========================================================

equity_curve = pd.DataFrame(
    equity_curve
)

equity_curve[
    "Cumulative_Return"
] = (

    equity_curve[
        "Portfolio_Value"
    ]

    / INITIAL_CAPITAL

    - 1
)

# =========================================================
# METRICS
# =========================================================

returns = equity_curve[
    "Period_Return"
]

years = (
    len(returns)
    / 12
)

cagr = (

    (
        capital
        / INITIAL_CAPITAL
    )

    ** (1 / years)

    - 1
)

volatility = (
    returns.std()
    * np.sqrt(12)
)

sharpe = (
    cagr
    / max(
        volatility,
        1e-9
    )
)

# =========================================================
# SAVE
# =========================================================

equity_curve.to_csv(
    OUTPUT_DIR
    / "walk_forward_equity_curve.csv",
    index=False,
)

pd.DataFrame(
    rebalance_history
).to_csv(
    OUTPUT_DIR
    / "rebalance_history.csv",
    index=False,
)

pd.DataFrame({

    "Metric": [

        "CAGR",
        "Volatility",
        "Sharpe",
        "Final_Capital",
        "Run_Date",
    ],

    "Value": [

        cagr,
        volatility,
        sharpe,
        capital,
        datetime.now()
        .strftime(
            "%Y-%m-%d"
        ),
    ]
}).to_csv(

    OUTPUT_DIR
    / "walk_forward_results.csv",

    index=False,
)

# =========================================================
# COMPLETION REPORT
# =========================================================

print("\n" + "=" * 70)

print(
    "🏁 WALK FORWARD BACKTEST COMPLETE"
)

print("=" * 70)

print(
    f"Rebalance Periods : "
    f"{len(rebalance_history):,}"
)

print(
    f"CAGR              : "
    f"{cagr:.2%}"
)

print(
    f"Volatility        : "
    f"{volatility:.2%}"
)

print(
    f"Sharpe Ratio      : "
    f"{sharpe:.2f}"
)

print(
    f"Final Capital     : "
    f"₹{capital:,.0f}"
)

print(
    f"Total Return      : "
    f"{(capital / INITIAL_CAPITAL - 1):.2%}"
)

print(
    f"\nEquity Curve:\n"
    f"{OUTPUT_DIR / 'walk_forward_equity_curve.csv'}"
)

print(
    f"\nResults:\n"
    f"{OUTPUT_DIR / 'walk_forward_results.csv'}"
)

print(
    f"\nRebalance History:\n"
    f"{OUTPUT_DIR / 'rebalance_history.csv'}"
)

print("=" * 70)