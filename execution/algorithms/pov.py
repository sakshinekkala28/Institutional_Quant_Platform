"""
====================================================================
Institutional Quant Platform

POV Algorithm

Author : Institutional Quant Platform

Purpose
-------
Institutional Participation of Volume (POV)
execution algorithm.

Executes a fixed percentage of observed
market volume.

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
class POVAlgorithm(
    ExecutionAlgorithm
):
    """
    Institutional POV execution algorithm.
    """

    participation_rate: float = 0.10

    def __post_init__(

        self,

    ) -> None:

        super().__init__(

            name="POV"

        )

        if not (

            0.0

            <

            self.participation_rate

            <=

            1.0

        ):

            raise ValueError(

                "Participation rate "

                "must be in (0,1]."

            )

    # =====================================================
    # PARTICIPATION
    # =====================================================

    def participation_quantity(

        self,

        market_volume: float,

    ) -> float:

        return (

            market_volume

            *

            self.participation_rate

        )

    # =====================================================
    # EXECUTION SCHEDULE
    # =====================================================

    def schedule(

        self,

        order: Order,

        market_volume: float,

    ) -> list[float]:

        slice_quantity = min(

            order.quantity,

            self.participation_quantity(

                market_volume

            ),

        )

        slices: list[float] = []

        remaining = order.quantity

        while remaining > 0.0:

            quantity = min(

                remaining,

                slice_quantity,

            )

            slices.append(

                quantity

            )

            remaining -= quantity

        return slices

    # =====================================================
    # EXECUTE
    # =====================================================

    def execute(

        self,

        order: Order,

    ) -> ExecutionReport:

        #
        # Example market volume.
        # In production this comes
        # from Market Data.
        #

        market_volume = 1_000_000.0

        schedule = self.schedule(

            order,

            market_volume,

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

            "POV execution completed."

        )

        report.metadata[

            "ParticipationRate"

        ] = self.participation_rate

        report.metadata[

            "MarketVolume"

        ] = market_volume

        report.metadata[

            "Slices"

        ] = schedule

        return report

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Participation="

            f"{self.participation_rate:.1%}"

            f")"

        )

    __str__ = __repr__