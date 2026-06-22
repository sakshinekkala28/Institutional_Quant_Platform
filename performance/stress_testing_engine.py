from __future__ import annotations

import logging

from dataclasses import dataclass

from pathlib import Path

import pandas as pd

from core.settings import settings

# ==========================================================
# PATHS
# ==========================================================

ROOT_DIR = (

    settings
    .environment
    .ROOT_DIR

)

PERFORMANCE_DIR = (

    ROOT_DIR

    / "data"

    / "performance"

)

PERFORMANCE_FORECAST_FILE = (

    PERFORMANCE_DIR

    / "performance_forecast.csv"

)

PERFORMANCE_SUMMARY_FILE = (

    PERFORMANCE_DIR

    / "performance_summary.csv"

)

GOVERNANCE_DECISION_FILE = (

    PERFORMANCE_DIR

    / "governance_decision.csv"

)

STRESS_TEST_RESULTS_FILE = (

    PERFORMANCE_DIR

    / "stress_test_results.csv"

)

STRESS_TEST_DASHBOARD_FILE = (

    PERFORMANCE_DIR

    / "stress_test_dashboard.csv"

)

STRESS_COMMITTEE_IMPACT_FILE = (

    PERFORMANCE_DIR

    / "stress_committee_impact.csv"

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
# STRESS MODEL
# ==========================================================

@dataclass

class StressScenario:

    Scenario: str

    Return_Impact: float

    Volatility_Impact: float

    Drawdown_Impact: float

    Stress_Score: float

    Committee_Decision: str

# ==========================================================
# REPOSITORY
# ==========================================================

class StressRepository:

    @staticmethod
    def load_forecast() -> pd.DataFrame:

        logger.info(

            "Loading Forecast"

        )

        return pd.read_csv(

            PERFORMANCE_FORECAST_FILE

        )

    @staticmethod
    def load_summary() -> pd.DataFrame:

        logger.info(

            "Loading Summary"

        )

        return pd.read_csv(

            PERFORMANCE_SUMMARY_FILE

        )

    @staticmethod
    def load_committee() -> pd.DataFrame:

        logger.info(

            "Loading Committee Decision"

        )

        return pd.read_csv(

            GOVERNANCE_DECISION_FILE

        )
    
# ==========================================================
# VALIDATOR
# ==========================================================

class StressValidator:

    @staticmethod
    def validate(

        forecast: pd.DataFrame,

        summary: pd.DataFrame,

        committee: pd.DataFrame

    ):

        if forecast.empty:

            raise ValueError(

                "Forecast Empty"

            )

        if summary.empty:

            raise ValueError(

                "Summary Empty"

            )

        if committee.empty:

            raise ValueError(

                "Committee Empty"

            )

        logger.info(

            "Stress Validation Passed"

        )

# ==========================================================
# GFC STRESS ENGINE
# ==========================================================

class GFCStressEngine:

    @staticmethod
    def build(

        forecast: pd.DataFrame

    ) -> dict:

        logger.info(

            "Building 2008 GFC Stress"

        )

        row = (

            forecast

            .iloc[0]

        )

        return {

            "Scenario":

                "2008_GFC",

            "Return_Impact":

                -0.55,

            "Volatility_Impact":

                float(

                    row[
                        "Expected_Volatility"
                    ]

                    * 3.00

                ),

            "Drawdown_Impact":

                float(

                    row[
                        "Expected_Max_Drawdown"
                    ]

                    * 3.50

                )

        }
    
# ==========================================================
# COVID CRASH ENGINE
# ==========================================================

class CovidStressEngine:

    @staticmethod
    def build(

        forecast: pd.DataFrame

    ) -> dict:

        logger.info(

            "Building COVID Crash Stress"

        )

        row = (

            forecast

            .iloc[0]

        )

        return {

            "Scenario":

                "COVID_CRASH",

            "Return_Impact":
                -0.35,


            "Volatility_Impact":

                float(

                    row[
                        "Expected_Volatility"
                    ]

                    * 2.50

                ),

            "Drawdown_Impact":

                float(

                    row[
                        "Expected_Max_Drawdown"
                    ]

                    * 2.80

                )

        }
    
# ==========================================================
# RATE HIKE SHOCK ENGINE
# ==========================================================

class RateHikeStressEngine:

    @staticmethod
    def build(

        forecast: pd.DataFrame

    ) -> dict:

        logger.info(

            "Building Rate Hike Shock"

        )

        row = (

            forecast

            .iloc[0]

        )

        return {

            "Scenario":

                "RATE_HIKE_SHOCK",

            "Return_Impact":

                float(

                    row[
                        "Expected_Return_12M"
                    ]

                    - 0.20

                ),

            "Volatility_Impact":

                float(

                    row[
                        "Expected_Volatility"
                    ]

                    * 1.60

                ),

            "Drawdown_Impact":

                float(

                    row[
                        "Expected_Max_Drawdown"
                    ]

                    * 1.80

                )

        }
    
# ==========================================================
# LIQUIDITY SHOCK ENGINE
# ==========================================================

class LiquidityStressEngine:

    @staticmethod
    def build(

        forecast: pd.DataFrame

    ) -> dict:

        logger.info(

            "Building Liquidity Shock"

        )

        row = (

            forecast

            .iloc[0]

        )

        return {

            "Scenario":

                "LIQUIDITY_SHOCK",

            "Return_Impact":
                -0.25,

            "Volatility_Impact":

                float(

                    row[
                        "Expected_Volatility"
                    ]

                    * 1.90

                ),

            "Drawdown_Impact":

                float(

                    row[
                        "Expected_Max_Drawdown"
                    ]

                    * 2.00

                )

        }

# ==========================================================
# MARKET CRASH ENGINE
# ==========================================================

class MarketCrashStressEngine:

    @staticmethod
    def build(

        forecast: pd.DataFrame

    ) -> dict:

        logger.info(

            "Building Market Crash Stress"

        )

        row = (

            forecast

            .iloc[0]

        )

        return {

            "Scenario":

                "MARKET_CRASH_30",

            "Return_Impact":
                -0.30,


            "Volatility_Impact":

                float(

                    row[
                        "Expected_Volatility"
                    ]

                    * 2.00

                ),

            "Drawdown_Impact":

                float(

                    row[
                        "Expected_Max_Drawdown"
                    ]

                    * 3.0

                )

        }
    
# ==========================================================
# VOLATILITY SHOCK ENGINE
# ==========================================================

class VolatilityStressEngine:

    @staticmethod
    def build(

        forecast: pd.DataFrame

    ) -> dict:

        logger.info(

            "Building Volatility Shock"

        )

        row = (

            forecast

            .iloc[0]

        )

        return {

            "Scenario":

                "VOLATILITY_SHOCK",

            "Return_Impact":

                float(

                    row[
                        "Expected_Return_12M"
                    ]

                    - 0.10

                ),

            "Volatility_Impact":

                float(

                    row[
                        "Expected_Volatility"
                    ]

                    * 2.80

                ),

            "Drawdown_Impact":

                float(

                    row[
                        "Expected_Max_Drawdown"
                    ]

                    * 1.50

                )

        }
    
# ==========================================================
# STRESS BUILDER ENGINE
# ==========================================================

class StressBuilderEngine:

    @staticmethod
    def build(

        forecast: pd.DataFrame

    ) -> pd.DataFrame:

        return pd.DataFrame(

            [

                GFCStressEngine.build(

                    forecast

                ),

                CovidStressEngine.build(

                    forecast

                ),

                RateHikeStressEngine.build(

                    forecast

                ),

                LiquidityStressEngine.build(

                    forecast

                ),

                MarketCrashStressEngine.build(

                    forecast

                ),

                VolatilityStressEngine.build(

                    forecast

                )

            ]

        )
    
# ==========================================================
# STRESS SCORE ENGINE
# ==========================================================

class StressScoreEngine:

    @staticmethod
    def calculate(

        stress_df: pd.DataFrame

    ) -> pd.DataFrame:

        logger.info(

            "Calculating Stress Scores"

        )

        df = (

            stress_df

            .copy()

        )

        scores = []

        for _, row in df.iterrows():

            score = 50.0

            adjustment = (

                row["Return_Impact"] * 40

            )

            if adjustment < -50:

                adjustment = -50

            score += adjustment

            if row["Return_Impact"] < -0.50:

                score -= 25

            elif row["Return_Impact"] < -0.35:

                score -= 15

            elif row["Return_Impact"] < -0.20:

                score -= 8

            elif row["Return_Impact"] < -0.10:

                score -= 4

            if row[
                "Volatility_Impact"
            ] > 0.60:

                score -= 20

            elif row[
                "Volatility_Impact"
            ] > 0.40:

                score -= 10

            if row[
                "Drawdown_Impact"
            ] > 0.50:

                score -= 15

            elif row[
                "Drawdown_Impact"
            ] > 0.30:

                score -= 10

            scores.append(

                max(

                    score,

                    0

                )

            )

        df[

            "Stress_Score"

        ] = scores

        return df
    
# ==========================================================
# STRESS RANKING ENGINE
# ==========================================================

class StressRankingEngine:

    @staticmethod
    def build(

        stress_df: pd.DataFrame

    ) -> pd.DataFrame:

        logger.info(

            "Building Stress Rankings"

        )

        df = (

            stress_df

            .copy()

        )

        df = (

            df

            .sort_values(

                "Stress_Score",

                ascending=False

            )

        )

        df[

            "Stress_Rank"

        ] = (

            range(

                1,

                len(df) + 1

            )

        )

        return df
    
# ==========================================================
# STRESS COMMITTEE IMPACT ENGINE
# ==========================================================

class StressCommitteeImpactEngine:

    @staticmethod
    def build(

        stress_df: pd.DataFrame

    ) -> pd.DataFrame:

        logger.info(

            "Building Stress Committee Impact"

        )

        results = []

        for _, row in stress_df.iterrows():

            score = row[

                "Stress_Score"

            ]

            if score >= 85:

                decision = (

                    "APPROVE"

                )

            elif score >= 60:

                decision = (

                    "APPROVE_WITH_CAUTION"

                )

            elif score >= 35:

                decision = (

                    "REVIEW_REQUIRED"

                )

            else:

                decision = (

                    "REJECT"

                )

            results.append(

                {

                    "Scenario":

                        row[
                            "Scenario"
                        ],

                    "Stress_Score":

                        score,

                    "Committee_Decision":

                        decision

                }

            )

        return pd.DataFrame(

            results

        )
    
# ==========================================================
# STRESS SUMMARY ENGINE
# ==========================================================

class StressSummaryEngine:

    @staticmethod
    def build(

        stress_df: pd.DataFrame

    ) -> pd.DataFrame:

        logger.info(

            "Building Stress Summary"

        )

        best = (

            stress_df

            .sort_values(

                "Stress_Score",

                ascending=False

            )

            .iloc[0]

        )

        worst = (

            stress_df

            .sort_values(

                "Stress_Score",

                ascending=True

            )

            .iloc[0]

        )

        return pd.DataFrame(

            [

                {

                    "Metric":

                        "Best_Stress_Scenario",

                    "Value":

                        best[
                            "Scenario"
                        ]

                },

                {

                    "Metric":

                        "Worst_Stress_Scenario",

                    "Value":

                        worst[
                            "Scenario"
                        ]

                },

                {

                    "Metric":

                        "Best_Stress_Score",

                    "Value":

                        best[
                            "Stress_Score"
                        ]

                },

                {

                    "Metric":

                        "Worst_Stress_Score",

                    "Value":

                        worst[
                            "Stress_Score"
                        ]

                }

            ]

        )
    
# ==========================================================
# STRESS DASHBOARD ENGINE
# ==========================================================

class StressDashboardEngine:

    @staticmethod
    def build(

        stress_df: pd.DataFrame,

        committee_impact_df: pd.DataFrame

    ) -> pd.DataFrame:

        logger.info(

            "Building Stress Dashboard"

        )

        best = (

            stress_df

            .sort_values(

                "Stress_Score",

                ascending=False

            )

            .iloc[0]

        )

        worst = (

            stress_df

            .sort_values(

                "Stress_Score",

                ascending=True

            )

            .iloc[0]

        )

        return pd.DataFrame(

            [

                {

                    "Metric":

                        "Best_Stress_Scenario",

                    "Value":

                        best[
                            "Scenario"
                        ]

                },

                {

                    "Metric":

                        "Best_Stress_Score",

                    "Value":

                        best[
                            "Stress_Score"
                        ]

                },

                {

                    "Metric":

                        "Worst_Stress_Scenario",

                    "Value":

                        worst[
                            "Scenario"
                        ]

                },

                {

                    "Metric":

                        "Worst_Stress_Score",

                    "Value":

                        worst[
                            "Stress_Score"
                        ]

                },

                {

                    "Metric":

                        "Approved_Scenarios",

                    "Value":

                        (

                            committee_impact_df[
                                "Committee_Decision"
                            ]

                            ==

                            "APPROVE"

                        )

                        .sum()

                },

                {
                    "Metric":
                        "Rejected_Scenarios",

                    "Value":
                        (
                            committee_impact_df[
                                "Committee_Decision"
                            ]
                            ==
                            "REJECT"
                        ).sum()
                }

            ]

        )
    
# ==========================================================
# EXPORT ENGINE
# ==========================================================

class ExportEngine:

    @staticmethod
    def save(

        stress_df: pd.DataFrame,

        dashboard_df: pd.DataFrame,

        committee_impact_df: pd.DataFrame

    ):

        logger.info(

            "Exporting Stress Reports"

        )

        stress_df.to_csv(

            STRESS_TEST_RESULTS_FILE,

            index=False

        )

        dashboard_df.to_csv(

            STRESS_TEST_DASHBOARD_FILE,

            index=False

        )

        committee_impact_df.to_csv(

            STRESS_COMMITTEE_IMPACT_FILE,

            index=False

        )

        logger.info(

            "Stress Reports Exported"

        )
    
# ==========================================================
# STRESS TESTING ENGINE
# ==========================================================

class StressTestingEngine:

    def run(

        self

    ) -> pd.DataFrame:

        logger.info(

            "Starting Stress Testing"

        )

        forecast = (

            StressRepository

            .load_forecast()

        )

        summary = (

            StressRepository

            .load_summary()

        )

        committee = (

            StressRepository

            .load_committee()

        )

        StressValidator.validate(

            forecast,

            summary,

            committee

        )

        stress_df = (

            StressBuilderEngine

            .build(

                forecast

            )

        )

        stress_df = (

            StressScoreEngine

            .calculate(

                stress_df

            )

        )

        stress_df = (

            StressRankingEngine

            .build(

                stress_df

            )

        )

        committee_impact_df = (

            StressCommitteeImpactEngine

            .build(

                stress_df

            )

        )

        dashboard_df = (

            StressDashboardEngine

            .build(

                stress_df,

                committee_impact_df

            )

        )

        ExportEngine.save(

            stress_df,

            dashboard_df,

            committee_impact_df

        )

        logger.info(

            "Stress Testing Complete"

        )

        return stress_df
    
# ==========================================================
# RUNNER
# ==========================================================

def run_example():

    result = (

        StressTestingEngine()

        .run()

    )

    print()

    print(

        "=" * 80

    )

    print(

        "STRESS TEST SUMMARY"

    )

    print(

        "=" * 80

    )

    print(

        result[

            [

                "Scenario",

                "Stress_Score",

                "Stress_Rank"

            ]

        ]

    )

    print(

        "=" * 80

    )


if __name__ == "__main__":

    run_example()