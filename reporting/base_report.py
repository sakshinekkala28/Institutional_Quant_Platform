"""
====================================================================
Institutional Quant Platform

Base Report

Author : Institutional Quant Platform

Purpose
-------
Abstract base class for all reporting
engines.

Provides

• Report Metadata
• Validation
• Export Contract
• Common Utilities

Inherited By

• PDFReport
• HTMLReport
• ExcelReport
• JSONReport

====================================================================
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from datetime import datetime


class BaseReport(
    ABC
):
    """
    Institutional base report.
    """

    def __init__(

        self,

        title: str,

        author: str = "Institutional Quant Platform",

    ) -> None:

        if not title:

            raise ValueError(

                "Report title "

                "cannot be empty."

            )

        self._title = title

        self._author = author

        self._created_at = (

            datetime.utcnow()

        )

        self._metadata: dict = {}

    # =====================================================
    # PROPERTIES
    # =====================================================

    @property
    def title(

        self,

    ) -> str:

        return self._title

    @property
    def author(

        self,

    ) -> str:

        return self._author

    @property
    def created_at(

        self,

    ) -> datetime:

        return self._created_at

    @property
    def metadata(

        self,

    ) -> dict:

        return self._metadata

    # =====================================================
    # METADATA
    # =====================================================

    def add_metadata(

        self,

        key: str,

        value,

    ) -> None:

        self._metadata[

            key

        ] = value

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self,

    ) -> dict:

        return {

            "Title":

                self.title,

            "Author":

                self.author,

            "Created":

                self.created_at.isoformat(),

            "Metadata":

                self.metadata,

        }

    # =====================================================
    # EXPORT
    # =====================================================

    @abstractmethod
    def export(

        self,

        destination: str,

    ) -> None:
        """
        Export report.
        """

        raise NotImplementedError

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