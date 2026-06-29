"""
====================================================================
Institutional Quant Platform

HTML Report

Author : Institutional Quant Platform

Purpose
-------
Institutional HTML report generator.

Exports a unified report package
to HTML format.

Inherited From

• BaseReport

====================================================================
"""

from __future__ import annotations

from html import escape
from pathlib import Path

from reporting.base_report import BaseReport


class HTMLReport(
    BaseReport
):
    """
    Institutional HTML report.
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

        if path.suffix.lower() != ".html":

            path = path.with_suffix(

                ".html"

            )

        html = []

        # =================================================
        # HEADER
        # =================================================

        html.append(

            "<!DOCTYPE html>"

        )

        html.append(

            "<html>"

        )

        html.append(

            "<head>"

        )

        html.append(

            '<meta charset="UTF-8">'

        )

        html.append(

            f"<title>{escape(self.title)}</title>"

        )

        html.append(

            """
<style>

body{

font-family:Arial,Helvetica,sans-serif;

margin:40px;

background:#fafafa;

color:#222;

}

h1{

border-bottom:2px solid #444;

padding-bottom:10px;

}

h2{

margin-top:35px;

color:#1f4e79;

}

table{

border-collapse:collapse;

width:100%;

margin-top:10px;

margin-bottom:20px;

}

th,td{

border:1px solid #cccccc;

padding:8px;

text-align:left;

}

th{

background:#eeeeee;

}

.metadata{

background:#f4f4f4;

padding:15px;

margin-bottom:20px;

border-radius:5px;

}

.footer{

margin-top:50px;

font-size:12px;

color:#777;

}

</style>
            """

        )

        html.append(

            "</head>"

        )

        html.append(

            "<body>"

        )

        # =================================================
        # TITLE
        # =================================================

        html.append(

            f"<h1>{escape(self.title)}</h1>"

        )

        # =================================================
        # METADATA
        # =================================================

        html.append(

            '<div class="metadata">'

        )

        html.append(

            f"<p><b>Author:</b> "

            f"{escape(self.author)}</p>"

        )

        html.append(

            f"<p><b>Generated:</b> "

            f"{self.created_at}</p>"

        )

        metadata = self.report_data.get(

            "Metadata",

            {},

        )

        if metadata:

            html.append(

                "<h3>Metadata</h3>"

            )

            html.append(

                "<table>"

            )

            html.append(

                "<tr><th>Key</th><th>Value</th></tr>"

            )

            for key, value in metadata.items():

                html.append(

                    "<tr>"

                    f"<td>{escape(str(key))}</td>"

                    f"<td>{escape(str(value))}</td>"

                    "</tr>"

                )

            html.append(

                "</table>"

            )

        html.append(

            "</div>"

        )

        # =================================================
        # SECTIONS
        # =================================================

        sections = self.report_data.get(

            "Sections",

            {},

        )

        for section, values in sections.items():

            html.append(

                f"<h2>{escape(section)}</h2>"

            )

            if isinstance(

                values,

                dict,

            ):

                html.append(

                    "<table>"

                )

                html.append(

                    "<tr><th>Metric</th><th>Value</th></tr>"

                )

                for key, value in values.items():

                    html.append(

                        "<tr>"

                        f"<td>{escape(str(key))}</td>"

                        f"<td>{escape(str(value))}</td>"

                        "</tr>"

                    )

                html.append(

                    "</table>"

                )

            else:

                html.append(

                    f"<p>{escape(str(values))}</p>"

                )

        # =================================================
        # FOOTER
        # =================================================

        html.append(

            '<div class="footer">'

        )

        html.append(

            "Generated by "

            "Institutional Quant Platform"

        )

        html.append(

            "</div>"

        )

        html.append(

            "</body>"

        )

        html.append(

            "</html>"

        )

        path.write_text(

            "\n".join(html),

            encoding="utf-8",

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

                "HTML",

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