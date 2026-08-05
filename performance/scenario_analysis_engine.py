from __future__ import annotations

import logging
from dataclasses import dataclass

import pandas as pd

from core.settings import settings

# ==========================================================
# PATHS
# ==========================================================

ROOT_DIR = settings.environment.ROOT_DIR

PERFORMANCE_DIR = ROOT_DIR / "data" / "performance"

PERFORMANCE_FORECAST_FILE = PERFORMANCE_DIR / "performance_forecast.csv"

PERFORMANCE_SUMMARY_FILE = PERFORMANCE_DIR / "performance_summary.csv"

GOVERNANCE_DECISION_FILE = PERFORMANCE_DIR / "governance_decision.csv"

SCENARIO_ANALYSIS_FILE = PERFORMANCE_DIR / "scenario_analysis.csv"

SCENARIO_DASHBOARD_FILE = PERFORMANCE_DIR / "scenario_dashboard.csv"

SCENARIO_COMMITTEE_IMPACT_FILE = PERFORMANCE_DIR / "scenario_committee_impact.csv"

# ==========================================================
# LOGGING
# ==========================================================

logging.basicConfig(
    level=logging.INFO, format=("%(asctime)s | %(levelname)s | %(message)s")
)

logger = logging.getLogger(__name__)

# ==========================================================
# SCENARIO MODEL
# ==========================================================


@dataclass
class ScenarioResult:
    Scenario: str

    Expected_Return: float

    Expected_Volatility: float

    Expected_Drawdown: float

    Expected_Sharpe: float

    Committee_Impact: str


# ==========================================================
# REPOSITORY
# ==========================================================


class ScenarioRepository:
    @staticmethod
    def load_forecast() -> pd.DataFrame:

        logger.info("Loading Forecast")

        return pd.read_csv(PERFORMANCE_FORECAST_FILE)

    @staticmethod
    def load_summary() -> pd.DataFrame:

        logger.info("Loading Performance Summary")

        return pd.read_csv(PERFORMANCE_SUMMARY_FILE)

    @staticmethod
    def load_committee() -> pd.DataFrame:

        logger.info("Loading Governance Decision")

        return pd.read_csv(GOVERNANCE_DECISION_FILE)


# ==========================================================
# VALIDATOR
# ==========================================================


class ScenarioValidator:
    @staticmethod
    def validate(
        forecast: pd.DataFrame, summary: pd.DataFrame, committee: pd.DataFrame
    ):

        if forecast.empty:
            raise ValueError("Forecast Empty")

        if summary.empty:
            raise ValueError("Summary Empty")

        if committee.empty:
            raise ValueError("Committee Decision Empty")

        logger.info("Scenario Validation Passed")


# ==========================================================
# BULL SCENARIO ENGINE
# ==========================================================


class BullScenarioEngine:
    @staticmethod
    def build(forecast: pd.DataFrame) -> ScenarioResult:

        logger.info("Building Bull Scenario")

        row = forecast.iloc[0]

        return ScenarioResult(
            Scenario="BULL",
            Expected_Return=float(row["Expected_Return_12M"] * 1.25),
            Expected_Volatility=float(row["Expected_Volatility"] * 0.90),
            Expected_Drawdown=float(row["Expected_Max_Drawdown"] * 0.80),
            Expected_Sharpe=float(row["Expected_Sharpe"] * 1.15),
            Committee_Impact="STRONG_APPROVAL",
        )


# ==========================================================
# BASE SCENARIO ENGINE
# ==========================================================


class BaseScenarioEngine:
    @staticmethod
    def build(forecast: pd.DataFrame) -> ScenarioResult:

        logger.info("Building Base Scenario")

        row = forecast.iloc[0]

        return ScenarioResult(
            Scenario="BASE",
            Expected_Return=float(row["Expected_Return_12M"]),
            Expected_Volatility=float(row["Expected_Volatility"]),
            Expected_Drawdown=float(row["Expected_Max_Drawdown"]),
            Expected_Sharpe=float(row["Expected_Sharpe"]),
            Committee_Impact="APPROVE",
        )


# ==========================================================
# BEAR SCENARIO ENGINE
# ==========================================================


