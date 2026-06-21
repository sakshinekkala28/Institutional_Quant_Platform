from __future__ import annotations

# ==========================================================
# IMPORTS
# ==========================================================

import logging

from pathlib import Path

import pandas as pd

from core.settings import settings

from execution.transaction_cost_engine import (

    CostUniverseBuilder,

    CostDataPreparation,

    TransactionCostPipeline,

    TransactionCostEngine

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

logger = logging.getLogger(
    __name__
)


# ==========================================================
# PATH CONFIGURATION
# ==========================================================

TRADE_FILE = (

    "data/live/trade_list.csv"

)

SECURITY_MASTER_FILE = (

    "data/raw/security_master.csv"

)

VOLATILITY_FILE = (

    "data/risk/stock_volatility.csv"

)

OUTPUT_DIR = (

    "data/execution"

)

CAPACITY_REPORT_FILE = (

    f"{OUTPUT_DIR}/capacity_stress_test.csv"

)

BOTTLENECK_REPORT_FILE = (

    f"{OUTPUT_DIR}/capacity_bottlenecks.csv"

)

SECTOR_REPORT_FILE = (

    f"{OUTPUT_DIR}/capacity_by_sector.csv"

)

AUDIT_LOG_FILE = (

    f"{OUTPUT_DIR}/capacity_audit_log.csv"

)


# ==========================================================
# CAPACITY STRESS ENGINE
# ==========================================================

class CapacityStressEngine:

    def __init__(self):

        logger.info(

            "Initializing Capacity Stress Engine"

        )

        self.output_dir = Path(

            OUTPUT_DIR

        )

        self.output_dir.mkdir(

            parents=True,

            exist_ok=True

        )

        self.universe_builder = (

            CostUniverseBuilder(

                SECURITY_MASTER_FILE,

                VOLATILITY_FILE

            )

        )

        self.cost_engine = (

            TransactionCostEngine()

        )

        self.aum_scenarios = (

            settings
            .portfolio
            .AUM_SCENARIOS

        )

        logger.info(

            f"AUM Scenarios Loaded: "

            f"{len(self.aum_scenarios)}"

        )

        logger.info(

            f"Scenarios: "

            f"{self.aum_scenarios}"

        )

    # ==========================================================
    # AUM EVALUATION
    # ==========================================================

    def evaluate_aum(

        self,

        trades: pd.DataFrame,

        aum: float

    ) -> tuple[

        pd.DataFrame,

        pd.DataFrame,

        pd.DataFrame

    ]:

        logger.info(

            f"Evaluating AUM Scenario: "

            f"₹{aum:,.0f}"

        )

        df = trades.copy()

        # ======================================================
        # SCALE TRADES
        # ======================================================

        df[
            "Trade_Value"
        ] = (

            df[
                "Trade_Weight"
            ]

            .abs()

            *

            aum

        )

        logger.info(

            f"Total Trade Value: "

            f"₹{df['Trade_Value'].sum():,.0f}"

        )

        # ======================================================
        # ENRICHMENT
        # ======================================================

        enriched = (

            self.universe_builder

            .build(

                df

            )

        )

        logger.info(

            f"Enriched Securities: "

            f"{len(enriched):,}"

        )

        # ======================================================
        # COST EVALUATION
        # ======================================================

        cost_df = (

            self.cost_engine

            .evaluate(

                enriched

            )

        )


        logger.info(

            f"Cost Evaluated: "

            f"{len(cost_df):,}"

        )

        # ======================================================
        # BOTTLENECKS
        # ======================================================

        bottlenecks = (

            cost_df

            .sort_values(

                "Capacity_Score"

            )

            .head(

                20

            )

            .copy()

        )

        bottlenecks[
            "AUM"
        ] = aum

        # ======================================================
        # SECTOR CAPACITY
        # ======================================================

        if "Sector" not in cost_df.columns:

            logger.warning(

                "Sector column missing. "

                "Skipping sector analysis."

            )

            sector_summary = pd.DataFrame(

                columns=[

                    "Sector",

                    "Average_Capacity",

                    "Worst_Capacity",

                    "Average_Cost_bps",

                    "Securities",

                    "AUM"

                ]

            )

        else:

            sector_summary = (

                cost_df

                .groupby(

                    "Sector",

                    dropna=False

                )

                .agg(

                    Average_Capacity=(

                        "Capacity_Score",

                        "mean"

                    ),

                    Worst_Capacity=(

                        "Capacity_Score",

                        "min"

                    ),

                    Average_Cost_bps=(

                        "Total_Cost_bps",

                        "mean"

                    ),

                    Securities=(

                        "Symbol",

                        "count"

                    )

                )

                .reset_index()

            )

            sector_summary[
                "AUM"
            ] = aum


        return (

            cost_df,

            bottlenecks,

            sector_summary

        )


    # ==========================================================
    # LIQUIDITY ANALYSIS
    # ==========================================================

    @staticmethod
    def build_liquidity_summary(

        cost_df: pd.DataFrame

    ) -> dict:

        return {

            "Warning_Trades":

                int(

                    (

                        cost_df[
                            "Liquidity_Flag"
                        ]

                        ==

                        "WARNING"

                    ).sum()

                ),

            "Critical_Trades":

                int(

                    (

                        cost_df[
                            "Liquidity_Flag"
                        ]

                        ==

                        "CRITICAL"

                    ).sum()

                ),

            "Average_Capacity":

                round(

                    cost_df[
                        "Capacity_Score"
                    ]

                    .mean(),

                    2

                ),

            "Worst_Capacity":

                round(

                    cost_df[
                        "Capacity_Score"
                    ]

                    .min(),

                    2

                ),

            "Average_Cost_bps":

                round(

                    cost_df[
                        "Total_Cost_bps"
                    ]

                    .mean(),

                    2

                ),

            "Worst_Cost_bps":

                round(

                    cost_df[
                        "Total_Cost_bps"
                    ]

                    .max(),

                    2

                )

        }
    
    # ==========================================================
    # STRESS TEST ORCHESTRATION
    # ==========================================================

    def run_stress_test(

        self,

        trades: pd.DataFrame

    ) -> tuple[

        pd.DataFrame,

        pd.DataFrame,

        pd.DataFrame

    ]:

        logger.info(

            "Running Capacity Stress Test"

        )

        summary_results = []

        bottleneck_results = []

        sector_results = []

        for aum in (

            self.aum_scenarios

        ):

            (

                cost_df,

                bottlenecks,

                sector_summary

            ) = (

                self.evaluate_aum(

                    trades,

                    aum

                )

            )

            liquidity_summary = (

                self.build_liquidity_summary(

                    cost_df

                )

            )

            summary_results.append(

                {

                    "AUM":

                        aum,

                    **liquidity_summary

                }

            )

            bottleneck_results.append(

                bottlenecks

            )

            sector_results.append(

                sector_summary

            )

        summary_df = pd.DataFrame(

            summary_results

        )

        bottleneck_df = pd.concat(

            bottleneck_results,

            ignore_index=True

        )

        sector_df = pd.concat(

            sector_results,

            ignore_index=True

        )

        logger.info(

            "Stress Test Complete"

        )

        return (

            summary_df,

            bottleneck_df,

            sector_df

        )


    # ==========================================================
    # CAPACITY TREND ANALYSIS
    # ==========================================================

    @staticmethod
    def build_capacity_trends(

        summary_df: pd.DataFrame

    ) -> pd.DataFrame:

        trends = (

            summary_df.copy()

        )

        trends[

            "Capacity_Deterioration"

        ] = (

            trends[

                "Average_Capacity"

            ]

            .iloc[0]

            -

            trends[

                "Average_Capacity"

            ]

        )

        trends[

            "Cost_Expansion"

        ] = (

            trends[

                "Average_Cost_bps"

            ]

            -

            trends[

                "Average_Cost_bps"

            ]

            .iloc[0]

        )

        return trends


    # ==========================================================
    # BOTTLENECK SUMMARY
    # ==========================================================

    @staticmethod
    def build_bottleneck_summary(

        bottleneck_df: pd.DataFrame

    ) -> pd.DataFrame:

        return (

            bottleneck_df

            .groupby(

                [

                    "Symbol"

                ]

            )

            .agg(

                Worst_Capacity=(

                    "Capacity_Score",

                    "min"

                ),

                Highest_Cost=(

                    "Total_Cost_bps",

                    "max"

                ),

                Appearances=(

                    "Symbol",

                    "count"

                )

            )

            .reset_index()

            .sort_values(

                "Worst_Capacity"

            )

        )


    # ==========================================================
    # SECTOR SUMMARY
    # ==========================================================

    @staticmethod
    def build_sector_summary(

        sector_df: pd.DataFrame

    ) -> pd.DataFrame:

        if sector_df.empty:

            return pd.DataFrame()

        if "Sector" not in sector_df.columns:

            return pd.DataFrame()

        return (

            sector_df

            .groupby(

                "Sector",

                dropna=False

            )

            .agg(

                Average_Capacity=(

                    "Average_Capacity",

                    "mean"

                ),

                Worst_Capacity=(

                    "Worst_Capacity",

                    "min"

                ),

                Average_Cost_bps=(

                    "Average_Cost_bps",

                    "mean"

                )

            )

            .reset_index()

            .sort_values(

                "Worst_Capacity"

            )

        )
    
    # ==========================================================
    # EXPORT RESULTS
    # ==========================================================

    def save_results(

        self,

        summary_df: pd.DataFrame,

        bottleneck_df: pd.DataFrame,

        sector_df: pd.DataFrame

    ):

        summary_df.to_csv(

            CAPACITY_REPORT_FILE,

            index=False

        )

        bottleneck_df.to_csv(

            BOTTLENECK_REPORT_FILE,

            index=False

        )

        sector_df.to_csv(

            SECTOR_REPORT_FILE,

            index=False

        )

        logger.info(

            "Capacity Reports Exported"

        )

    # ==========================================================
    # AUDIT LOG
    # ==========================================================

    def create_audit_log(

        self,

        summary_df: pd.DataFrame

    ):

        audit = pd.DataFrame(

            {

                "Timestamp": [

                    pd.Timestamp.now()

                ],

                "Scenarios": [

                    len(

                        summary_df

                    )

                ],

                "Max_AUM": [

                    summary_df[
                        "AUM"
                    ].max()

                ],

                "Min_Capacity": [

                    summary_df[
                        "Worst_Capacity"
                    ].min()

                ],

                "Max_Cost_bps": [

                    summary_df[
                        "Worst_Cost_bps"
                    ].max()

                ]

            }

        )

        audit.to_csv(

            AUDIT_LOG_FILE,

            index=False

        )

        logger.info(

            "Audit Log Saved"

        )

    # ==========================================================
    # DASHBOARD
    # ==========================================================

    @staticmethod
    def print_dashboard(

        summary_df: pd.DataFrame

    ):

        print()

        print(

            "=" * 80

        )

        print(

            "INSTITUTIONAL CAPACITY STRESS TEST"

        )

        print(

            "=" * 80

        )

        print(

            summary_df

        )

        print(

            "=" * 80

        )

        print(

            f"Scenarios Tested: "

            f"{len(summary_df)}"

        )

        print(

            f"Worst Capacity: "

            f"{summary_df['Worst_Capacity'].min():.2f}"

        )

        print(

            f"Highest Cost (bps): "

            f"{summary_df['Worst_Cost_bps'].max():.2f}"

        )

        print(

            "=" * 80

        )

# ==========================================================
# CLI RUNNER
# ==========================================================

def run_example():

    logger.info(

        "Loading Trade File"

    )

    trades = pd.read_csv(

        TRADE_FILE

    )

    logger.info(

        f"Trades Loaded: "

        f"{len(trades):,}"

    )

    engine = (

        CapacityStressEngine()

    )

    (

        summary_df,

        bottleneck_df,

        sector_df

    ) = (

        engine.run_stress_test(

            trades

        )

    )

    summary_df = (

        engine.build_capacity_trends(

            summary_df

        )

    )

    bottleneck_df = (

        engine.build_bottleneck_summary(

            bottleneck_df

        )

    )

    sector_df = (

        engine.build_sector_summary(

            sector_df

        )

    )

    engine.save_results(

        summary_df,

        bottleneck_df,

        sector_df

    )

    engine.create_audit_log(

        summary_df

    )

    engine.print_dashboard(

        summary_df

    )


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    run_example()