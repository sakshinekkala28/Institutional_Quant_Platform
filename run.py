import pandas as pd

df = pd.read_csv(
    "data/backtests/backtest_results.csv"
)

print(df.columns.tolist())
print(df.head())