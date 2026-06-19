from pathlib import Path
import pandas as pd
import numpy as np
import yfinance as yf
import time
from datetime import datetime

# =====================================================
# PATHS
# =====================================================

ROOT_DIR = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    ROOT_DIR
    / "data"
    / "raw"
    / "security_master.csv"
)

OUTPUT_FILE = (
    ROOT_DIR
    / "data"
    / "factors"
    / "fundamental_factor_master.csv"
)

# =====================================================
# SETTINGS
# =====================================================

BATCH_SIZE = 25
SLEEP_BETWEEN_BATCHES = 5

# =====================================================
# LOAD UNIVERSE
# =====================================================

print("\nBuilding Fundamental Factor Master...")

universe = pd.read_csv(INPUT_FILE)

required_cols = [
    "Symbol",
    "Yahoo_Symbol"
]

for col in required_cols:

    if col not in universe.columns:

        raise ValueError(
            f"Missing column: {col}"
        )

# =====================================================
# HELPERS
# =====================================================

def safe_float(value):

    try:

        if value is None:

            return np.nan

        return float(value)

    except:

        return np.nan


def get_growth(current, previous):

    try:

        if previous in [0, None]:

            return np.nan

        return (
            (current - previous)
            /
            abs(previous)
        )

    except:

        return np.nan


# =====================================================
# FACTOR COLLECTION
# =====================================================

results = []

symbols = universe["Yahoo_Symbol"].dropna().unique()

total = len(symbols)

print(
    f"Universe Size: {total}"
)

for batch_start in range(
    0,
    total,
    BATCH_SIZE
):

    batch = symbols[
        batch_start:
        batch_start + BATCH_SIZE
    ]

    print(
        f"\nBatch "
        f"{batch_start + 1}"
        f" - "
        f"{min(batch_start + BATCH_SIZE, total)}"
    )

    for ticker_symbol in batch:

        try:

            ticker = yf.Ticker(
                ticker_symbol
            )

            info = ticker.info

            financials = (
                ticker.financials
            )

            balance_sheet = (
                ticker.balance_sheet
            )

            symbol_row = universe[
                universe[
                    "Yahoo_Symbol"
                ]
                ==
                ticker_symbol
            ]

            symbol = (
                symbol_row.iloc[0]
                ["Symbol"]
            )

            roe = safe_float(
                info.get(
                    "returnOnEquity"
                )
            )

            pb = safe_float(
                info.get(
                    "priceToBook"
                )
            )

            pe = safe_float(
                info.get(
                    "trailingPE"
                )
            )

            market_cap = safe_float(
                info.get(
                    "marketCap"
                )
            )

            debt_to_equity = safe_float(
                info.get(
                    "debtToEquity"
                )
            )

            revenue_growth = safe_float(
                info.get(
                    "revenueGrowth"
                )
            )

            earnings_growth = safe_float(
                info.get(
                    "earningsGrowth"
                )
            )

            operating_margin = safe_float(
                info.get(
                    "operatingMargins"
                )
            )

            net_margin = safe_float(
                info.get(
                    "profitMargins"
                )
            )

            roce = np.nan

            try:

                ebit = safe_float(
                    info.get(
                        "ebitda"
                    )
                )

                total_assets = safe_float(
                    balance_sheet.loc[
                        "Total Assets"
                    ].iloc[0]
                )

                current_liabilities = safe_float(
                    balance_sheet.loc[
                        "Current Liabilities"
                    ].iloc[0]
                )

                capital_employed = (
                    total_assets
                    -
                    current_liabilities
                )

                if (
                    capital_employed
                    and
                    capital_employed > 0
                ):

                    roce = (
                        ebit
                        /
                        capital_employed
                    )

            except:

                pass

            profit_growth = np.nan

            try:

                net_income = (
                    financials.loc[
                        "Net Income"
                    ]
                )

                if len(
                    net_income
                ) >= 2:

                    profit_growth = (
                        get_growth(
                            net_income.iloc[0],
                            net_income.iloc[1]
                        )
                    )

            except:

                pass

            results.append({

                "Symbol":
                symbol,

                "Yahoo_Symbol":
                ticker_symbol,

                "PE":
                pe,

                "PB":
                pb,

                "ROE":
                roe,

                "ROCE":
                roce,

                "Debt_To_Equity":
                debt_to_equity,

                "Revenue_Growth":
                revenue_growth,

                "EPS_Growth":
                earnings_growth,

                "Profit_Growth":
                profit_growth,

                "Operating_Margin":
                operating_margin,

                "Net_Margin":
                net_margin,

                "Market_Cap":
                market_cap,

                "Factor_Date":
                datetime.today()
                .strftime(
                    "%Y-%m-%d"
                )

            })

        except Exception as e:

            print(
                f"Failed: "
                f"{ticker_symbol}"
            )

            continue

    time.sleep(
        SLEEP_BETWEEN_BATCHES
    )

# =====================================================
# BUILD DATAFRAME
# =====================================================

factor_df = pd.DataFrame(
    results
)

# =====================================================
# CLEANING
# =====================================================

numeric_cols = [

    "PE",
    "PB",
    "ROE",
    "ROCE",
    "Debt_To_Equity",
    "Revenue_Growth",
    "EPS_Growth",
    "Profit_Growth",
    "Operating_Margin",
    "Net_Margin"

]

for col in numeric_cols:

    factor_df[col] = pd.to_numeric(
        factor_df[col],
        errors="coerce"
    )

    factor_df[col] = (
        factor_df[col]
        .replace(
            [np.inf, -np.inf],
            np.nan
        )
    )

# =====================================================
# SAVE
# =====================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

factor_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\nSaved:")
print(OUTPUT_FILE)

print(
    "\nRows:",
    len(factor_df)
)

print(
    "Columns:",
    len(factor_df.columns)
)

print(
    "\nBuild Complete."
)