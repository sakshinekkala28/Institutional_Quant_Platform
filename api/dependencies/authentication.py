"""
====================================================================
Institutional Quant Platform

Authentication Dependency

Author : Institutional Quant Platform

Purpose
-------
Authentication dependency providers.

Provides

• Current User
• JWT Validation
• API Key Validation
• Anonymous User
• User Claims
• Authentication Status

Used By

• FastAPI Routers
• Authorization Dependency
• Middleware

====================================================================
"""

from __future__ import annotations

from typing import Any

from fastapi import Depends
from fastapi import HTTPException
from fastapi import Request
from fastapi.security import APIKeyHeader
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.security import HTTPBearer


# ==========================================================
# SECURITY SCHEMES
# ==========================================================


bearer_scheme = HTTPBearer(

    auto_error=False,

)

api_key_scheme = APIKeyHeader(

    name="X-API-Key",

    auto_error=False,

)


# ==========================================================
# CURRENT USER
# ==========================================================


def get_current_user(

    request: Request,

) -> dict[str, Any]:
    """
    Current authenticated user.
    """

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
# OPTIONAL USER
# ==========================================================


def get_optional_user(

    request: Request,

) -> dict[str, Any] | None:
    """
    Return authenticated user
    or None.
    """

    return getattr(

        request.state,

        "user",

        None,

    )


# ==========================================================
# USERNAME
# ==========================================================


def get_username(

    user: dict = Depends(

        get_current_user,

    ),

) -> str:

    return user.get(

        "username",

        "",

    )


# ==========================================================
# ROLE
# ==========================================================


def get_role(

    user: dict = Depends(

        get_current_user,

    ),

) -> str:

    return user.get(

        "role",

        "",

    )


# ==========================================================
# CLAIMS
# ==========================================================


def get_claims(

    user: dict = Depends(

        get_current_user,

    ),

) -> dict:

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


# ==========================================================
# JWT VALIDATION
# ==========================================================


def validate_bearer_token(

    credentials: HTTPAuthorizationCredentials | None = Depends(

        bearer_scheme,

    ),

) -> str | None:
    """
    Placeholder.

    Replace with JWT validation.
    """

    if credentials is None:

        return None

    token = credentials.credentials

    if len(token) < 10:

        raise HTTPException(

            status_code=401,

            detail="Invalid bearer token.",

        )

    return token


# ==========================================================
# API KEY VALIDATION
# ==========================================================


def validate_api_key(

    api_key: str | None = Depends(

        api_key_scheme,

    ),

) -> str | None:
    """
    Placeholder.

    Replace with database lookup.
    """

    if api_key is None:

        return None

    if len(api_key) < 8:

        raise HTTPException(

            status_code=401,

            detail="Invalid API key.",

        )

    return api_key


# ==========================================================
# SERVICE ACCOUNT
# ==========================================================


def get_service_account(

    api_key: str | None = Depends(

        validate_api_key,

    ),

) -> dict | None:

    if api_key is None:

        return None

    return {

        "username":

            "service",

        "role":

            "system",

        "api_key":

            api_key,

    }


# ==========================================================
# ANONYMOUS
# ==========================================================


def anonymous_user(

) -> dict:

    return {

        "username":

            "anonymous",

        "role":

            "guest",

        "authenticated":

            False,

    }


# ==========================================================
# AUTH SUMMARY
# ==========================================================


def authentication_summary(

    request: Request,

) -> dict:

    user = getattr(

        request.state,

        "user",

        None,

    )

    return {

        "authenticated":

            user is not None,

        "username":

            (

                user.get(

                    "username",

                )

                if user

                else None

            ),

        "role":

            (

                user.get(

                    "role",

                )

                if user

                else None

            ),

    }


# ==========================================================
# EXPORTS
# ==========================================================


__all__ = [

    "bearer_scheme",

    "api_key_scheme",

    "get_current_user",

    "get_optional_user",

    "get_username",

    "get_role",

    "get_claims",

    "is_authenticated",

    "validate_bearer_token",

    "validate_api_key",

    "get_service_account",

    "anonymous_user",

    "authentication_summary",

]