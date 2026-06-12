import pandas as pd

liq = pd.read_csv(
    "data/liquidity/liquidity_master.csv"
)

print(liq.columns.tolist())