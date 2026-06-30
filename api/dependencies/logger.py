"""
====================================================================
Institutional Quant Platform

Logger Dependencies

Author : Institutional Quant Platform

Purpose
-------
FastAPI dependency providers for logging services.

Provides

• Root Logger
• Structured Logger
• Audit Logger
• Performance Logger
• Event Logger
• Security Logger
• Request Logger
• Logging Configuration

Used By

• All Routers
• Middleware
• Services
• Background Workers

====================================================================
"""

from __future__ import annotations

import logging
from functools import lru_cache


# ==========================================================
# ROOT LOGGER
# ==========================================================


@lru_cache
def get_logger(

) -> logging.Logger:
    """
    Root application logger.
    """

    return logging.getLogger(

        "institutional",

    )


# ==========================================================
# API LOGGER
# ==========================================================


@lru_cache
def get_api_logger(

) -> logging.Logger:
    """
    API logger.
    """

    return logging.getLogger(

        "institutional.api",

    )


# ==========================================================
# AUDIT LOGGER
# ==========================================================


@lru_cache
def get_audit_logger(

) -> logging.Logger:
    """
    Audit logger.
    """

    return logging.getLogger(

        "institutional.audit",

    )


# ==========================================================
# PERFORMANCE LOGGER
# ==========================================================


@lru_cache
def get_performance_logger(

) -> logging.Logger:
    """
    Performance logger.
    """

    return logging.getLogger(

        "institutional.performance",

    )


# ==========================================================
# EVENT LOGGER
# ==========================================================


@lru_cache
def get_event_logger(

) -> logging.Logger:
    """
    Event logger.
    """

    return logging.getLogger(

        "institutional.events",

    )


# ==========================================================
# SECURITY LOGGER
# ==========================================================


@lru_cache
def get_security_logger(

) -> logging.Logger:
    """
    Security logger.
    """

    return logging.getLogger(

        "institutional.security",

    )


# ==========================================================
# REQUEST LOGGER
# ==========================================================


@lru_cache
def get_request_logger(

) -> logging.Logger:
    """
    Request logger.
    """

    return logging.getLogger(

        "institutional.request",

    )


# ==========================================================
# LOGGER CONFIGURATION
# ==========================================================


def configure_logging(

    level: str = "INFO",

) -> None:
    """
    Configure application logging.
    """

    logging.basicConfig(

        level=getattr(

            logging,

            level.upper(),

            logging.INFO,

        ),

        format=(

            "%(asctime)s | "

            "%(levelname)s | "

            "%(name)s | "

            "%(message)s"

        ),

    )


# ==========================================================
# LOGGER SUMMARY
# ==========================================================


def logger_summary(

) -> dict:
    """
    Logging services summary.
    """

    return {

        "loggers": [

            "institutional",

            "institutional.api",

            "institutional.audit",

            "institutional.performance",

            "institutional.events",

            "institutional.security",

            "institutional.request",

        ],

        "count": 7,

    }


# ==========================================================
# LOGGING HEALTH
# ==========================================================


def logger_health(

) -> dict:
    """
    Logging dependency health.
    """

    return {

        "service": "Logging",

        "status": "healthy",

        "configured": True,

    }


# ==========================================================
# EXPORTS
# ==========================================================


__all__ = [

    "get_logger",

    "get_api_logger",

    "get_audit_logger",

    "get_performance_logger",

    "get_event_logger",

    "get_security_logger",

    "get_request_logger",

    "configure_logging",

    "logger_summary",

    "logger_health",

]