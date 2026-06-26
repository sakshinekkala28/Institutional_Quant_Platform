"""
====================================================================
Institutional Quant Platform

Optimization Result

Author : Institutional Quant Platform

Purpose
-------
Institutional optimization result.

Represents the mathematical output of an
optimization algorithm.

Used By

• Optimization Service
• Portfolio Builder
• Optimizer Factory
• Reporting Layer

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

import pandas as pd


@dataclass(slots=True)
class OptimizationResult:
    """
    Institutional optimization result.
    """

    symbols: list[str]

    weights: np.ndarray

    objective_value: float = 0.0

    expected_return: float = 0.0

    expected_risk: float = 0.0

    expected_sharpe: float = 0.0

    turnover: float = 0.0

    iterations: int = 0

    success: bool = True

    message: str = ""

    metadata: dict = field(

        default_factory=dict

    )

    __hash__ = None

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __post_init__(

        self

    ) -> None:

        self.weights = np.asarray(

            self.weights,

            dtype=np.float64,

        )

        self.validate()

    # =====================================================
    # COLLECTION
    # =====================================================

    def __len__(

        self

    ) -> int:

        return len(

            self.weights

        )

    def __iter__(

        self

    ):

        return iter(

            self.weights

        )

    def __getitem__(

        self,

        key: int | str,

    ) -> float:

        if isinstance(

            key,

            int,

        ):

            return float(

                self.weights[key]

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

                self.weights[index]

            )

        raise TypeError(

            "Key must be int or str."

        )

    # =====================================================
    # PROPERTIES
    # =====================================================

    @property
    def holdings(

        self

    ) -> int:

        return len(

            self

        )

    @property
    def fully_invested(

        self

    ) -> bool:

        return abs(

            self.weights.sum()

            - 1.0

        ) < 1e-6

    # =====================================================
    # VALIDATION
    # =====================================================

    def validate(

        self

    ) -> None:

        if len(

            self.symbols

        ) != len(

            self.weights

        ):

            raise ValueError(

                "Symbols and weights size mismatch."

            )

        if np.isnan(

            self.weights

        ).any():

            raise ValueError(

                "Weights contain NaN."

            )

        if np.isinf(

            self.weights

        ).any():

            raise ValueError(

                "Weights contain infinite values."

            )

    # =====================================================
    # EXPORT
    # =====================================================

    def to_dict(

        self

    ) -> dict[str, float]:

        return {

            symbol: float(

                weight

            )

            for symbol, weight

            in zip(

                self.symbols,

                self.weights,

                strict=True,

            )

        }

    def to_series(

        self

    ) -> pd.Series:

        return pd.Series(

            self.weights,

            index=self.symbols,

            name="Weight",

        )

    def to_dataframe(

        self

    ) -> pd.DataFrame:

        return pd.DataFrame(

            {

                "Symbol": self.symbols,

                "Weight": self.weights,

            }

        )

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self

    ) -> dict:

        return {

            "Holdings":

                self.holdings,

            "Expected_Return":

                self.expected_return,

            "Expected_Risk":

                self.expected_risk,

            "Expected_Sharpe":

                self.expected_sharpe,

            "Objective":

                self.objective_value,

            "Success":

                self.success,

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Holdings={self.holdings}, "

            f"Success={self.success}"

            f")"

        )

    __str__ = __repr__