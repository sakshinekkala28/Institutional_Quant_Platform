"""
====================================================================
Institutional Quant Platform

Logging Middleware

Author : Institutional Quant Platform

Purpose
-------
Structured request/response logging middleware.

Features

• Request Logging
• Response Logging
• Latency Measurement
• Correlation ID
• User Logging
• Exception Logging
• Performance Metrics

Used By

• Event Logger
• Performance Logger
• Dashboard
• Monitoring

====================================================================
"""

from __future__ import annotations

import logging
import time
import uuid
from typing import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


# ==========================================================
# LOGGER
# ==========================================================

logger = logging.getLogger(

    "institutional.api",

)


# ==========================================================
# LOGGING MIDDLEWARE
# ==========================================================


class LoggingMiddleware(
    BaseHTTPMiddleware,
):
    """
    Structured request logger.
    """

    async def dispatch(

        self,

        request: Request,

        call_next: Callable,

    ):

        correlation_id = str(

            uuid.uuid4(),

        )

        request.state.correlation_id = (

            correlation_id

        )

        start = time.perf_counter()

        method = request.method

        path = request.url.path

        client = (

            request.client.host

            if request.client

            else "Unknown"

        )

        user = getattr(

            request.state,

            "user",

            None,

        )

        username = (

            user.get(

                "username",

                "Anonymous",

            )

            if user

            else "Anonymous"

        )

        logger.info(

            "Incoming Request",

            extra={

                "correlation_id":

                    correlation_id,

                "method":

                    method,

                "path":

                    path,

                "client":

                    client,

                "user":

                    username,

            },

        )

        try:

            response = await call_next(

                request,

            )

        except Exception:

            elapsed = (

                time.perf_counter()

                -

                start

            )

            logger.exception(

                "Unhandled Exception",

                extra={

                    "correlation_id":

                        correlation_id,

                    "method":

                        method,

                    "path":

                        path,

                    "elapsed_ms":

                        round(

                            elapsed

                            * 1000,

                            2,

                        ),

                },

            )

            raise

        elapsed = (

            time.perf_counter()

            -

            start

        )

        response.headers[

            "X-Correlation-ID"

        ] = correlation_id

        response.headers[

            "X-Response-Time"

        ] = (

            f"{elapsed:.6f}"

        )

        logger.info(

            "Outgoing Response",

            extra={

                "correlation_id":

                    correlation_id,

                "status_code":

                    response.status_code,

                "elapsed_ms":

                    round(

                        elapsed

                        * 1000,

                        2,

                    ),

                "method":

                    method,

                "path":

                    path,

                "user":

                    username,

            },

        )

        return response


# ==========================================================
# LOGGING CONFIGURATION
# ==========================================================


def configure_logging(

    level: str = "INFO",

):

    logging.basicConfig(

        level=getattr(

            logging,

            level.upper(),

            logging.INFO,

        ),

        format=(

            "%(asctime)s "

            "%(levelname)s "

            "%(name)s "

            "%(message)s"

        ),

    )


# ==========================================================
# REQUEST LOGGER
# ==========================================================


def log_request(

    request: Request,

):

    logger.info(

        "%s %s",

        request.method,

        request.url.path,

    )


# ==========================================================
# RESPONSE LOGGER
# ==========================================================


def log_response(

    status_code: int,

    elapsed_ms: float,

):

    logger.info(

        "Status=%s Time=%.2f ms",

        status_code,

        elapsed_ms,

    )


# ==========================================================
# PERFORMANCE LOGGER
# ==========================================================


def log_performance(

    operation: str,

    execution_time: float,

):

    logger.info(

        "%s completed in %.3f sec",

        operation,

        execution_time,

    )


# ==========================================================
# AUDIT LOGGER
# ==========================================================


def log_audit(

    user: str,

    action: str,

):

    logger.info(

        "AUDIT | %s | %s",

        user,

        action,

    )