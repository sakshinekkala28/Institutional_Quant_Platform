# ==========================================================
# SIGNAL ENGINE
# Institutional Quant Platform
# Version 5.0
# ==========================================================

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd


# ==========================================================
# CONFIGURATION
# ==========================================================

@dataclass(frozen=True)
class SignalConfig:

    ENGINE_VERSION: str = "5.0.0"

    TARGET_HOLDINGS: int = 40

    DEFAULT_BETA: float = 1.0

    DEFAULT_VOLATILITY: float = 0.25

    ALPHA_CUTOFF_QUANTILE: float = 0.50

    MIN_LIQUIDITY_PERCENTILE: float = 0.25

    SIGNAL_HALF_LIFE_DAYS: int = 90


# ==========================================================
# PATH MANAGER
# ==========================================================

class PathManager:

    def __init__(self):

        self.root = Path(__file__).resolve().parents[1]

    @property
    def signal_file(self):
        return self.root / "data/signals/signal_master.csv"

    @property
    def portfolio_file(self):
        return self.root / "data/portfolios/live_portfolio.csv"

    @property
    def security_master_file(self):
        return self.root / "data/raw/security_master.csv"

    @property
    def beta_file(self):
        return self.root / "data/risk/beta_master.csv"

    @property
    def volatility_file(self):
        return self.root / "data/risk/stock_volatility.csv"

    @property
    def factor_file(self):
        return self.root / "data/factors/factor_master.csv"

    @property
    def fundamental_factor_file(self):
        return (
            self.root
            / "data/factors/fundamental_factor_master.csv"
        )

    @property
    def regime_file(self):
        return self.root / "data/regime/market_regime.csv"

    @property
    def factor_exposure_file(self):
        return (
            self.root
            / "data/risk/factor_exposures.csv"
        )


# ==========================================================
# DATA LOADER
# ==========================================================

class DataLoader:

    @staticmethod
    def load_csv(
        path: Path,
        required_columns: Optional[List[str]] = None
    ) -> pd.DataFrame:

        try:

            if not path.exists():

                raise FileNotFoundError(
                    f"{path.name} not found"
                )

            df = pd.read_csv(path)

            if len(df) == 0:

                raise ValueError(
                    f"{path.name} empty"
                )

            if required_columns:

                missing = [

                    c

                    for c in required_columns

                    if c not in df.columns

                ]

                if missing:

                    raise ValueError(
                        f"{path.name} missing {missing}"
                    )

            print(
                f"✓ Loaded {path.name}"
                f" ({len(df):,} rows)"
            )

            return df

        except Exception as e:

            print(
                f"⚠ Failed {path.name}: {e}"
            )

            return pd.DataFrame()


# ==========================================================
# DATA VALIDATOR
# ==========================================================

class DataValidator:

    @staticmethod
    def validate_columns(
        df,
        required_columns,
        file_name
    ):

        missing = [

            c

            for c in required_columns

            if c not in df.columns

        ]

        if missing:

            raise ValueError(
                f"{file_name} missing {missing}"
            )

    @staticmethod
    def coverage_report(df):

        report = []

        for col in df.columns:

            report.append({

                "Column": col,

                "Coverage_%":

                round(

                    df[col]
                    .notna()
                    .mean()
                    * 100,

                    2

                )

            })

        return pd.DataFrame(report)

    @staticmethod
    def duplicate_symbols(df):

        if "Symbol" not in df.columns:

            return pd.DataFrame()

        return df[
            df["Symbol"]
            .duplicated(keep=False)
        ]
    
# ==========================================================
# DATA STANDARDIZER
# ==========================================================

class DataStandardizer:

    @staticmethod
    def standardize_master_columns(
        df: pd.DataFrame
    ) -> pd.DataFrame:

        mappings = [

            ("Sector_x", "Sector_y", "Sector"),

            (
                "Market_Cap_x",
                "Market_Cap_y",
                "Market_Cap"
            ),

            (
                "ADV_20D_x",
                "ADV_20D_y",
                "ADV_20D"
            ),

            (
                "Beta_x",
                "Beta_y",
                "Beta"
            )

        ]

        for left, right, final in mappings:

            if left in df.columns:

                df[final] = (

                    df[left]

                    .fillna(
                        df.get(right)
                    )

                )

            elif right in df.columns:

                df[final] = df[right]

        duplicate_cols = [

            c

            for c in df.columns

            if c.endswith("_x")

            or c.endswith("_y")

        ]

        df = df.drop(
            columns=duplicate_cols,
            errors="ignore"
        )

        return df

    @staticmethod
    def standardize_security_master(
        security_master: pd.DataFrame
    ) -> pd.DataFrame:

        if (
            "ADV" in security_master.columns
            and
            "ADV_20D" not in security_master.columns
        ):

            security_master["ADV_20D"] = (
                security_master["ADV"]
            )

        return security_master


