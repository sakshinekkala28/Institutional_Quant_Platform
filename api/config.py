"""
====================================================================
Institutional Quant Platform

API Configuration

Author : Institutional Quant Platform

Purpose
-------
Centralized API configuration.

Provides

• Application Settings
• Environment Variables
• CORS Configuration
• API Metadata
• Runtime Configuration

Used By

• FastAPI
• Middleware
• Routers
• Dependencies

====================================================================
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict


# ==========================================================
# SETTINGS
# ==========================================================


class Settings(
    BaseSettings,
):
    """
    Application settings.
    """

    # =====================================================
    # APPLICATION
    # =====================================================

    APP_NAME: str = Field(

        default="Institutional Quant Platform",

    )

    APP_VERSION: str = Field(

        default="1.0.0",

    )

    ENVIRONMENT: str = Field(

        default="development",

    )

    DEBUG: bool = Field(

        default=False,

    )

    # =====================================================
    # API
    # =====================================================

    API_HOST: str = Field(

        default="0.0.0.0",

    )

    API_PORT: int = Field(

        default=8000,

    )

    API_PREFIX: str = Field(

        default="/api/v1",

    )

    # =====================================================
    # SECURITY
    # =====================================================

    SECRET_KEY: str = Field(

        default="CHANGE_ME",

    )

    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(

        default=60,

    )

    # =====================================================
    # CORS
    # =====================================================

    ALLOWED_ORIGINS: list[str] = Field(

        default=[

            "*",

        ],

    )

    ALLOWED_METHODS: list[str] = Field(

        default=[

            "*",

        ],

    )

    ALLOWED_HEADERS: list[str] = Field(

        default=[

            "*",

        ],

    )

    # =====================================================
    # DATABASE
    # =====================================================

    DATABASE_URL: str = Field(

        default="sqlite:///institutional_quant.db",

    )

    # =====================================================
    # LOGGING
    # =====================================================

    LOG_LEVEL: str = Field(

        default="INFO",

    )

    LOG_DIRECTORY: Path = Field(

        default=Path(

            "logs",

        ),

    )

    # =====================================================
    # MONITORING
    # =====================================================

    ENABLE_METRICS: bool = Field(

        default=True,

    )

    ENABLE_TELEMETRY: bool = Field(

        default=True,

    )

    ENABLE_HEALTH_CHECK: bool = Field(

        default=True,

    )

    # =====================================================
    # CACHE
    # =====================================================

    CACHE_ENABLED: bool = Field(

        default=True,

    )

    CACHE_TTL_SECONDS: int = Field(

        default=300,

    )

    # =====================================================
    # MODEL CONFIG
    # =====================================================

    model_config = SettingsConfigDict(

        env_file=".env",

        env_file_encoding="utf-8",

        case_sensitive=True,

        extra="ignore",

    )


# ==========================================================
# SETTINGS FACTORY
# ==========================================================


@lru_cache
def get_settings(

) -> Settings:
    """
    Cached settings instance.
    """

    return Settings()


# ==========================================================
# API METADATA
# ==========================================================


def api_metadata(

) -> dict:
    """
    FastAPI metadata.
    """

    settings = get_settings()

    return {

        "title":

            settings.APP_NAME,

        "version":

            settings.APP_VERSION,

        "description":

            (

                "Institutional-grade "

                "quantitative investment "

                "platform."

            ),

        "contact": {

            "name":

                "Institutional Quant Platform",

        },

    }


# ==========================================================
# CORS CONFIGURATION
# ==========================================================


def cors_configuration(

) -> dict:
    """
    CORS settings.
    """

    settings = get_settings()

    return {

        "allow_origins":

            settings.ALLOWED_ORIGINS,

        "allow_credentials":

            True,

        "allow_methods":

            settings.ALLOWED_METHODS,

        "allow_headers":

            settings.ALLOWED_HEADERS,

    }


# ==========================================================
# RUNTIME SUMMARY
# ==========================================================


def summary(

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

        "Debug":

            settings.DEBUG,

        "Metrics":

            settings.ENABLE_METRICS,

        "Telemetry":

            settings.ENABLE_TELEMETRY,

    }