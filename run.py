import pandas as pd

df = pd.read_csv(
    "data/factors/factor_snapshot_master.csv"
)

print(df.columns.tolist())