# ==========================================================
# FACTOR NORMALIZER
# ==========================================================

class FactorNormalizer:

    @staticmethod
    def percentile_rank(
        series: pd.Series
    ) -> pd.Series:

        return (
            series
            .rank(
                pct=True,
                method="average"
            )
            .fillna(0.5)
        )

    @staticmethod
    def z_score(
        series: pd.Series
    ) -> pd.Series:

        std = series.std()

        if std == 0:

            return pd.Series(
                0,
                index=series.index
            )

        return (
            (
                series
                -
                series.mean()
            )
            /
            std
        )

    @staticmethod
    def winsorized_rank(
        series: pd.Series,
        lower=0.01,
        upper=0.99
    ) -> pd.Series:

        s = series.copy()

        s = s.clip(
            lower=s.quantile(lower),
            upper=s.quantile(upper)
        )

        return (
            s.rank(
                pct=True
            )
            .fillna(0.5)
        )


# ==========================================================
# SIGNAL FRESHNESS ENGINE
# ==========================================================

class SignalFreshnessEngine:

    @staticmethod
    def apply(
        df: pd.DataFrame,
        half_life_days: int = 90
    ) -> pd.DataFrame:

        if "Signal_Date" not in df.columns:

            df["Freshness_Factor"] = 1.0

            return df

        df["Signal_Date"] = pd.to_datetime(

            df["Signal_Date"],

            errors="coerce"

        )

        age_days = (

            pd.Timestamp.today()

            -

            df["Signal_Date"]

        ).dt.days

        age_days = age_days.fillna(
            half_life_days
        )

        df["Freshness_Factor"] = np.exp(

            -age_days

            /

            half_life_days

        )

        return df


# ==========================================================
# COVERAGE ANALYTICS
# ==========================================================

class CoverageAnalytics:

    @staticmethod
    def report(
        target: pd.DataFrame
    ):

        metrics = {

            "Sector Coverage":

            round(

                target["Sector"]

                .notna()

                .mean()

                * 100,

                2

            )

            if "Sector" in target.columns

            else 0,

            "Market Cap Coverage":

            round(

                target["Market_Cap"]

                .notna()

                .mean()

                * 100,

                2

            )

            if "Market_Cap" in target.columns

            else 0,

            "ADV Coverage":

            round(

                target["ADV_20D"]

                .notna()

                .mean()

                * 100,

                2

            )

            if "ADV_20D" in target.columns

            else 0,

            "Beta Coverage":

            round(

                target["Beta"]

                .notna()

                .mean()

                * 100,

                2

            )

            if "Beta" in target.columns

            else 0,

            "Volatility Coverage":

            round(

                target["Volatility_252D"]

                .notna()

                .mean()

                * 100,

                2

            )

            if "Volatility_252D" in target.columns

            else 0

        }

        report = pd.DataFrame({

            "Metric": metrics.keys(),

            "Coverage_%": metrics.values()

        })

        return report

    @staticmethod
    def print_report(
        target: pd.DataFrame
    ):

        report = CoverageAnalytics.report(
            target
        )

        print(
            "\n📊 DATA COVERAGE REPORT"
        )

        print(report)

        return report


# ==========================================================
# FACTOR EXPOSURE EXPORTER
# ==========================================================

class ExposureExporter:

    @staticmethod
    def export(
        df: pd.DataFrame,
        output_path: Path
    ):

        required_cols = [

            "Symbol",

            "Sector",

            "Beta",

            "Momentum_Factor",

            "Quality_Factor",

            "Value_Factor",

            "Growth_Factor",

            "Volatility_252D"

        ]

        available = [

            c

            for c in required_cols

            if c in df.columns

        ]

        exposure_df = (
            df[available]
            .copy()
        )

        exposure_df.to_csv(
            output_path,
            index=False
        )

        print(
            "✓ Saved factor_exposures.csv"
        )

        return exposure_df
    
# ==========================================================
# FACTOR ENGINE
# ==========================================================

