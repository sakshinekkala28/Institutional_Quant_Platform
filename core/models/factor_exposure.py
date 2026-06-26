"""
====================================================================
Institutional Quant Platform

Factor Exposure

Author : Institutional Quant Platform

Purpose
-------
Institutional multi-factor exposure model.

Represents factor exposures for a security or
portfolio.

Used By

• Factor Risk Engine
• Portfolio Optimizer
• Alpha Engine
• Risk Attribution
• Performance Attribution
• Constraint Engine

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field


@dataclass(slots=True)
class FactorExposure:
    """
    Institutional factor exposure model.
    """

    security_id: str

    symbol: str

    exposures: dict[str, float] = field(

        default_factory=dict

    )

    metadata: dict[str, str] = field(

        default_factory=dict

    )

    __hash__ = None

    # =====================================================
    # COLLECTION PROTOCOL
    # =====================================================

    def __len__(

        self

    ) -> int:

        return len(

            self.exposures

        )

    def __iter__(

        self

    ):

        return iter(

            self.exposures.items()

        )

    def __contains__(

        self,

        factor: str

    ) -> bool:

        return factor in self.exposures

    def __getitem__(

        self,

        factor: str

    ) -> float:

        try:

            return self.exposures[

                factor

            ]

        except KeyError as exc:

            raise KeyError(

                f"Unknown factor '{factor}'."

            ) from exc

    # =====================================================
    # BASIC
    # =====================================================

    @property
    def factor_count(

        self

    ) -> int:

        return len(

            self

        )

    @property
    def is_empty(

        self

    ) -> bool:

        return len(

            self

        ) == 0

    @property
    def factors(

        self

    ) -> list[str]:

        return sorted(

            self.exposures.keys()

        )

    @property
    def values(

        self

    ) -> list[float]:

        return [

            self.exposures[

                factor

            ]

            for factor

            in self.factors

        ]

    # =====================================================
    # LOOKUPS
    # =====================================================

    def exposure(

        self,

        factor: str

    ) -> float:

        return self.exposures.get(

            factor,

            0.0

        )

    def exists(

        self,

        factor: str

    ) -> bool:

        return factor in self

    # =====================================================
    # MODIFICATION
    # =====================================================

    def add(

        self,

        factor: str,

        value: float

    ) -> None:

        self.exposures[

            factor

        ] = value

    def remove(

        self,

        factor: str

    ) -> None:

        self.exposures.pop(

            factor,

            None

        )

    def update(

        self,

        factor: str,

        value: float

    ) -> None:

        if factor not in self:

            raise KeyError(

                f"Unknown factor '{factor}'."

            )

        self.exposures[

            factor

        ] = value

    # =====================================================
    # VALIDATION
    # =====================================================

    def validate(

        self

    ) -> None:

        if not self.security_id:

            raise ValueError(

                "security_id is required."

            )

        if not self.symbol:

            raise ValueError(

                "symbol is required."

            )

        for factor, value in self.exposures.items():

            if not isinstance(

                value,

                (int, float)

            ):

                raise TypeError(

                    f"Factor '{factor}' "

                    "must be numeric."

                )

    # =====================================================
    # EXPORT
    # =====================================================

    def to_dict(

        self

    ) -> dict:

        return {

            "security_id":

                self.security_id,

            "symbol":

                self.symbol,

            "factor_count":

                self.factor_count,

            "exposures":

                dict(

                    self.exposures

                )

        }

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self

    ) -> dict:

        return {

            "security_id":

                self.security_id,

            "symbol":

                self.symbol,

            "factor_count":

                self.factor_count,

            "factors":

                self.factors

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self

    ) -> str:

        return (

            f"FactorExposure("

            f"{self.symbol}, "

            f"{self.factor_count} factors)"

        )

    __str__ = __repr__