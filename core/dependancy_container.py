# ==========================================================
# DEPENDENCY CONTAINER
# Enterprise Dependency Injection Framework
# ==========================================================

from __future__ import annotations

from typing import Dict
from typing import Any


# ==========================================================
# SERVICE REGISTRY
# ==========================================================

class ServiceRegistry:

    def __init__(self):

        self._services: Dict[str, Any] = {}

    def register(

        self,

        name: str,

        service: Any

    ):

        self._services[name] = service

    def get(

        self,

        name: str

    ):

        if name not in self._services:

            raise KeyError(

                f"Service not registered: {name}"

            )

        return self._services[name]

    def exists(

        self,

        name: str

    ):

        return name in self._services
    
# ==========================================================
# LAZY SERVICE LOADER
# ==========================================================

class LazyService:

    def __init__(

        self,

        factory

    ):

        self.factory = factory

        self.instance = None

    def get(self):

        if self.instance is None:

            self.instance = self.factory()

        return self.instance


# ==========================================================
# SERVICE FACTORY
# ==========================================================

class ServiceFactory:

    def __init__(self):

        self.factories = {}

    def register(

        self,

        name,

        factory

    ):

        self.factories[name] = (

            LazyService(factory)

        )

    def resolve(

        self,

        name

    ):

        return (

            self.factories[name]

            .get()

        )
    
# ==========================================================
# PLATFORM SERVICES
# ==========================================================

from alpha.signal_engine import (
    SignalEngine
)

from portfolio.portfolio_engine import (
    PortfolioEngine
)

from risk.risk_engine import (
    RiskEngine
)

from execution.trade_engine import (
    TradeEngine
)

from execution.execution_engine import (
    ExecutionEngine
)

from reporting.reporting_engine import (
    ReportingEngine
)


# ==========================================================
# SERVICE BUILDER
# ==========================================================

class PlatformServiceBuilder:

    @staticmethod
    def build(factory):

        factory.register(

            "signal_engine",

            SignalEngine

        )

        factory.register(

            "portfolio_engine",

            PortfolioEngine

        )

        factory.register(

            "risk_engine",

            RiskEngine

        )

        factory.register(

            "trade_engine",

            TradeEngine

        )

        factory.register(

            "execution_engine",

            ExecutionEngine

        )

        factory.register(

            "reporting_engine",

            ReportingEngine

        )

        return factory
    
# ==========================================================
# DEPENDENCY CONTAINER
# ==========================================================

class DependencyContainer:

    def __init__(self):

        self.factory = (

            PlatformServiceBuilder

            .build(

                ServiceFactory()

            )

        )

    @property
    def signal_engine(self):

        return (

            self.factory

            .resolve(
                "signal_engine"
            )

        )

    @property
    def portfolio_engine(self):

        return (

            self.factory

            .resolve(
                "portfolio_engine"
            )

        )

    @property
    def risk_engine(self):

        return (

            self.factory

            .resolve(
                "risk_engine"
            )

        )

    @property
    def trade_engine(self):

        return (

            self.factory

            .resolve(
                "trade_engine"
            )

        )

    @property
    def execution_engine(self):

        return (

            self.factory

            .resolve(
                "execution_engine"
            )

        )

    @property
    def reporting_engine(self):

        return (

            self.factory

            .resolve(
                "reporting_engine"
            )

        )


# ==========================================================
# GLOBAL CONTAINER
# ==========================================================

container = DependencyContainer()