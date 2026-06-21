# ==========================================================
# TRANSACTION COST ENGINE
# Institutional Quant Platform
# Part 1
# ==========================================================

from __future__ import annotations
from core.settings import (settings)

from dataclasses import dataclass
from pathlib import Path

import logging
import numpy as np
import pandas as pd


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
# COST CONFIGURATION
# ==========================================================

@dataclass
class CostConfig:

    # ------------------------------------------
    # COMMISSION
    # ------------------------------------------

    COMMISSION_BPS: float = 2.0

    # ------------------------------------------
    # SPREAD MODEL
    # ------------------------------------------

    SMALL_CAP_SPREAD_BPS: float = 20.0

    MID_CAP_SPREAD_BPS: float = 10.0

    LARGE_CAP_SPREAD_BPS: float = 5.0

    # ------------------------------------------
    # SLIPPAGE MODEL
    # ------------------------------------------

    BASE_SLIPPAGE_BPS: float = 3.0

    VOLATILITY_MULTIPLIER: float = 0.50

    # ------------------------------------------
    # IMPACT MODEL
    # ------------------------------------------

    IMPACT_COEFFICIENT: float = 15.0

    # ------------------------------------------
    # CAPACITY MODEL
    # ------------------------------------------

    ADV_WARNING_THRESHOLD: float = 0.05

    ADV_CRITICAL_THRESHOLD: float = 0.10

    # ------------------------------------------
    # RISK LIMITS
    # ------------------------------------------

    MAX_TOTAL_COST_BPS: float = 100.0


# ==========================================================
# COST INPUT MODEL
# ==========================================================

@dataclass
class CostInput:

    symbol: str

    trade_value: float

    adv: float

    market_cap: float

    volatility: float

    sector: str | None = None


# ==========================================================
# COST OUTPUT MODEL
# ==========================================================

@dataclass
class CostOutput:

    symbol: str

    commission_bps: float

    spread_bps: float

    slippage_bps: float

    impact_bps: float

    total_cost_bps: float

    capacity_score: float

    liquidity_flag: str


# ==========================================================
# COMMISSION MODEL
# ==========================================================

class CommissionModel:

    def __init__(

        self,

        config: CostConfig

    ):

        self.config = config

    def estimate(

        self,

        trade_value: float

    ) -> float:

        return float(

            self.config
            .COMMISSION_BPS

        )


# ==========================================================
# SPREAD MODEL
# ==========================================================

class SpreadModel:

    def __init__(

        self,

        config: CostConfig

    ):

        self.config = config

    def estimate(

        self,

        market_cap: float

    ) -> float:

        if pd.isna(
            market_cap
        ):

            return (

                self.config
                .MID_CAP_SPREAD_BPS

            )

        if market_cap >= 500000000000:

            return (

                self.config
                .LARGE_CAP_SPREAD_BPS

            )

        if market_cap >= 50000000000:

            return (

                self.config
                .MID_CAP_SPREAD_BPS

            )

        return (

            self.config
            .SMALL_CAP_SPREAD_BPS

        )


# ==========================================================
# TRADE VALIDATOR
# ==========================================================

class TradeValidator:

    @staticmethod
    def validate(
        trade_df: pd.DataFrame
    ) -> None:

        required_columns = [

            "Symbol",

            "Trade_Weight"

        ]

        missing = [

            col

            for col

            in required_columns

            if col

            not in trade_df.columns

        ]

        if missing:

            raise ValueError(

                f"Missing Columns: "
                f"{missing}"

            )

        logger.info(
            "Trade Validation Passed"
        )


# ==========================================================
# SECURITY MASTER LOADER
# ==========================================================

class SecurityMasterLoader:

    def __init__(

        self,

        file_path: str | Path

    ):

        self.file_path = Path(
            file_path
        )

    def load(
        self
    ) -> pd.DataFrame:

        logger.info(
            "Loading Security Master"
        )

        return pd.read_csv(
            self.file_path
        )


# ==========================================================
# VOLATILITY LOADER
# ==========================================================

class VolatilityLoader:

    def __init__(

        self,

        file_path: str | Path

    ):

        self.file_path = Path(
            file_path
        )

    def load(
        self
    ) -> pd.DataFrame:

        logger.info(
            "Loading Volatility Data"
        )

        return pd.read_csv(
            self.file_path
        )


# ==========================================================
# COST DATA PREPARATION
# ==========================================================

