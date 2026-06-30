"""
====================================================================
Institutional Quant Platform

Backtest Dependencies

Author : Institutional Quant Platform

Purpose
-------
FastAPI dependency providers for backtesting services.

Provides

• Backtest Engine
• Performance Analyzer
• Benchmark Engine
• Attribution Engine
• Statistics Engine
• Report Generator
• Walk Forward Engine
• Scenario Engine

Used By

• Backtest Router
• Portfolio Router
• Optimization Router
• Monitoring Router

====================================================================
"""

from __future__ import annotations

from functools import lru_cache

from backtesting.backtest_engine import (
    BacktestEngine,
)

from backtesting.performance_analyzer import (
    PerformanceAnalyzer,
)

from backtesting.benchmark_engine import (
    BenchmarkEngine,
)

from backtesting.attribution_engine import (
    AttributionEngine,
)

from backtesting.statistics_engine import (
    StatisticsEngine,
)

from backtesting.report_generator import (
    ReportGenerator,
)

from backtesting.walk_forward_engine import (
    WalkForwardEngine,
)

from backtesting.scenario_engine import (
    ScenarioEngine,
)


# ==========================================================
# BACKTEST ENGINE
# ==========================================================


@lru_cache
def get_backtest_engine(

) -> BacktestEngine:
    """
    Primary backtest engine.
    """

    return BacktestEngine()


# ==========================================================
# PERFORMANCE ANALYZER
# ==========================================================


@lru_cache
def get_performance_analyzer(

) -> PerformanceAnalyzer:
    """
    Performance analyzer.
    """

    return PerformanceAnalyzer()


# ==========================================================
# BENCHMARK ENGINE
# ==========================================================


@lru_cache
def get_benchmark_engine(

) -> BenchmarkEngine:
    """
    Benchmark comparison engine.
    """

    return BenchmarkEngine()


# ==========================================================
# ATTRIBUTION ENGINE
# ==========================================================


@lru_cache
def get_attribution_engine(

) -> AttributionEngine:
    """
    Performance attribution engine.
    """

    return AttributionEngine()


# ==========================================================
# STATISTICS ENGINE
# ==========================================================


@lru_cache
def get_statistics_engine(

) -> StatisticsEngine:
    """
    Statistical analysis engine.
    """

    return StatisticsEngine()


# ==========================================================
# REPORT GENERATOR
# ==========================================================


@lru_cache
def get_report_generator(

) -> ReportGenerator:
    """
    Report generator.
    """

    return ReportGenerator()


# ==========================================================
# WALK FORWARD ENGINE
# ==========================================================


@lru_cache
def get_walk_forward_engine(

) -> WalkForwardEngine:
    """
    Walk-forward validation engine.
    """

    return WalkForwardEngine()


# ==========================================================
# SCENARIO ENGINE
# ==========================================================


@lru_cache
def get_scenario_engine(

) -> ScenarioEngine:
    """
    Scenario analysis engine.
    """

    return ScenarioEngine()


# ==========================================================
# HEALTH
# ==========================================================


def backtest_health(

) -> dict:
    """
    Dependency health.
    """

    return {

        "engine": "BacktestEngine",

        "status": "healthy",

        "singleton": True,

    }


# ==========================================================
# SUMMARY
# ==========================================================


def backtest_summary(

) -> dict:
    """
    Registered services.
    """

    return {

        "services": [

            "BacktestEngine",

            "PerformanceAnalyzer",

            "BenchmarkEngine",

            "AttributionEngine",

            "StatisticsEngine",

            "ReportGenerator",

            "WalkForwardEngine",

            "ScenarioEngine",

        ],

        "count": 8,

    }


# ==========================================================
# EXPORTS
# ==========================================================


__all__ = [

    "get_backtest_engine",

    "get_performance_analyzer",

    "get_benchmark_engine",

    "get_attribution_engine",

    "get_statistics_engine",

    "get_report_generator",

    "get_walk_forward_engine",

    "get_scenario_engine",

    "backtest_health",

    "backtest_summary",

]