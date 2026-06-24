from __future__ import annotations

import logging

from pathlib import Path

import pandas as pd

import numpy as np


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


ROOT_DIR = (

    Path(__file__)

    .resolve()

    .parents[1]

)

DATA_DIR = (

    ROOT_DIR

    / "data"

)

PERFORMANCE_DIR = (

    DATA_DIR

    / "performance"

)

FORECAST_FILE = (

    PERFORMANCE_DIR

    / "performance_forecast.csv"

)

MACRO_REGIME_FILE = (

    DATA_DIR

    / "regime"

    / "macro_regime_dashboard.csv"

)

OUTPUT_FILE = (

    PERFORMANCE_DIR

    / "multi_horizon_forecast_dashboard.csv"

)

class MultiHorizonForecastValidator:

    @staticmethod
    def validate():

        if not FORECAST_FILE.exists():

            raise FileNotFoundError(

                FORECAST_FILE

            )

        logger.info(

            "Forecast Validation Passed"

        )

class MultiHorizonForecastRepository:

    @staticmethod
    def load():

        logger.info(

            "Loading Forecast Data"

        )

        return pd.read_csv(

            FORECAST_FILE

        )
    
class ForecastMetricsExtractor:

    @staticmethod
    def extract(

        forecast

    ):

        if (

            "Metric" in forecast.columns

            and

            "Value" in forecast.columns

        ):

            metrics = dict(

                zip(

                    forecast["Metric"],

                    forecast["Value"]

                )

            )

        else:

            metrics = (

                forecast

                .iloc[0]

                .to_dict()

            )
            
        expected_return = float(

            metrics.get(

                "Expected_Return_12M",

                0

            )

        )

        confidence = float(

            metrics.get(

                "Forecast_Confidence",

                50

            )

        )

        regime = str(

            metrics.get(

                "Forecast_Regime",

                "NEUTRAL"

            )

        )

        return {

            "Expected_Return_12M":

                expected_return,

            "Forecast_Confidence":

                confidence,

            "Forecast_Regime":

                regime

        }
    
class HorizonProjectionEngine:

    @staticmethod
    def build(

        metrics

    ):

        annual_return = (

            metrics[

                "Expected_Return_12M"

            ]

        )

        confidence = (

            metrics[

                "Forecast_Confidence"

            ]

        )

        regime = (

            metrics[

                "Forecast_Regime"

            ]

        )

        monthly_return = (

            (1 + annual_return)

            ** (1 / 12)

            - 1

        )

        forecast_1m = (

            monthly_return

        )

        forecast_3m = (

            (1 + monthly_return)

            ** 3

            - 1

        )

        forecast_6m = (

            (1 + monthly_return)

            ** 6

            - 1

        )

        forecast_12m = (

            annual_return

        )

        return {

            "Forecast_Regime":

                regime,

            "Forecast_Confidence":

                confidence,

            "Forecast_1M":

                forecast_1m,

            "Forecast_3M":

                forecast_3m,

            "Forecast_6M":

                forecast_6m,

            "Forecast_12M":

                forecast_12m

        }

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

class MacroHorizonAdjuster:

    @staticmethod
    def adjust(

        horizon_metrics,

        macro_metrics

    ):

        macro_regime = str(

            macro_metrics.get(

                "Macro_Regime",

                "NEUTRAL"

            )

        )

        if macro_regime == "STRONG_RISK_ON":

            multiplier = 1.20

        elif macro_regime == "RISK_ON":

            multiplier = 1.10

        elif macro_regime == "RISK_OFF":

            multiplier = 0.80

        elif macro_regime == "CRISIS":

            multiplier = 0.50

        else:

            multiplier = 1.00

        horizon_metrics[

            "Forecast_1M"

        ] *= multiplier

        horizon_metrics[

            "Forecast_3M"

        ] *= multiplier

        horizon_metrics[

            "Forecast_6M"

        ] *= multiplier

        horizon_metrics[

            "Forecast_12M"

        ] *= multiplier

        return horizon_metrics

class HorizonConsistencyValidator:

    @staticmethod
    def validate(

        metrics

    ):

        if (

            metrics["Forecast_1M"]

            >

            metrics["Forecast_3M"]

        ):

            raise ValueError(

                "Invalid Horizon Structure"

            )

        if (

            metrics["Forecast_3M"]

            >

            metrics["Forecast_6M"]

        ):

            raise ValueError(

                "Invalid Horizon Structure"

            )

        if (

            metrics["Forecast_6M"]

            >

            metrics["Forecast_12M"]

        ):

            raise ValueError(

                "Invalid Horizon Structure"

            )


