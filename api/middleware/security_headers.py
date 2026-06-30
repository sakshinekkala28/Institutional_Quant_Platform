"""
====================================================================
Institutional Quant Platform

Security Headers Middleware

Author : Institutional Quant Platform

Purpose
-------
Adds security-related HTTP headers to every response.

Features

• Strict Transport Security (HSTS)
• Content Security Policy (CSP)
• X-Frame-Options
• X-Content-Type-Options
• Referrer Policy
• Permissions Policy
• X-XSS-Protection
• Cache Control
• Remove Server Header

Used By

• FastAPI
• API Gateway
• Reverse Proxy

====================================================================
"""

from __future__ import annotations

from collections.abc import Callable

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware


# ==========================================================
# DEFAULT HEADERS
# ==========================================================


DEFAULT_SECURITY_HEADERS = {

    "Strict-Transport-Security":

        "max-age=31536000; includeSubDomains",

    "X-Frame-Options":

        "DENY",

    "X-Content-Type-Options":

        "nosniff",

    "Referrer-Policy":

        "strict-origin-when-cross-origin",

    "Permissions-Policy":

        (

            "accelerometer=(), "

            "camera=(), "

            "geolocation=(), "

            "gyroscope=(), "

            "microphone=(), "

            "payment=(), "

            "usb=()"

        ),

    "X-XSS-Protection":

        "1; mode=block",

    "Cache-Control":

        "no-store",

}


DEFAULT_CSP = (

    "default-src 'self'; "

    "script-src 'self'; "

    "style-src 'self' 'unsafe-inline'; "

    "img-src 'self' data:; "

    "font-src 'self'; "

    "connect-src 'self'; "

    "object-src 'none'; "

    "frame-ancestors 'none'; "

    "base-uri 'self'; "

    "form-action 'self';"

)


# ==========================================================
# SECURITY MIDDLEWARE
# ==========================================================


class SecurityHeadersMiddleware(
    BaseHTTPMiddleware,
):
    """
    Security headers middleware.
    """

    async def dispatch(

        self,

        request: Request,

        call_next: Callable,

    ):

        response = await call_next(

            request,

        )

        for header, value in (

            DEFAULT_SECURITY_HEADERS.items()

        ):

            response.headers[

                header

            ] = value

        response.headers[

            "Content-Security-Policy"

        ] = DEFAULT_CSP

        # =============================================
        # Remove Information Disclosure
        # =============================================

        response.headers.pop(

            "Server",

            None,

        )

        response.headers.pop(

            "X-Powered-By",

            None,

        )

        return response


# ==========================================================
# HELPERS
# ==========================================================


def security_headers(

) -> dict:

    """
    Return configured headers.
    """

    headers = dict(

        DEFAULT_SECURITY_HEADERS,

    )

    headers[

        "Content-Security-Policy"

    ] = DEFAULT_CSP

    return headers


# ==========================================================
# VALIDATION
# ==========================================================


def validate_headers(

) -> bool:
    """
    Validate configuration.
    """

    required = [

        "Strict-Transport-Security",

        "X-Frame-Options",

        "X-Content-Type-Options",

        "Content-Security-Policy",

    ]

    configured = security_headers()

    return all(

        header in configured

        for header

        in required

    )


# ==========================================================
# SECURITY SCORE
# ==========================================================


def security_score(

) -> dict:
    """
    Basic security assessment.
    """

    configured = security_headers()

    score = 0

    checks = {

        "HSTS":

            "Strict-Transport-Security",

        "CSP":

            "Content-Security-Policy",

        "Frame Protection":

            "X-Frame-Options",

        "Content Type":

            "X-Content-Type-Options",

        "Referrer Policy":

            "Referrer-Policy",

        "Permissions Policy":

            "Permissions-Policy",

        "XSS Protection":

            "X-XSS-Protection",

    }

    results = {}

    for name, header in checks.items():

        enabled = (

            header

            in configured

        )

        results[name] = enabled

        if enabled:

            score += 1

    return {

        "score":

            score,

        "maximum":

            len(

                checks,

            ),

        "percentage":

            round(

                score

                /

                len(checks)

                *

                100,

                2,

            ),

        "checks":

            results,

    }


# ==========================================================
# EXPORTS
# ==========================================================


__all__ = [

    "DEFAULT_SECURITY_HEADERS",

    "DEFAULT_CSP",

    "SecurityHeadersMiddleware",

    "security_headers",

    "validate_headers",

    "security_score",

]