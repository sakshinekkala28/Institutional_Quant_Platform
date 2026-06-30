"""
====================================================================
Institutional Quant Platform

Data Monitor

Author : Institutional Quant Platform

Purpose
-------
Institutional data quality monitoring.

Monitors

• Data Freshness
• Missing Values
• Duplicate Records
• Schema Validation
• Completeness
• Data Volume

Used By

• ETL Pipeline
• Dashboard
• Alert Engine
• Scheduler

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

import pandas as pd


# ==========================================================
# DATA MONITOR RESULT
# ==========================================================


@dataclass(slots=True)
class DataMonitorResult:
    """
    Data quality monitoring result.
    """

    metric: str

    status: str

    value: float | int | str

    threshold: float | int | None

    timestamp: datetime

    metadata: dict

    def summary(

        self,

    ) -> dict:

        return {

            "Metric":

                self.metric,

            "Status":

                self.status,

            "Value":

                self.value,

            "Threshold":

                self.threshold,

            "Timestamp":

                self.timestamp.isoformat(),

            "Metadata":

                self.metadata,

        }


# ==========================================================
# DATA MONITOR
# ==========================================================


class DataMonitor:
    """
    Institutional data monitoring.
    """

    # =====================================================
    # DATA FRESHNESS
    # =====================================================

    @staticmethod
    def check_freshness(

        last_updated: datetime,

        max_age_hours: int = 24,

    ) -> DataMonitorResult:

        age = (

            datetime.utcnow()

            -

            last_updated

        ).total_seconds() / 3600

        return DataMonitorResult(

            metric="Data Freshness",

            status=(

                "OK"

                if age <= max_age_hours

                else "WARNING"

            ),

            value=round(

                age,

                2,

            ),

            threshold=max_age_hours,

            timestamp=datetime.utcnow(),

            metadata={

                "Unit":

                    "Hours",

            },

        )

    # =====================================================
    # MISSING VALUES
    # =====================================================

    @staticmethod
    def check_missing(

        dataframe: pd.DataFrame,

    ) -> DataMonitorResult:

        missing = int(

            dataframe

            .isna()

            .sum()

            .sum()

        )

        return DataMonitorResult(

            metric="Missing Values",

            status=(

                "OK"

                if missing == 0

                else "WARNING"

            ),

            value=missing,

            threshold=0,

            timestamp=datetime.utcnow(),

            metadata={

                "Rows":

                    len(dataframe),

            },

        )

    # =====================================================
    # DUPLICATES
    # =====================================================

    @staticmethod
    def check_duplicates(

        dataframe: pd.DataFrame,

    ) -> DataMonitorResult:

        duplicates = int(

            dataframe

            .duplicated()

            .sum()

        )

        return DataMonitorResult(

            metric="Duplicate Records",

            status=(

                "OK"

                if duplicates == 0

                else "WARNING"

            ),

            value=duplicates,

            threshold=0,

            timestamp=datetime.utcnow(),

            metadata={

                "Rows":

                    len(dataframe),

            },

        )

    # =====================================================
    # SCHEMA VALIDATION
    # =====================================================

    @staticmethod
    def validate_schema(

        dataframe: pd.DataFrame,

        required_columns: list[str],

    ) -> DataMonitorResult:

        missing = [

            column

            for column

            in required_columns

            if column

            not in dataframe.columns

        ]

        return DataMonitorResult(

            metric="Schema Validation",

            status=(

                "OK"

                if not missing

                else "CRITICAL"

            ),

            value=len(

                missing

            ),

            threshold=0,

            timestamp=datetime.utcnow(),

            metadata={

                "MissingColumns":

                    missing,

            },

        )

    # =====================================================
    # COMPLETENESS
    # =====================================================

    @staticmethod
    def completeness(

        dataframe: pd.DataFrame,

    ) -> DataMonitorResult:

        total = (

            dataframe.shape[0]

            *

            dataframe.shape[1]

        )

        filled = int(

            dataframe.count().sum()

        )

        percentage = (

            100

            *

            filled

            /

            total

            if total

            else 0

        )

        return DataMonitorResult(

            metric="Completeness",

            status=(

                "OK"

                if percentage >= 99

                else "WARNING"

            ),

            value=round(

                percentage,

                2,

            ),

            threshold=99,

            timestamp=datetime.utcnow(),

            metadata={},

        )

    # =====================================================
    # DATA VOLUME
    # =====================================================

    @staticmethod
    def volume(

        dataframe: pd.DataFrame,

        minimum_rows: int,

    ) -> DataMonitorResult:

        rows = len(

            dataframe

        )

        return DataMonitorResult(

            metric="Data Volume",

            status=(

                "OK"

                if rows >= minimum_rows

                else "WARNING"

            ),

            value=rows,

            threshold=minimum_rows,

            timestamp=datetime.utcnow(),

            metadata={},

        )

    # =====================================================
    # FULL REPORT
    # =====================================================

    @classmethod
    def report(

        cls,

        dataframe: pd.DataFrame,

        required_columns: list[str],

        last_updated: datetime,

        minimum_rows: int,

    ) -> dict:

        return {

            "Freshness":

                cls.check_freshness(

                    last_updated,

                ).summary(),

            "Missing":

                cls.check_missing(

                    dataframe,

                ).summary(),

            "Duplicates":

                cls.check_duplicates(

                    dataframe,

                ).summary(),

            "Schema":

                cls.validate_schema(

                    dataframe,

                    required_columns,

                ).summary(),

            "Completeness":

                cls.completeness(

                    dataframe,

                ).summary(),

            "Volume":

                cls.volume(

                    dataframe,

                    minimum_rows,

                ).summary(),

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}()"

        )

    __str__ = __repr__