class CostDataPreparation:

    @staticmethod
    def prepare(

        trades: pd.DataFrame,

        security_master: pd.DataFrame,

        volatility: pd.DataFrame

    ) -> pd.DataFrame:

        merged = (

            trades

            .merge(

                security_master,

                on="Symbol",

                how="left"

            )

        )

        merged = (

            merged

            .merge(

                volatility,

                on="Symbol",

                how="left"

            )

        )

        if (

            "Trade_Value" not in merged.columns

            or

            merged[
                "Trade_Value"
            ]

            .isna()

            .all()

        ):

            portfolio_nav = (

                settings
                .portfolio
                .PORTFOLIO_NAV

            )

            merged[
                "Trade_Value"
            ] = (

                merged[
                    "Trade_Weight"
                ]

                .abs()

                *

                portfolio_nav

            )

        merged[
            "Trade_Value"
        ] = (

            merged[
                "Trade_Value"
            ]

            .clip(
                lower=1000
            )

        )

        logger.info(

            f"Cost Universe: "

            f"{len(merged):,}"

        )

        return merged

# ==========================================================
# SLIPPAGE MODEL
# ==========================================================

class SlippageModel:

    def __init__(

        self,

        config: CostConfig

    ):

        self.config = config

    def estimate(

        self,

        volatility: float

    ) -> float:

        if pd.isna(
            volatility
        ):

            volatility = 0.25

        return (

            self.config
            .BASE_SLIPPAGE_BPS

            +

            (

                volatility

                * 100

                *

                self.config
                .VOLATILITY_MULTIPLIER

            )

        )


# ==========================================================
# MARKET IMPACT MODEL
# ==========================================================

class MarketImpactModel:

    def __init__(

        self,

        config: CostConfig

    ):

        self.config = config

    def estimate(

        self,

        trade_value: float,

        adv: float

    ) -> float:

        if (

            pd.isna(adv)

            or

            adv <= 0

        ):

            return (

                self.config
                .IMPACT_COEFFICIENT

            )

        participation_rate = (

            trade_value

            /

            adv

        )

        impact = (

            self.config
            .IMPACT_COEFFICIENT

            *

            np.sqrt(

                abs(
                    participation_rate
                )

            )

        )

        return float(
            impact
        )


# ==========================================================
# LIQUIDITY MODEL
# ==========================================================

class LiquidityModel:

    def __init__(

        self,

        config: CostConfig

    ):

        self.config = config

    def classify(

        self,

        trade_value: float,

        adv: float

    ) -> str:

        if (

            pd.isna(adv)

            or

            adv <= 0

        ):

            return "CRITICAL"

        participation_rate = (

            trade_value

            /

            adv

        )

        if (

            participation_rate

            >=

            self.config
            .ADV_CRITICAL_THRESHOLD

        ):

            return "CRITICAL"

        if (

            participation_rate

            >=

            self.config
            .ADV_WARNING_THRESHOLD

        ):

            return "WARNING"

        return "NORMAL"


# ==========================================================
# CAPACITY MODEL
# ==========================================================

class CapacityModel:

    def __init__(

        self,

        config: CostConfig

    ):

        self.config = config

    def score(

        self,

        trade_value: float,

        adv: float

    ) -> float:

        if (

            pd.isna(adv)

            or

            adv <= 0

        ):

            return 0.0

        participation_rate = (

            trade_value

            /

            adv

        )

        score = (

            100

            /

            (

                1

                +

                10

                *

                participation_rate

            )

        )

        return round(
            score,
            2
        )


# ==========================================================
# COST SCORE ENGINE
# ==========================================================

class CostScoreEngine:

    def __init__(

        self,

        config: CostConfig

    ):

        self.config = config

    def total_cost(

        self,

        commission_bps: float,

        spread_bps: float,

        slippage_bps: float,

        impact_bps: float

    ) -> float:

        total = (

            commission_bps

            +

            spread_bps

            +

            slippage_bps

            +

            impact_bps

        )

        return round(
            total,
            2
        )

    def validate(

        self,

        total_cost_bps: float

    ) -> bool:

        return (

            total_cost_bps

            <=

            self.config
            .MAX_TOTAL_COST_BPS

        )


# ==========================================================
# COST ATTRIBUTION ENGINE
# ==========================================================

