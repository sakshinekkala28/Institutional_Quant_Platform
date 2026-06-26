"""
====================================================================
Institutional Quant Platform

Investor View

Author : Institutional Quant Platform

Purpose
-------
Institutional Black-Litterman investor view.

Represents investor views used to construct
posterior expected returns.

Used By

• BlackLittermanOptimizer
• BlackLittermanModel
• Portfolio Construction

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

import pandas as pd


@dataclass(slots=True)
class InvestorView:
    """
    Institutional investor view.
    """

    symbols: list[str]

    pick_matrix: np.ndarray

    expected_returns: np.ndarray

    confidence: np.ndarray

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

        self.pick_matrix = np.asarray(

            self.pick_matrix,

            dtype=np.float64,

        )

        self.expected_returns = np.asarray(

            self.expected_returns,

            dtype=np.float64,

        )

        self.confidence = np.asarray(

            self.confidence,

            dtype=np.float64,

        )

        self.validate()

    # =====================================================
    # PROPERTIES
    # =====================================================

    @property
    def number_of_assets(

        self

    ) -> int:

        return len(

            self.symbols

        )

    @property
    def number_of_views(

        self

    ) -> int:

        return self.pick_matrix.shape[0]

    # =====================================================
    # VALIDATION
    # =====================================================

    def validate(

        self

    ) -> None:

        if self.pick_matrix.ndim != 2:

            raise ValueError(

                "Pick matrix must be two-dimensional."

            )

        if self.pick_matrix.shape[1] != len(

            self.symbols

        ):

            raise ValueError(

                "Pick matrix dimension mismatch."

            )

        if self.expected_returns.shape[0] != self.number_of_views:

            raise ValueError(

                "Expected returns size mismatch."

            )

        if self.confidence.shape[0] != self.number_of_views:

            raise ValueError(

                "Confidence vector size mismatch."

            )

        if np.isnan(

            self.pick_matrix

        ).any():

            raise ValueError(

                "Pick matrix contains NaN."

            )

        if np.isnan(

            self.expected_returns

        ).any():

            raise ValueError(

                "Expected returns contain NaN."

            )

        if np.isnan(

            self.confidence

        ).any():

            raise ValueError(

                "Confidence contains NaN."

            )

    # =====================================================
    # EXPORT
    # =====================================================

    def to_dataframe(

        self

    ) -> pd.DataFrame:

        return pd.DataFrame(

            self.pick_matrix,

            columns=self.symbols,

        )

    def summary(

        self

    ) -> dict:

        return {

            "Assets":

                self.number_of_assets,

            "Views":

                self.number_of_views,

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Assets={self.number_of_assets}, "

            f"Views={self.number_of_views}"

            f")"

        )

    __str__ = __repr__