"""
=========================================================
NEWS ALPHA ENGINE
=========================================================

Output:
data/processed/news_rankings.csv
=========================================================
"""

from pathlib import Path

import feedparser
import pandas as pd

from textblob import TextBlob

# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

INPUT_FILE = (
    ROOT
    / "data"
    / "processed"
    / "cross_sectional_rankings.csv"
)

OUTPUT_FILE = (
    ROOT
    / "data"
    / "processed"
    / "news_rankings.csv"
)

# =========================================================
# CONFIG
# =========================================================

MAX_NEWS_PER_STOCK = 10

# =========================================================
# LOAD
# =========================================================

print("\n📥 Loading Rankings...")

df = pd.read_csv(
    INPUT_FILE
)

# =========================================================
# RSS FETCH
# =========================================================

def get_news_sentiment(symbol):

    try:

        rss_url = (
            f"https://news.google.com/rss/search"
            f"?q={symbol}+stock"
        )

        feed = feedparser.parse(
            rss_url
        )

        entries = feed.entries[
            :MAX_NEWS_PER_STOCK
        ]

        if len(entries) == 0:

            return (
                50,
                0,
                "LOW",
            )

        sentiments = []

        risk_flag = "LOW"

        risk_words = [
            "fraud",
            "downgrade",
            "default",
            "bankruptcy",
            "investigation",
            "sebi",
            "penalty",
            "raid",
        ]

        for item in entries:

            title = (
                item.title
                if hasattr(item, "title")
                else ""
            )

            polarity = (
                TextBlob(title)
                .sentiment
                .polarity
            )

            sentiments.append(
                polarity
            )

            lower = title.lower()

            if any(
                x in lower
                for x in risk_words
            ):
                risk_flag = "HIGH"

        avg_sentiment = (
            sum(sentiments)
            /
            len(sentiments)
        )

        news_alpha = (
            (avg_sentiment + 1)
            * 50
        )

        return (
            round(news_alpha, 2),
            len(entries),
            risk_flag,
        )

    except Exception:

        return (
            50,
            0,
            "LOW",
        )

# =========================================================
# PROCESS
# =========================================================

print(
    "\n📰 Building News Alpha..."
)

news_alpha = []
headline_count = []
event_risk = []

total = len(df)

for idx, symbol in enumerate(
    df["Symbol"],
    start=1,
):

    alpha, count, risk = (
        get_news_sentiment(
            symbol
        )
    )

    news_alpha.append(
        alpha
    )

    headline_count.append(
        count
    )

    event_risk.append(
        risk
    )

    if idx % 50 == 0:

        print(
            f"{idx:,}/{total:,}"
        )

# =========================================================
# ADD
# =========================================================

df["NEWS_ALPHA"] = (
    news_alpha
)

df["HEADLINE_COUNT"] = (
    headline_count
)

df["EVENT_RISK"] = (
    event_risk
)

# =========================================================
# NEWS SCORE
# =========================================================

df["NEWS_SCORE"] = (
    df["NEWS_ALPHA"]
    *
    (
        1
        +
        (
            df["HEADLINE_COUNT"]
            / 100
        )
    )
)

# =========================================================
# SORT
# =========================================================

df = df.sort_values(
    "NEWS_SCORE",
    ascending=False,
)

df["NEWS_RANK"] = range(
    1,
    len(df) + 1,
)

# =========================================================
# ROUND
# =========================================================

df["NEWS_SCORE"] = (
    df["NEWS_SCORE"]
    .round(2)
)

df["NEWS_ALPHA"] = (
    df["NEWS_ALPHA"]
    .round(2)
)

# =========================================================
# SAVE
# =========================================================

OUTPUT_FILE.parent.mkdir(
    parents=True,
    exist_ok=True,
)

df.to_csv(
    OUTPUT_FILE,
    index=False,
)

# =========================================================
# REPORT
# =========================================================

print("\n" + "=" * 70)

print(
    "🏁 NEWS ENGINE COMPLETE"
)

print("=" * 70)

print(
    f"Stocks Processed : {len(df):,}"
)

print(
    f"\nSaved:\n{OUTPUT_FILE}"
)

print("=" * 70)