class CostAttributionEngine:

    @staticmethod
    def build(

        df: pd.DataFrame

    ) -> pd.DataFrame:

        attribution = df.copy()

        attribution[
            "Commission_%"
        ] = (

            attribution[
                "Commission_Cost_bps"
            ]

            /

            attribution[
                "Total_Cost_bps"
            ]

        )

        attribution[
            "Spread_%"
        ] = (

            attribution[
                "Spread_Cost_bps"
            ]

            /

            attribution[
                "Total_Cost_bps"
            ]

        )

        attribution[
            "Slippage_%"
        ] = (

            attribution[
                "Slippage_Cost_bps"
            ]

            /

            attribution[
                "Total_Cost_bps"
            ]

        )

        attribution[
            "Impact_%"
        ] = (

            attribution[
                "Impact_Cost_bps"
            ]

            /

            attribution[
                "Total_Cost_bps"
            ]

        )

        return attribution


# ==========================================================
# EXECUTION QUALITY ENGINE
# ==========================================================

class ExecutionQualityEngine:

    @staticmethod
    def score(

        capacity_score: float,

        total_cost_bps: float

    ) -> float:

        quality = (

            capacity_score

            -

            (

                total_cost_bps

                * 0.50

            )

        )

        return round(

            max(
                quality,
                0
            ),

            2

        )


# ==========================================================
# COST REPORTING UTILITIES
# ==========================================================

class CostReporting:

    @staticmethod
    def summary(

        cost_df: pd.DataFrame

    ) -> dict:

        return {

            "Trades":

                len(cost_df),

            "Average_Cost_bps":

                round(

                    cost_df[
                        "Total_Cost_bps"
                    ].mean(),

                    2

                ),

            "Max_Cost_bps":

                round(

                    cost_df[
                        "Total_Cost_bps"
                    ].max(),

                    2

                ),

            "Average_Capacity":

                round(

                    cost_df[
                        "Capacity_Score"
                    ].mean(),

                    2

                )

        }
    
# ==========================================================
# TRANSACTION COST ENGINE
# ==========================================================

class TransactionCostEngine:

    def __init__(

        self,

        config: CostConfig | None = None

    ):

        self.config = (

            config

            or

            CostConfig()

        )

        self.commission_model = (

            CommissionModel(
                self.config
            )

        )

        self.spread_model = (

            SpreadModel(
                self.config
            )

        )

        self.slippage_model = (

            SlippageModel(
                self.config
            )

        )

        self.impact_model = (

            MarketImpactModel(
                self.config
            )

        )

        self.capacity_model = (

            CapacityModel(
                self.config
            )

        )

        self.liquidity_model = (

            LiquidityModel(
                self.config
            )

        )

        self.cost_score_engine = (

            CostScoreEngine(
                self.config
            )

        )

    # ======================================================
    # SINGLE TRADE EVALUATION
    # ======================================================

    def evaluate_trade(

        self,

        trade_row: pd.Series

    ) -> dict:

        symbol = trade_row.get(
            "Symbol"
        )

        trade_value = abs(

            trade_row.get(

                "Trade_Value",

                0

            )

        )

        adv = trade_row.get(
            "ADV"
        )

        market_cap = trade_row.get(
            "Market_Cap"
        )

        volatility = trade_row.get(
            "Volatility_252D",
            0.25
        )

        commission_bps = (

            self.commission_model
            .estimate(
                trade_value
            )

        )

        spread_bps = (

            self.spread_model
            .estimate(
                market_cap
            )

        )

        slippage_bps = (

            self.slippage_model
            .estimate(
                volatility
            )

        )

        impact_bps = (

            self.impact_model
            .estimate(

                trade_value,

                adv

            )

        )

        total_cost_bps = (

            self.cost_score_engine
            .total_cost(

                commission_bps,

                spread_bps,

                slippage_bps,

                impact_bps

            )

        )

        capacity_score = (

            self.capacity_model
            .score(

                trade_value,

                adv

            )

        )

        liquidity_flag = (

            self.liquidity_model
            .classify(

                trade_value,

                adv

            )

        )

        execution_quality = (

            ExecutionQualityEngine
            .score(

                capacity_score,

                total_cost_bps

            )

        )

        return {

            "Symbol":
                symbol,

            "Trade_Value":
                trade_value,

            "ADV":
                adv,

            "Market_Cap":
                market_cap,

            "Volatility_252D":
                volatility,

            "Sector":
                trade_row.get(
                    "Sector"
                ),

            "Industry":
                trade_row.get(
                    "Industry"
                ),

            "Market_Cap_Category":
                trade_row.get(
                    "Market_Cap_Category"
                ),

            "Commission_Cost_bps":
                commission_bps,

            "Spread_Cost_bps":
                spread_bps,

            "Slippage_Cost_bps":
                slippage_bps,

            "Impact_Cost_bps":
                impact_bps,

            "Total_Cost_bps":
                total_cost_bps,

            "Capacity_Score":
                capacity_score,

            "Liquidity_Flag":
                liquidity_flag,

            "Execution_Quality":
                execution_quality

        }
    
    # ======================================================
    # BATCH EVALUATION
    # ======================================================

    def evaluate(

        self,

        trades: pd.DataFrame

    ) -> pd.DataFrame:

        TradeValidator.validate(
            trades
        )

        results = []

        for _, row in (

            trades.iterrows()

        ):

            results.append(

                self.evaluate_trade(
                    row
                )

            )

        cost_df = pd.DataFrame(
            results
        )

        logger.info(

            f"Cost Evaluation Complete: "

            f"{len(cost_df):,}"

        )

        return cost_df

    # ======================================================
    # TRADE ENRICHMENT
    # ======================================================

    def enrich_trades(

        self,

        trades: pd.DataFrame,

        costs: pd.DataFrame

    ) -> pd.DataFrame:

        enriched = (

            trades

            .merge(

                costs,

                on="Symbol",

                how="left"

            )

        )

        return enriched


