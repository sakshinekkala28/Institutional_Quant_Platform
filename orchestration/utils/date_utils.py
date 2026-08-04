import pandas as pd


def normalize_datetime(
    series: pd.Series,
) -> pd.Series:
    """
    Convert mixed timezone-aware/naive timestamps
    into timezone-naive Asia/Kolkata datetimes.
    """

    series = pd.to_datetime(
        series,
        utc=True,
        errors="coerce",
    )

    return series.dt.tz_convert("Asia/Kolkata").dt.tz_localize(None)
