import pandas as pd

blotter = pd.read_csv(
    "data/execution/trade_blotter.csv"
)

prices = pd.read_parquet(
    "data/raw/security_price_history.parquet"
)

print("\nTrade Blotter Sample")
print(blotter["Symbol"].head(10).tolist())

print("\nPrice File Sample")
print(prices["Symbol"].head(10).tolist())