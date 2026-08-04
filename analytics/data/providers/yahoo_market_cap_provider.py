"""
=========================================================
YAHOO MARKET CAP PROVIDER
=========================================================
"""

import time

import yfinance as yf

from config.thresholds import MAX_RETRIES
from orchestration.models.market_cap_result import MarketCapResult
from orchestration.models.market_cap_status import MarketCapStatus

# =========================================================
# FETCH MARKET CAP
# =========================================================


def fetch_market_cap(
    symbol: str,
) -> MarketCapResult:
    """
    Fetch Market Cap
    from Yahoo Finance.
    """

    yahoo_symbol = f"{symbol}.NS"

    for attempt in range(MAX_RETRIES):
        try:
            ticker = yf.Ticker(
                yahoo_symbol,
            )

            # -------------------------------------------------
            # FAST INFO
            # -------------------------------------------------

            try:
                market_cap = ticker.fast_info.get(
                    "marketCap",
                    0,
                )

                if market_cap and market_cap > 0:
                    return MarketCapResult(
                        market_cap=float(market_cap),
                        status=MarketCapStatus.SUCCESS,
                        source="Yahoo",
                        attempts=attempt + 1,
                        error=None,
                    )

            except Exception:
                pass

            # -------------------------------------------------
            # INFO
            # -------------------------------------------------

            try:
                info = ticker.get_info()

                market_cap = info.get(
                    "marketCap",
                    0,
                )

                if market_cap and market_cap > 0:
                    return float(
                        market_cap,
                    )

            except Exception:
                pass

        except Exception as exc:
            error = str(exc).lower()

            if "429" in error or "rate limit" in error or "too many requests" in error:
                wait = 15 * (attempt + 1)

                print(f"⚠️ Rate Limit : {symbol}")

                print(f"Sleeping {wait}s")

                time.sleep(
                    wait,
                )

            else:
                print(f"❌ {symbol}: {exc}")

                time.sleep(
                    2,
                )

    return MarketCapResult(
        market_cap=0.0,
        status=MarketCapStatus.NO_MARKET_CAP,
        source="Yahoo",
        attempts=MAX_RETRIES,
        error="No market cap returned.",
    )
