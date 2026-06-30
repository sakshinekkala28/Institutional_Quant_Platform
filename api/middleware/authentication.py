"""
====================================================================
Institutional Quant Platform

Authentication Middleware

Author : Institutional Quant Platform

Purpose
-------
Authentication middleware for FastAPI.

Features

• Bearer Token Authentication
• JWT Support
• API Key Authentication
• User Context Injection
• Protected Routes
• Anonymous Route Support

Used By

• All API Routers
• Authorization Middleware

====================================================================
"""

from __future__ import annotations

from datetime import datetime
from typing import Callable

from fastapi import HTTPException
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


# ==========================================================
# AUTHENTICATION MIDDLEWARE
# ==========================================================


class AuthenticationMiddleware(
    BaseHTTPMiddleware,
):
    """
    Authentication middleware.
    """

    def __init__(

        self,

        app,

        api_key: str | None = None,

        excluded_paths: list[str] | None = None,

    ):

        super().__init__(

            app,

        )

        self.api_key = api_key

        self.excluded_paths = (

            excluded_paths

            or

            [

                "/",

                "/docs",

                "/redoc",

                "/openapi.json",

                "/health",

                "/version",

                "/metrics",

            ]

        )

    # =====================================================
    # DISPATCH
    # =====================================================

    async def dispatch(

        self,

        request: Request,

        call_next: Callable,

    ):

        path = request.url.path

        if path in self.excluded_paths:

            return await call_next(

                request,

            )

        authorization = (

            request.headers.get(

                "Authorization",

            )

        )

        api_key = (

            request.headers.get(

                "X-API-Key",

            )

        )

        # =================================================
        # API KEY
        # =================================================

        if (

            self.api_key

            and

            api_key == self.api_key

        ):

            request.state.user = {

                "username":

                    "api_key_user",

                "role":

                    "system",

                "authenticated":

                    True,

            }

            return await call_next(

                request,

            )

        # =================================================
        # BEARER TOKEN
        # =================================================

        if (

            authorization

            and

            authorization.startswith(

                "Bearer "

            )

        ):

            token = (

                authorization.replace(

                    "Bearer ",

                    "",

                )

            )

            if self.validate_token(

                token,

            ):

                request.state.user = {

                    "username":

                        "authenticated_user",

                    "role":

                        "trader",

                    "authenticated":

                        True,

                }

                return await call_next(

                    request,

                )

        # =================================================
        # FAILURE
        # =================================================

        return JSONResponse(

            status_code=401,

            content={

                "success":

                    False,

                "error":

                    "Authentication Failed",

                "status_code":

                    401,

                "timestamp":

                    datetime.utcnow().isoformat(),

            },

        )

    # =====================================================
    # TOKEN VALIDATION
    # =====================================================

    @staticmethod
    def validate_token(

        token: str,

    ) -> bool:
        """
        Placeholder validation.

        Replace with

        • JWT
        • OAuth2
        • OpenID Connect
        • LDAP
        """

        return (

            len(

                token,

            )

            >

            10

        )


# ==========================================================
# CURRENT USER
# ==========================================================


def get_current_user(

    request: Request,

):

    user = getattr(

        request.state,

        "user",

        None,

    )

    if user is None:

        raise HTTPException(

            status_code=401,

            detail="Authentication required.",

        )

    return user


# ==========================================================
# AUTHENTICATED
# ==========================================================


def is_authenticated(

    request: Request,

) -> bool:

    return (

        getattr(

            request.state,

            "user",

            None,

        )

        is not None

    )