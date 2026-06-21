# ==========================================================
# EXECUTION ENGINE
# Institutional Execution Simulation
# ==========================================================

from __future__ import annotations

import numpy as np
import pandas as pd


# ==========================================================
# ORDER BOOK SIMULATOR
# ==========================================================

class OrderBookSimulator:

    @staticmethod
    def estimate_fill_rate(
        trade_value,
        adv_20d
    ):

        if adv_20d <= 0:

            return 0.0

        participation = (
            trade_value / adv_20d
        )

        fill_rate = max(
            0.0,
            1.0 - participation
        )

        return min(
            fill_rate,
            1.0
        )


# ==========================================================
# PARTICIPATION MODEL
# ==========================================================

class ParticipationModel:

    @staticmethod
    def calculate(
        trades
    ):

        trades = trades.copy()

        trades[
            "Participation_Rate"
        ] = (

            trades["Trade_Value"]

            /

            trades["ADV_20D"]

        )

        return trades
    
# ==========================================================
# MARKET IMPACT MODEL
# ==========================================================

class MarketImpactModel:

    @staticmethod
    def estimate(
        trades
    ):

        trades = trades.copy()

        trades[
            "Market_Impact_bps"
        ] = (

            15

            *

            np.sqrt(

                trades[
                    "Participation_Rate"
                ]

                .clip(
                    lower=0
                )

            )

        )

        return trades


# ==========================================================
# SLIPPAGE MODEL
# ==========================================================

class SlippageModel:

    @staticmethod
    def estimate(
        trades
    ):

        trades = trades.copy()

        trades[
            "Slippage_bps"
        ] = (

            2

            +

            trades[
                "Market_Impact_bps"
            ]

            * 0.50

        )

        return trades
    
# ==========================================================
# VWAP MODEL
# ==========================================================

class VWAPExecutionModel:

    @staticmethod
    def estimate_price(
        trades
    ):

        trades = trades.copy()

        trades[
            "VWAP_Price"
        ] = (

            trades["Last_Price"]

            *

            (

                1

                +

                trades[
                    "Slippage_bps"
                ]

                / 10000

            )

        )

        return trades


# ==========================================================
# TWAP MODEL
# ==========================================================

class TWAPExecutionModel:

    @staticmethod
    def estimate_price(
        trades
    ):

        trades = trades.copy()

        trades[
            "TWAP_Price"
        ] = (

            trades["Last_Price"]

            *

            (

                1

                +

                trades[
                    "Slippage_bps"
                ]

                / 12000

            )

        )

        return trades
    
# ==========================================================
# EXECUTION ANALYTICS
# ==========================================================

class ExecutionAnalytics:

    @staticmethod
    def implementation_shortfall(
        trades
    ):

        trades = trades.copy()

        trades[
            "Implementation_Shortfall"
        ] = (

            trades[
                "VWAP_Price"
            ]

            -

            trades[
                "Last_Price"
            ]

        )

        return trades


# ==========================================================
# EXECUTION ENGINE
# ==========================================================

class ExecutionEngine:

    def run(
        self,
        trades
    ):

        trades = (
            ParticipationModel
            .calculate(trades)
        )

        trades = (
            MarketImpactModel
            .estimate(trades)
        )

        trades = (
            SlippageModel
            .estimate(trades)
        )

        trades = (
            VWAPExecutionModel
            .estimate_price(trades)
        )

        trades = (
            TWAPExecutionModel
            .estimate_price(trades)
        )

        trades = (
            ExecutionAnalytics
            .implementation_shortfall(
                trades
            )
        )

        print(
            "\n✓ Execution Simulation Complete"
        )

        return trades