class BearScenarioEngine:
    @staticmethod
    def build(forecast: pd.DataFrame) -> ScenarioResult:

        logger.info("Building Bear Scenario")

        row = forecast.iloc[0]

        return ScenarioResult(
            Scenario="BEAR",
            Expected_Return=float(row["Expected_Return_12M"] * 0.40),
            Expected_Volatility=float(row["Expected_Volatility"] * 1.40),
            Expected_Drawdown=float(row["Expected_Max_Drawdown"] * 1.80),
            Expected_Sharpe=float(row["Expected_Sharpe"] * 0.50),
            Committee_Impact="REVIEW_REQUIRED",
        )


# ==========================================================
# CRISIS SCENARIO ENGINE
# ==========================================================


class CrisisScenarioEngine:
    @staticmethod
    def build(forecast: pd.DataFrame) -> ScenarioResult:

        logger.info("Building Crisis Scenario")

        row = forecast.iloc[0]

        return ScenarioResult(
            Scenario="CRISIS",
            Expected_Return=float(row["Expected_Return_12M"] * -0.50),
            Expected_Volatility=float(row["Expected_Volatility"] * 2.50),
            Expected_Drawdown=float(row["Expected_Max_Drawdown"] * 3.00),
            Expected_Sharpe=float(row["Expected_Sharpe"] * -0.50),
            Committee_Impact="REJECT",
        )


# ==========================================================
# SCENARIO BUILDER ENGINE
# ==========================================================


class ScenarioBuilderEngine:
    @staticmethod
    def build(forecast: pd.DataFrame) -> pd.DataFrame:

        bull = BullScenarioEngine.build(forecast)

        base = BaseScenarioEngine.build(forecast)

        bear = BearScenarioEngine.build(forecast)

        crisis = CrisisScenarioEngine.build(forecast)

        return pd.DataFrame(
            [bull.__dict__, base.__dict__, bear.__dict__, crisis.__dict__]
        )


# ==========================================================
# SCENARIO SCORE ENGINE
# ==========================================================


class ScenarioScoreEngine:
    @staticmethod
    def calculate(scenario_df: pd.DataFrame) -> pd.DataFrame:

        logger.info("Calculating Scenario Scores")

        df = scenario_df.copy()

        scores = []

        for _, row in df.iterrows():
            score = 50.0

            score += min(row["Expected_Return"] * 100, 30)

            score += min(row["Expected_Sharpe"] * 10, 20)

            if row["Expected_Return"] < 0:
                score -= 40

            elif row["Expected_Return"] < 0.10:
                score -= 20

            elif row["Expected_Return"] < 0.20:
                score -= 10

            if row["Expected_Volatility"] > 0.40:
                score -= 30

            elif row["Expected_Volatility"] > 0.25:
                score -= 15

            if row["Expected_Drawdown"] > 0.40:
                score -= 30

            elif row["Expected_Drawdown"] > 0.25:
                score -= 15

            scores.append(max(score, 0))

        df["Scenario_Score"] = scores

        return df


# ==========================================================
# SCENARIO STRESS RANKING ENGINE
# ==========================================================


class ScenarioStressRankingEngine:
    @staticmethod
    def build(scenario_df: pd.DataFrame) -> pd.DataFrame:

        logger.info("Building Scenario Rankings")

        df = scenario_df.copy()

        df = df.sort_values("Scenario_Score", ascending=False)

        df["Scenario_Rank"] = range(1, len(df) + 1)

        return df


# ==========================================================
# COMMITTEE IMPACT ENGINE
# ==========================================================


class CommitteeImpactEngine:
    @staticmethod
    def build(scenario_df: pd.DataFrame) -> pd.DataFrame:

        logger.info("Building Committee Impact")

        impacts = []

        for _, row in scenario_df.iterrows():
            score = row["Scenario_Score"]

            if score >= 85:
                decision = "APPROVE"

            elif score >= 70:
                decision = "APPROVE_WITH_CAUTION"

            elif score >= 40:
                decision = "REVIEW_REQUIRED"

            else:
                decision = "REJECT"

            impacts.append(
                {
                    "Scenario": row["Scenario"],
                    "Scenario_Score": score,
                    "Committee_Decision": decision,
                }
            )

        return pd.DataFrame(impacts)


