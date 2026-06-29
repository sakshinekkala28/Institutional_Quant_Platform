"""
====================================================================
Institutional Quant Platform

JSON Report

Author : Institutional Quant Platform

Purpose
-------
Institutional JSON report generator.

Exports a unified report package
to JSON format.

Inherited From

• BaseReport

====================================================================
"""

from __future__ import annotations

import json

from pathlib import Path
from datetime import datetime

from reporting.base_report import BaseReport


class JSONReport(
    BaseReport
):
    """
    Institutional JSON report.
    """

    def __init__(

        self,

        title: str,

        report_data: dict,

        author: str = "Institutional Quant Platform",

        indent: int = 4,

    ) -> None:

        super().__init__(

            title=title,

            author=author,

        )

        self.report_data = report_data

        self.indent = indent

    # =====================================================
    # SERIALIZATION
    # =====================================================

    @staticmethod
    def _serialize(

        value,

    ):

        if isinstance(

            value,

            datetime,

        ):

            return value.isoformat()

        if isinstance(

            value,

            Path,

        ):

            return str(

                value

            )

        if hasattr(

            value,

            "tolist",

        ):

            return value.tolist()

        if hasattr(

            value,

            "__dict__",

        ):

            return value.__dict__

        return str(

            value

        )

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

        if path.suffix.lower() != ".json":

            path = path.with_suffix(

                ".json"

            )

        payload = {

            "Title":

                self.title,

            "Author":

                self.author,

            "Generated":

                self.created_at,

            "Report":

                self.report_data,

        }

        with path.open(

            "w",

            encoding="utf-8",

        ) as file:

            json.dump(

                payload,

                file,

                indent=self.indent,

                default=self._serialize,

                ensure_ascii=False,

            )

    # =====================================================
    # LOAD
    # =====================================================

    @staticmethod
    def load(

        filename: str | Path,

    ) -> dict:

        path = Path(

            filename

        )

        with path.open(

            "r",

            encoding="utf-8",

        ) as file:

            return json.load(

                file

            )

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self,

    ) -> dict:

        return {

            **super().summary(),

            "Format":

                "JSON",

            "Indent":

                self.indent,

            "Sections":

                len(

                    self.report_data.get(

                        "Sections",

                        {},

                    )

                ),

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Title='{self.title}', "

            f"Indent={self.indent}"

            f")"

        )

    __str__ = __repr__