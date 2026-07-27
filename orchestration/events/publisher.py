"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Event Publisher

High-level interface for publishing platform events.

Responsibilities
----------------
• Publish platform events
• Publish pipeline events
• Publish engine events
• Decouple producers from EventBus

=========================================================
"""

from __future__ import annotations

from typing import Any

from orchestration.events.event_bus import EventBus
from orchestration.events.events import Event

# ==========================================================
# PUBLISHER
# ==========================================================


class Publisher:
    """
    High-level event publisher.
    """

    def __init__(
        self,
        event_bus: EventBus,
    ) -> None:

        self._bus = event_bus

    # =====================================================
    # GENERIC
    # =====================================================

    def publish(
        self,
        event: Event,
        **payload: Any,
    ) -> None:
        """
        Publish an event.
        """

        self._bus.publish(
            event.value,
            **payload,
        )

    # =====================================================
    # PLATFORM
    # =====================================================

    def platform_started(
        self,
        **payload: Any,
    ) -> None:

        self.publish(
            Event.PLATFORM_STARTED,
            **payload,
        )

    # -----------------------------------------------------

    def platform_finished(
        self,
        **payload: Any,
    ) -> None:

        self.publish(
            Event.PLATFORM_FINISHED,
            **payload,
        )

    # -----------------------------------------------------

    def platform_failed(
        self,
        **payload: Any,
    ) -> None:

        self.publish(
            Event.PLATFORM_FAILED,
            **payload,
        )

    # =====================================================
    # PIPELINES
    # =====================================================

    def pipeline_started(
        self,
        **payload: Any,
    ) -> None:

        self.publish(
            Event.PIPELINE_STARTED,
            **payload,
        )

    # -----------------------------------------------------

    def pipeline_finished(
        self,
        **payload: Any,
    ) -> None:

        self.publish(
            Event.PIPELINE_FINISHED,
            **payload,
        )

    # -----------------------------------------------------

    def pipeline_failed(
        self,
        **payload: Any,
    ) -> None:

        self.publish(
            Event.PIPELINE_FAILED,
            **payload,
        )

    # =====================================================
    # ENGINES
    # =====================================================

    def engine_started(
        self,
        **payload: Any,
    ) -> None:

        self.publish(
            Event.ENGINE_STARTED,
            **payload,
        )

    # -----------------------------------------------------

    def engine_finished(
        self,
        **payload: Any,
    ) -> None:

        self.publish(
            Event.ENGINE_FINISHED,
            **payload,
        )

    # -----------------------------------------------------

    def engine_failed(
        self,
        **payload: Any,
    ) -> None:

        self.publish(
            Event.ENGINE_FAILED,
            **payload,
        )

    # =====================================================
    # EXECUTION
    # =====================================================

    def execution_started(
        self,
        **payload: Any,
    ) -> None:

        self.publish(
            Event.EXECUTION_STARTED,
            **payload,
        )

    # -----------------------------------------------------

    def execution_finished(
        self,
        **payload: Any,
    ) -> None:

        self.publish(
            Event.EXECUTION_FINISHED,
            **payload,
        )

    # -----------------------------------------------------

    def execution_failed(
        self,
        **payload: Any,
    ) -> None:

        self.publish(
            Event.EXECUTION_FAILED,
            **payload,
        )

    # =====================================================
    # RESOURCE
    # =====================================================

    def resource_registered(
        self,
        **payload: Any,
    ) -> None:

        self.publish(
            Event.RESOURCE_REGISTERED,
            **payload,
        )

    # -----------------------------------------------------

    def resource_released(
        self,
        **payload: Any,
    ) -> None:

        self.publish(
            Event.RESOURCE_RELEASED,
            **payload,
        )

    # =====================================================
    # PLUGINS
    # =====================================================

    def plugin_registered(
        self,
        **payload: Any,
    ) -> None:

        self.publish(
            Event.PLUGIN_REGISTERED,
            **payload,
        )

    # -----------------------------------------------------

    def plugin_loaded(
        self,
        **payload: Any,
    ) -> None:

        self.publish(
            Event.PLUGIN_LOADED,
            **payload,
        )

    # =====================================================
    # HEALTH
    # =====================================================

    def health_check(
        self,
        **payload: Any,
    ) -> None:

        self.publish(
            Event.HEALTH_CHECK,
            **payload,
        )

    # =====================================================
    # CONFIG
    # =====================================================

    def config_loaded(
        self,
        **payload: Any,
    ) -> None:

        self.publish(
            Event.CONFIG_LOADED,
            **payload,
        )

    # =====================================================
    # DUNDER
    # =====================================================

    def __repr__(
        self,
    ) -> str:

        return f"{self.__class__.__name__}()"