# ==========================================================
# SCENARIO SUMMARY ENGINE
# ==========================================================


class ScenarioSummaryEngine:
    @staticmethod
    def build(scenario_df: pd.DataFrame) -> pd.DataFrame:

        logger.info("Building Scenario Summary")

        best = scenario_df.sort_values("Scenario_Score", ascending=False).iloc[0]

        worst = scenario_df.sort_values("Scenario_Score", ascending=True).iloc[0]

        return pd.DataFrame(
            [
                {"Metric": "Best_Scenario", "Value": best["Scenario"]},
                {"Metric": "Worst_Scenario", "Value": worst["Scenario"]},
                {"Metric": "Best_Score", "Value": best["Scenario_Score"]},
                {"Metric": "Worst_Score", "Value": worst["Scenario_Score"]},
            ]
        )


# ==========================================================
# SCENARIO DASHBOARD ENGINE
# ==========================================================


class ScenarioDashboardEngine:
    @staticmethod
    def build(
        scenario_df: pd.DataFrame, committee_impact_df: pd.DataFrame
    ) -> pd.DataFrame:

        logger.info("Building Scenario Dashboard")

        best = scenario_df.sort_values("Scenario_Score", ascending=False).iloc[0]

        worst = scenario_df.sort_values("Scenario_Score", ascending=True).iloc[0]

        return pd.DataFrame(
            [
                {"Metric": "Best_Scenario", "Value": best["Scenario"]},
                {"Metric": "Best_Scenario_Score", "Value": best["Scenario_Score"]},
                {"Metric": "Worst_Scenario", "Value": worst["Scenario"]},
                {"Metric": "Worst_Scenario_Score", "Value": worst["Scenario_Score"]},
                {
                    "Metric": "Committee_Approvals",
                    "Value": (
                        committee_impact_df["Committee_Decision"] == "APPROVE"
                    ).sum(),
                },
            ]
        )


# ==========================================================
# EXPORT ENGINE
# ==========================================================


class ExportEngine:
    @staticmethod
    def save(
        scenario_df: pd.DataFrame,
        dashboard_df: pd.DataFrame,
        committee_impact_df: pd.DataFrame,
    ):

        logger.info("Exporting Scenario Reports")

        scenario_df.to_csv(SCENARIO_ANALYSIS_FILE, index=False)

        dashboard_df.to_csv(SCENARIO_DASHBOARD_FILE, index=False)

        committee_impact_df.to_csv(SCENARIO_COMMITTEE_IMPACT_FILE, index=False)

        logger.info("Scenario Reports Exported")


# ==========================================================
# SCENARIO ANALYSIS ENGINE
# ==========================================================


class ScenarioAnalysisEngine:
    def run(self) -> pd.DataFrame:

        logger.info("Starting Scenario Analysis")

        forecast = ScenarioRepository.load_forecast()

        summary = ScenarioRepository.load_summary()

        committee = ScenarioRepository.load_committee()

        ScenarioValidator.validate(forecast, summary, committee)

        scenario_df = ScenarioBuilderEngine.build(forecast)

        scenario_df = ScenarioScoreEngine.calculate(scenario_df)

        scenario_df = ScenarioStressRankingEngine.build(scenario_df)

        committee_impact_df = CommitteeImpactEngine.build(scenario_df)

        dashboard_df = ScenarioDashboardEngine.build(scenario_df, committee_impact_df)

        ExportEngine.save(scenario_df, dashboard_df, committee_impact_df)

        logger.info("Scenario Analysis Complete")

        return scenario_df


# ==========================================================
# RUNNER
# ==========================================================


def run_example():

    result = ScenarioAnalysisEngine().run()

    print()

    print("=" * 80)

    print("SCENARIO ANALYSIS SUMMARY")

    print("=" * 80)

    print(result[["Scenario", "Scenario_Score", "Scenario_Rank", "Committee_Impact"]])

    print("=" * 80)


if __name__ == "__main__":
    run_example()
