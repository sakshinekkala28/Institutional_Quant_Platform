"""
====================================================================
Institutional Quant Platform

Request Timer Middleware

Author : Institutional Quant Platform

Purpose
-------
Measure end-to-end request execution time.

Features

• High Precision Timer
• Request Latency
• Performance Metrics
• Slow Request Detection
• Response Headers
• Telemetry Integration
• Performance Logging

Used By

• Monitoring
• Performance Logger
• Dashboard
• Telemetry Engine

====================================================================
"""

from __future__ import annotations

import logging
import time
from collections.abc import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


logger = logging.getLogger(

    "institutional.timer",

)


# ==========================================================
# REQUEST TIMER
# ==========================================================


class RequestTimerMiddleware(
    BaseHTTPMiddleware,
):
    """
    Request execution timer.
    """

    def __init__(

        self,

        app,

        slow_request_ms: float = 1000.0,

    ):

        super().__init__(

            app,

        )

        self.slow_request_ms = (

            slow_request_ms

        )

    # =====================================================
    # DISPATCH
    # =====================================================

    async def dispatch(

        self,

        request: Request,

        call_next: Callable,

    ):

        start_time = (

            time.perf_counter()

        )

        request.state.start_time = (

            start_time

        )

        response = await call_next(

            request,

        )

        end_time = (

            time.perf_counter()

        )

        elapsed_seconds = (

            end_time

            -

            start_time

        )

        elapsed_ms = (

            elapsed_seconds

            * 1000

        )

        request.state.execution_time = (

            elapsed_seconds

        )

        # =============================================
        # RESPONSE HEADERS
        # =============================================

        response.headers[

            "X-Execution-Time"

        ] = (

            f"{elapsed_ms:.2f} ms"

        )

        response.headers[

            "Server-Timing"

        ] = (

            f"app;dur={elapsed_ms:.2f}"

        )

        # =============================================
        # PERFORMANCE LOGGING
        # =============================================

        logger.info(

            "Request Completed",

            extra={

                "method":

                    request.method,

                "path":

                    request.url.path,

                "execution_ms":

                    round(

                        elapsed_ms,

                        2,

                    ),

                "status":

                    response.status_code,

            },

        )

        # =============================================
        # SLOW REQUEST
        # =============================================

        if (

            elapsed_ms

            >

            self.slow_request_ms

        ):

            logger.warning(

                "Slow Request",

                extra={

                    "method":

                        request.method,

                    "path":

                        request.url.path,

                    "execution_ms":

                        round(

                            elapsed_ms,

                            2,

                        ),

                    "threshold":

                        self.slow_request_ms,

                },

            )

        return response


# ==========================================================
# TIMER UTILITIES
# ==========================================================


class Timer:
    """
    Manual performance timer.
    """

    def __init__(

        self,

    ):

        self.start = (

            time.perf_counter()

        )

    @property
    def elapsed_seconds(

        self,

    ) -> float:

        return (

            time.perf_counter()

            -

            self.start

        )

    @property
    def elapsed_milliseconds(

        self,

    ) -> float:

        return (

            self.elapsed_seconds

            * 1000

        )

    def reset(

        self,

    ):

        self.start = (

            time.perf_counter()

        )


# ==========================================================
# DECORATOR
# ==========================================================


def measure_time(

    logger_name: str = "institutional.timer",

):

    perf_logger = logging.getLogger(

        logger_name,

    )

    def decorator(

        function,

    ):

        async def wrapper(

            *args,

            **kwargs,

        ):

            start = (

                time.perf_counter()

            )

            result = await function(

                *args,

                **kwargs,

            )

            elapsed = (

                time.perf_counter()

                -

                start

            )

            perf_logger.info(

                "%s completed in %.3f sec",

                function.__name__,

                elapsed,

            )

            return result

        return wrapper

    return decorator


# ==========================================================
# SUMMARY
# ==========================================================


def timer_summary(

    threshold_ms: float,

) -> dict:

    return {

        "timer":

            "High Precision",

        "slow_request_threshold_ms":

            threshold_ms,

        "headers": [

            "X-Execution-Time",

            "Server-Timing",

        ],

    }


# ==========================================================
# EXPORTS
# ==========================================================


__all__ = [

    "RequestTimerMiddleware",

    "Timer",

    "measure_time",

    "timer_summary",

]