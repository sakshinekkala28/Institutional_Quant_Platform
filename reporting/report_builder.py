"""
====================================================================
Institutional Quant Platform

Report Builder

Author : Institutional Quant Platform

Purpose
-------
Institutional report builder.

Builds a unified report package from
multiple analytical engines.

Combines

• Backtest Report
• Risk Report
• Optimization Report
• Execution Report

Consumed By

• PDF Report
• HTML Report
• Excel Report
• JSON Report

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field

from backtesting.backtest_report import BacktestReport
from core.models.risk_report import RiskReport
from execution.execution_report import ExecutionReport
from optimization.optimization_report import (
    OptimizationReport,
)


@dataclass(slots=True)
class ReportBuilder:
    """
    Institutional report builder.
    """

    title: str = "Institutional Quant Report"

    sections: dict = field(

        default_factory=dict

    )

    metadata: dict = field(

        default_factory=dict

    )

    __hash__ = None

    # =====================================================
    # BACKTEST
    # =====================================================

    def add_backtest(

        self,

        report: BacktestReport,

    ) -> None:

        self.sections[

            "Backtest"

        ] = report.summary()

    # =====================================================
    # RISK
    # =====================================================

    def add_risk(

        self,

        report: RiskReport,

    ) -> None:

        self.sections[

            "Risk"

        ] = report.summary()

    # =====================================================
    # OPTIMIZATION
    # =====================================================

    def add_optimization(

        self,

        report: OptimizationReport,

    ) -> None:

        self.sections[

            "Optimization"

        ] = report.summary()

    # =====================================================
    # EXECUTION
    # =====================================================

    def add_execution(

        self,

        report: ExecutionReport,

    ) -> None:

        self.sections[

            "Execution"

        ] = report.summary()

    # =====================================================
    # CUSTOM SECTION
    # =====================================================

    def add_section(

        self,

        name: str,

        data: dict,

    ) -> None:

        self.sections[

            name

        ] = data

    # =====================================================
    # METADATA
    # =====================================================

    def add_metadata(

        self,

        key: str,

        value,

    ) -> None:

        self.metadata[

            key

        ] = value

    # =====================================================
    # BUILD
    # =====================================================

    def build(

        self,

    ) -> dict:

        return {

            "Title":

                self.title,

            "Metadata":

                self.metadata,

            "Sections":

                self.sections,

        }

    # =====================================================
    # RESET
    # =====================================================

    def clear(

        self,

    ) -> None:

        self.sections.clear()

        self.metadata.clear()

    # =====================================================
    # PROPERTIES
    # =====================================================

    @property
    def number_of_sections(

        self,

    ) -> int:

        return len(

            self.sections

        )

    @property
    def section_names(

        self,

    ) -> list[str]:

        return list(

            self.sections.keys()

        )

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self,

    ) -> dict:

        return {

            "Title":

                self.title,

            "Sections":

                self.section_names,

            "SectionCount":

                self.number_of_sections,

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Sections={self.number_of_sections}"

            f")"

        )

    __str__ = __repr__