from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[2]

PRICE_FILE = ROOT / "data/raw/security_price_history.parquet"
BENCHMARK_FILE = ROOT / "data/raw/benchmark_prices.csv"

OUTPUT_FILE = ROOT / "data/risk/stock_beta.csv"

print("Building Beta Model...")

# =====================================================
# LOAD DATA
# =====================================================

prices = pd.read_parquet(PRICE_FILE)

benchmark = pd.read_csv(
    BENCHMARK_FILE,
    parse_dates=["Date"]
)

benchmark["Date"] = pd.to_datetime(
    benchmark["Date"]
)

benchmark = benchmark.sort_values("Date")

# Find usable close column
if benchmark["Close"].notna().sum() > 100:
    close_col = "Close"
else:
    close_col = "Close.1"

benchmark["Benchmark_Return"] = (
    benchmark[close_col]
    .pct_change()
)

benchmark = benchmark[
    ["Date", "Benchmark_Return"]
].dropna()

results = []

# =====================================================
# BETA CALCULATION
# =====================================================

for symbol in prices["Symbol"].unique():

    try:

        stock = (
            prices[
                prices["Symbol"] == symbol
            ][["Date", "Close"]]
            .copy()
        )

        stock["Date"] = pd.to_datetime(
            stock["Date"]
        )

        stock = stock.sort_values("Date")

        stock["Stock_Return"] = (
            stock["Close"]
            .pct_change()
        )

        merged = stock.merge(
            benchmark[
                ["Date", "Benchmark_Return"]
            ],
            on="Date",
            how="inner"
        )

        merged = merged.dropna()

        if len(merged) < 252:
            continue

        stock_ret = merged["Stock_Return"]
        bench_ret = merged["Benchmark_Return"]

        covariance = np.cov(
            stock_ret,
            bench_ret
        )[0, 1]

        variance = np.var(
            bench_ret
        )

        if variance == 0:
            beta = 1.0
        else:
            beta = covariance / variance

        beta = np.clip(
            beta,
            0.25,
            3.00
        )

        results.append(
            {
                "Symbol": symbol,
                "Beta": round(beta, 4)
            }
        )

    except Exception:
        pass

# =====================================================
# SAVE
# =====================================================

beta_df = pd.DataFrame(results)

print("\nBETA SUMMARY")

print(
    beta_df["Beta"]
    .describe()
)

print(
    "\nTotal Symbols"
)

print(
    len(beta_df)
)

beta_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print(
    f"Saved {len(beta_df)} symbols"
)

print(OUTPUT_FILE)