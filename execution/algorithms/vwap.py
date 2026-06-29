"""
====================================================================
Institutional Quant Platform

VWAP Algorithm

Author : Institutional Quant Platform

Purpose
-------
Institutional Volume Weighted Average Price
(VWAP) execution algorithm.

Splits a large order according to the expected
market volume profile.

Inherited From

• ExecutionAlgorithm

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass

from execution.execution_algorithm import ExecutionAlgorithm
from execution.execution_report import ExecutionReport
from execution.order import Order


@dataclass(slots=True)
class VWAPAlgorithm(
    ExecutionAlgorithm
):
    """
    Institutional VWAP execution algorithm.
    """

    volume_profile: list[float]

    def __post_init__(

        self,

    ) -> None:

        super().__init__(

            name="VWAP"

        )

        self.validate_profile()

    # =====================================================
    # VALIDATION
    # =====================================================

    def validate_profile(

        self,

    ) -> None:

        if not self.volume_profile:

            raise ValueError(

                "Volume profile cannot be empty."

            )

        total = sum(

            self.volume_profile

        )

        if total <= 0:

            raise ValueError(

                "Volume profile must be positive."

            )

    # =====================================================
    # SCHEDULE
    # =====================================================

    def schedule(

        self,

        order: Order,

    ) -> list[float]:

        total = sum(

            self.volume_profile

        )

        return [

            (

                weight

                / total

            )

            * order.quantity

            for weight

            in self.volume_profile

        ]

    # =====================================================
    # EXECUTE
    # =====================================================

    def execute(

        self,

        order: Order,

    ) -> ExecutionReport:

        schedule = self.schedule(

            order

        )

        report = ExecutionReport()

        report.order = order

        report.executed_quantity = sum(

            schedule

        )

        report.remaining_quantity = max(

            0.0,

            order.quantity

            -

            report.executed_quantity,

        )

        report.average_price = (

            order.price

            if order.price is not None

            else 0.0

        )

        report.execution_value = (

            report.executed_quantity

            *

            report.average_price

        )

        report.fill_ratio = (

            report.executed_quantity

            /

            order.quantity

        )

        report.algorithm = self.name

        report.status = "FILLED"

        report.message = (

            "VWAP execution completed."

        )

        report.metadata[

            "Slices"

        ] = schedule

        report.metadata[

            "Volume_Profile"

        ] = self.volume_profile

        return report

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Intervals={len(self.volume_profile)}"

            f")"

        )

    __str__ = __repr__