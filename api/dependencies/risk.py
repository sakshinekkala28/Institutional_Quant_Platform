"""
====================================================================
Institutional Quant Platform

Risk Dependencies

Author : Institutional Quant Platform

Purpose
-------
FastAPI dependency providers for risk management services.

Provides

• Risk Engine
• VaR Engine
• Expected Shortfall Engine
• Stress Testing Engine
• Exposure Engine
• Factor Risk Engine
• Concentration Risk Engine
• Risk Monitor

Used By

• Risk Router
• Portfolio Router
• Optimization Router
• Execution Router
• Monitoring Router

====================================================================
"""

from __future__ import annotations

from functools import lru_cache

from risk.risk_engine import (
    RiskEngine,
)

from risk.var_engine import (
    ValueAtRiskEngine,
)

from risk.expected_shortfall_engine import (
    ExpectedShortfallEngine,
)

from risk.stress_testing_engine import (
    StressTestingEngine,
)

from risk.exposure_engine import (
    ExposureEngine,
)

from risk.factor_risk_engine import (
    FactorRiskEngine,
)

from risk.concentration_engine import (
    ConcentrationRiskEngine,
)

from risk.risk_monitor import (
    RiskMonitor,
)


# ==========================================================
# RISK ENGINE
# ==========================================================


@lru_cache
def get_risk_engine(

) -> RiskEngine:
    """
    Portfolio risk engine.
    """

    return RiskEngine()


# ==========================================================
# VALUE AT RISK
# ==========================================================


@lru_cache
def get_var_engine(

) -> ValueAtRiskEngine:
    """
    Value-at-Risk engine.
    """

    return ValueAtRiskEngine()


# ==========================================================
# EXPECTED SHORTFALL
# ==========================================================


@lru_cache
def get_expected_shortfall_engine(

) -> ExpectedShortfallEngine:
    """
    Expected Shortfall engine.
    """

    return ExpectedShortfallEngine()


# ==========================================================
# STRESS TESTING
# ==========================================================


@lru_cache
def get_stress_testing_engine(

) -> StressTestingEngine:
    """
    Stress testing engine.
    """

    return StressTestingEngine()


# ==========================================================
# EXPOSURE
# ==========================================================


@lru_cache
def get_exposure_engine(

) -> ExposureEngine:
    """
    Exposure analytics engine.
    """

    return ExposureEngine()


# ==========================================================
# FACTOR RISK
# ==========================================================


@lru_cache
def get_factor_risk_engine(

) -> FactorRiskEngine:
    """
    Factor risk model.
    """

    return FactorRiskEngine()


# ==========================================================
# CONCENTRATION RISK
# ==========================================================


@lru_cache
def get_concentration_engine(

) -> ConcentrationRiskEngine:
    """
    Concentration risk engine.
    """

    return ConcentrationRiskEngine()


# ==========================================================
# RISK MONITOR
# ==========================================================


@lru_cache
def get_risk_monitor(

) -> RiskMonitor:
    """
    Continuous risk monitor.
    """

    return RiskMonitor()


# ==========================================================
# HEALTH
# ==========================================================


def risk_health(

) -> dict:
    """
    Dependency health.
    """

    return {

        "engine": "RiskEngine",

        "status": "healthy",

        "singleton": True,

    }


# ==========================================================
# SUMMARY
# ==========================================================


def risk_summary(

) -> dict:
    """
    Registered services.
    """

    return {

        "services": [

            "RiskEngine",

            "ValueAtRiskEngine",

            "ExpectedShortfallEngine",

            "StressTestingEngine",

            "ExposureEngine",

            "FactorRiskEngine",

            "ConcentrationRiskEngine",

            "RiskMonitor",

        ],

        "count": 8,

    }


# ==========================================================
# EXPORTS
# ==========================================================


__all__ = [

    "get_risk_engine",

    "get_var_engine",

    "get_expected_shortfall_engine",

    "get_stress_testing_engine",

    "get_exposure_engine",

    "get_factor_risk_engine",

    "get_concentration_engine",

    "get_risk_monitor",

    "risk_health",

    "risk_summary",

]