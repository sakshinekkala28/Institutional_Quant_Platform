"""
====================================================================
Institutional Quant Platform

API Dependencies Package

Author : Institutional Quant Platform

Purpose
-------
Dependency Injection Package.

Provides

• Configuration
• Authentication
• Authorization
• Database
• Cache
• Logger
• Telemetry
• Portfolio Services
• Risk Services
• Execution Services

Used By

• FastAPI Routers
• Middleware
• Services

====================================================================
"""

from api.dependencies.authentication import get_current_user
from api.dependencies.authorization import require_permission, require_role
from api.dependencies.backtest import get_backtest_engine
from api.dependencies.cache import get_cache
from api.dependencies.config import get_settings
from api.dependencies.database import get_database
from api.dependencies.execution import get_execution_engine
from api.dependencies.logger import get_logger
from api.dependencies.monitoring import get_monitoring_service
from api.dependencies.optimization import get_optimizer
from api.dependencies.portfolio import get_portfolio_engine
from api.dependencies.risk import get_risk_engine
from api.dependencies.signals import get_signal_engine
from api.dependencies.telemetry import get_telemetry

__all__ = [
    "get_backtest_engine",
    "get_cache",
    "get_current_user",
    "get_database",
    "get_execution_engine",
    "get_logger",
    "get_monitoring_service",
    "get_optimizer",
    "get_portfolio_engine",
    "get_risk_engine",
    "get_settings",
    "get_signal_engine",
    "get_telemetry",
    "require_permission",
    "require_role",
]
