# Repository Structure

Version: 1.0

Status: APPROVED

---

# Purpose

This document defines the official repository structure of the
Institutional Quant Platform.

Every source file must belong to one and only one architectural layer.

No duplicate responsibilities are permitted.

---

# Repository Layout

Institutional_Quant_Platform/

├── analytics/

├── orchestration/

├── core/

├── api/

├── dashboard/

├── automation/

├── config/

├── data/

├── deployment/

├── monitoring/

├── tests/

├── docs/

---

# analytics/

Purpose

Contains all financial, quantitative and business calculations.

Examples

• Factor computation

• Signal generation

• Risk modelling

• Portfolio optimization

• Execution analysis

Analytics SHALL NOT

• schedule execution

• invoke APIs

• execute pipelines

• manage storage

• publish events

Analytics SHALL

• perform calculations

• validate results

• return EngineResult

---

# orchestration/

Purpose

Coordinates platform execution.

Contains

• Master Orchestrator

• Pipelines

• Executors

• Dependency Graph

• Events

• Plugins

• Scheduler

Responsibilities

• execution order

• dependency resolution

• retries

• event publishing

• execution reporting

---

# core/

Purpose

Shared reusable framework.

Contains

BaseEngine

BasePipeline

BaseRepository

BaseService

Validation

Logging

Metrics

Storage

Configuration

Caching

Core SHALL NOT

contain business calculations.

---

# api/

Purpose

REST interface.

Responsibilities

• Authentication

• Authorization

• Request validation

• Service invocation

API SHALL NOT

import analytics directly.

---

# dashboard/

Purpose

User Interface.

Responsibilities

• Visualization

• Reporting

• User interaction

Dashboard SHALL communicate only through API/services.

---

# automation/

Purpose

Scheduled execution.

Examples

Daily rebalance

Nightly data refresh

Monthly benchmark update

---

# config/

Purpose

Global configuration.

Contains

settings.py

paths.py

logging.py

risk.py

portfolio.py

execution.py

No hardcoded constants elsewhere.

---

# data/

Purpose

Persistent storage.

Recommended layout

raw/

processed/

factor/

signal/

portfolio/

execution/

performance/

reports/

logs/

Primary storage

DuckDB

Secondary storage

Parquet

Exports

CSV

---

# deployment/

Purpose

Deployment artefacts.

Docker

Kubernetes

Terraform

GitHub Actions

---

# monitoring/

Purpose

Operational monitoring.

Prometheus

Grafana

OpenTelemetry

Alert rules

Health checks

---

# tests/

Purpose

Repository verification.

Recommended layout

unit/

integration/

performance/

load/

regression/

golden/

---

# docs/

Purpose

Architecture documentation.

Developer guides.

Operational guides.

Architecture Decision Records.

---

# Dependency Rules

Allowed

API

↓

Services

↓

Master Orchestrator

↓

Pipelines

↓

Analytics

↓

Core

Forbidden

Analytics

↓

API

Dashboard

↓

Analytics

Analytics

↓

Pipelines

Analytics

↓

Orchestrator

---

# Import Rules

Allowed

analytics

imports

core

Allowed

orchestration

imports

analytics

Allowed

api

imports

services

Forbidden

analytics

imports

dashboard

Forbidden

analytics

imports

api

Forbidden

analytics

imports

orchestration

---

# Future Growth

New business capabilities belong inside analytics.

New orchestration capabilities belong inside orchestration.

Shared reusable utilities belong inside core.

---

# Repository Freeze

The repository structure defined in this document is considered stable.

New top-level folders require an Architecture Decision Record (ADR).

---

End of Document