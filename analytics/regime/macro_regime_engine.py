from __future__ import annotations

import logging

from pathlib import Path

import pandas as pd

import numpy as np

from analytics.regime.macro_repository import (
    MacroRepository,
    MacroLatestValueExtractor
)

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

    .parents[2]

)

DATA_DIR = (

    ROOT_DIR

    / "data"

)

REGIME_DIR = (

    DATA_DIR

    / "regime"

)

MACRO_HISTORY_FILE = (

    REGIME_DIR

    / "macro_regime_history.csv"

)

REGIME_DIR.mkdir(

    parents=True,

    exist_ok=True

)

OUTPUT_FILE = (

    REGIME_DIR

    / "macro_regime_dashboard.csv"

)

class MacroSignalEngine:

    @staticmethod
    def build(

        macro_values

    ):

        logger.info(

            "Building Macro Signals"

        )

        signals = {}

        us10y = macro_values["US10Y"]

        signals["US10Y"] = max(

            0,

            min(

                100,

                100 - (us10y * 10)

            )

        )

        india10y = macro_values["INDIA10Y"]

        signals["INDIA10Y"] = max(

            0,

            min(

                100,

                100 - (india10y * 10)

            )

        )

        cpi = macro_values["CPI"]

        signals["CPI"] = max(

            0,

            min(

                100,

                100 - (cpi * 12)

            )

        )

        wpi = macro_values["WPI"]

        signals["WPI"] = max(

            0,

            min(

                100,

                100 - (wpi * 15)

            )

        )

        usdinr = macro_values["USDINR"]

        signals["USDINR"] = max(

            0,

            min(

                100,

                120 - usdinr

            )

        )

        vix = macro_values["VIX"]

        signals["VIX"] = max(

            0,

            min(

                100,

                100 - (vix * 3)

            )

        )

        return signals
    
class MacroScoreEngine:

    @staticmethod
    def calculate(

        signals

    ):

        logger.info(

            "Calculating Macro Score"

        )

        score = np.mean(

            list(

                signals.values()

            )

        )

        return round(

            score,

            2

        )
    
class MacroRegimeClassifier:

    @staticmethod
    def classify(

        score

    ):

        logger.info(

            "Classifying Macro Regime"

        )

        if score >= 80:

            return (

                "STRONG_RISK_ON",

                "AGGRESSIVE_OVERWEIGHT"

            )

        if score >= 65:

            return (

                "RISK_ON",

                "OVERWEIGHT"

            )

        if score >= 50:

            return (

                "NEUTRAL",

                "MARKET_WEIGHT"

            )

        if score >= 35:

            return (

                "RISK_OFF",

                "UNDERWEIGHT"

            )

        return (

            "CRISIS",

            "DEFENSIVE"

        )
    
class MacroRiskEngine:

    @staticmethod
    def build(

        signals

    ):

        logger.info(

            "Calculating Macro Risk"

        )

        average_signal = np.mean(

            list(

                signals.values()

            )

        )

        if average_signal >= 75:

            return "LOW"

        if average_signal >= 50:

            return "MODERATE"

        return "HIGH"


class MacroHistoryEngine:

    @staticmethod
    def archive(

        score,

        regime,

        risk

    ):

        history_record = pd.DataFrame(

            [

                {

                    "Date":

                        pd.Timestamp.now()

                        .strftime(

                            "%Y-%m-%d"

                        ),

                    "Macro_Score":

                        score,

                    "Macro_Regime":

                        regime,

                    "Macro_Risk_Level":

                        risk

                }

            ]

        )

        if MACRO_HISTORY_FILE.exists():

            existing = pd.read_csv(

                MACRO_HISTORY_FILE

            )

            history_record = pd.concat(

                [

                    existing,

                    history_record

                ],

                ignore_index=True

            )

        history_record.to_csv(

            MACRO_HISTORY_FILE,

            index=False

        )

class MacroConfidenceEngine:

    @staticmethod
    def calculate(

        signals

    ):

        dispersion = np.std(

            list(

                signals.values()

            )

        )

        confidence = max(

            0,

            100 - dispersion

        )

        return round(

            confidence,

            2

        )


class MacroDashboardBuilder:

    @staticmethod
    def build(

        macro_values,

        score,

        confidence,

        regime,

        recommendation,

        risk

    ):

        rows = [

            {

                "Metric":

                    "Macro_Score",

                "Value":

                    score

            },

            {

                "Metric":

                    "Macro_Regime",

                "Value":

                    regime

            },

            {

                "Metric":

                    "Macro_Risk_Level",

                "Value":

                    risk

            },

            {
                "Metric":

                    "Macro_Confidence",

                "Value":

                    confidence
            },

            {

                "Metric":

                    "Macro_Recommendation",

                "Value":

                    recommendation

            }

        ]

        for (

            metric,

            value

        ) in macro_values.items():

            rows.append(

                {

                    "Metric":

                        metric,

                    "Value":

                        value

                }

            )

        return pd.DataFrame(

            rows

        )
    
class MacroRegimeExporter:

    @staticmethod
    def export(

        dashboard

    ):

        logger.info(

            "Exporting Macro Dashboard"

        )

        dashboard.to_csv(

            OUTPUT_FILE,

            index=False

        )

def run_example():

    logger.info(

        "Starting Macro Regime Engine"

    )

    logger.info(

        "Validating Macro Repository"

    )

    macro_data = (

        MacroRepository

        .load()

    )

    macro_values = (

        MacroLatestValueExtractor

        .extract(

            macro_data

        )

    )

    signals = (

        MacroSignalEngine

        .build(

            macro_values

        )

    )

    score = (

        MacroScoreEngine

        .calculate(

            signals

        )

    )

    (

        regime,

        recommendation

    ) = (

        MacroRegimeClassifier

        .classify(

            score

        )

    )

    risk = (

        MacroRiskEngine

        .build(

            signals

        )

    )

    confidence = (

        MacroConfidenceEngine

        .calculate(

            signals

        )

    )

    dashboard = (

        MacroDashboardBuilder

        .build(

            macro_values,

            score,

            confidence,

            regime,

            recommendation,

            risk

        )

    )

    MacroRegimeExporter.export(

        dashboard

    )

    MacroHistoryEngine.archive(

        score,

        regime,

        risk

    )

    print()

    print("=" * 80)

    print(

        "MACRO REGIME DASHBOARD"

    )

    print("=" * 80)

    print(

        dashboard

    )

    print("=" * 80)


if __name__ == "__main__":

    run_example()