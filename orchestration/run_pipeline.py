"""
====================================================================
Institutional Quant Platform

Daily Institutional Pipeline

Author : Institutional Quant Platform

Purpose
-------
Daily production orchestration.

Responsibilities

• Initialize Platform
• Execute All Engines
• Generate All Data Artifacts
• Validate Outputs
• Publish Reports
• Update Dashboard
• Refresh API Cache

====================================================================
"""

from __future__ import annotations

import logging
import time
from pathlib import Path

from orchestration.pipeline import InstitutionalPipeline
from orchestration.context import PipelineContext
from orchestration.workflow import PIPELINE

logger = logging.getLogger(__name__)


def banner() -> None:

    print()

    print("=" * 80)

    print("Institutional Quant Platform")

    print("Daily Production Pipeline")

    print("=" * 80)

    print()


def main() -> None:

    banner()

    start = time.perf_counter()

    context = PipelineContext()

    pipeline = InstitutionalPipeline(

        workflow=PIPELINE,

        context=context,

    )

    pipeline.initialize()

    pipeline.execute()

    pipeline.publish()

    pipeline.shutdown()

    elapsed = time.perf_counter() - start

    logger.info(

        "Pipeline completed in %.2f seconds",

        elapsed,

    )


if __name__ == "__main__":

    main()