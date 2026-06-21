# ==========================================================
# BACKTEST ENGINE
# Institutional Performance Analytics
# ==========================================================

from __future__ import annotations

import numpy as np
import pandas as pd


def _to_series(data):

    if isinstance(
        data,
        pd.Series
    ):
        return data

    return pd.Series(data)

# ==========================================================
# PORTFOLIO RETURN ENGINE
# ==========================================================

class PortfolioReturnEngine:

    @staticmethod
    def calculate(
        weights,
        returns
    ):

        if not isinstance(
            returns,
            pd.Series
        ):
            returns = _to_series(returns)

        returns = np.asarray(returns)
        weights = np.asarray(weights)

        if returns.shape[-1] != len(weights):
            raise ValueError(
                "Returns columns must match weight vector length"
            )

        portfolio_returns = returns @ weights

        return portfolio_returns


# ==========================================================
# BENCHMARK ENGINE
# ==========================================================

class BenchmarkEngine:

    @staticmethod
    def excess_return(
        portfolio_returns,
        benchmark_returns
    ):

        return (

            portfolio_returns

            -

            benchmark_returns

        )
    
# ==========================================================
# PERFORMANCE METRICS
# ==========================================================

class PerformanceMetrics:

    @staticmethod
    def sharpe_ratio(
        returns,
        risk_free_rate=0.06
    ):

        returns = _to_series(returns)

        excess = (
            returns - risk_free_rate / 252
        )

        if excess.std() == 0:
            return 0.0

        return (
            np.sqrt(252)
            * excess.mean()
            / excess.std()
        )
    
    @staticmethod
    def sortino_ratio(
        returns,
        risk_free_rate=0.06
    ):

        returns = _to_series(returns)

        downside = (

            returns[
                returns < 0
            ]

        )

        if downside.std() == 0:
            return 0.0

        return (

            np.sqrt(252)

            *

            (

                returns.mean()

                -

                risk_free_rate / 252

            )

            /

            downside.std()

        )

    @staticmethod
    def cagr(
        returns
    ):
        returns = _to_series(returns)

        cumulative = (

            1 + returns

        ).prod()

        years = (

            len(returns)

            / 252

        )

        return (

            cumulative

            **

            (1 / years)

            - 1

        )


# ==========================================================
# DRAWDOWN ENGINE
# ==========================================================

class DrawdownEngine:

    @staticmethod
    def max_drawdown(
        returns
    ):
        returns = _to_series(returns)

        cumulative = (

            1 + returns

        ).cumprod()

        running_max = (

            cumulative

            .cummax()

        )

        drawdown = (

            cumulative

            /

            running_max

            - 1

        )

        return drawdown.min()


# ==========================================================
# ROLLING ANALYTICS
# ==========================================================

class RollingAnalytics:

    @staticmethod
    def rolling_volatility(
        returns,
        window=63
    ):
        returns = _to_series(returns)

        return (

            returns

            .rolling(window)

            .std()

            *

            np.sqrt(252)

        )

    @staticmethod
    def rolling_sharpe(
        returns,
        window=63
    ):
        returns = _to_series(returns)

        return (

            returns

            .rolling(window)

            .mean()

            /

            returns

            .rolling(window)

            .std()

        ) * np.sqrt(252)
    
# ==========================================================
# ATTRIBUTION ENGINE
# ==========================================================

class AttributionEngine:

    @staticmethod
    def sector_attribution(
        portfolio
    ):

        if "Sector" not in portfolio.columns:

            return pd.DataFrame()

        attribution = (

            portfolio

            .groupby("Sector")

            ["Target_Weight"]

            .sum()

            .reset_index()

        )

        attribution.rename(

            columns={

                "Target_Weight":
                "Sector_Exposure"

            },

            inplace=True

        )

        return attribution


# ==========================================================
# MASTER BACKTEST ENGINE
# ==========================================================

class BacktestEngine:

    def run(
        self,
        portfolio_returns,
        benchmark_returns=None
    ):

        report = {}

        report["CAGR"] = (

            PerformanceMetrics

            .cagr(
                portfolio_returns
            )

        )

        report["Sharpe"] = (

            PerformanceMetrics

            .sharpe_ratio(
                portfolio_returns
            )

        )

        report["Sortino"] = (

            PerformanceMetrics

            .sortino_ratio(
                portfolio_returns
            )

        )

        report["Max_Drawdown"] = (

            DrawdownEngine

            .max_drawdown(
                portfolio_returns
            )

        )

        if benchmark_returns is not None:

            excess = (

                BenchmarkEngine

                .excess_return(

                    portfolio_returns,

                    benchmark_returns

                )

            )

            report["Alpha"] = (

                excess.mean()

                * 252

            )

        print(
            "\n✓ Backtest Complete"
        )

        print(
            f"CAGR: "
            f"{report['CAGR']:.2%}"
        )

        print(
            f"Sharpe: "
            f"{report['Sharpe']:.2f}"
        )

        print(
            f"Max Drawdown: "
            f"{report['Max_Drawdown']:.2%}"
        )

        return report