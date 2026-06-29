"""
====================================================================
Institutional Quant Platform

Dashboard Export

Author : Institutional Quant Platform

Purpose
-------
Exports institutional analytics to a
dashboard-friendly structure.

Supports

• Streamlit
• Dash
• Flask
• FastAPI
• REST APIs
• React
• Vue

Combines

• Reports
• Charts
• Metrics
• Tables
• Metadata

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
import json

from reporting.report_builder import ReportBuilder


@dataclass(slots=True)
class DashboardExport:
    """
    Dashboard export engine.
    """

    title: str = "Institutional Dashboard"

    report: ReportBuilder | None = None

    charts: dict = field(

        default_factory=dict

    )

    tables: dict = field(

        default_factory=dict

    )

    metrics: dict = field(

        default_factory=dict

    )

    metadata: dict = field(

        default_factory=dict

    )

    __hash__ = None

    # =====================================================
    # REPORT
    # =====================================================

    def attach_report(

        self,

        report: ReportBuilder,

    ) -> None:

        self.report = report

    # =====================================================
    # CHARTS
    # =====================================================

    def add_chart(

        self,

        name: str,

        filename: str,

    ) -> None:

        self.charts[

            name

        ] = filename

    # =====================================================
    # TABLES
    # =====================================================

    def add_table(

        self,

        name: str,

        table,

    ) -> None:

        self.tables[

            name

        ] = table

    # =====================================================
    # METRICS
    # =====================================================

    def add_metric(

        self,

        name: str,

        value,

    ) -> None:

        self.metrics[

            name

        ] = value

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
    # EXPORT DICTIONARY
    # =====================================================

    def to_dict(

        self,

    ) -> dict:

        return {

            "title":

                self.title,

            "generated":

                datetime.utcnow()

                .isoformat(),

            "report":

                (

                    self.report.build()

                    if self.report

                    else None

                ),

            "metrics":

                self.metrics,

            "charts":

                self.charts,

            "tables":

                self.tables,

            "metadata":

                self.metadata,

        }

    # =====================================================
    # EXPORT JSON
    # =====================================================

    def export_json(

        self,

        filename: str,

        indent: int = 4,

    ) -> None:

        with open(

            filename,

            "w",

            encoding="utf-8",

        ) as file:

            json.dump(

                self.to_dict(),

                file,

                indent=indent,

                default=str,

            )

    # =====================================================
    # RESET
    # =====================================================

    def clear(

        self,

    ) -> None:

        self.report = None

        self.metrics.clear()

        self.tables.clear()

        self.charts.clear()

        self.metadata.clear()

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self,

    ) -> dict:

        return {

            "Title":

                self.title,

            "Charts":

                len(

                    self.charts

                ),

            "Tables":

                len(

                    self.tables

                ),

            "Metrics":

                len(

                    self.metrics

                ),

            "Metadata":

                len(

                    self.metadata

                ),

            "ReportAttached":

                self.report is not None,

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Charts={len(self.charts)}, "

            f"Tables={len(self.tables)}, "

            f"Metrics={len(self.metrics)})"

        )

    __str__ = __repr__