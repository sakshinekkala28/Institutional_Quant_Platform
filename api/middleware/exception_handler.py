"""
====================================================================
Institutional Quant Platform

Exception Handler Middleware

Author : Institutional Quant Platform

Purpose
-------
Centralized exception handling for FastAPI.

Features

• Standard Error Response
• Validation Errors
• HTTP Exceptions
• Internal Server Errors
• Correlation ID Support
• Structured Logging

Used By

• All API Routes
• Logging Middleware
• Monitoring
• Alert Engine

====================================================================
"""

from __future__ import annotations

import logging
import traceback
from datetime import datetime

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse


logger = logging.getLogger(

    "institutional.api",

)


# ==========================================================
# RESPONSE BUILDER
# ==========================================================


def error_response(

    *,

    status_code: int,

    error: str,

    message: str,

    request: Request,

    details=None,

):

    correlation_id = getattr(

        request.state,

        "correlation_id",

        None,

    )

    payload = {

        "success":

            False,

        "timestamp":

            datetime.utcnow().isoformat(),

        "status_code":

            status_code,

        "error":

            error,

        "message":

            message,

        "correlation_id":

            correlation_id,

        "path":

            request.url.path,

    }

    if details:

        payload["details"] = details

    return JSONResponse(

        status_code=status_code,

        content=payload,

    )


# ==========================================================
# HTTP EXCEPTION
# ==========================================================


async def http_exception_handler(

    request: Request,

    exc: HTTPException,

):

    logger.warning(

        "HTTP Exception",

        extra={

            "status_code":

                exc.status_code,

            "path":

                request.url.path,

        },

    )

    return error_response(

        status_code=exc.status_code,

        error="HTTP_EXCEPTION",

        message=str(

            exc.detail,

        ),

        request=request,

    )


# ==========================================================
# VALIDATION ERROR
# ==========================================================


async def validation_exception_handler(

    request: Request,

    exc: RequestValidationError,

):

    errors = []

    for item in exc.errors():

        errors.append(

            {

                "field":

                    ".".join(

                        str(x)

                        for x

                        in item["loc"]

                    ),

                "message":

                    item["msg"],

                "type":

                    item["type"],

            }

        )

    logger.warning(

        "Validation Error",

        extra={

            "path":

                request.url.path,

        },

    )

    return error_response(

        status_code=422,

        error="VALIDATION_ERROR",

        message="Request validation failed.",

        request=request,

        details=errors,

    )


# ==========================================================
# UNHANDLED EXCEPTION
# ==========================================================


async def unhandled_exception_handler(

    request: Request,

    exc: Exception,

):

    logger.exception(

        "Unhandled Exception",

        extra={

            "path":

                request.url.path,

        },

    )

    return error_response(

        status_code=500,

        error="INTERNAL_SERVER_ERROR",

        message="An unexpected error occurred.",

        request=request,

        details={

            "exception":

                exc.__class__.__name__,

        },

    )


# ==========================================================
# TRACEBACK LOGGER
# ==========================================================


def log_traceback(

    exc: Exception,

):

    logger.error(

        "".join(

            traceback.format_exception(

                exc,

            )

        )

    )


# ==========================================================
# REGISTER
# ==========================================================


def register_exception_handlers(

    app: FastAPI,

):

    app.add_exception_handler(

        HTTPException,

        http_exception_handler,

    )

    app.add_exception_handler(

        RequestValidationError,

        validation_exception_handler,

    )

    app.add_exception_handler(

        Exception,

        unhandled_exception_handler,

    )


# ==========================================================
# DECORATOR
# ==========================================================


def protect(

    function,

):

    async def wrapper(

        *args,

        **kwargs,

    ):

        try:

            return await function(

                *args,

                **kwargs,

            )

        except HTTPException:

            raise

        except Exception as exc:

            log_traceback(

                exc,

            )

            raise

    return wrapper