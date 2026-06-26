"""
====================================================================
Institutional Quant Platform

Base Service

Author : Institutional Quant Platform

Purpose
-------
Base class for all domain services.

Provides

• Lifecycle Hooks
• Logging
• Timing
• Validation Hooks
• Common Utilities

====================================================================
"""

from __future__ import annotations

from abc import ABC
from abc import abstractmethod

from time import perf_counter

from core.logging_manager import LoggingManager


class BaseService(ABC):
    """
    Base class for all services.
    """

    def __init__(

        self

    ) -> None:

        self._logger = LoggingManager.get_logger(

            self.__class__.__name__

        )

    # =====================================================
    # LIFECYCLE
    # =====================================================

    def before_execute(

        self

    ) -> None:

        """
        Hook executed before service execution.
        """

        self._logger.debug(

            "Starting %s",

            self.__class__.__name__

        )

    def after_execute(

        self,

        elapsed_seconds: float

    ) -> None:

        """
        Hook executed after service execution.
        """

        self._logger.debug(

            "%s completed in %.4f seconds",

            self.__class__.__name__,

            elapsed_seconds

        )

    # =====================================================
    # EXECUTION
    # =====================================================

    def execute(

        self,

        *args,

        **kwargs

    ):

        """
        Execute service.
        """

        self.before_execute()

        start = perf_counter()

        try:

            result = self.run(

                *args,

                **kwargs

            )

            return result

        finally:

            elapsed = (

                perf_counter()

                - start

            )

            self.after_execute(

                elapsed

            )

    # =====================================================
    # ABSTRACT
    # =====================================================

    @abstractmethod
    def run(

        self,

        *args,

        **kwargs

    ):

        """
        Execute service logic.
        """

        raise NotImplementedError