class RegimeAdjustmentEngine:

    @staticmethod
    def adjust(

        projections

    ):

        regime = projections[

            "Forecast_Regime"

        ]

        multiplier = 1.0

        if regime == "BULL":

            multiplier = 1.10

        elif regime == "BEAR":

            multiplier = 0.75

        elif regime == "CRISIS":

            multiplier = 0.50

        for key in [

            "Forecast_1M",

            "Forecast_3M",

            "Forecast_6M",

            "Forecast_12M"

        ]:

            projections[key] *= multiplier

        return projections


class ForecastBiasEngine:

    @staticmethod
    def calculate(

        projections,

        macro_metrics

    ):

        forecast_12m = (

            projections[

                "Forecast_12M"

            ]

        )

        confidence = (

            projections[

                "Forecast_Confidence"

            ]

        )

        macro_risk = str(

            macro_metrics.get(

                "Macro_Risk_Level",

                "MODERATE"

            )

        )

        confidence = (

            projections[

                "Forecast_Confidence"

            ]

        )

        if (

            macro_risk == "HIGH"

            and

            forecast_12m >= 0.15

        ):

            return "CAUTIOUS_BULLISH"

        if (

            forecast_12m >= 0.25

            and

            confidence >= 80

        ):

            return "STRONGLY_BULLISH"

        if (

            forecast_12m >= 0.15

            and

            confidence >= 65

        ):

            return "BULLISH"

        if (

            forecast_12m >= 0.05

            and

            confidence >= 50

        ):

            return "NEUTRAL"

        if forecast_12m >= 0:

            return "CAUTIOUS"

        return "BEARISH"
    
    
class MultiHorizonDashboard:

    @staticmethod
    def build(

        projections,

        macro_metrics,

        forecast_bias

    ):

        return pd.DataFrame(

            [

                {

                    "Metric":

                        "Forecast_Regime",

                    "Value":

                        projections[
                            "Forecast_Regime"
                        ]

                },

                {

                    "Metric":

                        "Forecast_Confidence",

                    "Value":

                        projections[
                            "Forecast_Confidence"
                        ]

                },

                {

                    "Metric":

                        "Forecast_Bias",

                    "Value":

                        forecast_bias

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

                        "Forecast_1M",

                    "Value":

                        round(

                            projections[
                                "Forecast_1M"
                            ],

                            4

                        )

                },

                {

                    "Metric":

                        "Forecast_3M",

                    "Value":

                        round(

                            projections[
                                "Forecast_3M"
                            ],

                            4

                        )

                },

                {

                    "Metric":

                        "Forecast_6M",

                    "Value":

                        round(

                            projections[
                                "Forecast_6M"
                            ],

                            4

                        )

                },

                {

                    "Metric":

                        "Forecast_12M",

                    "Value":

                        round(

                            projections[
                                "Forecast_12M"
                            ],

                            4

                        )

                }

            ]

        )
    
class MultiHorizonForecastExporter:

    @staticmethod
    def export(

        dashboard

    ):

        logger.info(

            "Exporting Multi Horizon Forecast"

        )

        dashboard.to_csv(

            OUTPUT_FILE,

            index=False

        )

def run_example():

    logger.info(

        "Starting Multi Horizon Forecast Engine"

    )

    MultiHorizonForecastValidator.validate()

    forecast = (

        MultiHorizonForecastRepository

        .load()

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

    metrics = (

        ForecastMetricsExtractor

        .extract(

            forecast

        )

    )

    projections = (

        HorizonProjectionEngine

        .build(

            metrics

        )

    )

    projections = (

        RegimeAdjustmentEngine

        .adjust(

            projections

        )

    )

    projections = (

        MacroHorizonAdjuster

        .adjust(

            projections,

            macro_metrics

        )

    )

    HorizonConsistencyValidator.validate(

        projections

    )

    forecast_bias = (

        ForecastBiasEngine

        .calculate(

            projections,

            macro_metrics

        )

    )

    dashboard = (

        MultiHorizonDashboard

        .build(

            projections,

            macro_metrics,

            forecast_bias

        )

    )

    MultiHorizonForecastExporter.export(

        dashboard

    )

    print()

    print("=" * 80)

    print(

        "MULTI HORIZON FORECAST"

    )

    print("=" * 80)

    print(

        dashboard

    )

    print("=" * 80)


if __name__ == "__main__":

    run_example()