# ==========================================================
# PORTFOLIO COST AGGREGATOR
# ==========================================================

class PortfolioCostAggregator:

    @staticmethod
    def aggregate(

        cost_df: pd.DataFrame

    ) -> dict:

        if len(cost_df) == 0:

            return {}

        return {

            "Trades":

                len(cost_df),

            "Average_Cost_bps":

                round(

                    cost_df[
                        "Total_Cost_bps"
                    ].mean(),

                    2

                ),

            "Median_Cost_bps":

                round(

                    cost_df[
                        "Total_Cost_bps"
                    ].median(),

                    2

                ),

            "Max_Cost_bps":

                round(

                    cost_df[
                        "Total_Cost_bps"
                    ].max(),

                    2

                ),

            "Average_Capacity":

                round(

                    cost_df[
                        "Capacity_Score"
                    ].mean(),

                    2

                )

        }


# ==========================================================
# COST VALIDATION
# ==========================================================

class CostValidator:

    @staticmethod
    def validate(

        cost_df: pd.DataFrame

    ):

        required_columns = [

            "Symbol",

            "Total_Cost_bps",

            "Capacity_Score"

        ]

        missing = [

            col

            for col

            in required_columns

            if col

            not in cost_df.columns

        ]

        if missing:

            raise ValueError(

                f"Missing Columns: "

                f"{missing}"

            )

        logger.info(
            "Cost Validation Passed"
        )


# ==========================================================
# COST DATA ENRICHMENT
# ==========================================================

class CostUniverseBuilder:

    def __init__(

        self,

        security_master_path,

        volatility_path

    ):

        self.security_master_loader = (

            SecurityMasterLoader(
                security_master_path
            )

        )

        self.volatility_loader = (

            VolatilityLoader(
                volatility_path
            )

        )

    def build(

        self,

        trades: pd.DataFrame

    ) -> pd.DataFrame:

        security_master = (

            self.security_master_loader
            .load()

        )

        volatility = (

            self.volatility_loader
            .load()

        )

        return (

            CostDataPreparation
            .prepare(

                trades,

                security_master,

                volatility

            )

        )


# ==========================================================
# COST ANALYTICS
# ==========================================================

class CostAnalytics:

    @staticmethod
    def build(

        enriched_cost_df: pd.DataFrame

    ) -> pd.DataFrame:

        analytics = (

            enriched_cost_df

            .groupby(
                "Liquidity_Flag"
            )

            .agg(

                Trades=(

                    "Symbol",

                    "count"

                ),

                Average_Cost=(

                    "Total_Cost_bps",

                    "mean"

                ),

                Average_Capacity=(

                    "Capacity_Score",

                    "mean"

                )

            )

            .reset_index()

        )

        return analytics
    
# ==========================================================
# AUDIT LOGGER
# ==========================================================

class CostAuditLogger:

    def __init__(

        self,

        output_dir="data/execution"

    ):

        self.output_dir = Path(
            output_dir
        )

        self.output_dir.mkdir(

            parents=True,

            exist_ok=True

        )

    def save(
        self,
        audit_record
    ):

        audit_file = (

            self.output_dir

            /

            "transaction_cost_audit.csv"

        )

        audit_df = pd.DataFrame(
            [audit_record]
        )

        if audit_file.exists():

            existing = pd.read_csv(
                audit_file
            )

            audit_df = pd.concat(

                [

                    existing,

                    audit_df

                ],

                ignore_index=True

            )

        audit_df.to_csv(

            audit_file,

            index=False

        )

        logger.info(
            "Audit Log Saved"
        )


