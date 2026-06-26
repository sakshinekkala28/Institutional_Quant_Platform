"""
====================================================================
Institutional Quant Platform

Covariance Matrix

Author : Institutional Quant Platform

Purpose
-------
Institutional covariance matrix model.

Represents the covariance structure between portfolio assets.

Used By

• Risk Engine
• Optimizer
• Black-Litterman
• HRP
• Mean-Variance Optimization
• Risk Budgeting
• Stress Testing

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(slots=True)
class CovarianceMatrix:
    """
    Institutional covariance matrix.
    """

    assets: list[str]

    matrix: np.ndarray

    __hash__ = None

    def __post_init__(

        self

    ) -> None:

        self.matrix = np.asarray(

            self.matrix,

            dtype=np.float64

        )

        self.validate()

    # =====================================================
    # COLLECTION PROTOCOL
    # =====================================================

    def __len__(

        self

    ) -> int:

        return self.dimension

    def __getitem__(

        self,

        index: int

    ) -> np.ndarray:

        return self.matrix[index]

    def __iter__(

        self

    ):

        return iter(

            self.matrix

        )

    # =====================================================
    # BASIC
    # =====================================================

    @property
    def dimension(

        self

    ) -> int:

        return self.matrix.shape[0]

    @property
    def shape(

        self

    ) -> tuple[int, int]:

        return self.matrix.shape

    @property
    def is_square(

        self

    ) -> bool:

        rows, cols = self.shape

        return rows == cols

    @property
    def is_symmetric(

        self

    ) -> bool:

        return np.allclose(

            self.matrix,

            self.matrix.T

        )

    @property
    def diagonal(

        self

    ) -> np.ndarray:

        return np.diag(

            self.matrix

        )

    # =====================================================
    # VALIDATION
    # =====================================================

    @property
    def is_positive_semidefinite(

        self

    ) -> bool:

        eigenvalues = np.linalg.eigvalsh(

            self.matrix

        )

        return np.all(

            eigenvalues >= -1e-10

        )

    def validate(

        self

    ) -> None:

        if not self.is_square:

            raise ValueError(

                "Covariance matrix must be square."

            )

        if len(

            self.assets

        ) != self.dimension:

            raise ValueError(

                "Asset count must equal matrix dimension."

            )

        if not self.is_symmetric:

            raise ValueError(

                "Covariance matrix must be symmetric."

            )

    # =====================================================
    # LOOKUPS
    # =====================================================

    def index(

        self,

        asset: str

    ) -> int:

        try:

            return self.assets.index(

                asset

            )

        except ValueError as exc:

            raise KeyError(

                f"Unknown asset '{asset}'."

            ) from exc

    def variance(

        self,

        asset: str

    ) -> float:

        idx = self.index(

            asset

        )

        return float(

            self.matrix[idx, idx]

        )

    def covariance(

        self,

        asset_a: str,

        asset_b: str

    ) -> float:

        i = self.index(

            asset_a

        )

        j = self.index(

            asset_b

        )

        return float(

            self.matrix[i, j]

        )

    def correlation(

        self,

        asset_a: str,

        asset_b: str

    ) -> float:

        cov = self.covariance(

            asset_a,

            asset_b

        )

        sigma_a = np.sqrt(

            self.variance(

                asset_a

            )

        )

        sigma_b = np.sqrt(

            self.variance(

                asset_b

            )

        )

        if sigma_a <= 0 or sigma_b <= 0:

            return 0.0

        return float(

            cov /

            (sigma_a * sigma_b)

        )

    # =====================================================
    # SUBMATRIX
    # =====================================================

    def submatrix(

        self,

        selected_assets: list[str]

    ) -> "CovarianceMatrix":

        indices = [

            self.index(

                asset

            )

            for asset

            in selected_assets

        ]

        matrix = self.matrix[

            np.ix_(

                indices,

                indices

            )

        ]

        return CovarianceMatrix(

            assets=selected_assets,

            matrix=matrix

        )

    # =====================================================
    # EXPORT
    # =====================================================

    def to_numpy(

        self

    ) -> np.ndarray:

        return self.matrix.copy()

    def to_dict(

        self

    ) -> dict[str, dict[str, float]]:

        return {

            asset_i: {

                asset_j: float(

                    self.matrix[i, j]

                )

                for j, asset_j

                in enumerate(

                    self.assets

                )

            }

            for i, asset_i

            in enumerate(

                self.assets

            )

        }

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self

    ) -> dict:

        return {

            "dimension": self.dimension,

            "shape": self.shape,

            "is_square": self.is_square,

            "is_symmetric": self.is_symmetric,

            "is_positive_semidefinite":

                self.is_positive_semidefinite

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self

    ) -> str:

        return (

            f"CovarianceMatrix("

            f"dimension={self.dimension}"

            f")"

        )

    __str__ = __repr__