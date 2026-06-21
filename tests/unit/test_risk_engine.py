import pandas as pd

from risk.risk_engine import (
    RiskEngine
)


def test_risk_report():

    portfolio = pd.DataFrame({

        "Target_Weight":[

            0.25,

            0.25,

            0.25,

            0.25

        ],

        "Beta":[

            1.0,

            1.1,

            0.9,

            1.0

        ]

    })

    report = (

        RiskEngine()

        .evaluate(
            portfolio
        )

    )

    assert (
        "Portfolio_Beta"
        in report
    )