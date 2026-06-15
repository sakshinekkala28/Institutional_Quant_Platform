import pandas as pd

df = pd.read_parquet(
    "data/raw/security_price_history.parquet"
)

print(df.columns.tolist())
print(df.shape)
print(df.head())