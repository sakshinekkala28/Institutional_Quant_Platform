"""
====================================================================
Institutional Quant Platform

Optimization Service

Author : Institutional Quant Platform

Purpose
-------
Institutional portfolio optimization
orchestration service.

Coordinates

• Optimizer
• Constraints
• Risk Service
• Governance
• Portfolio Validation

Produces

• Optimized Portfolio
• Optimization Report

====================================================================
"""

from __future__ import annotations

from core.models.portfolio import Portfolio

from core.services.risk_service import RiskService

from optimization.base_optimizer import BaseOptimizer

from optimization.constraint_engine import ConstraintEngine

from optimization.optimization_report import OptimizationReport


class OptimizationService:
    """
    Institutional Optimization Service.
    """

    def __init__(

        self,

        optimizer: BaseOptimizer,

        constraint_engine: ConstraintEngine,

        risk_service: RiskService,

    ) -> None:

        self.optimizer = optimizer

        self.constraint_engine = constraint_engine

        self.risk_service = risk_service

    # =====================================================
    # VALIDATE
    # =====================================================

    def validate(

        self,

        portfolio: Portfolio,

    ) -> None:

        self.constraint_engine.validate(

            portfolio

        )

    # =====================================================
    # OPTIMIZE
    # =====================================================

    def optimize(

        self,

        portfolio: Portfolio,

    ) -> Portfolio:

        self.validate(

            portfolio

        )

        optimized = self.optimizer.optimize(

            portfolio

        )

        self.constraint_engine.validate(

            optimized

        )

        return optimized

    # =====================================================
    # ANALYZE
    # =====================================================

    def analyze(

        self,

        portfolio: Portfolio,

    ) -> dict:

        optimized = self.optimize(

            portfolio

        )

        risk = self.risk_service.summary()

        return {

            "portfolio": optimized,

            "risk": risk,

        }

    # =====================================================
    # REPORT
    # =====================================================

    def report(

        self,

        portfolio: Portfolio,

    ) -> OptimizationReport:

        optimized = self.optimize(

            portfolio

        )

        report = OptimizationReport()

        report.original_portfolio = portfolio

        report.optimized_portfolio = optimized

        report.risk_summary = (

            self.risk_service.summary()

        )

        return report

    # =====================================================
    # REPRESENTATION
    # =====================================================

    def __repr__(

        self,

    ) -> str:

        return (

            f"{self.__class__.__name__}("

            f"Optimizer={self.optimizer.__class__.__name__}"

            f")"

        )

    __str__ = __repr__