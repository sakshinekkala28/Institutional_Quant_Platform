import pandas as pd

brinson = pd.read_csv(
    "data/performance/brinson_sector_attribution.csv"
)

print(
    brinson["Total_Effect"].describe()
)