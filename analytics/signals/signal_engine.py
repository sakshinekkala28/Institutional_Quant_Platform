"""
====================================================================
Institutional Quant Platform

Signal Engine

Purpose
-------
Institutional Security Signal Generation.

Inputs
------
data/factors/factor_snapshot_master.csv
data/regime/market_regime.csv
data/portfolios/live_portfolio.csv

Outputs
-------
data/signals/signal_master.csv
data/signals/buy_list.csv
data/signals/sell_list.csv
data/signals/watchlist.csv
data/signals/signal_dashboard.csv
data/logs/signal_report.csv

====================================================================
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

# =========================================================
# CONFIGURATION
# =========================================================

ENGINE_VERSION = "1.0.0"

BUY_THRESHOLD = 70

STRONG_BUY_THRESHOLD = 85

REDUCE_THRESHOLD = 40

SELL_THRESHOLD = 25


# =========================================================
# PATHS
# =========================================================

ROOT = Path(__file__).resolve().parents[2]

FACTOR_FILE = (
    ROOT
    / "data"
    / "factors"
    / "factor_snapshot_master.csv"
)

REGIME_FILE = (
    ROOT
    / "data"
    / "regime"
    / "market_regime.csv"
)

PORTFOLIO_FILE = (
    ROOT
    / "data"
    / "portfolios"
    / "live_portfolio.csv"
)

OUTPUT_DIR = (
    ROOT
    / "data"
    / "signals"
)

REPORT_FILE = (
    ROOT
    / "data"
    / "logs"
    / "signal_report.csv"
)


# =========================================================
# REQUIRED COLUMNS
# =========================================================

REQUIRED_FACTOR_COLUMNS = {
    "Symbol",
    "Company_Name",
    "Sector",
    "Momentum_12M",
    "Momentum_6M",
    "Momentum_3M",
    "Distance_SMA200",
    "ADV_20D",
    "Volatility_60D",
    "Max_Drawdown_252D",
}

REQUIRED_REGIME_COLUMNS = {
    "Regime",
}

REQUIRED_PORTFOLIO_COLUMNS = {
    "Symbol",
}


# =========================================================
# VALIDATION
# =========================================================


def validate_inputs(
    factors: pd.DataFrame,
    regime: pd.DataFrame,
    portfolio: pd.DataFrame,
) -> None:
    """
    Validate all signal-engine input datasets.
    """

    missing_factor_columns = (
        REQUIRED_FACTOR_COLUMNS
        - set(factors.columns)
    )

    if missing_factor_columns:

        raise ValueError(
            "Missing factor columns: "
            f"{sorted(missing_factor_columns)}"
        )

    missing_regime_columns = (
        REQUIRED_REGIME_COLUMNS
        - set(regime.columns)
    )

    if missing_regime_columns:

        raise ValueError(
            "Missing regime columns: "
            f"{sorted(missing_regime_columns)}"
        )

    missing_portfolio_columns = (
        REQUIRED_PORTFOLIO_COLUMNS
        - set(portfolio.columns)
    )

    if missing_portfolio_columns:

        raise ValueError(
            "Missing portfolio columns: "
            f"{sorted(missing_portfolio_columns)}"
        )

    if factors.empty:

        raise ValueError(
            "Factor snapshot is empty."
        )

    if regime.empty:

        raise ValueError(
            "Market regime dataset is empty."
        )


# =========================================================
# SIGNAL CLASSIFICATION
# =========================================================


def classify(
    score: float,
) -> str:
    """
    Classify a security using its signal score.
    """

    if score >= STRONG_BUY_THRESHOLD:

        return "STRONG_BUY"

    if score >= BUY_THRESHOLD:

        return "BUY"

    if score >= REDUCE_THRESHOLD:

        return "HOLD"

    if score >= SELL_THRESHOLD:

        return "REDUCE"

    return "SELL"


# =========================================================
# REGIME ADJUSTMENT
# =========================================================


def calculate_regime_bonus(
    current_regime: str,
) -> float:
    """
    Calculate signal-score adjustment from market regime.
    """

    if "BULL_LOW_VOL" in current_regime:

        return 15.0

    if "BULL" in current_regime:

        return 10.0

    if "BEAR_HIGH_VOL" in current_regime:

        return -15.0

    if "BEAR" in current_regime:

        return -10.0

    return 0.0


# =========================================================
# SIGNAL SCORE
# =========================================================


def calculate_signal_score(
    factors: pd.DataFrame,
    regime_bonus: float,
) -> pd.DataFrame:
    """
    Calculate cross-sectional security signal scores.
    """

    factors = factors.copy()

    factors["MOM12"] = (
        factors["Momentum_12M"]
        .rank(
            pct=True,
        )
    )

    factors["MOM6"] = (
        factors["Momentum_6M"]
        .rank(
            pct=True,
        )
    )

    factors["MOM3"] = (
        factors["Momentum_3M"]
        .rank(
            pct=True,
        )
    )

    factors["TREND"] = (
        factors["Distance_SMA200"]
        .rank(
            pct=True,
        )
    )

    factors["LIQ"] = (
        factors["ADV_20D"]
        .rank(
            pct=True,
        )
    )

    factors["VOL"] = (
        1
        - factors["Volatility_60D"]
        .rank(
            pct=True,
        )
    )

    factors["DD"] = (
        1
        - factors["Max_Drawdown_252D"]
        .rank(
            pct=True,
        )
    )

    factors["Signal_Score"] = (
        20 * factors["MOM12"]
        + 15 * factors["MOM6"]
        + 10 * factors["MOM3"]
        + 15 * factors["TREND"]
        + 10 * factors["LIQ"]
        + 15 * factors["VOL"]
        + 15 * factors["DD"]
    )

    factors["Signal_Score"] += (
        regime_bonus
    )

    factors["Signal_Score"] = (
        factors["Signal_Score"]
        .clip(
            0,
            100,
        )
    )

    return factors


# =========================================================
# ENGINE
# =========================================================


def main() -> dict:
    """
    Execute the institutional signal engine.
    """

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    REPORT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # =====================================================
    # LOAD
    # =====================================================

    print(
        "\n📥 Loading Inputs..."
    )

    if not FACTOR_FILE.exists():

        raise FileNotFoundError(
            f"Factor file not found: {FACTOR_FILE}"
        )

    if not REGIME_FILE.exists():

        raise FileNotFoundError(
            f"Regime file not found: {REGIME_FILE}"
        )

    if not PORTFOLIO_FILE.exists():

        raise FileNotFoundError(
            f"Portfolio file not found: "
            f"{PORTFOLIO_FILE}"
        )

    factors = pd.read_csv(
        FACTOR_FILE
    )

    regime = pd.read_csv(
        REGIME_FILE
    )

    portfolio = pd.read_csv(
        PORTFOLIO_FILE
    )

    validate_inputs(
        factors,
        regime,
        portfolio,
    )

    # =====================================================
    # LATEST SNAPSHOT
    # =====================================================

    if "Snapshot_Date" in factors.columns:

        factors["Snapshot_Date"] = (
            pd.to_datetime(
                factors["Snapshot_Date"],
                errors="coerce",
            )
        )

        latest_date = (
            factors["Snapshot_Date"]
            .max()
        )

        if pd.notna(latest_date):

            factors = factors[
                factors["Snapshot_Date"]
                == latest_date
            ].copy()

    # =====================================================
    # CURRENT REGIME
    # =====================================================

    current_regime = str(
        regime.iloc[-1]["Regime"]
    )

    regime_bonus = (
        calculate_regime_bonus(
            current_regime
        )
    )

    # =====================================================
    # SIGNAL SCORE
    # =====================================================

    factors = calculate_signal_score(
        factors,
        regime_bonus,
    )

    # =====================================================
    # PORTFOLIO FLAG
    # =====================================================

    current_positions = set(
        portfolio["Symbol"]
        .dropna()
        .astype(str)
        .str.upper()
    )

    factors["In_Portfolio"] = (
        factors["Symbol"]
        .astype(str)
        .str.upper()
        .isin(current_positions)
    )

    # =====================================================
    # CLASSIFICATION
    # =====================================================

    factors["Signal"] = (
        factors["Signal_Score"]
        .apply(
            classify
        )
    )

    # =====================================================
    # MASTER
    # =====================================================

    signal_master = factors[
        [
            "Symbol",
            "Company_Name",
            "Sector",
            "Signal",
            "Signal_Score",
            "In_Portfolio",
        ]
    ].copy()

    signal_master = (
        signal_master
        .sort_values(
            "Signal_Score",
            ascending=False,
        )
        .reset_index(
            drop=True
        )
    )

    # =====================================================
    # BUY LIST
    # =====================================================

    buy_list = signal_master[
        signal_master["Signal"].isin(
            [
                "STRONG_BUY",
                "BUY",
            ]
        )
    ].copy()

    # =====================================================
    # SELL LIST
    # =====================================================

    sell_list = signal_master[
        signal_master["Signal"].isin(
            [
                "SELL",
                "REDUCE",
            ]
        )
    ].copy()

    # =====================================================
    # WATCHLIST
    # =====================================================

    watchlist = (
        signal_master
        .head(100)
        .copy()
    )

    # =====================================================
    # DASHBOARD
    # =====================================================

    dashboard = pd.DataFrame(
        {
            "Metric": [
                "Engine_Version",
                "Regime",
                "Regime_Bonus",
                "Universe_Size",
                "Strong_Buys",
                "Buys",
                "Holds",
                "Reduces",
                "Sells",
            ],
            "Value": [
                ENGINE_VERSION,
                current_regime,
                regime_bonus,
                len(signal_master),
                (
                    signal_master["Signal"]
                    == "STRONG_BUY"
                ).sum(),
                (
                    signal_master["Signal"]
                    == "BUY"
                ).sum(),
                (
                    signal_master["Signal"]
                    == "HOLD"
                ).sum(),
                (
                    signal_master["Signal"]
                    == "REDUCE"
                ).sum(),
                (
                    signal_master["Signal"]
                    == "SELL"
                ).sum(),
            ],
        }
    )

    # =====================================================
    # SAVE
    # =====================================================

    signal_master.to_csv(
        OUTPUT_DIR
        / "signal_master.csv",
        index=False,
    )

    buy_list.to_csv(
        OUTPUT_DIR
        / "buy_list.csv",
        index=False,
    )

    sell_list.to_csv(
        OUTPUT_DIR
        / "sell_list.csv",
        index=False,
    )

    watchlist.to_csv(
        OUTPUT_DIR
        / "watchlist.csv",
        index=False,
    )

    dashboard.to_csv(
        OUTPUT_DIR
        / "signal_dashboard.csv",
        index=False,
    )

    dashboard.to_csv(
        REPORT_FILE,
        index=False,
    )

    # =====================================================
    # REPORT
    # =====================================================

    strong_buys = int(
        (
            signal_master["Signal"]
            == "STRONG_BUY"
        ).sum()
    )

    buys = int(
        (
            signal_master["Signal"]
            == "BUY"
        ).sum()
    )

    sells = int(
        (
            signal_master["Signal"]
            == "SELL"
        ).sum()
    )

    print(
        "\n" + "=" * 70
    )

    print(
        "🏁 SIGNAL ENGINE COMPLETE"
    )

    print(
        "=" * 70
    )

    print(
        f"Engine Version : "
        f"{ENGINE_VERSION}"
    )

    print(
        f"Regime         : "
        f"{current_regime}"
    )

    print(
        f"Universe       : "
        f"{len(signal_master):,}"
    )

    print(
        f"Strong Buys    : "
        f"{strong_buys:,}"
    )

    print(
        f"Buys           : "
        f"{buys:,}"
    )

    print(
        f"Sells          : "
        f"{sells:,}"
    )

    print(
        f"\nOutput Directory:\n"
        f"{OUTPUT_DIR}"
    )

    print(
        "=" * 70
    )

    return {
        "engine": "Signal Engine",
        "version": ENGINE_VERSION,
        "regime": current_regime,
        "universe_size": len(
            signal_master
        ),
        "strong_buys": strong_buys,
        "buys": buys,
        "sells": sells,
        "output_directory": str(
            OUTPUT_DIR
        ),
    }


# =========================================================
# CLI
# =========================================================

if __name__ == "__main__":

    main()
