import pandas as pd

df = pd.read_csv(
    "data/raw/updated_stocks.csv"
)

print(
    "CIGNITITEC" in
    df["Symbol"].values
)