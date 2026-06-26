"""
====================================================================
Institutional Quant Platform

Asset Returns

Author : Institutional Quant Platform

Purpose
-------
Institutional universe return series.

Represents historical returns for every asset
within the investment universe.

Used By

• Risk Engine
• Portfolio Optimizer
• Covariance Builder
• Factor Models
• Performance Attribution
• Alpha Models
• Stress Testing

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from core.models.return_series import ReturnSeries


@dataclass(slots=True)
class AssetReturns:
    """
    Institutional asset return universe.
    """

    series: dict[str, ReturnSeries] = field(

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

            self.series

        )

    def __iter__(

        self

    ):

        return iter(

            self.series.items()

        )

    def __contains__(

        self,

        symbol: str

    ) -> bool:

        return symbol in self.series

    def __getitem__(

        self,

        symbol: str

    ) -> ReturnSeries:

        try:

            return self.series[

                symbol

            ]

        except KeyError as exc:

            raise KeyError(

                f"Unknown asset '{symbol}'."

            ) from exc

    def __bool__(

        self

    ) -> bool:

        return bool(

            self.series

        )

    # =====================================================
    # BASIC
    # =====================================================

    @property
    def asset_count(

        self

    ) -> int:

        return len(

            self

        )

    @property
    def symbols(

        self

    ) -> list[str]:

        return sorted(

            self.series.keys()

        )

    @property
    def is_empty(

        self

    ) -> bool:

        return len(

            self

        ) == 0

    # =====================================================
    # LOOKUPS
    # =====================================================

    def get(

        self,

        symbol: str

    ) -> ReturnSeries | None:

        return self.series.get(

            symbol

        )

    def exists(

        self,

        symbol: str

    ) -> bool:

        return symbol in self

    # =====================================================
    # MODIFICATION
    # =====================================================

    def add(

        self,

        symbol: str,

        returns: ReturnSeries

    ) -> None:

        self.series[

            symbol

        ] = returns

    def remove(

        self,

        symbol: str

    ) -> None:

        self.series.pop(

            symbol,

            None

        )

    def update(

        self,

        symbol: str,

        returns: ReturnSeries

    ) -> None:

        if symbol not in self:

            raise KeyError(

                f"Unknown asset '{symbol}'."

            )

        self.series[

            symbol

        ] = returns

    # =====================================================
    # VALIDATION
    # =====================================================

    def validate(

        self

    ) -> None:

        for symbol, returns in self.series.items():

            if not symbol:

                raise ValueError(

                    "Asset symbol cannot be empty."

                )

            if not isinstance(

                returns,

                ReturnSeries

            ):

                raise TypeError(

                    f"{symbol} must map to ReturnSeries."

                )

    # =====================================================
    # EXPORT
    # =====================================================

    def to_dict(

        self

    ) -> dict[str, list[float]]:

        return {

            symbol:

            returns.to_list()

            for symbol, returns

            in self.series.items()

        }

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self

    ) -> dict:

        return {

            "asset_count":

                self.asset_count,

            "symbols":

                self.symbols

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self

    ) -> str:

        return (

            f"AssetReturns("

            f"{self.asset_count} assets)"

        )

    __str__ = __repr__