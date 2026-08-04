from enum import Enum


class MarketCapStatus(str, Enum):
    SUCCESS = "SUCCESS"

    NO_MARKET_CAP = "NO_MARKET_CAP"

    RATE_LIMIT = "RATE_LIMIT"

    NETWORK_ERROR = "NETWORK_ERROR"

    UNKNOWN = "UNKNOWN"
