"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Platform Events

Central event definitions.

=========================================================
"""

from __future__ import annotations

from enum import StrEnum

# ==========================================================
# PLATFORM EVENTS
# ==========================================================


class Event(StrEnum):
    # ------------------------------------------------------
    # PLATFORM
    # ------------------------------------------------------

    PLATFORM_STARTED = "platform.started"

    PLATFORM_FINISHED = "platform.finished"

    PLATFORM_FAILED = "platform.failed"

    # ------------------------------------------------------
    # PIPELINES
    # ------------------------------------------------------

    PIPELINE_STARTED = "pipeline.started"

    PIPELINE_FINISHED = "pipeline.finished"

    PIPELINE_FAILED = "pipeline.failed"

    # ------------------------------------------------------
    # ENGINES
    # ------------------------------------------------------

    ENGINE_STARTED = "engine.started"

    ENGINE_FINISHED = "engine.finished"

    ENGINE_FAILED = "engine.failed"

    # ------------------------------------------------------
    # EXECUTION
    # ------------------------------------------------------

    EXECUTION_STARTED = "execution.started"

    EXECUTION_FINISHED = "execution.finished"

    EXECUTION_FAILED = "execution.failed"

    # ------------------------------------------------------
    # RESOURCE
    # ------------------------------------------------------

    RESOURCE_REGISTERED = "resource.registered"

    RESOURCE_RELEASED = "resource.released"

    # ------------------------------------------------------
    # HEALTH
    # ------------------------------------------------------

    HEALTH_CHECK = "health.check"

    # ------------------------------------------------------
    # PLUGINS
    # ------------------------------------------------------

    PLUGIN_REGISTERED = "plugin.registered"

    PLUGIN_LOADED = "plugin.loaded"

    # ------------------------------------------------------
    # CONFIG
    # ------------------------------------------------------

    CONFIG_LOADED = "config.loaded"
