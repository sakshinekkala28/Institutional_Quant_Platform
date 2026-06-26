"""
====================================================================
Institutional Quant Platform

Equilibrium Returns

Author : Institutional Quant Platform

Purpose
-------
Institutional equilibrium (implied) return vector.

Represents the market-implied equilibrium
returns (Π) used as the prior in the
Black-Litterman model.

Π = δ Σ w_market

Used By

• BlackLittermanModel
• BlackLittermanOptimizer
• MeanVarianceOptimizer

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(slots=True)
class EquilibriumReturns:
    """
    Institutional equilibrium return vector.
    """

    symbols: list[str]

    values: np.ndarray

    risk_aversion: float

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

    # =====================================================
    # VALIDATION
    # =====================================================

    def validate(

        self

    ) -> None:

        if len(

            self.symbols

        ) != len(

            self.values

        ):

            raise ValueError(

                "Symbols and equilibrium returns size mismatch."

            )

        if np.isnan(

            self.values

        ).any():

            raise ValueError(

                "Equilibrium returns contain NaN."

            )

        if np.isinf(

            self.values

        ).any():

            raise ValueError(

                "Equilibrium returns contain infinite values."

            )

        if self.risk_aversion <= 0.0:

            raise ValueError(

                "Risk aversion must be positive."

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

            self.values,

            index=self.symbols,

            name="Equilibrium Return",

        )

    def to_dataframe(

        self

    ) -> pd.DataFrame:

        return pd.DataFrame(

            {

                "Symbol": self.symbols,

                "Equilibrium_Return": self.values,

            }

        )

    def to_dict(

        self

    ) -> dict[str, float]:

        return {

            symbol: float(value)

            for symbol, value

            in zip(

                self.symbols,

                self.values,

                strict=True,

            )

        }

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

            "Risk_Aversion":

                self.risk_aversion,

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

            f"RiskAversion={self.risk_aversion:.2f}"

            f")"

        )

    __str__ = __repr__