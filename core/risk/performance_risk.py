"""
====================================================================
Institutional Quant Platform

Performance Risk

Author : Institutional Quant Platform

Purpose
-------
Institutional performance-adjusted risk model.

Provides

• Sharpe Ratio
• Sortino Ratio
• Treynor Ratio
• Omega Ratio
• Calmar Ratio
• Gain/Loss Ratio
• Upside Capture Ratio
• Downside Capture Ratio

Inherited From

• BaseRiskModel

====================================================================
"""

from __future__ import annotations

import numpy as np

from core.models.risk_report import RiskReport

from core.risk.base_risk_model import BaseRiskModel


class PerformanceRisk(

    BaseRiskModel

):
    """
    Institutional performance-adjusted risk model.
    """

    # =====================================================
    # INTERNAL
    # =====================================================

    @property
    def portfolio_returns(

        self

    ) -> np.ndarray:
        """
        Weighted portfolio return series.
        """

        returns = np.vstack(

            [

                self.asset_returns[
                    symbol
                ].values

                for symbol

                in self.symbols

            ]

        )

        weights = np.asarray(

            self.weights,

            dtype=np.float64

        )

        return (

            weights

            @ returns

        )

    @property
    def benchmark_returns(

        self

    ) -> np.ndarray:
        """
        Benchmark return series.
        """

        if self.benchmark is None:

            raise ValueError(

                "Benchmark is required."

            )

        return np.asarray(

            self.benchmark
                .return_series
                .values,

            dtype=np.float64

        )

    @property
    def risk_free_rate(

        self

    ) -> float:
        """
        Risk-free rate.
        """

        if self.benchmark is None:

            return 0.0

        return (

            self.benchmark

            .risk_free_rate

        )

    # =====================================================
    # DOWNSIDE RETURNS
    # =====================================================

    @property
    def downside_returns(

        self

    ) -> np.ndarray:
        """
        Portfolio returns below
        the risk-free rate.
        """

        returns = (

            self.portfolio_returns

        )

        return returns[

            returns

            <

            self.risk_free_rate

        ]

    # =====================================================
    # DOWNSIDE DEVIATION
    # =====================================================

    @property
    def downside_deviation(

        self

    ) -> float:
        """
        Downside deviation.
        """

        downside = (

            self.downside_returns

        )

        if downside.size == 0:

            return 0.0

        deviations = (

            downside

            -

            self.risk_free_rate

        )

        return float(

            np.sqrt(

                np.mean(

                    deviations ** 2

                )

            )

        )

    # =====================================================
    # UPSIDE RETURNS
    # =====================================================

    @property
    def upside_returns(

        self

    ) -> np.ndarray:
        """
        Portfolio returns above
        the risk-free rate.
        """

        returns = (

            self.portfolio_returns

        )

        return returns[

            returns

            >=

            self.risk_free_rate

        ]
    
    # =====================================================
    # SHARPE RATIO
    # =====================================================

    @property
    def sharpe_ratio(

        self

    ) -> float:
        """
        Annualized Sharpe Ratio.

        Sharpe =
            (Rp - Rf) / σp
        """

        portfolio_returns = (

            self.portfolio_returns

        )

        if portfolio_returns.size < 2:

            return 0.0

        excess_returns = (

            portfolio_returns

            -

            self.risk_free_rate

        )

        volatility = float(

            np.std(

                excess_returns,

                ddof=1

            )

        )

        if volatility <= 0.0:

            return 0.0

        return float(

            np.mean(

                excess_returns

            )

            /

            volatility

        )

    # =====================================================
    # SORTINO RATIO
    # =====================================================

    @property
    def sortino_ratio(

        self

    ) -> float:
        """
        Annualized Sortino Ratio.

        Sortino =
            (Rp - Rf) / Downside Deviation
        """

        downside = (

            self.downside_deviation

        )

        if downside <= 0.0:

            return 0.0

        excess_return = float(

            np.mean(

                self.portfolio_returns

            )

            -

            self.risk_free_rate

        )

        return excess_return / downside

    # =====================================================
    # TREYNOR RATIO
    # =====================================================

    @property
    def treynor_ratio(

        self

    ) -> float:
        """
        Treynor Ratio.

        Treynor =
            (Rp - Rf) / Beta
        """

        benchmark = (

            self.benchmark_returns

        )

        portfolio = (

            self.portfolio_returns

        )

        benchmark_variance = float(

            np.var(

                benchmark,

                ddof=1

            )

        )

        if benchmark_variance <= 0.0:

            return 0.0

        beta = float(

            np.cov(

                portfolio,

                benchmark,

                ddof=1

            )[0, 1]

            /

            benchmark_variance

        )

        if abs(

            beta

        ) < 1e-12:

            return 0.0

        excess_return = float(

            np.mean(

                portfolio

            )

            -

            self.risk_free_rate

        )

        return excess_return / beta

    # =====================================================
    # OMEGA RATIO
    # =====================================================

    @property
    def omega_ratio(

        self

    ) -> float:
        """
        Omega Ratio.

        Threshold =
            Risk-free rate.
        """

        returns = (

            self.portfolio_returns

        )

        threshold = (

            self.risk_free_rate

        )

        gains = np.clip(

            returns - threshold,

            a_min=0.0,

            a_max=None

        )

        losses = np.clip(

            threshold - returns,

            a_min=0.0,

            a_max=None

        )

        denominator = float(

            np.sum(

                losses

            )

        )

        if denominator <= 0.0:

            return float(

                "inf"

            )

        numerator = float(

            np.sum(

                gains

            )

        )

        return numerator / denominator
    
    # =====================================================
    # MAXIMUM DRAWDOWN
    # =====================================================

    @property
    def maximum_drawdown(

        self

    ) -> float:
        """
        Maximum Drawdown.

        Returns
        -------
        float
            Absolute maximum drawdown.
        """

        returns = (

            self.portfolio_returns

        )

        if returns.size == 0:

            return 0.0

        cumulative = np.cumprod(

            1.0 + returns

        )

        running_max = np.maximum.accumulate(

            cumulative

        )

        drawdowns = (

            cumulative

            /

            running_max

        ) - 1.0

        return float(

            abs(

                np.min(

                    drawdowns

                )

            )

        )

    # =====================================================
    # CALMAR RATIO
    # =====================================================

    @property
    def calmar_ratio(

        self

    ) -> float:
        """
        Annualized Calmar Ratio.
        """

        maximum_drawdown = (

            self.maximum_drawdown

        )

        if maximum_drawdown <= 0.0:

            return 0.0

        annual_return = (

            float(

                np.mean(

                    self.portfolio_returns

                )

            )

            * 252.0

        )

        return (

            annual_return

            /

            maximum_drawdown

        )

    # =====================================================
    # GAIN / LOSS RATIO
    # =====================================================

    @property
    def gain_loss_ratio(

        self

    ) -> float:
        """
        Gain/Loss Ratio.
        """

        gains = (

            self.upside_returns

        )

        losses = (

            self.downside_returns

        )

        if losses.size == 0:

            return float(

                "inf"

            )

        average_gain = float(

            np.mean(

                gains

            )

        ) if gains.size else 0.0

        average_loss = abs(

            float(

                np.mean(

                    losses

                )

            )

        )

        if average_loss <= 0.0:

            return float(

                "inf"

            )

        return (

            average_gain

            /

            average_loss

        )

    # =====================================================
    # UPSIDE CAPTURE
    # =====================================================

    @property
    def upside_capture_ratio(

        self

    ) -> float:
        """
        Upside Capture Ratio.
        """

        benchmark = (

            self.benchmark_returns

        )

        portfolio = (

            self.portfolio_returns

        )

        mask = (

            benchmark > 0.0

        )

        if not np.any(

            mask

        ):

            return 0.0

        benchmark_up = float(

            np.mean(

                benchmark[mask]

            )

        )

        if abs(

            benchmark_up

        ) < 1e-12:

            return 0.0

        portfolio_up = float(

            np.mean(

                portfolio[mask]

            )

        )

        return (

            portfolio_up

            /

            benchmark_up

        )

    # =====================================================
    # DOWNSIDE CAPTURE
    # =====================================================

    @property
    def downside_capture_ratio(

        self

    ) -> float:
        """
        Downside Capture Ratio.
        """

        benchmark = (

            self.benchmark_returns

        )

        portfolio = (

            self.portfolio_returns

        )

        mask = (

            benchmark < 0.0

        )

        if not np.any(

            mask

        ):

            return 0.0

        benchmark_down = abs(

            float(

                np.mean(

                    benchmark[mask]

                )

            )

        )

        if benchmark_down <= 0.0:

            return 0.0

        portfolio_down = abs(

            float(

                np.mean(

                    portfolio[mask]

                )

            )

        )

        return (

            portfolio_down

            /

            benchmark_down

        )
    
    # =====================================================
    # CALCULATE
    # =====================================================

    def calculate(

        self

    ) -> RiskReport:
        """
        Calculate performance-adjusted
        portfolio risk metrics.

        Returns
        -------
        RiskReport
        """

        report = self.create_report()

        report.sharpe_ratio = (

            self.sharpe_ratio

        )

        report.sortino_ratio = (

            self.sortino_ratio

        )

        report.calmar_ratio = (

            self.calmar_ratio

        )

        report.maximum_drawdown = (

            self.maximum_drawdown

        )

        report.metadata.update(

            {

                "treynor_ratio":

                    self.treynor_ratio,

                "omega_ratio":

                    self.omega_ratio,

                "gain_loss_ratio":

                    self.gain_loss_ratio,

                "upside_capture_ratio":

                    self.upside_capture_ratio,

                "downside_capture_ratio":

                    self.downside_capture_ratio,

                "risk_model":

                    self.__class__.__name__

            }

        )

        return report

    # =====================================================
    # SUMMARY
    # =====================================================

    def summary(

        self

    ) -> dict[str, float]:
        """
        Performance risk summary.

        Returns
        -------
        dict
        """

        return {

            "sharpe_ratio":

                self.sharpe_ratio,

            "sortino_ratio":

                self.sortino_ratio,

            "treynor_ratio":

                self.treynor_ratio,

            "omega_ratio":

                self.omega_ratio,

            "calmar_ratio":

                self.calmar_ratio,

            "gain_loss_ratio":

                self.gain_loss_ratio,

            "maximum_drawdown":

                self.maximum_drawdown,

            "upside_capture_ratio":

                self.upside_capture_ratio,

            "downside_capture_ratio":

                self.downside_capture_ratio

        }

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Sharpe={self.sharpe_ratio:.4f}, "

            f"Sortino={self.sortino_ratio:.4f}, "

            f"Calmar={self.calmar_ratio:.4f}"

            f")"

        )

    __str__ = __repr__