"""
======================================================================

Institutional Quant Platform

Rebalance Service

Author
------
Institutional Quant Platform

Purpose
-------
Enterprise Portfolio Rebalancing Service.

Responsibilities
----------------
• Portfolio Comparison
• Trade Generation
• Turnover Analysis
• Transaction Cost Estimation
• Drift Analysis
• Rebalance Validation

======================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from threading import Lock
from threading import RLock

from typing import Any
from typing import Dict
from typing import Optional

import pandas as pd

from core.services.base_service import BaseService


# ============================================================
# Exceptions
# ============================================================

class RebalanceError(Exception):
    """Base rebalance exception."""


class RebalanceProfileNotFound(RebalanceError):
    """Rebalance profile not found."""


# ============================================================
# Rebalance Profile
# ============================================================

@dataclass(slots=True)
class RebalanceProfile:

    name: str

    current_portfolio: str

    target_portfolio: str

    parameters: Dict[str, Any] = field(

        default_factory=dict

    )

    metadata: Dict[str, Any] = field(

        default_factory=dict

    )


# ============================================================
# Rebalance Service
# ============================================================

class RebalanceService(BaseService):
    """
    Enterprise Portfolio Rebalancing Service.
    """

    _instance = None

    _instance_lock = Lock()

    def __new__(

        cls,

        *args,

        **kwargs

    ):

        if cls._instance is None:

            with cls._instance_lock:

                if cls._instance is None:

                    cls._instance = super().__new__(cls)

        return cls._instance

    def __init__(

        self

    ):

        if getattr(

            self,

            "_initialized",

            False

        ):

            return

        super().__init__()

        self._lock = RLock()

        self._profiles: Dict[str, RebalanceProfile] = {}

        self._enabled = True

        self._initialized = True

        self._logger.info(

            "RebalanceService initialized."

        )

    # =====================================================
    # Lifecycle
    # =====================================================

    def enable(

        self

    ):

        self._enabled = True

    def disable(

        self

    ):

        self._enabled = False

    def enabled(

        self

    ):

        return self._enabled

    # =====================================================
    # Registration
    # =====================================================

    def register(

        self,

        name: str,

        current_portfolio: str,

        target_portfolio: str,

        parameters: Optional[Dict[str, Any]] = None,

        metadata: Optional[Dict[str, Any]] = None

    ) -> None:
        """
        Register rebalance profile.
        """

        profile = RebalanceProfile(

            name=name,

            current_portfolio=current_portfolio,

            target_portfolio=target_portfolio,

            parameters=parameters or {},

            metadata=metadata or {}

        )

        with self._lock:

            self._profiles[name] = profile

    # =====================================================
    # Retrieval
    # =====================================================

    def get(

        self,

        name: str

    ) -> RebalanceProfile:

        if name not in self._profiles:

            raise RebalanceProfileNotFound(

                name

            )

        return self._profiles[name]

    # =====================================================
    # BaseService
    # =====================================================

    def run(

        self

    ):

        return self.statistics()
    
    # =====================================================
    # Parameter Management
    # =====================================================

    def update_parameter(

        self,

        profile: str,

        name: str,

        value: Any

    ) -> None:
        """
        Update rebalance parameter.
        """

        self.get(

            profile

        ).parameters[name] = value

    def parameter(

        self,

        profile: str,

        name: str,

        default: Any = None

    ) -> Any:
        """
        Return rebalance parameter.
        """

        return self.get(

            profile

        ).parameters.get(

            name,

            default

        )

    # =====================================================
    # Portfolio Comparison
    # =====================================================

    def compare(

        self,

        current: pd.DataFrame,

        target: pd.DataFrame,

        symbol_column: str = "symbol",

        weight_column: str = "weight"

    ) -> pd.DataFrame:
        """
        Compare current and target portfolios.
        """

        comparison = current.merge(

            target,

            on=symbol_column,

            how="outer",

            suffixes=(

                "_current",

                "_target"

            )

        )

        comparison = comparison.fillna(

            0.0

        )

        comparison["weight_change"] = (

            comparison[

                f"{weight_column}_target"

            ]

            -

            comparison[

                f"{weight_column}_current"

            ]

        )

        return comparison

    # =====================================================
    # Trade Generation
    # =====================================================

    def generate_trades(

        self,

        comparison: pd.DataFrame,

        symbol_column: str = "symbol"

    ) -> pd.DataFrame:
        """
        Generate rebalance trades.
        """

        trades = comparison.copy()

        trades["side"] = trades[

            "weight_change"

        ].apply(

            lambda x:

            "BUY"

            if x > 0

            else

            (

                "SELL"

                if x < 0

                else

                "HOLD"

            )

        )

        trades["trade_weight"] = (

            trades["weight_change"]

            .abs()

        )

        return trades

    # =====================================================
    # Turnover
    # =====================================================

    def turnover(

        self,

        comparison: pd.DataFrame

    ) -> float:
        """
        Portfolio turnover.
        """

        return float(

            comparison[

                "weight_change"

            ]

            .abs()

            .sum()

            / 2.0

        )

    # =====================================================
    # Drift
    # =====================================================

    def drift(

        self,

        comparison: pd.DataFrame

    ) -> float:
        """
        Portfolio drift.
        """

        return float(

            comparison[

                "weight_change"

            ]

            .abs()

            .mean()

        )

    # =====================================================
    # New Positions
    # =====================================================

    def new_positions(

        self,

        comparison: pd.DataFrame

    ) -> pd.DataFrame:
        """
        Positions entering portfolio.
        """

        return comparison.loc[

            (

                comparison[

                    "weight_current"

                ]

                == 0

            )

            &

            (

                comparison[

                    "weight_target"

                ]

                > 0

            )

        ]

    # =====================================================
    # Closed Positions
    # =====================================================

    def closed_positions(

        self,

        comparison: pd.DataFrame

    ) -> pd.DataFrame:
        """
        Positions leaving portfolio.
        """

        return comparison.loc[

            (

                comparison[

                    "weight_current"

                ]

                > 0

            )

            &

            (

                comparison[

                    "weight_target"

                ]

                == 0

            )

        ]

    # =====================================================
    # Updated Positions
    # =====================================================

    def updated_positions(

        self,

        comparison: pd.DataFrame

    ) -> pd.DataFrame:
        """
        Existing positions with
        modified weights.
        """

        return comparison.loc[

            (

                comparison[

                    "weight_current"

                ]

                > 0

            )

            &

            (

                comparison[

                    "weight_target"

                ]

                > 0

            )

            &

            (

                comparison[

                    "weight_change"

                ]

                != 0

            )

        ]

    # =====================================================
    # Validation
    # =====================================================

    def validate(

        self,

        comparison: pd.DataFrame

    ) -> bool:
        """
        Validate rebalance comparison.
        """

        required = [

            "weight_current",

            "weight_target",

            "weight_change"

        ]

        missing = [

            column

            for column

            in required

            if column not in comparison.columns

        ]

        if missing:

            raise RebalanceError(

                f"Missing columns: {missing}"

            )

        return True

    # =====================================================
    # Statistics
    # =====================================================

    def statistics(

        self

    ) -> Dict[str, Any]:
        """
        Rebalance statistics.
        """

        return {

            "profiles":

                len(

                    self._profiles

                ),

            "enabled":

                self._enabled

        }
    
    # =====================================================
    # Transaction Cost
    # =====================================================

    def estimate_transaction_cost(

        self,

        trades: pd.DataFrame,

        cost_bps: float = 20.0,

        trade_weight_column: str = "trade_weight"

    ) -> float:
        """
        Estimate transaction cost in portfolio weight.
        """

        if trade_weight_column not in trades.columns:

            raise RebalanceError(

                f"Missing column '{trade_weight_column}'."

            )

        traded_weight = float(

            trades[trade_weight_column].sum()

        )

        return (

            traded_weight

            * cost_bps

            / 10000.0

        )

    # =====================================================
    # Cash Impact
    # =====================================================

    def cash_impact(

        self,

        trades: pd.DataFrame,

        portfolio_nav: float,

        trade_weight_column: str = "trade_weight",

        side_column: str = "side"

    ) -> Dict[str, float]:
        """
        Calculate cash impact.
        """

        buys = trades.loc[

            trades[side_column] == "BUY",

            trade_weight_column

        ].sum()

        sells = trades.loc[

            trades[side_column] == "SELL",

            trade_weight_column

        ].sum()

        return {

            "buy_value":

                float(

                    buys

                    * portfolio_nav

                ),

            "sell_value":

                float(

                    sells

                    * portfolio_nav

                ),

            "net_cash":

                float(

                    (sells - buys)

                    * portfolio_nav

                )

        }

    # =====================================================
    # Trade Summary
    # =====================================================

    def summary(

        self,

        trades: pd.DataFrame

    ) -> Dict[str, Any]:
        """
        Trade summary.
        """

        buy_count = int(

            (

                trades["side"]

                == "BUY"

            ).sum()

        )

        sell_count = int(

            (

                trades["side"]

                == "SELL"

            ).sum()

        )

        hold_count = int(

            (

                trades["side"]

                == "HOLD"

            ).sum()

        )

        return {

            "total_trades":

                len(trades),

            "buy_orders":

                buy_count,

            "sell_orders":

                sell_count,

            "hold_positions":

                hold_count,

            "turnover":

                self.turnover(

                    trades

                )

        }

    # =====================================================
    # Metadata
    # =====================================================

    def metadata(

        self,

        profile: str

    ) -> Dict[str, Any]:

        return dict(

            self.get(

                profile

            ).metadata

        )

    def update_metadata(

        self,

        profile: str,

        **kwargs

    ) -> None:

        self.get(

            profile

        ).metadata.update(

            kwargs

        )

    # =====================================================
    # Registry
    # =====================================================

    def exists(

        self,

        profile: str

    ) -> bool:

        return profile in self._profiles

    def names(

        self

    ) -> list[str]:

        return sorted(

            self._profiles.keys()

        )

    def remove(

        self,

        profile: str

    ) -> None:

        if profile not in self._profiles:

            raise RebalanceProfileNotFound(

                profile

            )

        del self._profiles[profile]

    def clear(

        self

    ) -> None:

        self._profiles.clear()

    # =====================================================
    # Snapshot
    # =====================================================

    def snapshot(

        self,

        profile: str

    ) -> Dict[str, Any]:
        """
        Rebalance profile snapshot.
        """

        instance = self.get(

            profile

        )

        return {

            "name":

                instance.name,

            "current_portfolio":

                instance.current_portfolio,

            "target_portfolio":

                instance.target_portfolio,

            "parameters":

                dict(

                    instance.parameters

                ),

            "metadata":

                dict(

                    instance.metadata

                )

        }

    # =====================================================
    # Health
    # =====================================================

    def health(

        self

    ) -> Dict[str, Any]:
        """
        Service health.
        """

        return {

            "status":

                "HEALTHY"

                if self._enabled

                else "DISABLED",

            "enabled":

                self._enabled,

            "profiles":

                len(

                    self._profiles

                )

        }

    # =====================================================
    # Lifecycle
    # =====================================================

    def startup(

        self

    ) -> None:

        self.enable()

        self._logger.info(

            "RebalanceService started."

        )

    def shutdown(

        self

    ) -> None:

        self.clear()

        self.disable()

        self._logger.info(

            "RebalanceService shutdown."

        )

    # =====================================================
    # Magic Methods
    # =====================================================

    def __contains__(

        self,

        profile: str

    ) -> bool:

        return self.exists(

            profile

        )

    def __len__(

        self

    ) -> int:

        return len(

            self._profiles

        )

    def __iter__(

        self

    ):

        return iter(

            self._profiles.items()

        )

    def __repr__(

        self

    ) -> str:

        return (

            f"{self.__class__.__name__}"

            f"(profiles={len(self)}, "

            f"enabled={self._enabled})"

        )


# ============================================================
# Global Singleton
# ============================================================

rebalance_service = RebalanceService()