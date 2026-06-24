from __future__ import annotations

import logging

from pathlib import Path

import pandas as pd


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

MACRO_DIR = (

    DATA_DIR

    / "macro"

)


US10Y_FILE = (

    MACRO_DIR

    / "us10y.csv"

)

INDIA10Y_FILE = (

    MACRO_DIR

    / "india10y.csv"

)

CPI_FILE = (

    MACRO_DIR

    / "cpi.csv"

)

WPI_FILE = (

    MACRO_DIR

    / "wpi.csv"

)

USDINR_FILE = (

    MACRO_DIR

    / "usdinr.csv"

)

VIX_FILE = (

    MACRO_DIR

    / "vix.csv"

)


class MacroValidator:

    REQUIRED_COLUMNS = [

        "Date",

        "Value"

    ]

    @staticmethod
    def validate():

        logger.info(

            "Validating Macro Files"

        )

        required_files = [

            US10Y_FILE,

            INDIA10Y_FILE,

            CPI_FILE,

            WPI_FILE,

            USDINR_FILE,

            VIX_FILE

        ]

        missing_files = [

            file_path

            for file_path in required_files

            if not file_path.exists()

        ]

        if missing_files:

            raise FileNotFoundError(

                f"Missing macro files: "

                f"{missing_files}"

            )

        logger.info(

            "Macro Files Found"

        )

    @staticmethod
    def validate_schema(

        dataframe: pd.DataFrame,

        dataset_name: str

    ):

        missing_columns = [

            column

            for column in

            MacroValidator.REQUIRED_COLUMNS

            if column not in dataframe.columns

        ]

        if missing_columns:

            raise ValueError(

                f"{dataset_name} "

                f"missing columns: "

                f"{missing_columns}"

            )


class MacroRepository:

    @staticmethod
    def _load_csv(

        file_path: Path,

        dataset_name: str

    ) -> pd.DataFrame:

        logger.info(

            f"Loading {dataset_name}"

        )

        df = pd.read_csv(

            file_path

        )

        MacroValidator.validate_schema(

            df,

            dataset_name

        )

        df["Date"] = pd.to_datetime(

            df["Date"]

        )

        df = (

            df

            .sort_values(

                "Date"

            )

            .reset_index(

                drop=True

            )

        )

        return df

    @staticmethod
    def load():

        MacroValidator.validate()

        return {

            "US10Y":

                MacroRepository

                ._load_csv(

                    US10Y_FILE,

                    "US10Y"

                ),

            "INDIA10Y":

                MacroRepository

                ._load_csv(

                    INDIA10Y_FILE,

                    "INDIA10Y"

                ),

            "CPI":

                MacroRepository

                ._load_csv(

                    CPI_FILE,

                    "CPI"

                ),

            "WPI":

                MacroRepository

                ._load_csv(

                    WPI_FILE,

                    "WPI"

                ),

            "USDINR":

                MacroRepository

                ._load_csv(

                    USDINR_FILE,

                    "USDINR"

                ),

            "VIX":

                MacroRepository

                ._load_csv(

                    VIX_FILE,

                    "VIX"

                )

        }


class MacroLatestValueExtractor:

    @staticmethod
    def extract(

        macro_data: dict

    ) -> dict:

        logger.info(

            "Extracting Latest Macro Values"

        )

        latest = {}

        for (

            metric,

            dataframe

        ) in macro_data.items():

            latest[metric] = float(

                dataframe

                .iloc[-1]

                ["Value"]

            )

        return latest


class MacroMetadataBuilder:

    @staticmethod
    def build(

        macro_data: dict

    ) -> pd.DataFrame:

        rows = []

        for (

            metric,

            dataframe

        ) in macro_data.items():

            rows.append(

                {

                    "Metric":

                        metric,

                    "Latest_Date":

                        dataframe

                        .iloc[-1]

                        ["Date"],

                    "Latest_Value":

                        dataframe

                        .iloc[-1]

                        ["Value"],

                    "Observations":

                        len(

                            dataframe

                        )

                }

            )

        return pd.DataFrame(

            rows

        )


def run_example():

    logger.info(

        "Starting Macro Repository"

    )

    macro_data = (

        MacroRepository

        .load()

    )

    latest = (

        MacroLatestValueExtractor

        .extract(

            macro_data

        )

    )

    metadata = (

        MacroMetadataBuilder

        .build(

            macro_data

        )

    )

    print()

    print(

        "=" * 80

    )

    print(

        "MACRO REPOSITORY"

    )

    print(

        "=" * 80

    )

    print()

    print(

        "Latest Values"

    )

    print(

        latest

    )

    print()

    print(

        metadata

    )

    print()

    print(

        "=" * 80

    )


if __name__ == "__main__":

    run_example()