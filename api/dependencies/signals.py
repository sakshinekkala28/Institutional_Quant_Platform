"""
====================================================================
Institutional Quant Platform

Signal Dependencies

Author : Institutional Quant Platform

Purpose
-------
FastAPI dependency providers for signal generation.

Provides

• Signal Engine
• Alpha Engine
• Factor Engine
• Universe Builder
• Regime Engine
• Selection Engine
• Signal Diagnostics

Used By

• Signals Router
• Portfolio Router
• Optimization Router
• Backtest Router

====================================================================
"""

from __future__ import annotations

from functools import lru_cache

from alpha.signal_engine import (
    SignalEngine,
)

from alpha.signal_engine import (
    AlphaEngine,
)

from alpha.signal_engine import (
    FactorEngine,
)

from alpha.signal_engine import (
    UniverseBuilder,
)

from alpha.signal_engine import (
    RegimeEngine,
)

from alpha.signal_engine import (
    SelectionScoreEngine,
)

from alpha.signal_engine import (
    FactorDiagnostics,
)


# ==========================================================
# SIGNAL ENGINE
# ==========================================================


@lru_cache
def get_signal_engine(

) -> SignalEngine:
    """
    Signal engine singleton.
    """

    return SignalEngine()


# ==========================================================
# ALPHA ENGINE
# ==========================================================


@lru_cache
def get_alpha_engine(

) -> AlphaEngine:
    """
    Alpha engine.
    """

    return AlphaEngine()


# ==========================================================
# FACTOR ENGINE
# ==========================================================


@lru_cache
def get_factor_engine(

) -> FactorEngine:
    """
    Factor engine.
    """

    return FactorEngine()


# ==========================================================
# UNIVERSE BUILDER
# ==========================================================


@lru_cache
def get_universe_builder(

) -> UniverseBuilder:
    """
    Universe builder.
    """

    return UniverseBuilder()


# ==========================================================
# REGIME ENGINE
# ==========================================================


@lru_cache
def get_regime_engine(

) -> RegimeEngine:
    """
    Market regime engine.
    """

    return RegimeEngine()


# ==========================================================
# SELECTION ENGINE
# ==========================================================


@lru_cache
def get_selection_engine(

) -> SelectionScoreEngine:
    """
    Selection engine.
    """

    return SelectionScoreEngine()


# ==========================================================
# FACTOR DIAGNOSTICS
# ==========================================================


@lru_cache
def get_factor_diagnostics(

) -> FactorDiagnostics:
    """
    Diagnostics engine.
    """

    return FactorDiagnostics()


# ==========================================================
# HEALTH
# ==========================================================


def signal_health(

) -> dict:
    """
    Dependency health.
    """

    return {

        "engine": "SignalEngine",

        "status": "healthy",

        "singleton": True,

    }


# ==========================================================
# SUMMARY
# ==========================================================


def signal_summary(

) -> dict:
    """
    Registered services.
    """

    return {

        "services": [

            "SignalEngine",

            "AlphaEngine",

            "FactorEngine",

            "UniverseBuilder",

            "RegimeEngine",

            "SelectionScoreEngine",

            "FactorDiagnostics",

        ],

        "count": 7,

    }


# ==========================================================
# EXPORTS
# ==========================================================


__all__ = [

    "get_signal_engine",

    "get_alpha_engine",

    "get_factor_engine",

    "get_universe_builder",

    "get_regime_engine",

    "get_selection_engine",

    "get_factor_diagnostics",

    "signal_health",

    "signal_summary",

]