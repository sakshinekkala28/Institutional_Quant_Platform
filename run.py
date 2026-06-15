import pandas as pd

df = pd.read_parquet(
    "data/raw/security_price_history.parquet"
)

print(df.dtypes)

print(df["Date"].head())

print(df.columns.tolist())