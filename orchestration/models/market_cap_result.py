from dataclasses import dataclass


@dataclass(slots=True)
class MarketCapResult:
    market_cap: float

    status: str

    source: str

    attempts: int

    error: str | None = None
