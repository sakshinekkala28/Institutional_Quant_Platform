import pandas as pd

df = pd.read_parquet(
    "data/risk/factor_covariance.parquet"
)

print(df.shape)

print(df.columns.tolist())

print(df.index.tolist())