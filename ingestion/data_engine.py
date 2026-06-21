import pandas as pd

# ==========================================================
# DATA SOURCE REGISTRY
# ==========================================================

from dataclasses import dataclass

@dataclass
class DataSource:

    name: str

    priority: int

    refresh_frequency: str

    enabled: bool = True


class DataRegistry:

    def __init__(self):

        self.sources = [

            DataSource(
                "NSE",
                1,
                "DAILY"
            ),

            DataSource(
                "SCREENER",
                2,
                "WEEKLY"
            ),

            DataSource(
                "YFINANCE",
                3,
                "DAILY"
            )

        ]

    def active_sources(self):

        return [

            s

            for s in self.sources

            if s.enabled

        ]
    
# ==========================================================
# SECURITY MASTER
# ==========================================================

class SecurityMaster:

    @staticmethod
    def build_master(
        security_df
    ):

        security_df = (

            security_df

            .drop_duplicates(
                subset=["Symbol"]
            )

        )

        security_df["Symbol"] = (

            security_df["Symbol"]

            .astype(str)

            .str.upper()

        )

        return security_df

    @staticmethod
    def validate(
        security_df
    ):

        duplicates = (

            security_df[
                "Symbol"
            ]

            .duplicated()

            .sum()

        )

        return {

            "Duplicates":
            duplicates,

            "Total":
            len(security_df)

        }
    
# ==========================================================
# DATA QUALITY
# ==========================================================

class DataQualityEngine:

    @staticmethod
    def missing_report(df):

        report = []

        for col in df.columns:

            report.append({

                "Column":
                col,

                "Missing_%":

                round(

                    df[col]

                    .isna()

                    .mean()

                    * 100,

                    2

                )

            })

        return pd.DataFrame(
            report
        )

    @staticmethod
    def outlier_report(
        df,
        column
    ):

        q1 = df[column].quantile(0.25)

        q3 = df[column].quantile(0.75)

        iqr = q3 - q1

        outliers = (

            df[column]

            >

            q3 + 1.5 * iqr

        ).sum()

        return outliers
    
# ==========================================================
# FEATURE STORE
# ==========================================================

class FeatureStore:

    def __init__(self):

        self.features = {}

    def register(
        self,
        name,
        data
    ):

        self.features[name] = data

    def get(
        self,
        name
    ):

        return self.features.get(name)


# ==========================================================
# DATA ENGINE
# ==========================================================

class DataEngine:

    def __init__(self):

        self.registry = DataRegistry()

        self.feature_store = FeatureStore()

    def run(
        self,
        security_master
    ):

        security_master = (

            SecurityMaster

            .build_master(
                security_master
            )

        )

        quality = (

            DataQualityEngine

            .missing_report(
                security_master
            )

        )

        self.feature_store.register(

            "security_master",

            security_master

        )

        return {

            "Security_Master":
            security_master,

            "Quality":
            quality

        }