import time

import numpy as np

from research.backtest_engine import (
    BacktestEngine
)


def test_backtest_speed():

    returns = np.random.normal(

        0.001,

        0.02,

        5000

    )

    start = time.time()

    BacktestEngine().run(
        returns
    )

    elapsed = (

        time.time()
        -
        start
    )

    assert elapsed < 2.0