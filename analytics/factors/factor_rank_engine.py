"""
=========================================================
FACTOR RANK ENGINE
=========================================================

Purpose:
Convert raw factor values into normalized
sector-neutral percentile ranks and generate
institutional Composite Alpha Scores.

Input
-----
data/factors/factor_master.csv

Outputs
-------
data/factors/factor_rank_master.csv

data/portfolios/top_50.csv
data/portfolios/top_100.csv
data/portfolios/top_250.csv

Reports
-------
data/logs/ranking_report.csv
data/logs/factor_exposure.csv
data/logs/sector_exposure.csv

=========================================================
"""

from __future__ import annotations

from datetime import datetime

import pandas as pd

from config.paths import (
    FACTOR_EXPOSURE_FILE,
    FACTOR_MASTER_FILE,
    FACTOR_RANK_MASTER_FILE,
    PORTFOLIO_DIRECTORY,
    RANKING_REPORT_FILE,
    SECTOR_EXPOSURE_FILE,
)
from config.settings import (
    DATE_FORMAT,
    ENGINE_VERSION,
)
from orchestration.models.engine_result import (
    EngineResult,
)
from orchestration.models.engine_status import (
    EngineStatus,
)
from utils.file_utils import (
    ensure_parent_directory,
)
from utils.logger import (
    get_logger,
)
from utils.timer import (
    Timer,
)

# =========================================================
# CONFIG
# =========================================================

ENGINE_NAME = "FactorRankEngine"

logger = get_logger(__name__)

# =========================================================
# FACTOR DEFINITIONS
# =========================================================

HIGHER_BETTER = [
    "Momentum_1M",
    "Momentum_3M",
    "Momentum_6M",
    "Momentum_12M",
    "ADV_20D",
    "Dollar_Volume",
    "Market_Cap",
    "Log_Market_Cap",
    "Distance_SMA50",
    "Distance_SMA200",
    "Distance_52W_High",
]

LOWER_BETTER = [
    "Volatility_20D",
    "Volatility_60D",
    "ATR_14",
    "Max_Drawdown_252D",
]

# =========================================================
# HELPERS
# =========================================================


def winsorize(
    series: pd.Series,
) -> pd.Series:
    """
    Winsorize a factor series using
    1st and 99th percentiles.
    """

    lower = series.quantile(0.01)

    upper = series.quantile(0.99)

    return series.clip(
        lower=lower,
        upper=upper,
    )


# =========================================================
# MAIN
# =========================================================


