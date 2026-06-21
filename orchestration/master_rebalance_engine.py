# ==========================================================
# MASTER REBALANCE ENGINE
# Institutional Quant Platform
# ==========================================================

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import logging
import pandas as pd

from alpha.signal_engine import (
    SignalEngine
)

from portfolio.portfolio_engine import (
    PortfolioEngine
)

from risk.risk_engine import (
    RiskEngine
)

# ==========================================================
# LOGGING
# ==========================================================

logging.basicConfig(

    level=logging.INFO,

    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(message)s"
    )

)

logger = logging.getLogger(__name__)


# ==========================================================
# MASTER ENGINE
# ==========================================================

class MasterRebalanceEngine:

    def __init__(self):

        self.start_time = datetime.now()

        self.data = None

        self.alpha_universe = None

        self.portfolio = None

        self.risk_report = None

        logger.info(
            "Institutional Quant Platform Started"
        )

    # ======================================================
    # LOAD DATA
    # ======================================================

    def load_data(self):

        signal_engine = SignalEngine()

        self.data = (
            signal_engine.load_data()
        )

        logger.info(
            "Data Loaded Successfully"
        )

        return self.data

    # ======================================================
    # BUILD ALPHA UNIVERSE
    # ======================================================

    def build_alpha_universe(self):

        signal_engine = SignalEngine()

        self.alpha_universe = (

            signal_engine
            .build_alpha_universe(
                self.data
            )

        )

        logger.info(

            f"Alpha Universe: "
            f"{len(self.alpha_universe):,}"

        )

        return self.alpha_universe
    
    # ======================================================
    # PORTFOLIO CONSTRUCTION
    # ======================================================

    def construct_portfolio(self):

        portfolio_engine = (

            PortfolioEngine(
                target_holdings=40
            )

        )

        self.portfolio = (

            portfolio_engine
            .construct(
                self.alpha_universe
            )

        )

        logger.info(

            f"Portfolio Holdings: "
            f"{len(self.portfolio)}"

        )

        return self.portfolio

    # ======================================================
    # RISK VALIDATION
    # ======================================================

    def run_risk_checks(self):

        risk_engine = RiskEngine()

        self.risk_report = (

            risk_engine.evaluate(
                self.portfolio
            )

        )

        logger.info(
            "Risk Validation Complete"
        )

        return self.risk_report
    
    # ======================================================
    # SAVE OUTPUTS
    # ======================================================

    def save_outputs(self):

        output_dir = (

            Path.cwd()

            / "data"

            / "live"

        )

        output_dir.mkdir(

            parents=True,

            exist_ok=True

        )

        self.portfolio.to_csv(

            output_dir
            / "target_portfolio.csv",

            index=False

        )

        exposure = self.risk_report.get(
            "Factor_Exposure"
        )

        if exposure is not None:

            exposure.to_csv(

                output_dir
                / "factor_exposure_report.csv",

                index=False

            )

        logger.info(
            "Outputs Saved"
        )

    # ======================================================
    # SUMMARY
    # ======================================================

    def print_summary(self):

        runtime = (

            datetime.now()

            -

            self.start_time

        )

        print("\n" + "=" * 70)

        print(
            "INSTITUTIONAL PORTFOLIO SUMMARY"
        )

        print("=" * 70)

        print(
            f"Holdings: "
            f"{len(self.portfolio)}"
        )

        print(
            f"Weight Sum: "
            f"{self.portfolio['Target_Weight'].sum():.4f}"
        )

        print(
            f"Max Position: "
            f"{self.portfolio['Target_Weight'].max():.4f}"
        )

        print(
            f"Runtime: {runtime}"
        )

        print("=" * 70)

    # ======================================================
    # MAIN RUN
    # ======================================================

    def run(self):

        self.load_data()

        self.build_alpha_universe()

        self.construct_portfolio()

        self.run_risk_checks()

        self.save_outputs()

        self.print_summary()

        return {

            "portfolio":
            self.portfolio,

            "risk":
            self.risk_report

        }


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    engine = MasterRebalanceEngine()

    results = engine.run()