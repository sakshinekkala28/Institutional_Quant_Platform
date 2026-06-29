"""
====================================================================
Institutional Quant Platform

Report Engine

Author : Institutional Quant Platform

Purpose
-------
Institutional reporting engine.

Coordinates

• Backtest Reports
• Risk Reports
• Optimization Reports
• Execution Reports

Produces

• PDF Reports
• HTML Reports
• Excel Reports
• JSON Reports

====================================================================
"""

from __future__ import annotations

from pathlib import Path

from backtesting.backtest_report import BacktestReport
from core.models.risk_report import RiskReport

from execution.execution_report import ExecutionReport

from optimization.optimization_report import (
    OptimizationReport,
)

from reporting.base_report import BaseReport


class ReportEngine:
    """
    Institutional report engine.
    """

    def __init__(

        self,

    ) -> None:

        self._reports: list[BaseReport] = []

    # =====================================================
    # REGISTER
    # =====================================================

    def register(

        self,

        report: BaseReport,

    ) -> None:

        self._reports.append(

            report

        )

    # =====================================================
    # BUILD METADATA
    # =====================================================

    @staticmethod
    def build_metadata(

        *,

        backtest: BacktestReport | None = None,

        risk: RiskReport | None = None,

        optimization: OptimizationReport | None = None,

        execution: ExecutionReport | None = None,

    ) -> dict:

        metadata: dict = {}

        if backtest is not None:

            metadata[

                "Backtest"

            ] = backtest.summary()

        if risk is not None:

            metadata[

                "Risk"

            ] = risk.summary()

        if optimization is not None:

            metadata[

                "Optimization"

            ] = optimization.summary()

        if execution is not None:

            metadata[

                "Execution"

            ] = execution.summary()

        return metadata

    # =====================================================
    # EXPORT ONE
    # =====================================================

    def export(

        self,

        report: BaseReport,

        destination: str | Path,

    ) -> None:

        report.export(

            str(

                destination

            )

        )

    # =====================================================
    # EXPORT ALL
    # =====================================================

    def export_all(

        self,

        directory: str | Path,

    ) -> None:

        directory = Path(

            directory

        )

        directory.mkdir(

            parents=True,

            exist_ok=True,

        )

        for report in self._reports:

            filename = (

                report.title

                .replace(

                    " ",

                    "_",

                )

                .lower()

            )

            report.export(

                str(

                    directory

                    /

                    filename

                )

            )

    # =====================================================
    # CLEAR
    # =====================================================

    def clear(

        self,

    ) -> None:

        self._reports.clear()

    # =====================================================
    # PROPERTIES
    # =====================================================

    @property
    def reports(

        self,

    ) -> list[BaseReport]:

        return list(

            self._reports

        )

    @property
    def count(

        self,

    ) -> int:

        return len(

            self._reports

        )

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self,

    ) -> dict:

        return {

            "RegisteredReports":

                self.count,

            "ReportTitles":

                [

                    report.title

                    for report

                    in self._reports

                ],

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Reports={self.count}"

            f")"

        )

    __str__ = __repr__