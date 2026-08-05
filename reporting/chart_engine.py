"""
====================================================================
Institutional Quant Platform

Chart Engine

Author : Institutional Quant Platform

Purpose
-------
Institutional chart generation engine.

Produces

• Equity Curve
• Drawdown Curve
• Rolling Sharpe
• Portfolio Allocation
• Sector Allocation
• Turnover
• Risk Contribution
• Factor Attribution

Used By

• PDF Report
• HTML Report
• Dashboard
• Streamlit

====================================================================
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np


@dataclass(slots=True)
class ScatterChartConfig:
    """
    Configuration for scatter chart generation.
    """

    x: Any
    y: Any
    filename: str | Path
    title: str = "Scatter Plot"
    xlabel: str = ""
    ylabel: str = ""


class ChartEngine:
    """
    Institutional chart engine.
    """

    # =====================================================
    # SAVE FIGURE
    # =====================================================

    @staticmethod
    def _save(
        figure,
        filename: str | Path,
    ) -> None:

        path = Path(filename)

        path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        figure.tight_layout()

        figure.savefig(
            path,
            dpi=300,
            bbox_inches="tight",
        )

        plt.close(figure)

    # =====================================================
    # EQUITY CURVE
    # =====================================================

    @classmethod
    def equity_curve(
        cls,
        equity,
        filename,
        title="Equity Curve",
    ):

        figure = plt.figure(figsize=(10, 5))

        plt.plot(
            equity,
            linewidth=2,
        )

        plt.title(title)

        plt.xlabel("Time")

        plt.ylabel("Portfolio Value")

        plt.grid(alpha=0.30)

        cls._save(
            figure,
            filename,
        )

    # =====================================================
    # DRAWDOWN
    # =====================================================

    @classmethod
    def drawdown(
        cls,
        drawdown,
        filename,
        title="Drawdown",
    ):

        figure = plt.figure(figsize=(10, 4))

        plt.fill_between(
            np.arange(len(drawdown)),
            drawdown,
            color="red",
            alpha=0.30,
        )

        plt.title(title)

        plt.grid(alpha=0.30)

        cls._save(
            figure,
            filename,
        )

    # =====================================================
    # ROLLING SHARPE
    # =====================================================

    @classmethod
    def rolling_sharpe(
        cls,
        sharpe,
        filename,
        title="Rolling Sharpe",
    ):

        figure = plt.figure(figsize=(10, 4))

        plt.plot(
            sharpe,
            linewidth=2,
        )

        plt.axhline(
            1.0,
            linestyle="--",
        )

        plt.title(title)

        plt.grid(alpha=0.30)

        cls._save(
            figure,
            filename,
        )

    # =====================================================
    # PIE CHART
    # =====================================================

    @classmethod
    def allocation(
        cls,
        labels,
        weights,
        filename,
        title="Portfolio Allocation",
    ):

        figure = plt.figure(figsize=(7, 7))

        plt.pie(
            weights,
            labels=labels,
            autopct="%1.1f%%",
            startangle=90,
        )

        plt.title(title)

        cls._save(
            figure,
            filename,
        )

    # =====================================================
    # BAR CHART
    # =====================================================

    @classmethod
    def bar(
        cls,
        labels,
        values,
        filename,
        title,
        ylabel,
    ):

        figure = plt.figure(figsize=(10, 5))

        plt.bar(
            labels,
            values,
        )

        plt.xticks(
            rotation=45,
            ha="right",
        )

        plt.ylabel(ylabel)

        plt.title(title)

        plt.grid(
            axis="y",
            alpha=0.30,
        )

        cls._save(
            figure,
            filename,
        )

    # =====================================================
    # HISTOGRAM
    # =====================================================

    @classmethod
    def histogram(
        cls,
        values,
        filename,
        bins=30,
        title="Distribution",
    ):

        figure = plt.figure(figsize=(8, 5))

        plt.hist(
            values,
            bins=bins,
        )

        plt.title(title)

        plt.grid(alpha=0.30)

        cls._save(
            figure,
            filename,
        )

    # =====================================================
    # HEATMAP
    # =====================================================

    @classmethod
    def heatmap(
        cls,
        matrix,
        filename,
        title="Heatmap",
    ):

        figure = plt.figure(figsize=(8, 6))

        plt.imshow(
            matrix,
            aspect="auto",
        )

        plt.colorbar()

        plt.title(title)

        cls._save(
            figure,
            filename,
        )

    # =====================================================
    # SCATTER
    # =====================================================

    @classmethod
    def scatter(
        cls,
        config: ScatterChartConfig,
    ) -> None:

        figure = plt.figure(figsize=(8, 5))

        plt.scatter(
            config.x,
            config.y,
        )

        plt.xlabel(config.xlabel)

        plt.ylabel(config.ylabel)

        plt.title(config.title)

        plt.grid(alpha=0.30)

        cls._save(
            figure,
            config.filename,
        )

    # =====================================================
    # SUMMARY
    # =====================================================

    @staticmethod
    def supported_charts():

        return [
            "EquityCurve",
            "Drawdown",
            "RollingSharpe",
            "Allocation",
            "Bar",
            "Histogram",
            "Heatmap",
            "Scatter",
        ]

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(
        self,
    ):

        return f"{self.__class__.__name__}({len(self.supported_charts())} Charts)"

    __str__ = __repr__
