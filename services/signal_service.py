"""
======================================================================

Institutional Quant Platform

Signal Service

Author
------
Institutional Quant Platform

Purpose
-------
Enterprise Signal Engine.

Responsibilities
----------------
• Alpha Signals
• Technical Signals
• Fundamental Signals
• Composite Ranking
• Universe Selection

======================================================================
"""

from __future__ import annotations

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

class SignalError(Exception):
    """Base signal exception."""


class SignalNotFound(SignalError):
    """Signal not available."""


# ============================================================
# Signal Service
# ============================================================

class SignalService(BaseService):

    """
    Institutional Signal Engine.
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

    def __init__(self):

        if getattr(

            self,

            "_initialized",

            False

        ):

            return

        super().__init__()

        self._lock = RLock()

        self._signals: Dict[str, pd.DataFrame] = {}

        self._metadata: Dict[str, Dict[str, Any]] = {}

        self._enabled = True

        self._initialized = True

        self._logger.info(

            "SignalService initialized."

        )

    # =====================================================
    # Lifecycle
    # =====================================================

    def enable(self):

        self._enabled = True

    def disable(self):

        self._enabled = False

    def enabled(self):

        return self._enabled

    # =====================================================
    # Registration
    # =====================================================

    def register_signal(

        self,

        name: str,

        dataframe: pd.DataFrame,

        metadata: Optional[Dict[str, Any]] = None

    ) -> None:
        """
        Register signal dataset.
        """

        with self._lock:

            self._signals[name] = dataframe

            self._metadata[name] = metadata or {}

            self._logger.info(

                "Registered signal '%s' (%d rows)",

                name,

                len(dataframe)

            )

    # =====================================================
    # Retrieval
    # =====================================================

    def get_signal(

        self,

        name: str

    ) -> pd.DataFrame:

        if name not in self._signals:

            raise SignalNotFound(

                name

            )

        return self._signals[name]

    # =====================================================
    # Standard Signals
    # =====================================================

    def alpha(self):

        return self.get_signal(

            "alpha"

        )

    def momentum(self):

        return self.get_signal(

            "momentum"

        )

    def quality(self):

        return self.get_signal(

            "quality"

        )

    def value(self):

        return self.get_signal(

            "value"

        )

    def growth(self):

        return self.get_signal(

            "growth"

        )

    def composite(self):

        return self.get_signal(

            "composite"

        )

    # =====================================================
    # BaseService
    # =====================================================

    def run(self):

        return self.statistics()
    
    # =====================================================
    # Ranking
    # =====================================================

    def rank(

        self,

        signal: str,

        score_column: str,

        ascending: bool = False,

        method: str = "dense"

    ) -> pd.DataFrame:
        """
        Rank securities by signal score.
        """

        dataframe = self.get_signal(

            signal

        ).copy()

        if score_column not in dataframe.columns:

            raise SignalError(

                f"Missing column '{score_column}'."

            )

        dataframe["rank"] = (

            dataframe[score_column]

            .rank(

                ascending=ascending,

                method=method

            )

            .astype(int)

        )

        return dataframe.sort_values(

            "rank"

        )

    # =====================================================
    # Top / Bottom Selection
    # =====================================================

    def top(

        self,

        signal: str,

        score_column: str,

        n: int = 25

    ) -> pd.DataFrame:
        """
        Top ranked securities.
        """

        ranked = self.rank(

            signal,

            score_column,

            ascending=False

        )

        return ranked.head(

            n

        )

    def bottom(

        self,

        signal: str,

        score_column: str,

        n: int = 25

    ) -> pd.DataFrame:
        """
        Lowest ranked securities.
        """

        ranked = self.rank(

            signal,

            score_column,

            ascending=True

        )

        return ranked.head(

            n

        )

    # =====================================================
    # Universe Filter
    # =====================================================

    def filter_universe(

        self,

        signal: str,

        **filters

    ) -> pd.DataFrame:
        """
        Filter signal universe.
        """

        dataframe = self.get_signal(

            signal

        )

        result = dataframe

        for column, value in filters.items():

            if column not in dataframe.columns:

                raise SignalError(

                    column

                )

            result = result.loc[

                result[column] == value

            ]

        return result

    # =====================================================
    # Normalization
    # =====================================================

    def zscore(

        self,

        signal: str,

        score_column: str,

        output_column: str = "zscore"

    ) -> pd.DataFrame:
        """
        Z-score normalization.
        """

        dataframe = self.get_signal(

            signal

        ).copy()

        mean = dataframe[score_column].mean()

        std = dataframe[score_column].std()

        if std == 0:

            dataframe[output_column] = 0.0

        else:

            dataframe[output_column] = (

                dataframe[score_column]

                - mean

            ) / std

        return dataframe

    # =====================================================
    # Percentile Rank
    # =====================================================

    def percentile_rank(

        self,

        signal: str,

        score_column: str,

        output_column: str = "percentile"

    ) -> pd.DataFrame:
        """
        Percentile ranking.
        """

        dataframe = self.get_signal(

            signal

        ).copy()

        dataframe[output_column] = (

            dataframe[score_column]

            .rank(

                pct=True

            )

        )

        return dataframe

    # =====================================================
    # Composite Score
    # =====================================================

    def composite_score(

        self,

        dataframe: pd.DataFrame,

        weights: Dict[str, float],

        output_column: str = "composite_score"

    ) -> pd.DataFrame:
        """
        Weighted composite score.
        """

        result = dataframe.copy()

        result[output_column] = 0.0

        total_weight = sum(

            weights.values()

        )

        if total_weight <= 0:

            raise SignalError(

                "Weights must sum to a positive value."

            )

        for column, weight in weights.items():

            if column not in result.columns:

                raise SignalError(

                    f"Missing column '{column}'."

                )

            result[output_column] += (

                result[column]

                *

                weight

            )

        result[output_column] /= total_weight

        return result

    # =====================================================
    # Validation
    # =====================================================

    def validate(

        self,

        signal: str,

        required_columns: list[str]

    ) -> bool:
        """
        Validate signal schema.
        """

        dataframe = self.get_signal(

            signal

        )

        missing = [

            column

            for column

            in required_columns

            if column not in dataframe.columns

        ]

        if missing:

            raise SignalError(

                f"Missing columns: {missing}"

            )

        if dataframe.empty:

            raise SignalError(

                "Signal dataset is empty."

            )

        return True

    # =====================================================
    # Statistics
    # =====================================================

    def statistics(

        self

    ) -> Dict[str, Any]:
        """
        Signal statistics.
        """

        return {

            "signals":

                len(self._signals),

            "rows":

                sum(

                    len(df)

                    for df

                    in self._signals.values()

                ),

            "registered":

                sorted(

                    self._signals.keys()

                )

        }
    
    # =====================================================
    # Sector Neutral Ranking
    # =====================================================

    def sector_neutral_rank(

        self,

        signal: str,

        sector_column: str,

        score_column: str,

        output_column: str = "sector_rank",

        ascending: bool = False

    ) -> pd.DataFrame:
        """
        Rank securities within each sector.
        """

        dataframe = self.get_signal(

            signal

        ).copy()

        self.validate(

            signal,

            [

                sector_column,

                score_column

            ]

        )

        dataframe[output_column] = (

            dataframe.groupby(

                sector_column

            )[score_column]

            .rank(

                ascending=ascending,

                method="dense"

            )

            .astype(int)

        )

        return dataframe

    # =====================================================
    # Winsorization
    # =====================================================

    def winsorize(

        self,

        signal: str,

        column: str,

        lower: float = 0.01,

        upper: float = 0.99

    ) -> pd.DataFrame:
        """
        Winsorize extreme values.
        """

        dataframe = self.get_signal(

            signal

        ).copy()

        self.validate(

            signal,

            [column]

        )

        lower_bound = dataframe[column].quantile(

            lower

        )

        upper_bound = dataframe[column].quantile(

            upper

        )

        dataframe[column] = dataframe[column].clip(

            lower_bound,

            upper_bound

        )

        return dataframe

    # =====================================================
    # Standardization
    # =====================================================

    def standardize(

        self,

        signal: str,

        column: str,

        output_column: str = "standardized"

    ) -> pd.DataFrame:
        """
        Min-Max normalization.
        """

        dataframe = self.get_signal(

            signal

        ).copy()

        minimum = dataframe[column].min()

        maximum = dataframe[column].max()

        if minimum == maximum:

            dataframe[output_column] = 0.0

        else:

            dataframe[output_column] = (

                dataframe[column]

                - minimum

            ) / (

                maximum

                - minimum

            )

        return dataframe

    # =====================================================
    # Merge Signals
    # =====================================================

    def merge(

        self,

        left_signal: str,

        right_signal: str,

        on: str = "symbol",

        how: str = "inner"

    ) -> pd.DataFrame:
        """
        Merge two registered signals.
        """

        left = self.get_signal(

            left_signal

        )

        right = self.get_signal(

            right_signal

        )

        return left.merge(

            right,

            on=on,

            how=how

        )

    # =====================================================
    # Signal Metadata
    # =====================================================

    def metadata(

        self,

        signal: str

    ) -> Dict[str, Any]:

        return dict(

            self._metadata.get(

                signal,

                {}

            )

        )

    def signal_names(

        self

    ) -> list[str]:

        return sorted(

            self._signals.keys()

        )

    def exists(

        self,

        signal: str

    ) -> bool:

        return signal in self._signals

    # =====================================================
    # Maintenance
    # =====================================================

    def remove_signal(

        self,

        signal: str

    ) -> None:

        if signal not in self._signals:

            raise SignalNotFound(

                signal

            )

        del self._signals[signal]

        self._metadata.pop(

            signal,

            None

        )

    def clear(

        self

    ) -> None:

        self._signals.clear()

        self._metadata.clear()

    # =====================================================
    # Health
    # =====================================================

    def health(

        self

    ) -> Dict[str, Any]:

        healthy = all(

            not dataframe.empty

            for dataframe

            in self._signals.values()

        )

        return {

            "status":

                "HEALTHY"

                if healthy

                else "WARNING",

            "enabled":

                self._enabled,

            "signals":

                len(

                    self._signals

                )

        }

    # =====================================================
    # Snapshot
    # =====================================================

    def snapshot(

        self

    ) -> Dict[str, Any]:

        return {

            "registered_signals":

                self.signal_names(),

            "statistics":

                self.statistics(),

            "metadata":

                dict(

                    self._metadata

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

            "SignalService started."

        )

    def shutdown(

        self

    ) -> None:

        self.clear()

        self.disable()

        self._logger.info(

            "SignalService shutdown."

        )

    # =====================================================
    # Magic Methods
    # =====================================================

    def __contains__(

        self,

        signal: str

    ) -> bool:

        return self.exists(

            signal

        )

    def __len__(

        self

    ) -> int:

        return len(

            self._signals

        )

    def __iter__(

        self

    ):

        return iter(

            self._signals.items()

        )

    def __repr__(

        self

    ) -> str:

        return (

            f"{self.__class__.__name__}"

            f"(signals={len(self)}, "

            f"enabled={self._enabled})"

        )


# ============================================================
# Global Singleton
# ============================================================

signal_service = SignalService()