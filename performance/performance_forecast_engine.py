from __future__ import annotations

import logging

from dataclasses import dataclass

from pathlib import Path

import numpy as np

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

DATA_DIR = (

    ROOT_DIR

    / "data"

)

PERFORMANCE_DIR = (

    ROOT_DIR

    / "data"

    / "performance"

)

PERFORMANCE_SUMMARY_FILE = (

    PERFORMANCE_DIR

    / "performance_summary.csv"

)

ROLLING_PERFORMANCE_FILE = (

    PERFORMANCE_DIR

    / "rolling_performance.csv"

)

REGIME_SCORECARD_FILE = (

    PERFORMANCE_DIR

    / "regime_scorecard.csv"

)

MACRO_REGIME_FILE = (

    DATA_DIR

    / "regime"

    / "macro_regime_dashboard.csv"

)

PERFORMANCE_FORECAST_FILE = (

    PERFORMANCE_DIR

    / "performance_forecast.csv"

)

REGIME_FORECAST_FILE = (

    PERFORMANCE_DIR

    / "regime_forecast.csv"

)

RETURN_DISTRIBUTION_FILE = (

    PERFORMANCE_DIR

    / "return_distribution.csv"

)

FORECAST_DASHBOARD_FILE = (

    PERFORMANCE_DIR

    / "forecast_dashboard.csv"

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
# FORECAST MODEL
# ==========================================================

@dataclass

class ForecastMetrics:

    Expected_Return_1M: float

    Expected_Return_3M: float

    Expected_Return_12M: float

    Expected_Volatility: float

    Expected_Sharpe: float

    Expected_Information_Ratio: float

    Expected_Max_Drawdown: float

    Rolling_Confidence: float

    Regime_Confidence: float

    Alpha_Confidence: float

    Forecast_Confidence: float

    Forecast_Regime: str

    Forecast_Risk_Grade: str

    Forecast_Recommendation: str

# ==========================================================
# PERFORMANCE REPOSITORY
# ==========================================================

class PerformanceRepository:

    @staticmethod
    def load_summary() -> pd.DataFrame:

        logger.info(

            "Loading Performance Summary"

        )

        if not PERFORMANCE_SUMMARY_FILE.exists():

            raise FileNotFoundError(

                PERFORMANCE_SUMMARY_FILE

            )

        return pd.read_csv(

            PERFORMANCE_SUMMARY_FILE

        )

    @staticmethod
    def load_rolling() -> pd.DataFrame:

        logger.info(

            "Loading Rolling Performance"

        )

        if not ROLLING_PERFORMANCE_FILE.exists():

            raise FileNotFoundError(

                ROLLING_PERFORMANCE_FILE

            )

        return pd.read_csv(

            ROLLING_PERFORMANCE_FILE

        )

    @staticmethod
    def load_regimes() -> pd.DataFrame:

        logger.info(

            "Loading Regime Scorecard"

        )

        if not REGIME_SCORECARD_FILE.exists():

            raise FileNotFoundError(

                REGIME_SCORECARD_FILE

            )

        return pd.read_csv(

            REGIME_SCORECARD_FILE

        )# ==========================================================
# FORECAST VALIDATOR
# ==========================================================

class ForecastValidator:

    @staticmethod
    def validate(

        summary: pd.DataFrame,

        rolling_df: pd.DataFrame,

        regime_df: pd.DataFrame

    ):

        if summary.empty:

            raise ValueError(

                "Performance Summary Empty"

            )

        if rolling_df.empty:

            raise ValueError(

                "Rolling Performance Empty"

            )

        if regime_df.empty:

            raise ValueError(

                "Regime Scorecard Empty"

            )

        rolling_required = [

            "Rolling_Return",

            "Rolling_Volatility",

            "Rolling_Sharpe",

            "Rolling_Information_Ratio",

            "Rolling_Alpha",

            "Rolling_Max_Drawdown",

            "Rolling_Performance_Score"

        ]

        missing = [

            col

            for col in rolling_required

            if col not in rolling_df.columns

        ]

        if missing:

            raise ValueError(

                f"Missing Rolling Columns: {missing}"

            )

        regime_required = [

            "Regime",

            "Annual_Return",

            "Annual_Volatility",

            "Sharpe",

            "Alpha",

            "Regime_Score"

        ]

        missing = [

            col

            for col in regime_required

            if col not in regime_df.columns

        ]

        if missing:

            raise ValueError(

                f"Missing Regime Columns: {missing}"

            )

        logger.info(

            "Forecast Validation Passed"

        )

# ==========================================================
# FORECAST CONFIGURATION
# ==========================================================

class ForecastConfig:

    RETURN_WEIGHT_ROLLING = (

        settings
        .forecast
        .RETURN_WEIGHT_ROLLING

    )

    RETURN_WEIGHT_REGIME = (

        settings
        .forecast
        .RETURN_WEIGHT_REGIME

    )

    RETURN_WEIGHT_HISTORICAL = (

        settings
        .forecast
        .RETURN_WEIGHT_HISTORICAL

    )

    RETURN_WEIGHT_ALPHA = (

        settings
        .forecast
        .RETURN_WEIGHT_ALPHA

    )

    VOL_WEIGHT_ROLLING = (

        settings
        .forecast
        .VOL_WEIGHT_ROLLING

    )

    VOL_WEIGHT_REGIME = (

        settings
        .forecast
        .VOL_WEIGHT_REGIME

    )

# ==========================================================
# EXPECTED RETURN ENGINE
# ==========================================================

class ExpectedReturnEngine:

    @staticmethod
    def calculate(

        summary: pd.DataFrame,

        rolling_df: pd.DataFrame,

        regime_df: pd.DataFrame

    ) -> dict:

        logger.info(

            "Calculating Expected Return"

        )

        summary_row = (

            summary

            .iloc[0]

        )

        rolling_row = (

            rolling_df

            .sort_values(

                "Date"

            )

            .iloc[-1]

        )

        best_regime = (

            regime_df

            .sort_values(

                "Regime_Score",

                ascending=False

            )

            .iloc[0]

        )

        expected_return = (

            ForecastConfig
            .RETURN_WEIGHT_ROLLING

            *

            rolling_row[
                "Rolling_Return"
            ]

            +

            ForecastConfig
            .RETURN_WEIGHT_REGIME

            *

            best_regime[
                "Annual_Return"
            ]

            +

            ForecastConfig
            .RETURN_WEIGHT_HISTORICAL

            *

            summary_row[
                "Annual_Return"
            ]

            +

            ForecastConfig
            .RETURN_WEIGHT_ALPHA

            *

            summary_row[
                "Alpha"
            ]

        )

        return {

            "Expected_Return_1M":

                expected_return

                / 12,

            "Expected_Return_3M":

                expected_return

                / 4,

            "Expected_Return_12M":

                expected_return

        }
    
# ==========================================================
# EXPECTED VOLATILITY ENGINE
# ==========================================================

class ExpectedVolatilityEngine:

    @staticmethod
    def calculate(

        rolling_df: pd.DataFrame,

        regime_df: pd.DataFrame

    ) -> float:

        logger.info(

            "Calculating Expected Volatility"

        )

        rolling_row = (

            rolling_df

            .sort_values(

                "Date"

            )

            .iloc[-1]

        )

        best_regime = (

            regime_df

            .sort_values(

                "Regime_Score",

                ascending=False

            )

            .iloc[0]

        )

        return (

            ForecastConfig
            .VOL_WEIGHT_ROLLING

            *

            rolling_row[
                "Rolling_Volatility"
            ]

            +

            ForecastConfig
            .VOL_WEIGHT_REGIME

            *

            best_regime[
                "Annual_Volatility"
            ]

        )
    
# ==========================================================
# EXPECTED SHARPE ENGINE
# ==========================================================

class ExpectedSharpeEngine:

    @staticmethod
    def calculate(

        expected_return: float,

        expected_volatility: float

    ) -> float:

        logger.info(

            "Calculating Expected Sharpe"

        )

        if (

            expected_volatility

            <= 0

        ):

            return 0.0

        return (

            expected_return

            -

            settings
            .performance
            .RISK_FREE_RATE

        ) / expected_volatility
    
# ==========================================================
# EXPECTED INFORMATION RATIO ENGINE
# ==========================================================

class ExpectedInformationRatioEngine:

    @staticmethod
    def calculate(

        summary: pd.DataFrame,

        rolling_df: pd.DataFrame

    ) -> float:

        logger.info(

            "Calculating Expected Information Ratio"

        )

        summary_row = (

            summary

            .iloc[0]

        )

        rolling_row = (

            rolling_df

            .sort_values(

                "Date"

            )

            .iloc[-1]

        )

        return float(

            np.mean(

                [

                    summary_row[
                        "Information_Ratio"
                    ],

                    rolling_row[
                        "Rolling_Information_Ratio"
                    ]

                ]

            )

        )
    
# ==========================================================
# EXPECTED DRAWDOWN ENGINE
# ==========================================================

class ExpectedDrawdownEngine:

    @staticmethod
    def calculate(

        summary: pd.DataFrame,

        rolling_df: pd.DataFrame,

        regime_df: pd.DataFrame

    ) -> float:

        logger.info(

            "Calculating Expected Drawdown"

        )

        summary_row = (

            summary

            .iloc[0]

        )

        rolling_row = (

            rolling_df

            .sort_values(

                "Date"

            )

            .iloc[-1]

        )

        best_regime = (

            regime_df

            .sort_values(

                "Regime_Score",

                ascending=False

            )

            .iloc[0]

        )

        drawdowns = [

            abs(

                summary_row[
                    "Max_Drawdown"
                ]

            ),

            abs(

                rolling_row[
                    "Rolling_Max_Drawdown"
                ]

            ),

            abs(

                best_regime[
                    "Max_Drawdown"
                ]

            )

        ]

        return float(

            np.mean(

                drawdowns

            )

        )
    
# ==========================================================
# REGIME FORECAST ENGINE
# ==========================================================

class RegimeForecastEngine:

    @staticmethod
    def calculate(

        regime_df: pd.DataFrame

    ) -> pd.DataFrame:

        logger.info(

            "Calculating Regime Forecast"

        )

        forecast = (

            regime_df[

                [

                    "Regime",

                    "Days",

                    "Sharpe",

                    "Information_Ratio",

                    "Alpha",

                    "Regime_Score"

                ]

            ]

            .copy()

        )

        forecast["Raw_Score"] = (

            forecast[
                "Regime_Score"
            ]

            *

            (

                1

                +

                forecast[
                    "Sharpe"
                ]

                .clip(

                    lower=0

                )

            )

        )

        total_score = (

            forecast[
                "Raw_Score"
            ]

            .sum()

        )

        if total_score > 0:

            forecast[

                "Probability"

            ] = (

                forecast[
                    "Raw_Score"
                ]

                /

                total_score

            )

        else:

            forecast[

                "Probability"

            ] = (

                1.0

                /

                len(

                    forecast

                )

            )

        forecast[

            "Probability"

        ] = (

            forecast[
                "Probability"
            ]

            * 100

        )

        forecast = (

            forecast

            .sort_values(

                "Probability",

                ascending=False

            )

            .reset_index(

                drop=True

            )

        )

        return forecast

# ==========================================================
# REGIME WEIGHTED FORECAST ENGINE
# ==========================================================

class RegimeWeightedForecastEngine:

    @staticmethod
    def weighted_return(

        regime_df: pd.DataFrame,

        regime_forecast: pd.DataFrame

    ) -> float:

        merged = (

            regime_df

            .merge(

                regime_forecast[

                    [

                        "Regime",

                        "Probability"

                    ]

                ],

                on="Regime",

                how="inner"

            )

        )

        return float(

            (

                merged[
                    "Annual_Return"
                ]

                *

                (

                    merged[
                        "Probability"
                    ]

                    / 100

                )

            ).sum()

        )

    @staticmethod
    def weighted_volatility(

        regime_df: pd.DataFrame,

        regime_forecast: pd.DataFrame

    ) -> float:

        merged = (

            regime_df

            .merge(

                regime_forecast[

                    [

                        "Regime",

                        "Probability"

                    ]

                ],

                on="Regime",

                how="inner"

            )

        )

        return float(

            (

                merged[
                    "Annual_Volatility"
                ]

                *

                (

                    merged[
                        "Probability"
                    ]

                    / 100

                )

            ).sum()

        )

    @staticmethod
    def weighted_drawdown(

        regime_df: pd.DataFrame,

        regime_forecast: pd.DataFrame

    ) -> float:

        merged = (

            regime_df

            .merge(

                regime_forecast[

                    [

                        "Regime",

                        "Probability"

                    ]

                ],

                on="Regime",

                how="inner"

            )

        )

        return float(

            (

                merged[
                    "Max_Drawdown"
                ]

                .abs()

                *

                (

                    merged[
                        "Probability"
                    ]

                    / 100

                )

            ).sum()

        )

class MacroRegimeLoader:

    @staticmethod
    def load():

        logger.info(

            "Loading Macro Regime"

        )

        if not MACRO_REGIME_FILE.exists():

            raise FileNotFoundError(

                MACRO_REGIME_FILE

            )
        
        return pd.read_csv(

            MACRO_REGIME_FILE

        )

class MacroForecastAdjuster:

    @staticmethod
    def adjust(

        expected_return,

        forecast_confidence,

        macro_metrics

    ):

        macro_regime = str(

            macro_metrics.get(

                "Macro_Regime",

                "NEUTRAL"

            )

        )

        if macro_regime == "STRONG_RISK_ON":

            expected_return *= 1.20

            forecast_confidence += 15

        elif macro_regime == "RISK_ON":

            expected_return *= 1.10

            forecast_confidence += 10

        elif macro_regime == "RISK_OFF":

            expected_return *= 0.75

            forecast_confidence -= 10

        elif macro_regime == "CRISIS":

            expected_return *= 0.50

            forecast_confidence -= 20

        forecast_confidence = max(

            0,

            min(

                100,

                forecast_confidence

            )

        )

        macro_confidence = float(

            macro_metrics.get(

                "Macro_Confidence",

                50

            )

        )

        forecast_confidence = (

            0.80

            * forecast_confidence

            +

            0.20

            * macro_confidence

        )

        forecast_confidence = max(

            0,

            min(

                100,

                forecast_confidence

            )

        )

        return (

            expected_return,

            forecast_confidence

        )
                
# ==========================================================
# RETURN DISTRIBUTION ENGINE
# ==========================================================

class ReturnDistributionEngine:

    @staticmethod
    def build(

        expected_return: float,

        expected_volatility: float

    ) -> pd.DataFrame:

        logger.info(

            "Building Return Distribution"

        )

        z_scores = {

            "Worst_Case":

                -2.33,

            "Bear_Case":

                -1.28,

            "Base_Case":

                0.00,

            "Bull_Case":

                1.28,

            "Best_Case":

                2.33

        }

        rows = []

        for scenario, z in (

            z_scores.items()

        ):

            projected_return = (

                expected_return

                +

                (

                    z

                    *

                    expected_volatility

                )

            )

            rows.append(

                {

                    "Scenario":

                        scenario,

                    "Z_Score":

                        z,

                    "Expected_Return":

                        projected_return

                }

            )

        return pd.DataFrame(

            rows

        )
    
# ==========================================================
# FORECAST CONFIDENCE ENGINE
# ==========================================================

class ForecastConfidenceEngine:

    @staticmethod
    def calculate(

        rolling_df: pd.DataFrame,

        regime_df: pd.DataFrame

    ) -> float:

        logger.info(

            "Calculating Forecast Confidence"

        )

        rolling_row = (

            rolling_df

            .sort_values(

                "Date"

            )

            .iloc[-1]

        )

        best_regime = (

            regime_df

            .sort_values(

                "Regime_Score",

                ascending=False

            )

            .iloc[0]

        )

        score = (

            (

                rolling_row[

                    "Rolling_Performance_Score"

                ]

                * 0.60

            )

            +

            (

                best_regime[

                    "Regime_Score"

                ]

                * 0.40

            )

        )

        return float(

            min(

                max(

                    score,

                    0

                ),

                100

            )

        )
    
# ==========================================================
# FORECAST REGIME SELECTOR
# ==========================================================

class ForecastRegimeSelector:

    @staticmethod
    def calculate(

        regime_forecast: pd.DataFrame

    ) -> str:

        logger.info(

            "Selecting Forecast Regime"

        )

        if regime_forecast.empty:

            return "UNKNOWN"

        return str(

            regime_forecast

            .iloc[0][

                "Regime"

            ]

        )

# ==========================================================
# CONFIDENCE BREAKDOWN ENGINE
# ==========================================================

class ConfidenceBreakdownEngine:

    @staticmethod
    def calculate(

        summary: pd.DataFrame,

        rolling_df: pd.DataFrame,

        regime_df: pd.DataFrame

    ) -> dict:

        logger.info(

            "Calculating Confidence Breakdown"

        )

        rolling_row = (

            rolling_df

            .sort_values(

                "Date"

            )

            .iloc[-1]

        )

        best_regime = (

            regime_df

            .sort_values(

                "Regime_Score",

                ascending=False

            )

            .iloc[0]

        )

        summary_row = (

            summary

            .iloc[0]

        )

        rolling_confidence = float(

            rolling_row[
                "Rolling_Performance_Score"
            ]

        )

        regime_confidence = (

            best_regime[
                "Regime_Score"
            ]

            * 0.90

        )

        alpha_confidence = float(

            min(

                100,

                max(

                    0,

                    (

                        (
                            summary_row[
                                "Information_Ratio"
                            ]
                            * 20
                        )

                        +

                        (
                            summary_row[
                                "Alpha"
                            ]
                            * 100
                        )

                    )

                )

            )

        )

        composite_confidence = (

            0.40

            *

            rolling_confidence

            +

            0.40

            *

            regime_confidence

            +

            0.20

            *

            alpha_confidence

        )

        return {

            "Rolling_Confidence":

                rolling_confidence,

            "Regime_Confidence":

                regime_confidence,

            "Alpha_Confidence":

                alpha_confidence,

            "Forecast_Confidence":

                composite_confidence

        }
    
# ==========================================================
# FORECAST RISK GRADE ENGINE
# ==========================================================

class ForecastRiskGradeEngine:

    @staticmethod
    def calculate(

        expected_volatility: float,

        expected_drawdown: float,

        forecast_confidence: float

    ) -> str:

        logger.info(

            "Calculating Forecast Risk Grade"

        )

        risk_score = 0

        # Volatility

        if expected_volatility < 0.15:

            risk_score += 25

        elif expected_volatility < 0.20:

            risk_score += 15

        elif expected_volatility < 0.25:

            risk_score += 5

        # Drawdown

        if expected_drawdown < 0.15:

            risk_score += 25

        elif expected_drawdown < 0.25:

            risk_score += 15

        elif expected_drawdown < 0.35:

            risk_score += 5

        # Confidence

        if forecast_confidence > 80:

            risk_score += 50

        elif forecast_confidence > 60:

            risk_score += 35

        elif forecast_confidence > 40:

            risk_score += 20

        if risk_score >= 75:

            return "LOW"

        elif risk_score >= 55:

            return "MODERATE"

        elif risk_score >= 35:

            return "HIGH"

        return "VERY_HIGH"

# ==========================================================
# FORECAST RECOMMENDATION ENGINE
# ==========================================================

class ForecastRecommendationEngine:

    @staticmethod
    def calculate(

        expected_sharpe: float,

        forecast_regime: str,

        forecast_risk_grade: str

    ) -> str:

        logger.info(

            "Calculating Forecast Recommendation"

        )

        if (

            expected_sharpe >= 1.50

            and

            forecast_regime == "BULL"

            and

            forecast_risk_grade in [

                "LOW",

                "MODERATE"

            ]

        ):

            return "OVERWEIGHT"

        elif (

            expected_sharpe >= 1.00

        ):

            return "MARKET_WEIGHT"

        elif (

            expected_sharpe >= 0.50

        ):

            return "UNDERWEIGHT"

        return "REDUCE"
        
# ==========================================================
# FORECAST DASHBOARD ENGINE
# ==========================================================

class ForecastDashboardEngine:

    @staticmethod
    def build(

        forecast_metrics: ForecastMetrics,

        regime_forecast: pd.DataFrame,

        macro_metrics

    ) -> pd.DataFrame:

        logger.info(

            "Building Forecast Dashboard"

        )

        top_probability = (

            regime_forecast

            .iloc[0][

                "Probability"

            ]

            if not regime_forecast.empty

            else 0.0

        )

        return pd.DataFrame(

            [

                {

                    "Metric":

                        "Expected_Return_1M",

                    "Value":

                        forecast_metrics
                        .Expected_Return_1M

                },

                {

                    "Metric":

                        "Expected_Return_3M",

                    "Value":

                        forecast_metrics
                        .Expected_Return_3M

                },

                {

                    "Metric":

                        "Expected_Return_12M",

                    "Value":

                        forecast_metrics
                        .Expected_Return_12M

                },

                {

                    "Metric":

                        "Expected_Volatility",

                    "Value":

                        forecast_metrics
                        .Expected_Volatility

                },

                {

                    "Metric":

                        "Expected_Sharpe",

                    "Value":

                        forecast_metrics
                        .Expected_Sharpe

                },

                {

                    "Metric":

                        "Expected_Information_Ratio",

                    "Value":

                        forecast_metrics
                        .Expected_Information_Ratio

                },

                {

                    "Metric":

                        "Expected_Max_Drawdown",

                    "Value":

                        forecast_metrics
                        .Expected_Max_Drawdown

                },

                {
                    "Metric":
                        "Rolling_Confidence",

                    "Value":
                        forecast_metrics
                        .Rolling_Confidence
                },

                {
                    "Metric":
                        "Regime_Confidence",

                    "Value":
                        forecast_metrics
                        .Regime_Confidence
                },

                {
                    "Metric":
                        "Alpha_Confidence",

                    "Value":
                        forecast_metrics
                        .Alpha_Confidence
                },

                {

                    "Metric":

                        "Forecast_Confidence",

                    "Value":

                        forecast_metrics
                        .Forecast_Confidence

                },

                {

                    "Metric":

                        "Forecast_Regime",

                    "Value":

                        forecast_metrics
                        .Forecast_Regime

                },

                {
                    "Metric":
                        "Forecast_Risk_Grade",

                    "Value":
                        forecast_metrics
                        .Forecast_Risk_Grade
                },

                {
                    "Metric":
                        "Forecast_Recommendation",

                    "Value":
                        forecast_metrics
                        .Forecast_Recommendation
                },

                {

                    "Metric":

                        "Macro_Score",

                    "Value":

                        macro_metrics.get(

                            "Macro_Score"

                        )

                },

                {

                    "Metric":

                        "Macro_Regime",

                    "Value":

                        macro_metrics.get(

                            "Macro_Regime"

                        )

                },

                {

                    "Metric":

                        "Macro_Risk_Level",

                    "Value":

                        macro_metrics.get(
                
                            "Macro_Risk_Level"

                        )

                },

                {

                    "Metric":

                        "Macro_Confidence",

                    "Value":

                        macro_metrics.get(

                            "Macro_Confidence"

                        )

                },

                {

                    "Metric":

                        "Macro_Recommendation",

                    "Value":

                        macro_metrics.get(

                            "Macro_Recommendation"

                        )

                },

                {

                    "Metric":

                        "Regime_Probability",

                    "Value":

                        top_probability

                }

            ]

        )
       
# ==========================================================
# EXPORT ENGINE
# ==========================================================

class ExportEngine:

    @staticmethod
    def save(

        forecast_df: pd.DataFrame,

        regime_forecast: pd.DataFrame,

        distribution_df: pd.DataFrame,

        dashboard_df: pd.DataFrame

    ):

        logger.info(

            "Exporting Forecast Reports"

        )

        forecast_df.to_csv(

            PERFORMANCE_FORECAST_FILE,

            index=False

        )

        regime_forecast.to_csv(

            REGIME_FORECAST_FILE,

            index=False

        )

        distribution_df.to_csv(

            RETURN_DISTRIBUTION_FILE,

            index=False

        )

        dashboard_df.to_csv(

            FORECAST_DASHBOARD_FILE,

            index=False

        )

        logger.info(

            "Forecast Reports Exported"

        )


class RecommendationOverrideEngine:

    @staticmethod
    def apply(

        forecast_recommendation,

        macro_recommendation

    ):

        ranking = {

            "OVERWEIGHT": 4,

            "MARKET_WEIGHT": 3,

            "UNDERWEIGHT": 2,

            "REDUCE": 1

        }

        if macro_recommendation == "AGGRESSIVE_OVERWEIGHT":

            macro_rank = 4

        elif macro_recommendation == "OVERWEIGHT":

            macro_rank = 3

        elif macro_recommendation == "UNDERWEIGHT":

            macro_rank = 2

        elif macro_recommendation == "REDUCE":

            macro_rank = 1

        else:

            macro_rank = forecast_rank


        forecast_rank = ranking.get(

            forecast_recommendation,

            1

        )

        final_rank = min(

            forecast_rank,

            macro_rank

        )

        reverse_map = {

            value: key

            for key, value

            in ranking.items()

        }

        return reverse_map[

            final_rank

        ]
    
# ==========================================================
# PERFORMANCE FORECAST ENGINE
# ==========================================================

class PerformanceForecastEngine:

    def run(

        self

    ):

        logger.info(

            "Starting Performance Forecast"

        )

        summary = (

            PerformanceRepository

            .load_summary()

        )

        rolling_df = (

            PerformanceRepository

            .load_rolling()

        )

        regime_df = (

            PerformanceRepository

            .load_regimes()

        )

        ForecastValidator.validate(

            summary,

            rolling_df,

            regime_df

        )

        macro_df = (

            MacroRegimeLoader

            .load()

        )

        macro_metrics = dict(

            zip(

                macro_df["Metric"],

                macro_df["Value"]

            )

        )

        regime_forecast = (

            RegimeForecastEngine

            .calculate(

                regime_df

            )

        )

        weighted_regime_return = (

            RegimeWeightedForecastEngine

            .weighted_return(

                regime_df,

                regime_forecast

            )

        )

        expected_returns = (

            ExpectedReturnEngine

            .calculate(

                summary,

                rolling_df,

                regime_df

            )

        )

        expected_returns[

            "Expected_Return_12M"

        ] = (

            0.60

            *

            expected_returns[

                "Expected_Return_12M"

            ]

            +

            0.40

            *

            weighted_regime_return

        )

        weighted_regime_volatility = (

            RegimeWeightedForecastEngine

            .weighted_volatility(

                regime_df,

                regime_forecast

            )

        )

        expected_volatility = (

            0.60

            *

            ExpectedVolatilityEngine

            .calculate(

                rolling_df,

                regime_df

            )

            +

            0.40

            *

            weighted_regime_volatility

        )

        expected_information_ratio = (

            ExpectedInformationRatioEngine

            .calculate(

                summary,

                rolling_df

            )

        )

        weighted_regime_drawdown = (

            RegimeWeightedForecastEngine

            .weighted_drawdown(

                regime_df,

                regime_forecast

            )

        )

        expected_drawdown = (

            0.60

            *

            ExpectedDrawdownEngine

            .calculate(

                summary,

                rolling_df,

                regime_df

            )

            +

            0.40

            *

            weighted_regime_drawdown

        )

        confidence_breakdown = (

            ConfidenceBreakdownEngine

            .calculate(

                summary,

                rolling_df,

                regime_df

            )

        )

        forecast_confidence = (

            confidence_breakdown[

                "Forecast_Confidence"

            ]

        )

        (

            expected_returns[

                "Expected_Return_12M"

            ],

            forecast_confidence

        ) = (

            MacroForecastAdjuster

            .adjust(

                expected_returns[

                    "Expected_Return_12M"

                ],

                forecast_confidence,

                macro_metrics

            )

        )

        expected_returns[

            "Expected_Return_3M"

        ] = (

            expected_returns[

                "Expected_Return_12M"

            ]

            / 4

        )

        expected_returns[

            "Expected_Return_1M"

        ] = (

            expected_returns[

                "Expected_Return_12M"

            ]

            / 12

        )

        expected_sharpe = (

            ExpectedSharpeEngine

            .calculate(

                expected_returns[

                    "Expected_Return_12M"

                ],

                expected_volatility

            )

        )

        forecast_risk_grade = (

            ForecastRiskGradeEngine

            .calculate(

                expected_volatility,

                expected_drawdown,

                forecast_confidence

            )

        )

        forecast_regime = (

            ForecastRegimeSelector

            .calculate(

                regime_forecast

            )

        )

        forecast_recommendation = (

            ForecastRecommendationEngine

            .calculate(

                expected_sharpe,

                forecast_regime,

                forecast_risk_grade

            )

        )

        macro_recommendation = str(

            macro_metrics.get(

                "Macro_Recommendation",

                ""

            )

        )

        forecast_recommendation = (

            RecommendationOverrideEngine

            .apply(

                forecast_recommendation,

                macro_recommendation

            )

        )

        distribution_df = (

            ReturnDistributionEngine

            .build(

                expected_returns[

                    "Expected_Return_12M"

                ],

                expected_volatility

            )

        )

        forecast_metrics = (

            ForecastMetrics(

                Expected_Return_1M=

                    expected_returns[

                        "Expected_Return_1M"

                    ],

                Expected_Return_3M=

                    expected_returns[

                        "Expected_Return_3M"

                    ],

                Expected_Return_12M=

                    expected_returns[

                        "Expected_Return_12M"

                    ],

                Expected_Volatility=

                    expected_volatility,

                Expected_Sharpe=

                    expected_sharpe,

                Expected_Information_Ratio=

                    expected_information_ratio,

                Expected_Max_Drawdown=

                    expected_drawdown,

                Rolling_Confidence=

                    confidence_breakdown[

                        "Rolling_Confidence"

                    ],

                Regime_Confidence=

                    confidence_breakdown[

                        "Regime_Confidence"

                    ],

                Alpha_Confidence=

                    confidence_breakdown[

                        "Alpha_Confidence"

                    ],

                Forecast_Confidence=

                    forecast_confidence,

                Forecast_Regime=

                    forecast_regime,

                Forecast_Risk_Grade=

                    forecast_risk_grade,

                Forecast_Recommendation=

                    forecast_recommendation

            )

        )

        forecast_df = pd.DataFrame(

            [

                forecast_metrics.__dict__

            ]

        )

        dashboard_df = (

            ForecastDashboardEngine

            .build(

                forecast_metrics,

                regime_forecast,

                macro_metrics

            )

        )

        ExportEngine.save(

            forecast_df,

            regime_forecast,

            distribution_df,

            dashboard_df

        )

        logger.info(

            "Performance Forecast Complete"

        )

        return forecast_metrics
    
# ==========================================================
# RUNNER
# ==========================================================

def run_example():

    metrics = (

        PerformanceForecastEngine()

        .run()

    )

    print()

    print(

        "=" * 80

    )

    print(

        "INSTITUTIONAL PERFORMANCE FORECAST"

    )

    print(

        "=" * 80

    )

    for key, value in (

        metrics.__dict__

        .items()

    ):

        print(

            f"{key}: {value}"

        )

    print(

        "=" * 80

    )


if __name__ == "__main__":

    run_example()