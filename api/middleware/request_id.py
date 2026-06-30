"""
====================================================================
Institutional Quant Platform

Request ID Middleware

Author : Institutional Quant Platform

Purpose
-------
Generate and propagate unique request identifiers.

Features

• UUID Request ID
• Correlation Support
• Incoming Header Support
• Response Header Injection
• Request Context
• Distributed Tracing Ready

Used By

• Logging Middleware
• Exception Handler
• Monitoring
• Telemetry
• Audit Logger

====================================================================
"""

from __future__ import annotations

import uuid
from collections.abc import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


# ==========================================================
# CONSTANTS
# ==========================================================

REQUEST_ID_HEADER = "X-Request-ID"

CORRELATION_ID_HEADER = "X-Correlation-ID"


# ==========================================================
# REQUEST ID MIDDLEWARE
# ==========================================================


class RequestIDMiddleware(
    BaseHTTPMiddleware,
):
    """
    Request identifier middleware.
    """

    async def dispatch(

        self,

        request: Request,

        call_next: Callable,

    ):

        request_id = (

            request.headers.get(

                REQUEST_ID_HEADER,

            )

            or

            str(

                uuid.uuid4(),

            )

        )

        correlation_id = (

            request.headers.get(

                CORRELATION_ID_HEADER,

            )

            or

            request_id

        )

        request.state.request_id = (

            request_id

        )

        request.state.correlation_id = (

            correlation_id

        )

        response = await call_next(

            request,

        )

        response.headers[

            REQUEST_ID_HEADER

        ] = request_id

        response.headers[

            CORRELATION_ID_HEADER

        ] = correlation_id

        return response


# ==========================================================
# UTILITIES
# ==========================================================


def get_request_id(

    request: Request,

) -> str:

    return getattr(

        request.state,

        "request_id",

        "",

    )


def get_correlation_id(

    request: Request,

) -> str:

    return getattr(

        request.state,

        "correlation_id",

        "",

    )


def request_context(

    request: Request,

) -> dict:

    return {

        "request_id":

            get_request_id(

                request,

            ),

        "correlation_id":

            get_correlation_id(

                request,

            ),

        "method":

            request.method,

        "path":

            request.url.path,

    }


# ==========================================================
# FACTORY
# ==========================================================


def generate_request_id(

) -> str:

    return str(

        uuid.uuid4(),

    )


def generate_correlation_id(

) -> str:

    return str(

        uuid.uuid4(),

    )


# ==========================================================
# SUMMARY
# ==========================================================


def request_id_summary(

) -> dict:

    return {

        "request_header":

            REQUEST_ID_HEADER,

        "correlation_header":

            CORRELATION_ID_HEADER,

        "generator":

            "UUID4",

        "distributed_tracing":

            True,

    }


# ==========================================================
# EXPORTS
# ==========================================================


__all__ = [

    "REQUEST_ID_HEADER",

    "CORRELATION_ID_HEADER",

    "RequestIDMiddleware",

    "get_request_id",

    "get_correlation_id",

    "request_context",

    "generate_request_id",

    "generate_correlation_id",

    "request_id_summary",

]