class FactorEngine:

    def __init__(
        self,
        df: pd.DataFrame
    ):

        self.df = df.copy()

    # ======================================================
    # MOMENTUM FACTOR
    # ======================================================

    def build_momentum_factor(self):

        momentum_cols = [

            "Momentum_1M",

            "Momentum_3M",

            "Momentum_6M",

            "Momentum_12M"

        ]

        available = [

            c

            for c in momentum_cols

            if c in self.df.columns

        ]

        if available:

            self.df["Momentum_Factor"] = (

                self.df[available]

                .rank(pct=True)

                .mean(axis=1)

            )

        else:

            self.df["Momentum_Factor"] = 0.50

    # ======================================================
    # QUALITY FACTOR
    # ======================================================

    def build_quality_factor(self):

        quality_cols = [

            "ROE",

            "ROCE",

            "Operating_Margin"

        ]

        available = [

            c

            for c in quality_cols

            if c in self.df.columns

            and

            self.df[c]
            .notna()
            .sum() > 20

        ]

        if available:

            self.df["Quality_Factor"] = (

                self.df[available]

                .rank(pct=True)

                .mean(axis=1)

            )

        else:

            self.df["Quality_Factor"] = 0.50

    # ======================================================
    # VALUE FACTOR
    # ======================================================

    def build_value_factor(self):

        if "PE" not in self.df.columns:

            self.df["Value_Factor"] = 0.50

            return

        valid_pe = (

            self.df["PE"]

            .where(
                self.df["PE"] > 0
            )

        )

        inverse_pe = (

            1

            /

            valid_pe

        )

        inverse_pe = inverse_pe.clip(

            lower=
            inverse_pe.quantile(0.01),

            upper=
            inverse_pe.quantile(0.99)

        )

        self.df["Value_Factor"] = (

            inverse_pe

            .rank(pct=True)

            .fillna(0.50)

        )

    # ======================================================
    # GROWTH FACTOR
    # ======================================================

    def build_growth_factor(self):

        growth_cols = [

            "Revenue_Growth",

            "EPS_Growth",

            "Profit_Growth"

        ]

        available = [

            c

            for c in growth_cols

            if c in self.df.columns

        ]

        if available:

            self.df["Growth_Factor"] = (

                self.df[available]

                .rank(pct=True)

                .mean(axis=1)

            )

        else:

            self.df["Growth_Factor"] = 0.50

    # ======================================================
    # LIQUIDITY FACTOR
    # ======================================================

    def build_liquidity_factor(self):

        if "ADV_20D" not in self.df.columns:

            self.df["Liquidity_Factor"] = 0.50

            return

        self.df["Liquidity_Factor"] = (

            self.df["ADV_20D"]

            .rank(pct=True)

            .fillna(0.50)

        )

    # ======================================================
    # LOW VOL FACTOR
    # ======================================================

    def build_low_vol_factor(self):

        if "Volatility_252D" not in self.df.columns:

            self.df["LowVol_Factor"] = 0.50

            return

        self.df["LowVol_Factor"] = (

            1

            -

            self.df["Volatility_252D"]

            .rank(pct=True)

        )

    # ======================================================
    # SIGNAL FACTOR
    # ======================================================

    def build_signal_factor(self):

        self.df["Signal_Factor"] = (

            self.df["Signal_Score"]

            .rank(pct=True)

            .fillna(0.50)

        )

    # ======================================================
    # RUN ALL FACTORS
    # ======================================================

    def run(self):

        self.build_signal_factor()

        self.build_momentum_factor()

        self.build_quality_factor()

        self.build_value_factor()

        self.build_growth_factor()

        self.build_liquidity_factor()

        self.build_low_vol_factor()

        return self.df


# ==========================================================
# FACTOR HEALTH ENGINE
# ==========================================================

class FactorHealthEngine:

    FACTORS = [

        "Signal_Factor",

        "Momentum_Factor",

        "Quality_Factor",

        "Value_Factor",

        "Growth_Factor",

        "Liquidity_Factor",

        "LowVol_Factor"

    ]

    @classmethod
    def report(
        cls,
        df
    ):

        records = []

        for factor in cls.FACTORS:

            if factor not in df.columns:
                continue

            records.append({

                "Factor": factor,

                "Coverage_%":

                round(

                    df[factor]

                    .notna()

                    .mean()

                    * 100,

                    2

                ),

                "Unique_Values":

                df[factor]

                .nunique(),

                "Std_Dev":

                round(

                    df[factor]

                    .std(),

                    4

                )

            })

        return pd.DataFrame(
            records
        )


