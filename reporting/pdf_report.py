"""
====================================================================
Institutional Quant Platform

PDF Report

Author : Institutional Quant Platform

Purpose
-------
Institutional PDF report generator.

Exports a unified report package
to PDF format.

Inherited From

• BaseReport

====================================================================
"""

from __future__ import annotations

from pathlib import Path

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

from reporting.base_report import BaseReport


class PDFReport(
    BaseReport
):
    """
    Institutional PDF report.
    """

    def __init__(

        self,

        title: str,

        report_data: dict,

        author: str = "Institutional Quant Platform",

    ) -> None:

        super().__init__(

            title=title,

            author=author,

        )

        self.report_data = report_data

    # =====================================================
    # EXPORT
    # =====================================================

    def export(

        self,

        destination: str,

    ) -> None:

        path = Path(

            destination

        )

        if path.suffix.lower() != ".pdf":

            path = path.with_suffix(

                ".pdf"

            )

        document = SimpleDocTemplate(

            str(path)

        )

        styles = (

            getSampleStyleSheet()

        )

        story = []

        # =================================================
        # TITLE
        # =================================================

        story.append(

            Paragraph(

                self.title,

                styles["Title"],

            )

        )

        story.append(

            Spacer(

                1,

                18,

            )

        )

        # =================================================
        # AUTHOR
        # =================================================

        story.append(

            Paragraph(

                f"<b>Author:</b> "

                f"{self.author}",

                styles["Normal"],

            )

        )

        story.append(

            Paragraph(

                f"<b>Generated:</b> "

                f"{self.created_at}",

                styles["Normal"],

            )

        )

        story.append(

            Spacer(

                1,

                16,

            )

        )

        # =================================================
        # METADATA
        # =================================================

        metadata = (

            self.report_data.get(

                "Metadata",

                {},

            )

        )

        if metadata:

            story.append(

                Paragraph(

                    "Metadata",

                    styles["Heading1"],

                )

            )

            for key, value in metadata.items():

                story.append(

                    Paragraph(

                        f"<b>{key}</b>: "

                        f"{value}",

                        styles["Normal"],

                    )

                )

            story.append(

                Spacer(

                    1,

                    16,

                )

            )

        # =================================================
        # SECTIONS
        # =================================================

        sections = (

            self.report_data.get(

                "Sections",

                {},

            )

        )

        for name, values in sections.items():

            story.append(

                Paragraph(

                    name,

                    styles["Heading1"],

                )

            )

            story.append(

                Spacer(

                    1,

                    8,

                )

            )

            if isinstance(

                values,

                dict,

            ):

                for key, value in values.items():

                    story.append(

                        Paragraph(

                            f"<b>{key}</b>: "

                            f"{value}",

                            styles["BodyText"],

                        )

                    )

            else:

                story.append(

                    Paragraph(

                        str(

                            values

                        ),

                        styles["BodyText"],

                    )

                )

            story.append(

                Spacer(

                    1,

                    16,

                )

            )

        # =================================================
        # BUILD PDF
        # =================================================

        document.build(

            story

        )

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self,

    ) -> dict:

        return {

            **super().summary(),

            "Sections":

                len(

                    self.report_data.get(

                        "Sections",

                        {},

                    )

                ),

            "Format":

                "PDF",

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Title='{self.title}'"

            f")"

        )

    __str__ = __repr__