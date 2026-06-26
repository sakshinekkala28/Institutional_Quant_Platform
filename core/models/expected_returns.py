"""
====================================================================
Institutional Quant Platform

Expected Returns

Author : Institutional Quant Platform

Purpose
-------
Institutional expected returns model.

Represents the expected return vector used by
portfolio optimizers.

Used By

• MeanVarianceOptimizer
• MaximumSharpeOptimizer
• BlackLittermanOptimizer
• PortfolioOptimizer
• Risk Engine

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

import pandas as pd


@dataclass(slots=True)
class ExpectedReturns:
    """
    Institutional expected returns vector.
    """

    symbols: list[str]

    values: np.ndarray

    __hash__ = None

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __post_init__(

        self

    ) -> None:

        self.values = np.asarray(

            self.values,

            dtype=np.float64,

        )

        self.validate()

    # =====================================================
    # COLLECTION PROTOCOL
    # =====================================================

    def __len__(

        self

    ) -> int:

        return len(

            self.values

        )

    def __iter__(

        self

    ):

        return iter(

            self.values

        )

    def __contains__(

        self,

        symbol: str,

    ) -> bool:

        return symbol in self.symbols

    def __getitem__(

        self,

        key: int | str,

    ) -> float:

        if isinstance(

            key,

            int,

        ):

            return float(

                self.values[key]

            )

        if isinstance(

            key,

            str,

        ):

            try:

                index = self.symbols.index(

                    key

                )

            except ValueError as exc:

                raise KeyError(

                    f"Unknown symbol '{key}'."

                ) from exc

            return float(

                self.values[index]

            )

        raise TypeError(

            "Key must be int or str."

        )

    # =====================================================
    # PROPERTIES
    # =====================================================

    @property
    def size(

        self

    ) -> int:

        return len(

            self

        )

    @property
    def mean(

        self

    ) -> float:

        return float(

            np.mean(

                self.values

            )

        )

    @property
    def minimum(

        self

    ) -> float:

        return float(

            np.min(

                self.values

            )

        )

    @property
    def maximum(

        self

    ) -> float:

        return float(

            np.max(

                self.values

            )

        )

    @property
    def volatility(

        self

    ) -> float:

        return float(

            np.std(

                self.values,

                ddof=1,

            )

        )

    # =====================================================
    # LOOKUPS
    # =====================================================

    def get(

        self,

        symbol: str,

        default: float | None = None,

    ) -> float | None:

        if symbol not in self:

            return default

        return self[

            symbol

        ]

    def to_dict(

        self

    ) -> dict[str, float]:

        return {

            symbol: float(

                value

            )

            for symbol, value

            in zip(

                self.symbols,

                self.values,

                strict=True,

            )

        }

    # =====================================================
    # VALIDATION
    # =====================================================

    def validate(

        self

    ) -> None:

        if len(

            self.symbols

        ) == 0:

            raise ValueError(

                "Expected returns cannot be empty."

            )

        if len(

            self.symbols

        ) != len(

            self.values

        ):

            raise ValueError(

                "Symbols and expected returns size mismatch."

            )

        if np.isnan(

            self.values

        ).any():

            raise ValueError(

                "Expected returns contain NaN."

            )

        if np.isinf(

            self.values

        ).any():

            raise ValueError(

                "Expected returns contain infinite values."

            )

    # =====================================================
    # EXPORT
    # =====================================================

    def to_numpy(

        self

    ) -> np.ndarray:

        return self.values.copy()

    def to_series(

        self

    ) -> pd.Series:

        return pd.Series(

            data=self.values,

            index=self.symbols,

            name="Expected Return",

        )

    def to_dataframe(

        self

    ) -> pd.DataFrame:

        return pd.DataFrame(

            {

                "Symbol": self.symbols,

                "Expected_Return": self.values,

            }

        )

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self

    ) -> dict:

        return {

            "Assets":

                self.size,

            "Mean":

                self.mean,

            "Minimum":

                self.minimum,

            "Maximum":

                self.maximum,

            "Volatility":

                self.volatility,

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Assets={self.size}, "

            f"Mean={self.mean:.4%}"

            f")"

        )

    __str__ = __repr__