# ==========================================================
# FACTOR CORRELATION ENGINE
# ==========================================================

class FactorCorrelationEngine:

    FACTORS = [

        "Signal_Factor",

        "Momentum_Factor",

        "Quality_Factor",

        "Value_Factor",

        "Growth_Factor",

        "Liquidity_Factor",

        "LowVol_Factor"

    ]

    @classmethod
    def correlation_matrix(
        cls,
        df
    ):

        available = [

            c

            for c in cls.FACTORS

            if c in df.columns

        ]

        return (

            df[available]

            .corr()

        )


# ==========================================================
# FACTOR DIAGNOSTICS ENGINE
# ==========================================================

class FactorDiagnostics:

    @staticmethod
    def run(df):

        print(
            "\n📊 FACTOR HEALTH CHECK"
        )

        health = (

            FactorHealthEngine

            .report(df)

        )

        print(health)

        print(
            "\n📈 FACTOR CORRELATION"
        )

        corr = (

            FactorCorrelationEngine

            .correlation_matrix(df)

        )

        print(corr)

        return {

            "health": health,

            "correlation": corr

        }
    
# ==========================================================
# REGIME ENGINE
# ==========================================================

class RegimeEngine:

    REGIME_WEIGHTS = {

        "BULL": {

            "Signal": 0.20,

            "Momentum": 0.25,

            "Quality": 0.10,

            "Value": 0.10,

            "Growth": 0.25,

            "Liquidity": 0.05,

            "LowVol": 0.05

        },

        "BEAR": {

            "Signal": 0.20,

            "Momentum": 0.10,

            "Quality": 0.25,

            "Value": 0.20,

            "Growth": 0.10,

            "Liquidity": 0.05,

            "LowVol": 0.10

        },

        "SIDEWAYS": {

            "Signal": 0.25,

            "Momentum": 0.20,

            "Quality": 0.15,

            "Value": 0.15,

            "Growth": 0.15,

            "Liquidity": 0.05,

            "LowVol": 0.05

        }

    }

    @classmethod
    def get_weights(
        cls,
        regime_name
    ):

        regime_name = str(
            regime_name
        ).upper()

        for key in cls.REGIME_WEIGHTS:

            if key in regime_name:

                return cls.REGIME_WEIGHTS[key]

        return cls.REGIME_WEIGHTS[
            "SIDEWAYS"
        ]


# ==========================================================
# ALPHA ENGINE
# ==========================================================

class AlphaEngine:

    @staticmethod
    def build_composite_alpha(
        df,
        regime_name="SIDEWAYS"
    ):

        weights = (

            RegimeEngine

            .get_weights(
                regime_name
            )

        )

        df["Composite_Alpha"] = (

            weights["Signal"]

            * df["Signal_Factor"]

            +

            weights["Momentum"]

            * df["Momentum_Factor"]

            +

            weights["Quality"]

            * df["Quality_Factor"]

            +

            weights["Value"]

            * df["Value_Factor"]

            +

            weights["Growth"]

            * df["Growth_Factor"]

            +

            weights["Liquidity"]

            * df["Liquidity_Factor"]

            +

            weights["LowVol"]

            * df["LowVol_Factor"]

        )

        df["Composite_Alpha"] = (

            df["Composite_Alpha"]

            .rank(pct=True)

        )

        return df


# ==========================================================
# SECTOR ALPHA ENGINE
# ==========================================================

class SectorAlphaEngine:

    @staticmethod
    def build(
        df
    ):

        if "Sector" not in df.columns:

            df["Sector_Alpha"] = 0.50

            return df

        sector_alpha = (

            df

            .groupby("Sector")

            ["Composite_Alpha"]

            .mean()

        )

        sector_alpha = (

            sector_alpha

            .rank(pct=True)

        )

        df["Sector_Alpha"] = (

            df["Sector"]

            .map(sector_alpha)

            .fillna(0.50)

        )

        return df


# ==========================================================
# UNIVERSE BUILDER
# ==========================================================

class UniverseBuilder:

    @staticmethod
    def build(
        df,
        config
    ):

        alpha_cutoff = (

            df["Composite_Alpha"]

            .quantile(
                config.ALPHA_CUTOFF_QUANTILE
            )

        )

        df = df[
            df["Composite_Alpha"]
            >= alpha_cutoff
        ].copy()

        if "ADV_20D" in df.columns:

            min_adv = (

                df["ADV_20D"]

                .quantile(
                    config.MIN_LIQUIDITY_PERCENTILE
                )

            )

            df = df[
                df["ADV_20D"]
                >= min_adv
            ].copy()

        return df


