# ==========================================================
# RUN PIPELINE
# ==========================================================

from alpha.signal_engine import SignalEngine
from portfolio.portfolio_engine import PortfolioEngine
from risk.risk_engine import RiskEngine
from execution.trade_engine import TradeEngine
from reporting.reporting_engine import ReportingEngine
from research.backtest_engine import BacktestEngine

import numpy as np

def main():

    print("\n========== PIPELINE START ==========")

    # ------------------------------------------------------
    # SIGNALS
    # ------------------------------------------------------

    signal_engine = SignalEngine()

    data = (
        signal_engine
        .load_data()
    )

    signal_universe = (
        signal_engine
        .build_alpha_universe(
            data
        )
    )

    print(
        f"Signals Generated: "
        f"{len(signal_universe)}"
    )

    # ------------------------------------------------------
    # PORTFOLIO
    # ------------------------------------------------------

    portfolio_engine = PortfolioEngine()

    portfolio = portfolio_engine.construct(
        signal_universe
    )

    # ------------------------------------------------------
    # RISK
    # ------------------------------------------------------

    risk_engine = RiskEngine()

    risk_report = risk_engine.evaluate(
        portfolio
    )

    # ------------------------------------------------------
    # TRADE
    # ------------------------------------------------------

    trade_engine = TradeEngine()

    current_portfolio = data["portfolio"]

    target_portfolio = portfolio

    trades = trade_engine.generate(
        current_portfolio,
        target_portfolio
    )

    # ------------------------------------------------------
    # REPORTING
    # ------------------------------------------------------

    backtest_engine = BacktestEngine()

    performance_report = (

        backtest_engine.run(

            np.random.normal(

                0.001,

                0.02,

                252

            )

        )

    )

    reporting_engine = ReportingEngine()

    reports = (

        reporting_engine.generate(

            portfolio,

            risk_report,

            performance_report,

            trades

        )

    )

    print(

        "\n✓ Reports Generated:"

    )

    print(

        reports.keys()

    )

if __name__ == "__main__":

    main()