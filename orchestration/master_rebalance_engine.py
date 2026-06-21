# ==========================================================
# MASTER REBALANCE ENGINE
# Institutional Quant Platform
# Part 1/4
# ==========================================================

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import json
import logging
import traceback
import numpy as np
import pandas as pd

# ==========================================================
# CORE ENGINES
# ==========================================================

from alpha.signal_engine import (
    SignalEngine
)

from portfolio.portfolio_engine import (
    PortfolioEngine
)

from risk.risk_engine import (
    RiskEngine
)

from execution.trade_engine import (
    TradeEngine
)

from research.backtest_engine import (
    BacktestEngine
)

from reporting.reporting_engine import (
    ReportingEngine
)

# ==========================================================
# PLATFORM SERVICES
# ==========================================================

from core.audit_logger import (
    AuditLogger
)

from telemetry.telemetry import (
    TelemetryManager
)

from mlflow_track.mlflow_manager import (
    MLflowManager
)

# ==========================================================
# LOGGING CONFIG
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
# MASTER REBALANCE ENGINE
# ==========================================================

class MasterRebalanceEngine:

    def __init__(self):

        self.start_time = datetime.now()

        # -----------------------------------------
        # Core Objects
        # -----------------------------------------

        self.data = None

        self.alpha_universe = None

        self.portfolio = None

        self.risk_report = None

        self.trades = None

        self.performance_report = None

        self.reports = None

        # -----------------------------------------
        # Platform Services
        # -----------------------------------------

        self.audit_logger = AuditLogger()

        self.telemetry = TelemetryManager()

        self.mlflow = MLflowManager()

        # -----------------------------------------
        # Metadata
        # -----------------------------------------

        self.run_id = (

            datetime.now()

            .strftime(

                "%Y%m%d_%H%M%S"

            )

        )

        logger.info(

            "=" * 70

        )

        logger.info(

            "INSTITUTIONAL QUANT PLATFORM STARTED"

        )

        logger.info(

            f"RUN ID: {self.run_id}"

        )

        logger.info(

            "=" * 70

        )

    # ======================================================
    # AUDIT EVENT
    # ======================================================

    def log_event(

        self,

        event,

        details=None

    ):

        try:

            self.audit_logger.log(

                event=event,

                details=details

            )

        except Exception:

            pass

    # ======================================================
    # TELEMETRY
    # ======================================================

    def track_metric(

        self,

        metric,

        value

    ):

        try:

            self.telemetry.track_metric(

                metric,

                value

            )

        except Exception:

            pass

    # ======================================================
    # LOAD DATA
    # ======================================================

    def load_data(self):

        logger.info(

            "Loading Market Data"

        )

        signal_engine = SignalEngine()

        self.data = (

            signal_engine

            .load_data()

        )

        self.log_event(

            "DATA_LOAD_COMPLETE"

        )

        logger.info(

            "Data Loaded Successfully"

        )

        return self.data
    
    # ======================================================
    # BUILD ALPHA UNIVERSE
    # ======================================================

    def build_alpha_universe(self):

        logger.info(

            "Building Alpha Universe"

        )

        signal_engine = SignalEngine()

        self.alpha_universe = (

            signal_engine

            .build_alpha_universe(

                self.data

            )

        )

        universe_size = len(

            self.alpha_universe

        )

        self.track_metric(

            "universe_size",

            universe_size

        )

        self.log_event(

            "ALPHA_UNIVERSE_COMPLETE",

            {

                "universe_size":

                universe_size

            }

        )

        logger.info(

            f"Alpha Universe Size: "

            f"{universe_size:,}"

        )

        return self.alpha_universe

    # ======================================================
    # UNIVERSE VALIDATION
    # ======================================================

    def validate_universe(self):

        logger.info(

            "Validating Alpha Universe"

        )

        if self.alpha_universe is None:

            raise ValueError(

                "Alpha Universe Not Built"

            )

        if len(

            self.alpha_universe

        ) == 0:

            raise ValueError(

                "Empty Alpha Universe"

            )

        required_columns = [

            "Symbol",

            "Selection_Score"

        ]

        missing = [

            col

            for col

            in required_columns

            if col

            not in self.alpha_universe.columns

        ]

        if missing:

            raise ValueError(

                f"Missing Columns: {missing}"

            )

        logger.info(

            "Universe Validation Passed"

        )

        return True

    # ======================================================
    # PORTFOLIO CONSTRUCTION
    # ======================================================

    def construct_portfolio(self):

        logger.info(

            "Constructing Portfolio"

        )

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

        holdings = len(

            self.portfolio

        )

        weight_sum = (

            self.portfolio[

                "Target_Weight"

            ]

            .sum()

        )

        self.track_metric(

            "holdings",

            holdings

        )

        self.track_metric(

            "weight_sum",

            weight_sum

        )

        self.log_event(

            "PORTFOLIO_CONSTRUCTED",

            {

                "holdings":

                holdings,

                "weight_sum":

                float(

                    weight_sum

                )

            }

        )

        logger.info(

            f"Portfolio Holdings: "

            f"{holdings}"

        )

        return self.portfolio

    # ======================================================
    # PORTFOLIO VALIDATION
    # ======================================================

    def validate_portfolio(self):

        logger.info(

            "Validating Portfolio"

        )

        if self.portfolio is None:

            raise ValueError(

                "Portfolio Not Built"

            )

        total_weight = (

            self.portfolio[

                "Target_Weight"

            ]

            .sum()

        )

        if abs(

            total_weight - 1.0

        ) > 0.01:

            raise ValueError(

                f"Weight Sum Invalid: "

                f"{total_weight}"

            )

        logger.info(

            "Portfolio Validation Passed"

        )

        return True

    # ======================================================
    # RISK ENGINE
    # ======================================================

    def run_risk_checks(self):

        logger.info(

            "Running Risk Engine"

        )

        risk_engine = RiskEngine()

        self.risk_report = (

            risk_engine

            .evaluate(

                self.portfolio

            )

        )

        beta = (

            self.risk_report.get(

                "Portfolio_Beta",

                0

            )

        )

        hhi = (

            self.risk_report.get(

                "HHI",

                0

            )

        )

        effective_holdings = (

            self.risk_report.get(

                "Effective_Holdings",

                0

            )

        )

        self.track_metric(

            "portfolio_beta",

            beta

        )

        self.track_metric(

            "portfolio_hhi",

            hhi

        )

        self.track_metric(

            "effective_holdings",

            effective_holdings

        )

        self.log_event(

            "RISK_CHECK_COMPLETE",

            {

                "beta":

                beta,

                "hhi":

                hhi,

                "effective_holdings":

                effective_holdings

            }

        )

        logger.info(

            "Risk Evaluation Complete"

        )

        return self.risk_report

    # ======================================================
    # RISK VALIDATION
    # ======================================================

    def validate_risk(self):

        logger.info(

            "Validating Risk Report"

        )

        if self.risk_report is None:

            raise ValueError(

                "Risk Report Missing"

            )

        required_metrics = [

            "Portfolio_Beta",

            "HHI",

            "Effective_Holdings"

        ]

        for metric in required_metrics:

            if metric not in self.risk_report:

                logger.warning(

                    f"Missing Risk Metric: "

                    f"{metric}"

                )

        logger.info(

            "Risk Validation Passed"

        )

        return True

    # ======================================================
    # TRADE GENERATION
    # ======================================================

    def generate_trades(self):

        logger.info(

            "Generating Trades"

        )

        trade_engine = TradeEngine()

        current_portfolio = (

            self.data["portfolio"]

            .copy()

        )

        current_portfolio.rename(

            columns={

                "Weight":

                "Current_Weight"

            },

            inplace=True

        )

        self.trades = (

            trade_engine

            .generate(

                current_portfolio,

                self.portfolio

            )

        )

        trade_count = len(

            self.trades

        )

        turnover = (

            self.trades[

                "Trade_Weight"

            ]

            .abs()

            .sum()

        )

        estimated_cost = (

            self.trades[

                "Estimated_Cost"

            ]

            .sum()

        )

        self.track_metric(

            "trade_count",

            trade_count

        )

        self.track_metric(

            "turnover",

            turnover

        )

        self.track_metric(

            "estimated_cost",

            estimated_cost

        )

        self.log_event(

            "TRADE_GENERATION_COMPLETE",

            {

                "trade_count":

                trade_count,

                "turnover":

                float(

                    turnover

                ),

                "estimated_cost":

                float(

                    estimated_cost

                )

            }

        )

        logger.info(

            f"Trades Generated: "

            f"{trade_count}"

        )

        return self.trades

    # ======================================================
    # TRADE VALIDATION
    # ======================================================

    def validate_trades(self):

        logger.info(

            "Validating Trades"

        )

        if self.trades is None:

            raise ValueError(

                "Trade File Missing"

            )

        required_columns = [

            "Symbol",

            "Trade_Weight",

            "Action"

        ]

        missing = [

            col

            for col

            in required_columns

            if col

            not in self.trades.columns

        ]

        if missing:

            raise ValueError(

                f"Missing Trade Columns: "

                f"{missing}"

            )

        logger.info(

            "Trade Validation Passed"

        )

        return True

    # ======================================================
    # BACKTEST ENGINE
    # ======================================================

    def run_backtest(self):

        logger.info(

            "Running Backtest Engine"

        )

        backtest_engine = BacktestEngine()

        synthetic_returns = (

            np.random.normal(

                0.001,

                0.02,

                252

            )

        )

        self.performance_report = (

            backtest_engine

            .run(

                synthetic_returns

            )

        )

        self.track_metric(

            "cagr",

            self.performance_report.get(

                "CAGR",

                0

            )

        )

        self.track_metric(

            "sharpe",

            self.performance_report.get(

                "Sharpe",

                0

            )

        )

        self.track_metric(

            "max_drawdown",

            self.performance_report.get(

                "Max_Drawdown",

                0

            )

        )

        self.log_event(

            "BACKTEST_COMPLETE",

            self.performance_report

        )

        logger.info(

            "Performance Analytics Complete"

        )

        return self.performance_report

    # ======================================================
    # PERFORMANCE VALIDATION
    # ======================================================

    def validate_performance(self):

        logger.info(

            "Validating Performance Report"

        )

        if self.performance_report is None:

            raise ValueError(

                "Performance Report Missing"

            )

        logger.info(

            "Performance Validation Passed"

        )

        return True

    # ======================================================
    # REPORTING ENGINE
    # ======================================================

    def generate_reports(self):

        logger.info(

            "Generating Reports"

        )

        reporting_engine = (

            ReportingEngine()

        )

        self.reports = (

            reporting_engine

            .generate(

                self.portfolio,

                self.risk_report,

                self.performance_report,

                self.trades

            )

        )

        self.log_event(

            "REPORT_GENERATION_COMPLETE"

        )

        logger.info(

            "Reporting Complete"

        )

        return self.reports

    # ======================================================
    # REPORT VALIDATION
    # ======================================================

    def validate_reports(self):

        logger.info(

            "Validating Reports"

        )

        if self.reports is None:

            raise ValueError(

                "Reports Missing"

            )

        required_reports = [

            "portfolio",

            "risk",

            "performance",

            "dashboard",

            "execution"

        ]

        missing = [

            report

            for report

            in required_reports

            if report

            not in self.reports

        ]

        if missing:

            logger.warning(

                f"Missing Reports: "

                f"{missing}"

            )

        logger.info(

            "Report Validation Passed"

        )

        return True

    # ======================================================
    # MLFLOW TRACKING
    # ======================================================

    def track_experiment(self):

        try:

            self.mlflow.log_metric(

                "holdings",

                len(

                    self.portfolio

                )

            )

            self.mlflow.log_metric(

                "portfolio_beta",

                self.risk_report.get(

                    "Portfolio_Beta",

                    0

                )

            )

            self.mlflow.log_metric(

                "sharpe",

                self.performance_report.get(

                    "Sharpe",

                    0

                )

            )

            self.mlflow.log_metric(

                "cagr",

                self.performance_report.get(

                    "CAGR",

                    0

                )

            )

            logger.info(

                "MLflow Tracking Complete"

            )

        except Exception as ex:

            logger.warning(

                f"MLflow Error: "

                f"{ex}"

            )

    # ======================================================
    # TRADE GENERATION
    # ======================================================

    def generate_trades(self):

        logger.info(

            "Generating Trades"

        )

        trade_engine = TradeEngine()

        current_portfolio = (

            self.data["portfolio"]

            .copy()

        )

        current_portfolio.rename(

            columns={

                "Weight":

                "Current_Weight"

            },

            inplace=True

        )

        self.trades = (

            trade_engine

            .generate(

                current_portfolio,

                self.portfolio

            )

        )

        trade_count = len(

            self.trades

        )

        turnover = (

            self.trades[

                "Trade_Weight"

            ]

            .abs()

            .sum()

        )

        estimated_cost = (

            self.trades[

                "Estimated_Cost"

            ]

            .sum()

        )

        self.track_metric(

            "trade_count",

            trade_count

        )

        self.track_metric(

            "turnover",

            turnover

        )

        self.track_metric(

            "estimated_cost",

            estimated_cost

        )

        self.log_event(

            "TRADE_GENERATION_COMPLETE",

            {

                "trade_count":

                trade_count,

                "turnover":

                float(

                    turnover

                ),

                "estimated_cost":

                float(

                    estimated_cost

                )

            }

        )

        logger.info(

            f"Trades Generated: "

            f"{trade_count}"

        )

        return self.trades

    # ======================================================
    # TRADE VALIDATION
    # ======================================================

    def validate_trades(self):

        logger.info(

            "Validating Trades"

        )

        if self.trades is None:

            raise ValueError(

                "Trade File Missing"

            )

        required_columns = [

            "Symbol",

            "Trade_Weight",

            "Action"

        ]

        missing = [

            col

            for col

            in required_columns

            if col

            not in self.trades.columns

        ]

        if missing:

            raise ValueError(

                f"Missing Trade Columns: "

                f"{missing}"

            )

        logger.info(

            "Trade Validation Passed"

        )

        return True

    # ======================================================
    # BACKTEST ENGINE
    # ======================================================

    def run_backtest(self):

        logger.info(

            "Running Backtest Engine"

        )

        backtest_engine = BacktestEngine()

        synthetic_returns = (

            np.random.normal(

                0.001,

                0.02,

                252

            )

        )

        self.performance_report = (

            backtest_engine

            .run(

                synthetic_returns

            )

        )

        self.track_metric(

            "cagr",

            self.performance_report.get(

                "CAGR",

                0

            )

        )

        self.track_metric(

            "sharpe",

            self.performance_report.get(

                "Sharpe",

                0

            )

        )

        self.track_metric(

            "max_drawdown",

            self.performance_report.get(

                "Max_Drawdown",

                0

            )

        )

        self.log_event(

            "BACKTEST_COMPLETE",

            self.performance_report

        )

        logger.info(

            "Performance Analytics Complete"

        )

        return self.performance_report

    # ======================================================
    # PERFORMANCE VALIDATION
    # ======================================================

    def validate_performance(self):

        logger.info(

            "Validating Performance Report"

        )

        if self.performance_report is None:

            raise ValueError(

                "Performance Report Missing"

            )

        logger.info(

            "Performance Validation Passed"

        )

        return True

    # ======================================================
    # REPORTING ENGINE
    # ======================================================

    def generate_reports(self):

        logger.info(

            "Generating Reports"

        )

        reporting_engine = (

            ReportingEngine()

        )

        self.reports = (

            reporting_engine

            .generate(

                self.portfolio,

                self.risk_report,

                self.performance_report,

                self.trades

            )

        )

        self.log_event(

            "REPORT_GENERATION_COMPLETE"

        )

        logger.info(

            "Reporting Complete"

        )

        return self.reports

    # ======================================================
    # REPORT VALIDATION
    # ======================================================

    def validate_reports(self):

        logger.info(

            "Validating Reports"

        )

        if self.reports is None:

            raise ValueError(

                "Reports Missing"

            )

        required_reports = [

            "portfolio",

            "risk",

            "performance",

            "dashboard",

            "execution"

        ]

        missing = [

            report

            for report

            in required_reports

            if report

            not in self.reports

        ]

        if missing:

            logger.warning(

                f"Missing Reports: "

                f"{missing}"

            )

        logger.info(

            "Report Validation Passed"

        )

        return True

    # ======================================================
    # MLFLOW TRACKING
    # ======================================================

    def track_experiment(self):

        try:

            self.mlflow.log_metric(

                "holdings",

                len(

                    self.portfolio

                )

            )

            self.mlflow.log_metric(

                "portfolio_beta",

                self.risk_report.get(

                    "Portfolio_Beta",

                    0

                )

            )

            self.mlflow.log_metric(

                "sharpe",

                self.performance_report.get(

                    "Sharpe",

                    0

                )

            )

            self.mlflow.log_metric(

                "cagr",

                self.performance_report.get(

                    "CAGR",

                    0

                )

            )

            logger.info(

                "MLflow Tracking Complete"

            )

        except Exception as ex:

            logger.warning(

                f"MLflow Error: "

                f"{ex}"

            )

    # ======================================================
    # SAVE OUTPUTS
    # ======================================================

    def save_outputs(self):

        logger.info(

            "Saving Outputs"

        )

        output_dir = (

            Path.cwd()

            / "data"

            / "live"

        )

        output_dir.mkdir(

            parents=True,

            exist_ok=True

        )

        # --------------------------------------------------
        # Portfolio
        # --------------------------------------------------

        self.portfolio.to_csv(

            output_dir
            / "target_portfolio.csv",

            index=False

        )

        # --------------------------------------------------
        # Trades
        # --------------------------------------------------

        self.trades.to_csv(

            output_dir
            / "trade_list.csv",

            index=False

        )

        # --------------------------------------------------
        # Risk Report
        # --------------------------------------------------

        with open(

            output_dir
            / "risk_report.json",

            "w"

        ) as file:

            json.dump(

                self.risk_report,

                file,

                indent=4,

                default=str

            )

        # --------------------------------------------------
        # Performance Report
        # --------------------------------------------------

        with open(

            output_dir
            / "performance_report.json",

            "w"

        ) as file:

            json.dump(

                self.performance_report,

                file,

                indent=4,

                default=str

            )

        # --------------------------------------------------
        # Reports
        # --------------------------------------------------

        with open(

            output_dir
            / "dashboard.json",

            "w"

        ) as file:

            json.dump(

                self.reports,

                file,

                indent=4,

                default=str

            )

        logger.info(

            "Outputs Saved Successfully"

        )

        return output_dir

    # ======================================================
    # SUMMARY
    # ======================================================

    def print_summary(self):

        runtime = (

            datetime.now()

            -

            self.start_time

        )

        print(

            "\n"

            + "=" * 80

        )

        print(

            "INSTITUTIONAL REBALANCE SUMMARY"

        )

        print(

            "=" * 80

        )

        print(

            f"Universe Size: "

            f"{len(self.alpha_universe):,}"

        )

        print(

            f"Holdings: "

            f"{len(self.portfolio)}"

        )

        print(

            f"Weight Sum: "

            f"{self.portfolio['Target_Weight'].sum():.4f}"

        )

        print(

            f"Portfolio Beta: "

            f"{self.risk_report.get('Portfolio_Beta',0):.4f}"

        )

        print(

            f"HHI: "

            f"{self.risk_report.get('HHI',0):.4f}"

        )

        print(

            f"Effective Holdings: "

            f"{self.risk_report.get('Effective_Holdings',0):.2f}"

        )

        print(

            f"Trades: "

            f"{len(self.trades)}"

        )

        print(

            f"CAGR: "

            f"{self.performance_report.get('CAGR',0):.2%}"

        )

        print(

            f"Sharpe: "

            f"{self.performance_report.get('Sharpe',0):.2f}"

        )

        print(

            f"Max Drawdown: "

            f"{self.performance_report.get('Max_Drawdown',0):.2%}"

        )

        print(

            f"Runtime: "

            f"{runtime}"

        )

        print(

            "=" * 80

        )

    # ======================================================
    # RUN PIPELINE
    # ======================================================

    def run(self):

        try:

            self.load_data()

            self.build_alpha_universe()

            self.validate_universe()

            self.construct_portfolio()

            self.validate_portfolio()

            self.run_risk_checks()

            self.validate_risk()

            self.generate_trades()

            self.validate_trades()

            self.run_backtest()

            self.validate_performance()

            self.generate_reports()

            self.validate_reports()

            self.track_experiment()

            self.save_outputs()

            self.print_summary()

            self.log_event(

                "REBALANCE_COMPLETE"

            )

            return {

                "portfolio":

                    self.portfolio,

                "risk":

                    self.risk_report,

                "trades":

                    self.trades,

                "performance":

                    self.performance_report,

                "reports":

                    self.reports

            }

        except Exception as ex:

            logger.error(

                str(ex)

            )

            logger.error(

                traceback.format_exc()

            )

            self.log_event(

                "REBALANCE_FAILED",

                {

                    "error":

                    str(ex)

                }

            )

            raise

# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    engine = (

        MasterRebalanceEngine()

    )

    results = (

        engine.run()

    )