# ==========================================================
# MLFLOW INTEGRATION
# ==========================================================

class CostMLflowTracker:

    @staticmethod
    def log_metrics(
        summary
    ):

        try:

            import mlflow

            for key, value in (

                summary.items()

            ):

                if isinstance(

                    value,

                    (
                        int,
                        float
                    )

                ):

                    mlflow.log_metric(

                        key,

                        float(value)

                    )

        except Exception as ex:

            logger.warning(

                f"MLflow Error: "

                f"{ex}"

            )


# ==========================================================
# TELEMETRY
# ==========================================================

class CostTelemetry:

    @staticmethod
    def track():

        try:

            from telemetry.telemetry import (
                PIPELINE_RUNS
            )

            PIPELINE_RUNS.add(1)

        except Exception:

            pass


# ==========================================================
# REPORT EXPORTER
# ==========================================================

class CostReportExporter:

    def __init__(

        self,

        output_dir="data/execution"

    ):

        self.output_dir = Path(
            output_dir
        )

        self.output_dir.mkdir(

            parents=True,

            exist_ok=True

        )

    def export(

        self,

        enriched_cost_df,

        analytics_df

    ):

        enriched_cost_df.to_csv(

            self.output_dir

            /

            "transaction_cost_report.csv",

            index=False

        )

        analytics_df.to_csv(

            self.output_dir

            /

            "transaction_cost_analytics.csv",

            index=False

        )

        enriched_cost_df.to_parquet(

            self.output_dir

            /

            "transaction_cost_report.parquet",

            index=False

        )

        logger.info(
            "Reports Exported"
        )


# ==========================================================
# TRANSACTION COST PIPELINE
# ==========================================================

class TransactionCostPipeline:

    def __init__(

        self,

        security_master_path,

        volatility_path

    ):

        self.engine = (

            TransactionCostEngine()

        )

        self.universe_builder = (

            CostUniverseBuilder(

                security_master_path,

                volatility_path

            )

        )

        self.audit_logger = (

            CostAuditLogger()

        )

        self.exporter = (

            CostReportExporter()

        )

    def run(

        self,

        trades

    ):

        logger.info(

            "Starting Transaction Cost Pipeline"

        )

        enriched_trades = (

            self.universe_builder
            .build(
                trades
            )

        )

        cost_df = (

            self.engine
            .evaluate(
                enriched_trades
            )

        )

        CostValidator.validate(
            cost_df
        )

        final_df = (

            self.engine
            .enrich_trades(

                enriched_trades,

                cost_df

            )

        )

        analytics_df = (

            CostAnalytics
            .build(
                final_df
            )

        )

        summary = (

            PortfolioCostAggregator
            .aggregate(
                final_df
            )

        )

        audit_record = {

            "Run_Time":

                pd.Timestamp.now(),

            **summary

        }

        self.audit_logger.save(
            audit_record
        )

        self.exporter.export(

            final_df,

            analytics_df

        )

        CostMLflowTracker.log_metrics(
            summary
        )

        CostTelemetry.track()

        logger.info(

            "Transaction Cost Pipeline Complete"

        )

        return {

            "costs":
                final_df,

            "analytics":
                analytics_df,

            "summary":
                summary

        }


# ==========================================================
# MASTER REBALANCE ENGINE INTEGRATION
# ==========================================================

class RebalanceCostIntegration:

    @staticmethod
    def apply(

        trades,

        security_master_path,

        volatility_path

    ):

        pipeline = (

            TransactionCostPipeline(

                security_master_path,

                volatility_path

            )

        )

        results = (

            pipeline.run(
                trades
            )

        )

        return results


# ==========================================================
# CLI RUNNER
# ==========================================================

def run_example():

    trade_file = Path(

        "data/live/trade_list.csv"

    )

    if not trade_file.exists():

        logger.warning(

            "trade_list.csv not found"

        )

        return

    trades = pd.read_csv(
        trade_file
    )

    pipeline = (

        TransactionCostPipeline(

            "data/raw/security_master.csv",

            "data/risk/stock_volatility.csv"

        )

    )

    results = pipeline.run(
        trades
    )

    print(
        "\nTransaction Cost Summary"
    )

    print(
        results["summary"]
    )


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    run_example()