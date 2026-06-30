"""
====================================================================
Institutional Quant Platform

Configuration Dependency

Author : Institutional Quant Platform

Purpose
-------
FastAPI dependency providers for application configuration.

Provides

• Settings
• Environment
• Runtime Configuration
• Feature Flags
• API Information

Used By

• API Routers
• Middleware
• Services
• Background Jobs

====================================================================
"""

from __future__ import annotations

from functools import lru_cache

from api.config import Settings
from api.config import get_settings as _get_settings


# ==========================================================
# SETTINGS
# ==========================================================


@lru_cache
def get_settings(

) -> Settings:
    """
    Return application settings.
    """

    return _get_settings()


# ==========================================================
# ENVIRONMENT
# ==========================================================


def get_environment(

) -> str:
    """
    Current environment.
    """

    return (

        get_settings()

        .ENVIRONMENT

    )


# ==========================================================
# DEBUG
# ==========================================================


def is_debug(

) -> bool:
    """
    Debug mode.
    """

    return (

        get_settings()

        .DEBUG

    )


# ==========================================================
# APPLICATION
# ==========================================================


def application_name(

) -> str:
    """
    Application name.
    """

    return (

        get_settings()

        .APP_NAME

    )


def application_version(

) -> str:
    """
    Application version.
    """

    return (

        get_settings()

        .APP_VERSION

    )


# ==========================================================
# API
# ==========================================================


def api_host(

) -> str:

    return (

        get_settings()

        .API_HOST

    )


def api_port(

) -> int:

    return (

        get_settings()

        .API_PORT

    )


def api_prefix(

) -> str:

    return (

        get_settings()

        .API_PREFIX

    )


# ==========================================================
# DATABASE
# ==========================================================


def database_url(

) -> str:

    return (

        get_settings()

        .DATABASE_URL

    )


# ==========================================================
# LOGGING
# ==========================================================


def log_level(

) -> str:

    return (

        get_settings()

        .LOG_LEVEL

    )


# ==========================================================
# CACHE
# ==========================================================


def cache_enabled(

) -> bool:

    return (

        get_settings()

        .CACHE_ENABLED

    )


def cache_ttl(

) -> int:

    return (

        get_settings()

        .CACHE_TTL_SECONDS

    )


# ==========================================================
# TELEMETRY
# ==========================================================


def telemetry_enabled(

) -> bool:

    return (

        get_settings()

        .ENABLE_TELEMETRY

    )


def metrics_enabled(

) -> bool:

    return (

        get_settings()

        .ENABLE_METRICS

    )


def health_checks_enabled(

) -> bool:

    return (

        get_settings()

        .ENABLE_HEALTH_CHECK

    )


# ==========================================================
# FEATURE FLAGS
# ==========================================================


def feature_flags(

) -> dict:

    settings = get_settings()

    return {

        "cache":

            settings.CACHE_ENABLED,

        "telemetry":

            settings.ENABLE_TELEMETRY,

        "metrics":

            settings.ENABLE_METRICS,

        "health_checks":

            settings.ENABLE_HEALTH_CHECK,

        "debug":

            settings.DEBUG,

    }


# ==========================================================
# APPLICATION SUMMARY
# ==========================================================


def configuration_summary(

) -> dict:

    settings = get_settings()

    return {

        "Application":

            settings.APP_NAME,

        "Version":

            settings.APP_VERSION,

        "Environment":

            settings.ENVIRONMENT,

        "Host":

            settings.API_HOST,

        "Port":

            settings.API_PORT,

        "Database":

            settings.DATABASE_URL,

        "Logging":

            settings.LOG_LEVEL,

        "Cache":

            settings.CACHE_ENABLED,

        "Telemetry":

            settings.ENABLE_TELEMETRY,

        "Metrics":

            settings.ENABLE_METRICS,

    }


# ==========================================================
# EXPORTS
# ==========================================================


__all__ = [

    "get_settings",

    "get_environment",

    "is_debug",

    "application_name",

    "application_version",

    "api_host",

    "api_port",

    "api_prefix",

    "database_url",

    "log_level",

    "cache_enabled",

    "cache_ttl",

    "telemetry_enabled",

    "metrics_enabled",

    "health_checks_enabled",

    "feature_flags",

    "configuration_summary",

]