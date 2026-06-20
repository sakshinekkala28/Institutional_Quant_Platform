from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[2]

PRICE_FILE = (
    ROOT
    / "data"
    / "raw"
    / "security_price_history.parquet"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "risk"
    / "daily_returns.parquet"
)

print("Loading Security Price History...")

prices = pd.read_parquet(
    PRICE_FILE
)

print("Columns:")
print(prices.columns.tolist())

# ====================================================
# AUTO-DETECT COLUMN NAMES
# ====================================================

date_col = None
symbol_col = None
close_col = None

for col in prices.columns:

    c = col.lower()

    if c in ["date", "trade_date"]:
        date_col = col

    if c in ["symbol", "ticker", "security_id"]:
        symbol_col = col

    if c in [
        "close",
        "adj_close",
        "adjusted_close",
        "last_close"
    ]:
        close_col = col

print(
    f"Date={date_col} "
    f"Symbol={symbol_col} "
    f"Close={close_col}"
)

assert date_col is not None
assert symbol_col is not None
assert close_col is not None

# ====================================================
# SORT
# ====================================================

prices = prices.sort_values(
    [symbol_col, date_col]
)

# ====================================================
# LOG RETURNS
# ====================================================

prices["Return"] = (

    prices
    .groupby(symbol_col)[close_col]

    .transform(
        lambda x:
        np.log(
            x / x.shift(1)
        )
    )

)

daily_returns = (

    prices[
        [
            date_col,
            symbol_col,
            "Return"
        ]
    ]

    .dropna()

)

daily_returns.columns = [
    "Date",
    "Symbol",
    "Return"
]

# ====================================================
# SAVE
# ====================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

daily_returns.to_parquet(
    OUTPUT_FILE,
    index=False
)

print(
    "\nDaily Returns Shape:",
    daily_returns.shape
)

print(
    daily_returns.head()
)