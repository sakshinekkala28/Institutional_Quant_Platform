from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[2]

PRICE_FILE = ROOT / "data/raw/security_price_history.parquet"
OUTPUT_FILE = ROOT / "data/risk/stock_volatility.csv"

print("Building Volatility Model...")

prices = pd.read_parquet(PRICE_FILE)

print("\nPRICE FILE SHAPE")
print(prices.shape)

print("\nCOLUMNS")
print(prices.columns.tolist()[:20])

print("\nHEAD")
print(prices.head())

results = []

for symbol, df in prices.groupby("Symbol"):

    try:

        df = df.sort_values("Date")

        returns = df["Daily_Return"].dropna()

        if len(returns) < 100:
            continue

        vol_252 = (
            returns.std()
            * np.sqrt(252)
        )

        vol_252 = np.clip(
            vol_252,
            0.05,
            3.00
        )

        atr_pct = (
            returns.abs()
            .rolling(14)
            .mean()
            .iloc[-1]
        )

        results.append(
            {
                "Symbol": symbol.replace(".NS", ""),
                "Volatility_252D": round(vol_252, 4),
                "ATR_Pct": round(atr_pct, 4)
            }
        )

    except Exception:
        continue

vol_df = pd.DataFrame(results)

print("\nVOLATILITY SUMMARY")
print(vol_df["Volatility_252D"].describe())

print("\nATR SUMMARY")
print(vol_df["ATR_Pct"].describe())

print("\nTotal Symbols")
print(len(vol_df))

vol_df.to_csv(
    OUTPUT_FILE,
    index=False
)

print(f"Saved {len(vol_df)} symbols")
print(OUTPUT_FILE)