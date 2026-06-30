"""
====================================================================
Institutional Quant Platform

CORS Middleware

Author : Institutional Quant Platform

Purpose
-------
Centralized Cross-Origin Resource Sharing (CORS)
configuration for FastAPI.

Features

• Configurable Origins
• Configurable Methods
• Configurable Headers
• Credentials Support
• Production Ready
• Environment Aware

Used By

• FastAPI
• Web Dashboard
• Streamlit
• React
• Vue
• Angular

====================================================================
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.config import get_settings


# ==========================================================
# REGISTER CORS
# ==========================================================


def register_cors(

    app: FastAPI,

) -> None:
    """
    Register CORS middleware.
    """

    settings = get_settings()

    app.add_middleware(

        CORSMiddleware,

        allow_origins=(
            settings.ALLOWED_ORIGINS
        ),

        allow_credentials=True,

        allow_methods=(
            settings.ALLOWED_METHODS
        ),

        allow_headers=(
            settings.ALLOWED_HEADERS
        ),

        expose_headers=[

            "X-Correlation-ID",

            "X-Response-Time",

            "X-Request-ID",

        ],

        max_age=3600,

    )


# ==========================================================
# DEVELOPMENT CORS
# ==========================================================


def register_development_cors(

    app: FastAPI,

) -> None:
    """
    Development CORS.
    """

    app.add_middleware(

        CORSMiddleware,

        allow_origins=[

            "*",

        ],

        allow_credentials=True,

        allow_methods=[

            "*",

        ],

        allow_headers=[

            "*",

        ],

    )


# ==========================================================
# PRODUCTION CORS
# ==========================================================


def register_production_cors(

    app: FastAPI,

) -> None:
    """
    Production CORS.
    """

    settings = get_settings()

    app.add_middleware(

        CORSMiddleware,

        allow_origins=(
            settings.ALLOWED_ORIGINS
        ),

        allow_credentials=True,

        allow_methods=[

            "GET",

            "POST",

            "PUT",

            "PATCH",

            "DELETE",

        ],

        allow_headers=[

            "Authorization",

            "Content-Type",

            "X-API-Key",

            "X-Request-ID",

        ],

        expose_headers=[

            "X-Correlation-ID",

            "X-Response-Time",

        ],

        max_age=7200,

    )


# ==========================================================
# REGISTER AUTOMATICALLY
# ==========================================================


def configure_cors(

    app: FastAPI,

) -> None:
    """
    Environment-aware registration.
    """

    settings = get_settings()

    if (

        settings.ENVIRONMENT.lower()

        ==

        "development"

    ):

        register_development_cors(

            app,

        )

    else:

        register_production_cors(

            app,

        )


# ==========================================================
# CORS SUMMARY
# ==========================================================


def cors_summary(

) -> dict:
    """
    Current CORS configuration.
    """

    settings = get_settings()

    return {

        "Environment":

            settings.ENVIRONMENT,

        "AllowedOrigins":

            settings.ALLOWED_ORIGINS,

        "AllowedMethods":

            settings.ALLOWED_METHODS,

        "AllowedHeaders":

            settings.ALLOWED_HEADERS,

        "Credentials":

            True,

    }


# ==========================================================
# VALIDATION
# ==========================================================


def validate_cors_configuration(

) -> bool:
    """
    Validate CORS settings.
    """

    settings = get_settings()

    return (

        len(

            settings.ALLOWED_ORIGINS,

        )

        >

        0

    )


# ==========================================================
# EXPORTS
# ==========================================================


__all__ = [

    "register_cors",

    "register_development_cors",

    "register_production_cors",

    "configure_cors",

    "cors_summary",

    "validate_cors_configuration",

]