def main() -> EngineResult:
    """
    Generate institutional
    factor rankings.
    """

    with Timer() as timer:
        try:
            # =================================================
            # LOAD FACTOR MASTER
            # =================================================

            logger.info("Loading Factor Master...")

            if not FACTOR_MASTER_FILE.exists():
                raise FileNotFoundError(f"Missing file:\n{FACTOR_MASTER_FILE}")

            df = pd.read_csv(FACTOR_MASTER_FILE)

            if df.empty:
                raise ValueError("Factor Master is empty.")

            required_columns = [
                "Security_ID",
                "Symbol",
                "Sector",
                "Alpha_Score" if "Alpha_Score" in df.columns else None,
            ]

            required_columns = [
                column for column in required_columns if column is not None
            ]

            missing = [
                column for column in required_columns if column not in df.columns
            ]

            if missing:
                raise ValueError(f"Missing required columns: {missing}")

            logger.info(
                "Universe Loaded : %s securities",
                f"{len(df):,}",
            )

            # =================================================
            # FACTOR COVERAGE
            # =================================================

            coverage = []

            for factor in HIGHER_BETTER + LOWER_BETTER:
                if factor not in df.columns:
                    raise ValueError(f"Missing factor: {factor}")

                coverage_pct = df[factor].notna().mean() * 100

                coverage.append(
                    {
                        "Factor": factor,
                        "Coverage_Pct": round(
                            coverage_pct,
                            2,
                        ),
                    }
                )

            coverage_df = pd.DataFrame(coverage)

            logger.info(
                "Validated %s factors",
                len(coverage_df),
            )

            # =================================================
            # WINSORIZATION
            # =================================================

            logger.info("Winsorizing factor distributions...")

            for factor in HIGHER_BETTER + LOWER_BETTER:
                df[factor] = winsorize(df[factor])

            # =================================================
            # SECTOR-NEUTRAL PERCENTILE RANKS
            # =================================================

            logger.info("Computing sector-neutral rankings...")

            #
            # Higher values are better
            #

            for factor in HIGHER_BETTER:
                rank_column = f"{factor}_Rank"

                df[rank_column] = df.groupby("Sector")[factor].rank(
                    pct=True,
                    method="average",
                )

            #
            # Lower values are better
            #

            for factor in LOWER_BETTER:
                rank_column = f"{factor}_Rank"

                df[rank_column] = 1 - df.groupby("Sector")[factor].rank(
                    pct=True,
                    method="average",
                )

            # =================================================
            # RANK VALIDATION
            # =================================================

            rank_columns = [column for column in df.columns if column.endswith("_Rank")]

            validation = []

            for column in rank_columns:
                validation.append(
                    {
                        "Rank": column,
                        "Minimum": float(df[column].min()),
                        "Maximum": float(df[column].max()),
                        "Missing": int(df[column].isna().sum()),
                    }
                )

            validation_df = pd.DataFrame(validation)

            logger.info(
                "Generated %s normalized factors.",
                len(rank_columns),
            )

            # =================================================
            # OPTIONAL QUALITY CHECKS
            # =================================================

            #
            # Warn if any factor has
            # low data coverage.
            #

            low_coverage = coverage_df[coverage_df["Coverage_Pct"] < 90]

            if not low_coverage.empty:
                logger.warning(
                    "Factors below 90%% coverage: %s",
                    ", ".join(low_coverage["Factor"]),
                )

            #
            # Warn if any rank contains
            # missing values.
            #

            invalid = validation_df[validation_df["Missing"] > 0]

            if not invalid.empty:
                logger.warning(
                    "Rank columns with missing values: %s",
                    ", ".join(invalid["Rank"]),
                )

            logger.info("Ranking completed successfully.")

            # =================================================
            # COMPOSITE ALPHA SCORE
            # =================================================

            logger.info("Building Composite Alpha Score...")

            #
            # Institutional weighted
            # multi-factor alpha model
            #

            df["Alpha_Score"] = (
                0.30 * df["Momentum_12M_Rank"]
                + 0.20 * df["Momentum_6M_Rank"]
                + 0.15 * df["ADV_20D_Rank"]
                + 0.10 * df["Distance_52W_High_Rank"]
                + 0.10 * df["Log_Market_Cap_Rank"]
                + 0.15 * df["Volatility_20D_Rank"]
            )

            # =================================================
            # LIQUIDITY ADJUSTMENT
            # =================================================

            logger.info("Applying liquidity adjustment...")

            df["Liquidity_Penalty"] = 1 - df["ADV_20D_Rank"]

            df["Alpha_Adjusted"] = df["Alpha_Score"] - (0.10 * df["Liquidity_Penalty"])

            # =================================================
            # FINAL RANK
            # =================================================

            logger.info("Generating institutional ranking...")

            df["Rank"] = (
                df["Alpha_Adjusted"]
                .rank(
                    ascending=False,
                    method="dense",
                )
                .astype(int)
            )

            df["Percentile"] = df["Alpha_Adjusted"].rank(
                pct=True,
                ascending=True,
            )

            # =================================================
            # QUALITY METRICS
            # =================================================

            logger.info("Calculating ranking statistics...")

            alpha_statistics = {
                "Maximum": float(df["Alpha_Adjusted"].max()),
                "Minimum": float(df["Alpha_Adjusted"].min()),
                "Median": float(df["Alpha_Adjusted"].median()),
                "Average": float(df["Alpha_Adjusted"].mean()),
                "StdDev": float(df["Alpha_Adjusted"].std()),
            }

            logger.info(
                "Alpha Range : %.4f → %.4f",
                alpha_statistics["Minimum"],
                alpha_statistics["Maximum"],
            )

            # =================================================
            # METADATA
            # =================================================

            today = datetime.now().strftime(DATE_FORMAT)

            df["Ranking_Date"] = today

            df["Engine_Version"] = ENGINE_VERSION

            df["Ranking_Method"] = "Sector Neutral Percentile"

            df["Ranking_Model"] = "Institutional Composite Alpha"

            # =================================================
            # FINAL SORT
            # =================================================

            ranked = df.sort_values(
                "Alpha_Adjusted",
                ascending=False,
            ).reset_index(
                drop=True,
            )

            logger.info("Ranking complete.")

            logger.info(
                "Top Alpha : %.4f",
                ranked.iloc[0]["Alpha_Adjusted"],
            )

            # =================================================
            # PORTFOLIO GENERATION
            # =================================================

            logger.info("Generating model portfolios...")

            ensure_parent_directory(PORTFOLIO_DIRECTORY / "top_50.csv")

            top50 = ranked.head(50).copy()

            top100 = ranked.head(100).copy()

            top250 = ranked.head(250).copy()

            top50.to_csv(
                PORTFOLIO_DIRECTORY / "top_50.csv",
                index=False,
            )

            top100.to_csv(
                PORTFOLIO_DIRECTORY / "top_100.csv",
                index=False,
            )

            top250.to_csv(
                PORTFOLIO_DIRECTORY / "top_250.csv",
                index=False,
            )

            logger.info("Model portfolios created.")

            # =================================================
            # FACTOR EXPOSURE REPORT
            # =================================================

            logger.info("Building factor exposure report...")

            factor_exposure = pd.DataFrame(
                {
                    "Factor": [
                        "Momentum_12M",
                        "Momentum_6M",
                        "Volatility_20D",
                        "ADV_20D",
                        "Log_Market_Cap",
                    ],
                    "Exposure": [
                        top50["Momentum_12M_Rank"].mean(),
                        top50["Momentum_6M_Rank"].mean(),
                        top50["Volatility_20D_Rank"].mean(),
                        top50["ADV_20D_Rank"].mean(),
                        top50["Log_Market_Cap_Rank"].mean(),
                    ],
                }
            )

            ensure_parent_directory(FACTOR_EXPOSURE_FILE)

            factor_exposure.to_csv(
                FACTOR_EXPOSURE_FILE,
                index=False,
            )

            # =================================================
            # SECTOR EXPOSURE
            # =================================================

            logger.info("Building sector exposure...")

            sector_exposure = (
                top50.groupby("Sector")
                .size()
                .reset_index(name="Constituents")
                .sort_values(
                    "Constituents",
                    ascending=False,
                )
            )

            ensure_parent_directory(SECTOR_EXPOSURE_FILE)

            sector_exposure.to_csv(
                SECTOR_EXPOSURE_FILE,
                index=False,
            )

            # =================================================
            # PORTFOLIO STATISTICS
            # =================================================

            logger.info("Calculating portfolio statistics...")

            portfolio_statistics = {
                "Universe_Size": len(ranked),
                "Top50_Size": len(top50),
                "Top100_Size": len(top100),
                "Top250_Size": len(top250),
                "Top50_Min_Alpha": float(top50["Alpha_Adjusted"].min()),
                "Top100_Min_Alpha": float(top100["Alpha_Adjusted"].min()),
                "Average_Alpha": float(ranked["Alpha_Adjusted"].mean()),
                "Median_Alpha": float(ranked["Alpha_Adjusted"].median()),
                "Top50_Average_ADV": float(top50["ADV_20D"].mean()),
                "Top50_Average_MarketCap": float(top50["Market_Cap"].mean()),
            }

            logger.info("Portfolio generation completed.")

            # =================================================
            # SAVE RANK MASTER
            # =================================================

            ensure_parent_directory(FACTOR_RANK_MASTER_FILE)

            ranked.to_csv(
                FACTOR_RANK_MASTER_FILE,
                index=False,
            )

            # =================================================
            # BUILD EXECUTION REPORT
            # =================================================

            logger.info("Building ranking report...")

            report = pd.DataFrame(
                {
                    "Metric": [
                        "Universe_Size",
                        "Top50_Min_Alpha",
                        "Top100_Min_Alpha",
                        "Average_Alpha",
                        "Median_Alpha",
                        "Top50_Average_ADV",
                        "Top50_Average_MarketCap",
                        "Factors_Ranked",
                        "Ranking_Method",
                        "Run_Date",
                        "Engine_Version",
                    ],
                    "Value": [
                        portfolio_statistics["Universe_Size"],
                        portfolio_statistics["Top50_Min_Alpha"],
                        portfolio_statistics["Top100_Min_Alpha"],
                        portfolio_statistics["Average_Alpha"],
                        portfolio_statistics["Median_Alpha"],
                        portfolio_statistics["Top50_Average_ADV"],
                        portfolio_statistics["Top50_Average_MarketCap"],
                        len(rank_columns),
                        "Sector Neutral Percentile",
                        today,
                        ENGINE_VERSION,
                    ],
                }
            )

            ensure_parent_directory(RANKING_REPORT_FILE)

            report.to_csv(
                RANKING_REPORT_FILE,
                index=False,
            )

            # =================================================
            # EXECUTION SUMMARY
            # =================================================

            logger.info("=" * 70)

            logger.info("FACTOR RANK ENGINE COMPLETE")

            logger.info("=" * 70)

            logger.info(
                "Universe Size      : %s",
                f"{len(ranked):,}",
            )

            logger.info(
                "Top Alpha          : %.4f",
                ranked.iloc[0]["Alpha_Adjusted"],
            )

            logger.info(
                "Median Alpha       : %.4f",
                ranked["Alpha_Adjusted"].median(),
            )

            logger.info(
                "Generated Ranks    : %s",
                len(rank_columns),
            )

            logger.info(
                "Top50 Portfolio    : %s",
                PORTFOLIO_DIRECTORY / "top_50.csv",
            )

            logger.info(
                "Top100 Portfolio   : %s",
                PORTFOLIO_DIRECTORY / "top_100.csv",
            )

            logger.info(
                "Top250 Portfolio   : %s",
                PORTFOLIO_DIRECTORY / "top_250.csv",
            )

            logger.info(
                "Factor Master      : %s",
                FACTOR_RANK_MASTER_FILE,
            )

            logger.info("=" * 70)

            # =================================================
            # EXECUTION METADATA
            # =================================================

            execution_metadata = {
                "engine_version": ENGINE_VERSION,
                "records_processed": len(ranked),
                "rank_columns": len(rank_columns),
                "coverage_columns": len(coverage_df),
                "top50_size": len(top50),
                "top100_size": len(top100),
                "top250_size": len(top250),
                "highest_alpha": float(ranked["Alpha_Adjusted"].max()),
                "median_alpha": float(ranked["Alpha_Adjusted"].median()),
                "average_alpha": float(ranked["Alpha_Adjusted"].mean()),
                "run_date": today,
            }

            # =================================================
            # RETURN RESULT
            # =================================================

            return EngineResult(
                engine=ENGINE_NAME,
                status=EngineStatus.SUCCESS,
                records=len(ranked),
                output=FACTOR_RANK_MASTER_FILE,
                report=RANKING_REPORT_FILE,
                duration=timer.elapsed,
                metadata=execution_metadata,
            )

        # =====================================================
        # EXCEPTION HANDLING
        # =====================================================

        except Exception as exc:
            logger.exception("Factor Rank Engine failed.")

            return EngineResult(
                engine=ENGINE_NAME,
                status=EngineStatus.FAILED,
                duration=timer.elapsed,
                metadata={
                    "error": str(exc),
                },
            )


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    result = main()

    logger.info(
        "Engine Status : %s",
        result.status.value,
    )
