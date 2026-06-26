"""
====================================================================
Institutional Quant Platform

Black-Litterman Model

Author : Institutional Quant Platform

Purpose
-------
Institutional Black-Litterman Bayesian model.

Provides

• Posterior Expected Returns
• Posterior Covariance
• Bayesian Updating

Reference

Black & Litterman (1992)

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from core.models.confidence_matrix import ConfidenceMatrix
from core.models.covariance_matrix import CovarianceMatrix
from core.models.equilibrium_returns import EquilibriumReturns
from core.models.expected_returns import ExpectedReturns
from core.models.investor_view import InvestorView


@dataclass(slots=True)
class BlackLittermanModel:
    """
    Institutional Black-Litterman Model.
    """

    equilibrium_returns: EquilibriumReturns

    covariance_matrix: CovarianceMatrix

    investor_view: InvestorView

    confidence_matrix: ConfidenceMatrix

    tau: float = 0.05

    __hash__ = None

    # =====================================================
    # VALIDATION
    # =====================================================

    def __post_init__(

        self

    ) -> None:

        self.validate()

    def validate(

        self

    ) -> None:

        if self.tau <= 0.0:

            raise ValueError(

                "Tau must be positive."

            )

    # =====================================================
    # ALIASES
    # =====================================================

    @property
    def sigma(

        self

    ) -> np.ndarray:

        return self.covariance_matrix.matrix

    @property
    def pi(

        self

    ) -> np.ndarray:

        return self.equilibrium_returns.values

    @property
    def P(

        self

    ) -> np.ndarray:

        return self.investor_view.pick_matrix

    @property
    def Q(

        self

    ) -> np.ndarray:

        return self.investor_view.expected_returns

    @property
    def omega(

        self

    ) -> np.ndarray:

        return self.confidence_matrix.matrix

    # =====================================================
    # POSTERIOR RETURNS
    # =====================================================

    @property
    def posterior_expected_returns(

        self

    ) -> ExpectedReturns:

        sigma = self.sigma

        tau_sigma = self.tau * sigma

        middle = np.linalg.inv(

            self.P

            @ tau_sigma

            @ self.P.T

            +

            self.omega

        )

        adjustment = (

            tau_sigma

            @ self.P.T

            @ middle

            @ (

                self.Q

                -

                self.P

                @ self.pi

            )

        )

        posterior = (

            self.pi

            +

            adjustment

        )

        return ExpectedReturns(

            symbols=self.equilibrium_returns.symbols,

            values=posterior,

        )

    # =====================================================
    # POSTERIOR COVARIANCE
    # =====================================================

    @property
    def posterior_covariance(

        self

    ) -> CovarianceMatrix:

        sigma = self.sigma

        tau_sigma = self.tau * sigma

        middle = np.linalg.inv(

            self.P

            @ tau_sigma

            @ self.P.T

            +

            self.omega

        )

        posterior = (

            sigma

            +

            tau_sigma

            -

            tau_sigma

            @ self.P.T

            @ middle

            @ self.P

            @ tau_sigma

        )

        return CovarianceMatrix(

            symbols=self.equilibrium_returns.symbols,

            matrix=posterior,

        )

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self

    ) -> dict:

        posterior = self.posterior_expected_returns

        return {

            "Assets":

                posterior.size,

            "Views":

                self.investor_view.number_of_views,

            "Tau":

                self.tau,

            "Posterior_Mean":

                posterior.mean,

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Assets={len(self.equilibrium_returns)}, "

            f"Views={self.investor_view.number_of_views}, "

            f"Tau={self.tau:.3f}"

            f")"

        )

    __str__ = __repr__