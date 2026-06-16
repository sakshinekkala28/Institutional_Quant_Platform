import pandas as pd

fc = pd.read_parquet(
    "data/risk/factor_covariance.parquet"
)

print(fc.shape)
print(fc.columns.tolist())