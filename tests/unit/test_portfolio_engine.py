import pandas as pd

from portfolio.portfolio_engine import (
    PortfolioEngine
)


def test_portfolio_construction():

    df = pd.DataFrame({

        "Symbol":[

            "A",

            "B",

            "C"

        ],

        "Selection_Score":[

            100,

            90,

            80

        ],

        "Volatility_252D":[

            0.20,

            0.25,

            0.30

        ],

        "Sector":[

            "IT",

            "BANKING",

            "AUTO"

        ],

        "Market_Cap":[

            100,

            90,

            80

        ]

    })

    engine = PortfolioEngine(
        target_holdings=3
    )

    portfolio = engine.construct(df)

    assert len(portfolio) == 3