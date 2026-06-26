"""
====================================================================
Institutional Quant Platform

Confidence Matrix

Author : Institutional Quant Platform

Purpose
-------
Institutional Black-Litterman confidence matrix.

Represents the confidence covariance matrix (Ω)
associated with investor views.

Used By

• InvestorView
• BlackLittermanModel
• BlackLittermanOptimizer

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

import pandas as pd


@dataclass(slots=True)
class ConfidenceMatrix:
    """
    Institutional confidence covariance matrix.
    """

    matrix: np.ndarray

    __hash__ = None

    # =====================================================
    # INITIALIZATION
    # =====================================================

    def __post_init__(

        self

    ) -> None:

        self.matrix = np.asarray(

            self.matrix,

            dtype=np.float64,

        )

        self.validate()

    # =====================================================
    # COLLECTION PROTOCOL
    # =====================================================

    def __len__(

        self

    ) -> int:

        return self.matrix.shape[0]

    def __getitem__(

        self,

        item,

    ):

        return self.matrix[item]

    # =====================================================
    # PROPERTIES
    # =====================================================

    @property
    def shape(

        self

    ) -> tuple[int, int]:

        return self.matrix.shape

    @property
    def dimension(

        self

    ) -> int:

        return self.matrix.shape[0]

    @property
    def diagonal(

        self

    ) -> np.ndarray:

        return np.diag(

            self.matrix

        )

    @property
    def determinant(

        self

    ) -> float:

        return float(

            np.linalg.det(

                self.matrix

            )

        )

    @property
    def inverse(

        self

    ) -> np.ndarray:

        return np.linalg.inv(

            self.matrix

        )

    # =====================================================
    # VALIDATION
    # =====================================================

    def validate(

        self

    ) -> None:

        if self.matrix.ndim != 2:

            raise ValueError(

                "Confidence matrix must be two-dimensional."

            )

        rows, cols = self.matrix.shape

        if rows != cols:

            raise ValueError(

                "Confidence matrix must be square."

            )

        if np.isnan(

            self.matrix

        ).any():

            raise ValueError(

                "Confidence matrix contains NaN."

            )

        if np.isinf(

            self.matrix

        ).any():

            raise ValueError(

                "Confidence matrix contains infinite values."

            )

        if not np.allclose(

            self.matrix,

            self.matrix.T,

        ):

            raise ValueError(

                "Confidence matrix must be symmetric."

            )

    # =====================================================
    # EXPORT
    # =====================================================

    def to_numpy(

        self

    ) -> np.ndarray:

        return self.matrix.copy()

    def to_dataframe(

        self

    ) -> pd.DataFrame:

        return pd.DataFrame(

            self.matrix

        )

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self

    ) -> dict:

        return {

            "Dimension":

                self.dimension,

            "Determinant":

                self.determinant,

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Dimension={self.dimension}"

            f")"

        )

    __str__ = __repr__