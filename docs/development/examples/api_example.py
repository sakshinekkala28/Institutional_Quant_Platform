"""
Institutional Quant Platform
Production Reference API

Reference implementation demonstrating the
recommended API architecture.

API
    ↓
Service
    ↓
Repository
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Protocol

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict

logger = logging.getLogger(__name__)

app = FastAPI(
    title="Institutional Quant Platform",
    version="1.0.0",
)

# =====================================================================
# Domain Model
# =====================================================================


@dataclass(slots=True, frozen=True)
class Security:
    symbol: str
    company_name: str
    sector: str
    market_cap: float


# =====================================================================
# DTOs
# =====================================================================


class SecurityRequest(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
    )

    symbol: str
    company_name: str
    sector: str
    market_cap: float


class SecurityResponse(BaseModel):
    symbol: str
    company_name: str
    sector: str
    market_cap: float


class APIResponse(BaseModel):
    success: bool
    message: str
    data: dict | None = None


# =====================================================================
# Repository Contract
# =====================================================================


class SecurityRepository(Protocol):
    def get(self, symbol: str) -> Security | None: ...

    def save(self, security: Security) -> None: ...


# =====================================================================
# Repository Implementation
# =====================================================================


class InMemoryRepository:
    def __init__(self):

        self._storage: dict[str, Security] = {}

    def get(self, symbol: str) -> Security | None:

        return self._storage.get(symbol)

    def save(self, security: Security) -> None:

        self._storage[security.symbol] = security


repository = InMemoryRepository()


# =====================================================================
# Service Layer
# =====================================================================


class SecurityService:
    def __init__(
        self,
        repository: SecurityRepository,
    ):
        self.repository = repository

    def register(
        self,
        request: SecurityRequest,
    ) -> None:

        security = Security(
            symbol=request.symbol,
            company_name=request.company_name,
            sector=request.sector,
            market_cap=request.market_cap,
        )

        self.repository.save(security)

    def find(
        self,
        symbol: str,
    ) -> Security:

        security = self.repository.get(symbol)

        if security is None:
            raise ValueError(f"{symbol} not found.")

        return security


# =====================================================================
# Dependency Injection
# =====================================================================


def get_service() -> SecurityService:

    return SecurityService(repository)


# =====================================================================
# Health Endpoint
# =====================================================================


@app.get("/health")
def health():

    return {
        "status": "healthy",
        "service": "institutional_quant_platform",
    }


# =====================================================================
# API Endpoints
# =====================================================================


@app.post(
    "/api/v1/security",
    response_model=APIResponse,
)
def create_security(
    request: SecurityRequest,
    service: SecurityService = Depends(get_service),
):

    logger.info(
        "Registering %s",
        request.symbol,
    )

    service.register(request)

    return APIResponse(
        success=True,
        message="Security created successfully.",
    )


@app.get(
    "/api/v1/security/{symbol}",
    response_model=SecurityResponse,
)
def get_security(
    symbol: str,
    service: SecurityService = Depends(get_service),
):

    try:
        security = service.find(symbol)

    except ValueError as exc:
        raise HTTPException(
            status_code=404,
            detail=str(exc),
        ) from exc

    return SecurityResponse(
        symbol=security.symbol,
        company_name=security.company_name,
        sector=security.sector,
        market_cap=security.market_cap,
    )


# =====================================================================
# Root Endpoint
# =====================================================================


@app.get("/")
def root():

    return {
        "platform": "Institutional Quant Platform",
        "version": "1.0.0",
        "status": "running",
    }
