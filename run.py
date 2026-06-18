import pandas as pd

cov = pd.read_parquet(
    "data/risk/shrinkage_covariance.parquet"
)

print(cov.shape)

print(cov.head())

print(cov.index[:10])

print(cov.columns[:10])