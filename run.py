from pathlib import Path
import pandas as pd

ROOT = Path.cwd()

print("ROOT:", ROOT)

beta_file = (
    ROOT
    / "data"
    / "risk"
    / "beta_master.csv"
)

print("FILE:", beta_file)
print("EXISTS:", beta_file.exists())

beta_df = pd.read_csv(beta_file)

print(beta_df.head())

print(beta_df["Beta"].describe())

print(
    "Unique Betas:",
    beta_df["Beta"].nunique()
)