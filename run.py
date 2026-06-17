import pandas as pd

security_master = pd.read_csv(
    "data/raw/security_master.csv"
)

print(
    security_master["Sector"].isna().mean() * 100
)
