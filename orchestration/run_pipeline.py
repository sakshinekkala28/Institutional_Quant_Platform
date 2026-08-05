"""
=========================================================
INSTITUTIONAL QUANT PLATFORM
=========================================================

Run Pipeline

Platform entry point.

Responsibilities
----------------
• Parse CLI arguments
• Configure orchestrator
• Execute platform
• Handle failures
• Generate execution summary
• Return proper exit codes

Usage
-----

python -m orchestration.run_pipeline

python -m orchestration.run_pipeline \
    --executor parallel

python -m orchestration.run_pipeline \
    --executor retry

=========================================================
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from orchestration.models.engine_status import EngineStatus
from orchestration.orchestrator import Orchestrator

logger = logging.getLogger(__name__)


# =========================================================
# CLI
# =========================================================


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.
    """

    parser = argparse.ArgumentParser(description=("Institutional Quant Platform"))

    parser.add_argument(
        "--executor",
        default="sequential",
        choices=[
            "sequential",
            "parallel",
            "retry",
            "distributed",
        ],
        help="Execution backend.",
    )

    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print execution summary.",
    )

    parser.add_argument(
        "--report",
        type=Path,
        help="Export execution report.",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose logging.",
    )

    return parser.parse_args()


# =========================================================
# LOGGING
# =========================================================


def configure_logging(
    verbose: bool,
) -> None:
    """
    Configure platform logging.
    """

    level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=level,
        format=("%(asctime)s %(levelname)s %(name)s : %(message)s"),
    )


# =========================================================
# MAIN
# =========================================================


def main() -> int:
    """
    Platform entry point.
    """

    args = parse_arguments()

    configure_logging(
        args.verbose,
    )

    orchestrator = Orchestrator(
        executor=args.executor,
    )

    try:
        result = orchestrator.run()

        # ----------------------------------------------
        # Optional report export
        # ----------------------------------------------

        if args.report:
            orchestrator.report.save(
                args.report,
            )

            logger.info(
                "Execution report written to %s",
                args.report,
            )

        # ----------------------------------------------
        # Optional summary
        # ----------------------------------------------

        if args.summary:
            print()

            print("=" * 70)

            print("PLATFORM EXECUTION SUMMARY")

            print("=" * 70)

            for key, value in (orchestrator.summary()).items():
                print(f"{key:<20}: {value}")

            print("=" * 70)

            print()

        return 0 if result.status == EngineStatus.SUCCESS else 1

    except KeyboardInterrupt:
        logger.warning("Execution interrupted.")

        return 130

    except Exception:
        logger.exception("Platform execution failed.")

        return 1


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    sys.exit(main())
