from pathlib import Path

import pandas as pd

import logging


logging.basicConfig(

    level=logging.INFO,

    format="%(asctime)s | %(levelname)s | %(message)s"

)

logger = logging.getLogger(__name__)


DATA_DIR = Path("data")

MONITORING_DIR = DATA_DIR / "monitoring"

HISTORY_FILE = (

    MONITORING_DIR

    / "alert_history.csv"

)

class AlertHistoryEngine:

    @staticmethod
    def append(

        alerts

    ):

        logger.info(

            "Updating Alert History"

        )

        if alerts is None:

            return

        if isinstance(

            alerts,

            list

        ):

            if len(

                alerts

            ) == 0:

                return

            alerts = pd.DataFrame(

                alerts

            )

        if alerts.empty:

            return

        records = []

        run_date = (

            pd.Timestamp.now()

            .strftime(

                "%Y-%m-%d"

            )

        )

        for _, row in alerts.iterrows():

            records.append(

                {

                    "Date":

                        run_date,

                    "Severity":

                        row["Severity"],

                    "Category":

                        row["Category"],

                    "Message":

                        row["Message"]

                }

            )

        df = pd.DataFrame(

            records

        )

        if HISTORY_FILE.exists():

            existing = pd.read_csv(

                HISTORY_FILE

            )

            df = pd.concat(

                [

                    existing,

                    df

                ],

                ignore_index=True

            )

        df.to_csv(

            HISTORY_FILE,

            index=False

        )

        return df
    
def run_example():

    alerts = pd.read_csv(

        MONITORING_DIR

        / "monitor_alerts.csv"

    )

    AlertHistoryEngine.append(

        alerts

    )

    print()

    print(

        "=" * 80

    )

    print(

        "ALERT HISTORY UPDATED"

    )

    print(

        "=" * 80

    )


if __name__ == "__main__":

    run_example()