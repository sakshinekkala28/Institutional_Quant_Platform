# ==========================================================
# TYPES
# Domain Models
# ==========================================================

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from typing import Optional


# ==========================================================
# SIGNAL MODEL
# ==========================================================

@dataclass(slots=True)
class Signal:

    symbol: str

    signal_score: float

    momentum_score: float

    quality_score: float

    value_score: float

    rank: int

    timestamp: datetime


# ==========================================================
# ALPHA MODEL
# ==========================================================

@dataclass(slots=True)
class AlphaModelResult:

    model_name: str

    model_version: str

    universe_size: int

    selected_stocks: int

    generated_at: datetime

# ==========================================================
# PORTFOLIO POSITION
# ==========================================================

@dataclass(slots=True)
class PortfolioPosition:

    symbol: str

    weight: float

    sector: str

    market_cap: float

    beta: float

    volatility: float


# ==========================================================
# PORTFOLIO
# ==========================================================

@dataclass(slots=True)
class Portfolio:

    portfolio_id: str

    holdings: int

    total_weight: float

    rebalance_date: datetime

    model_version: str

# ==========================================================
# TRADE
# ==========================================================

@dataclass(slots=True)
class Trade:

    symbol: str

    action: str

    current_weight: float

    target_weight: float

    trade_weight: float


# ==========================================================
# EXECUTION REPORT
# ==========================================================

@dataclass(slots=True)
class ExecutionReport:

    total_trades: int

    turnover: float

    average_slippage_bps: float

    market_impact_bps: float

    execution_timestamp: datetime

# ==========================================================
# RISK REPORT
# ==========================================================

@dataclass(slots=True)
class RiskReport:

    portfolio_beta: float

    tracking_error: float

    portfolio_volatility: float

    hhi: float

    effective_holdings: float


# ==========================================================
# GOVERNANCE REPORT
# ==========================================================

@dataclass(slots=True)
class GovernanceReport:

    approved: bool

    position_limit_pass: bool

    sector_limit_pass: bool

    turnover_pass: bool

    concentration_pass: bool

    review_timestamp: datetime


# ==========================================================
# PLATFORM RUN
# ==========================================================

@dataclass(slots=True)
class PlatformRun:

    run_id: str

    model_version: str

    config_version: str

    start_time: datetime

    end_time: Optional[datetime]

    status: str