# ==========================================================
# SELECTION SCORE ENGINE
# ==========================================================

class SelectionScoreEngine:

    @staticmethod
    def build(
        df
    ):

        sector_count = (

            df["Sector"]

            .map(
                df["Sector"]
                .value_counts()
            )

        )

        diversification_bonus = (

            1

            /

            np.sqrt(
                sector_count
            )

        )

        df["Selection_Score"] = (

            df["Composite_Alpha"]

            *

            (

                0.80

                +

                0.40

                *

                df["Sector_Alpha"]

            )

            *

            diversification_bonus

        )

        return df


# ==========================================================
# SIGNAL ENGINE
# ==========================================================

class SignalEngine:

    def __init__(self):

        self.config = SignalConfig()

        self.paths = PathManager()

        self.loader = DataLoader()

    def load_data(self):

        data = {

            "signals":

            self.loader.load_csv(

                self.paths.signal_file,

                required_columns=[

                    "Symbol",

                    "Signal",

                    "Signal_Score"

                ]

            ),

            "portfolio":

            self.loader.load_csv(

                self.paths.portfolio_file

            ),

            "security_master":

            self.loader.load_csv(

                self.paths.security_master_file

            ),

            "beta":

            self.loader.load_csv(

                self.paths.beta_file

            ),

            "volatility":

            self.loader.load_csv(

                self.paths.volatility_file

            ),

            "factor_master":

            self.loader.load_csv(

                self.paths.factor_file

            ),

            "fundamental_factor":

            self.loader.load_csv(

                self.paths.fundamental_factor_file

            ),

            "regime":

            self.loader.load_csv(

                self.paths.regime_file

            )

        }

        return data

    def build_alpha_universe(
        self,
        data
    ):

        signals = data["signals"]

        security_master = (

            DataStandardizer

            .standardize_security_master(

                data["security_master"]

            )

        )

        target = signals.merge(

            security_master,

            on="Symbol",

            how="left"

        )

        if len(
            data["factor_master"]
        ):

            target = target.merge(

                data["factor_master"],

                on="Symbol",

                how="left"

            )

        if len(
            data["fundamental_factor"]
        ):

            target = target.merge(

                data["fundamental_factor"],

                on="Symbol",

                how="left"

            )

        target = (

            DataStandardizer

            .standardize_master_columns(
                target
            )

        )

        if len(
            data["volatility"]
        ) > 0:

            vol_cols = [

                c

                for c in data[
                    "volatility"
                ].columns

                if "vol"
                in c.lower()

            ]

            if vol_cols:

                target = target.merge(

                    data["volatility"][

                        [
                            "Symbol",

                            vol_cols[0]

                        ]

                    ],

                    on="Symbol",

                    how="left"

                )

                target.rename(

                    columns={

                        vol_cols[0]:

                        "Volatility_252D"

                    },

                    inplace=True

                )

        if len(
            data["beta"]
        ) > 0:

            target = target.merge(

                data["beta"],

                on="Symbol",

                how="left"

            )

        target["Beta"] = (

            target["Beta"]

            .fillna(
                self.config.DEFAULT_BETA
            )

        )

        target["Volatility_252D"] = (

            target["Volatility_252D"]

            .fillna(
                self.config.DEFAULT_VOLATILITY
            )

        )

        target = SignalFreshnessEngine.apply(

            target,

            self.config.SIGNAL_HALF_LIFE_DAYS

        )

        target = (

            FactorEngine(target)

            .run()

        )

        regime_name = "SIDEWAYS"

        if len(data["regime"]) > 0:

            regime_name = (

                data["regime"]

                .iloc[-1]

                .get(
                    "Regime",
                    "SIDEWAYS"
                )

            )

        target = (

            AlphaEngine

            .build_composite_alpha(

                target,

                regime_name

            )

        )

        target = (

            SectorAlphaEngine

            .build(target)

        )

        target = (

            SelectionScoreEngine

            .build(target)

        )

        target = (

            UniverseBuilder

            .build(

                target,

                self.config

            )

        )

        CoverageAnalytics.print_report(
            target
        )

        FactorDiagnostics.run(
            target
        )

        ExposureExporter.export(

            target,

            self.paths.factor_exposure_file

        )

        print(
            "\n✓ Alpha Universe Built"
        )

        print(
            f"Universe Size: {len(target):,}"
        )

        return target