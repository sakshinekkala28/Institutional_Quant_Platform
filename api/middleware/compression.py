"""
====================================================================
Institutional Quant Platform

Compression Middleware

Author : Institutional Quant Platform

Purpose
-------
Response compression middleware.

Features

• GZip Compression
• Brotli Ready
• Configurable Threshold
• Content-Type Filtering
• Compression Metrics
• Response Optimization

Used By

• FastAPI
• API Gateway
• Monitoring

====================================================================
"""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware


logger = logging.getLogger(

    "institutional.compression",

)


# ==========================================================
# CONSTANTS
# ==========================================================


DEFAULT_MINIMUM_SIZE = 1024

DEFAULT_COMPRESS_LEVEL = 6


COMPRESSIBLE_CONTENT_TYPES = [

    "application/json",

    "application/javascript",

    "application/xml",

    "application/octet-stream",

    "text/plain",

    "text/html",

    "text/css",

    "text/javascript",

    "text/csv",

]


# ==========================================================
# REGISTER GZIP
# ==========================================================


def register_gzip(

    app: FastAPI,

    minimum_size: int = DEFAULT_MINIMUM_SIZE,

    compresslevel: int = DEFAULT_COMPRESS_LEVEL,

) -> None:
    """
    Register GZip middleware.
    """

    app.add_middleware(

        GZipMiddleware,

        minimum_size=minimum_size,

        compresslevel=compresslevel,

    )

    logger.info(

        "GZip middleware registered.",

    )


# ==========================================================
# CONTENT TYPE
# ==========================================================


def compressible(

    content_type: str,

) -> bool:
    """
    Check whether content should
    be compressed.
    """

    if not content_type:

        return False

    return any(

        content_type.startswith(

            item,

        )

        for item

        in COMPRESSIBLE_CONTENT_TYPES

    )


# ==========================================================
# SUMMARY
# ==========================================================


def compression_summary(

) -> dict:

    return {

        "algorithm":

            "gzip",

        "minimum_size":

            DEFAULT_MINIMUM_SIZE,

        "compression_level":

            DEFAULT_COMPRESS_LEVEL,

        "supported_types":

            COMPRESSIBLE_CONTENT_TYPES,

    }


# ==========================================================
# ESTIMATION
# ==========================================================


def estimated_savings(

    original_size: int,

    ratio: float = 0.35,

) -> dict:
    """
    Estimate compressed size.
    """

    compressed = int(

        original_size

        *

        ratio

    )

    saved = (

        original_size

        -

        compressed

    )

    return {

        "original_bytes":

            original_size,

        "compressed_bytes":

            compressed,

        "saved_bytes":

            saved,

        "saving_percent":

            round(

                (

                    saved

                    /

                    original_size

                )

                *

                100,

                2,

            )

        if original_size

        else 0,

    }


# ==========================================================
# BROTLI PLACEHOLDER
# ==========================================================


class BrotliConfiguration:
    """
    Future Brotli configuration.

    Placeholder for production
    reverse proxy integration.
    """

    enabled: bool = False

    quality: int = 5

    mode: str = "generic"

    lgwin: int = 22

    lgblock: int = 0


# ==========================================================
# VALIDATION
# ==========================================================


def validate_configuration(

    minimum_size: int,

    compresslevel: int,

) -> bool:
    """
    Validate compression config.
    """

    if minimum_size < 0:

        return False

    if compresslevel < 1:

        return False

    if compresslevel > 9:

        return False

    return True


# ==========================================================
# EXPORTS
# ==========================================================


__all__ = [

    "DEFAULT_MINIMUM_SIZE",

    "DEFAULT_COMPRESS_LEVEL",

    "COMPRESSIBLE_CONTENT_TYPES",

    "register_gzip",

    "compressible",

    "compression_summary",

    "estimated_savings",

    "BrotliConfiguration",

    "validate_configuration",

]