import pandas as pd

df = pd.read_parquet(
    "data/risk/factor_expected_returns.parquet"
)

print(
    df["Expected_Return"]
    .describe()
)

print(
    df.sort_values(
        "Expected_Return",
        ascending=False
    )
    .head(20)
)