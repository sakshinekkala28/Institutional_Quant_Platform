# ==========================================================
# TRADE ENGINE
# Institutional Execution Layer
# ==========================================================

from __future__ import annotations

import numpy as np
import pandas as pd


# ==========================================================
# TRADE GENERATOR
# ==========================================================

class TradeGenerator:

    @staticmethod
    def generate(
        current_portfolio,
        target_portfolio
    ):

        if (
            "Current_Weight" not in current_portfolio.columns
        ):

            if (
                "Weight"
                in current_portfolio.columns
            ):

                current_portfolio = (
                    current_portfolio
                    .rename(
                        columns={
                            "Weight":
                            "Current_Weight"
                        }
                    )
                )

            else:

                raise ValueError(
                    "Current portfolio missing "
                    "Current_Weight column"
                )

        current = (

            current_portfolio[

                [
                    "Symbol",
                    "Current_Weight"
                ]

            ]

            .copy()

        )

        target = target_portfolio[

            ["Symbol", "Target_Weight"]

        ].copy()

        trades = current.merge(

            target,

            on="Symbol",

            how="outer"

        )

        trades["Current_Weight"] = (

            trades["Current_Weight"]

            .fillna(0)

        )

        trades["Target_Weight"] = (

            trades["Target_Weight"]

            .fillna(0)

        )

        trades["Trade_Weight"] = (

            trades["Target_Weight"]

            -

            trades["Current_Weight"]

        )

        return trades


# ==========================================================
# REBALANCE ENGINE
# ==========================================================

class RebalanceEngine:

    @staticmethod
    def classify(
        trades
    ):

        conditions = [

            trades["Trade_Weight"] > 0,

            trades["Trade_Weight"] < 0

        ]

        choices = [

            "BUY",

            "SELL"

        ]

        trades["Action"] = np.select(

            conditions,

            choices,

            default="HOLD"

        )

        return trades
    
# ==========================================================
# TURNOVER ENGINE
# ==========================================================

class TurnoverEngine:

    @staticmethod
    def calculate_turnover(
        trades
    ):

        turnover = (

            trades[
                "Trade_Weight"
            ]

            .abs()

            .sum()

        )

        return turnover

    @staticmethod
    def reduce_turnover(
        trades,
        threshold=0.001
    ):

        trades = trades.copy()

        trades.loc[

            trades[
                "Trade_Weight"
            ].abs()

            < threshold,

            "Trade_Weight"

        ] = 0

        trades = (

            RebalanceEngine

            .classify(trades)

        )

        return trades

    @staticmethod
    def trade_count(
        trades
    ):

        return (

            trades["Action"]

            != "HOLD"

        ).sum()
    
# ==========================================================
# TRANSACTION COST MODEL
# ==========================================================

class TransactionCostModel:

    @staticmethod
    def estimate_cost(
        trades
    ):

        trades = trades.copy()

        trades["Estimated_Cost_bps"] = (

            5

            +

            10

            *

            trades[
                "Trade_Weight"
            ]

            .abs()

        )

        trades["Estimated_Cost"] = (

            trades[
                "Estimated_Cost_bps"
            ]

            / 10000

        )

        return trades

    @staticmethod
    def total_cost(
        trades
    ):

        return (

            trades[
                "Estimated_Cost"
            ]

            .sum()

        )


# ==========================================================
# CAPACITY MODEL
# ==========================================================

class CapacityModel:

    @staticmethod
    def participation_rate(
        trades
    ):

        if "ADV_20D" not in trades.columns:

            trades[
                "Participation_Rate"
            ] = np.nan

            return trades

        trades[
            "Participation_Rate"
        ] = (

            trades[
                "Trade_Value"
            ]

            /

            trades[
                "ADV_20D"
            ]

        )

        return trades
    
# ==========================================================
# EXECUTION PRIORITY
# ==========================================================

class ExecutionPriorityModel:

    @staticmethod
    def prioritize(
        trades
    ):

        trades = trades.copy()

        trades["Priority_Score"] = (

            trades[
                "Trade_Weight"
            ]

            .abs()

        )

        trades = trades.sort_values(

            "Priority_Score",

            ascending=False

        )

        trades["Priority"] = np.arange(

            1,

            len(trades) + 1

        )

        return trades


# ==========================================================
# TRADE ENGINE
# ==========================================================

class TradeEngine:

    def generate(

        self,

        current_portfolio,

        target_portfolio

    ):

        trades = (

            TradeGenerator

            .generate(

                current_portfolio,

                target_portfolio

            )

        )

        trades = (

            RebalanceEngine

            .classify(
                trades
            )

        )

        trades = (

            TurnoverEngine

            .reduce_turnover(
                trades
            )

        )

        trades = (

            TransactionCostModel

            .estimate_cost(
                trades
            )

        )

        trades = (

            ExecutionPriorityModel

            .prioritize(
                trades
            )

        )

        turnover = (

            TurnoverEngine

            .calculate_turnover(
                trades
            )

        )

        trade_count = (

            TurnoverEngine

            .trade_count(
                trades
            )

        )

        total_cost = (

            TransactionCostModel

            .total_cost(
                trades
            )

        )

        print(
            "\n✓ Trade Generation Complete"
        )

        print(
            f"Turnover: "
            f"{turnover:.4f}"
        )

        print(
            f"Trades: "
            f"{trade_count}"
        )

        print(
            f"Cost: "
            f"{total_cost:.4f}"
        )

        return trades