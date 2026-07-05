"""
Institutional Quant Platform
============================

Adapter Factory

Dynamically wraps existing engines without modifying them.
"""

from __future__ import annotations

import inspect
from typing import Any, Callable

from orchestration.base_engine import BaseEngine


class GenericEngineAdapter(BaseEngine):
    """
    Wraps an existing class or callable as a BaseEngine.
    """

    TARGET = None

    def execute(self, context):

        if self.TARGET is None:
            raise RuntimeError(f"{self.NAME}: TARGET not configured.")

        target = self.TARGET

        # Function
        if inspect.isfunction(target):
            return target()

        # Existing class
        if inspect.isclass(target):

            instance = target()

            if hasattr(instance, "run") and callable(instance.run):
                return instance.run()

            if hasattr(instance, "execute") and callable(instance.execute):
                return instance.execute()

            raise RuntimeError(
                f"{self.NAME}: Target class has no run() or execute()."
            )

        # Callable object
        if callable(target):
            return target()

        raise RuntimeError(
            f"{self.NAME}: Unsupported target type {type(target)}."
        )


def create_adapter(
    *,
    name: str,
    stage: str,
    target: Callable[..., Any] | type,
    depends_on=None,
    outputs=None,
    description="",
):
    """
    Dynamically create a BaseEngine adapter.
    """

    depends_on = depends_on or []
    outputs = outputs or []

    attrs = {
        "NAME": name,
        "STAGE": stage,
        "DESCRIPTION": description,
        "DEPENDS_ON": depends_on,
        "OUTPUTS": outputs,
        "TARGET": target,
    }

    return type(
        f"{name.title().replace('_', '')}Adapter",
        (GenericEngineAdapter,),
        attrs,
    )