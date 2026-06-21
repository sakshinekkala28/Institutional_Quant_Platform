from orchestration.master_rebalance_engine import (
    MasterRebalanceEngine
)


def test_rebalance_run():

    engine = (
        MasterRebalanceEngine()
    )

    result = engine.run()

    assert result is not None