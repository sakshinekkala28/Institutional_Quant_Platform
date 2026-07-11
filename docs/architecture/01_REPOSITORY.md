# Repository Structure

**Version:** 1.0  
**Status:** APPROVED  
**Owner:** Architecture Team  
**Last Updated:** YYYY-MM-DD

---

# Purpose

This document defines the official repository structure of the **Institutional Quant Platform**.

It establishes architectural boundaries, module responsibilities, dependency rules, and governance principles to ensure a scalable, maintainable, and enterprise-grade codebase.

Every source file belongs to one and only one architectural layer.

No duplicate responsibilities are permitted.

Changes to the repository structure require formal architectural approval.

---

# Repository Layout

```text
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

├── pyproject.toml
├── Makefile
├── README.md
└── LICENSE
```

---

# Architectural Layers

```text
Presentation Layer
──────────────────
dashboard/
api/

        │
        ▼

Application Layer
─────────────────
automation/
orchestration/

        │
        ▼

Domain Layer
────────────
analytics/

        │
        ▼

Infrastructure Layer
────────────────────
core/
config/
data/
deployment/
monitoring/

        │
        ▼

Supporting Assets
─────────────────
tests/
docs/
```

---

# Module Ownership

| Module | Responsibility |
|---------|----------------|
| analytics | Quantitative models and business logic |
| orchestration | Workflow orchestration and pipelines |
| core | Shared framework and infrastructure |
| api | External REST interfaces |
| dashboard | User interface and visualization |
| automation | Scheduled jobs and automation |
| config | Platform configuration |
| data | Persistent storage |
| deployment | Infrastructure and deployment |
| monitoring | Observability and telemetry |
| tests | Verification and quality assurance |
| docs | Documentation |

---

# Repository Rules

The repository follows these architectural principles.

- Every directory shall have a single responsibility.
- No duplicate functionality is permitted.
- No cyclic dependencies are allowed.
- Shared functionality belongs in `core`.
- Business logic belongs in `analytics`.
- Infrastructure concerns remain isolated from business logic.
- Cross-module communication shall occur only through approved interfaces.
- New top-level modules require an approved Architecture Decision Record (ADR).

---

# analytics/

## Purpose

Contains all quantitative, financial, and business calculations.

### Responsibilities

- Factor computation
- Alpha generation
- Signal generation
- Universe selection
- Portfolio optimization
- Risk modelling
- Performance analytics
- Execution analytics

### analytics SHALL

- Perform deterministic calculations
- Validate business logic
- Produce domain models
- Return standardized engine results

### analytics SHALL NOT

- Invoke REST APIs
- Schedule execution
- Execute pipelines
- Publish events
- Access presentation layers
- Manage infrastructure
- Persist storage directly

---

# orchestration/

## Purpose

Coordinates platform execution.

### Contains

- Master Orchestrator
- Pipelines
- Executors
- Dependency Graph
- Scheduler
- Event Bus
- Plugin Manager

### Responsibilities

- Dependency resolution
- Pipeline execution
- Retry policies
- Event publication
- Workflow coordination
- Execution reporting

---

# core/

## Purpose

Shared reusable platform framework.

### Contains

- BaseEngine
- BasePipeline
- BaseRepository
- BaseService
- Validation
- Logging
- Metrics
- Storage Interfaces
- Configuration
- Exceptions
- Serialization
- Caching
- Utilities

### core SHALL NOT

Contain domain-specific business calculations.

---

# api/

## Purpose

Provides external REST interfaces.

### Responsibilities

- Authentication
- Authorization
- Request validation
- Response serialization
- API versioning
- Service invocation

### api SHALL NOT

Import analytics directly.

---

# dashboard/

## Purpose

User interface.

### Responsibilities

- Portfolio Dashboard
- Risk Dashboard
- Analytics Dashboard
- Monitoring Dashboard
- Visualization
- User interaction

### dashboard SHALL

Communicate only through APIs or application services.

---

# automation/

## Purpose

Scheduled platform execution.

### Examples

- Daily rebalance
- Nightly data refresh
- Weekly reports
- Monthly benchmark updates
- Health monitoring
- Scheduled exports

---

# config/

## Purpose

Centralized platform configuration.

### Contains

```text
settings.py
paths.py
logging.py
risk.py
portfolio.py
execution.py
api.py
database.py
```

No hardcoded configuration values shall exist elsewhere.

---

# data/

## Purpose

Persistent storage layer.

### Recommended Layout

```text
raw/
intermediate/
processed/
features/
signals/
portfolios/
executions/
performance/
reports/
logs/
```

### Primary Storage

- DuckDB

### Secondary Storage

- Apache Parquet

### Export Formats

- CSV
- Excel
- JSON

---

# deployment/

## Purpose

Deployment infrastructure.

### Contains

- Docker
- Kubernetes
- Helm
- Terraform
- GitHub Actions
- Environment Configuration

---

# monitoring/

## Purpose

Platform observability.

### Contains

- Prometheus
- Grafana
- OpenTelemetry
- Alert Rules
- Health Checks
- Distributed Tracing
- Metrics Collection

---

# tests/

## Purpose

Repository verification.

### Recommended Layout

```text
tests/

unit/
integration/
performance/
load/
security/
regression/
golden/
```

All production modules should include corresponding automated tests.

---

# docs/

## Purpose

Project documentation.

Contains

- Architecture
- Developer Guides
- API Documentation
- Operations
- Security
- Tutorials
- ADRs
- Reference Documentation

---

# Configuration Files

## pyproject.toml

Central Python project configuration.

---

## Makefile

Developer automation commands.

---

## requirements.txt

Runtime dependencies.

---

## requirements-dev.txt

Development dependencies.

---

## README.md

Repository overview.

---

## LICENSE

Project license.

---

# Dependency Rules

The repository follows strict architectural boundaries.

```text
Dashboard
      │
      ▼
API
      │
      ▼
Application Services
      │
      ▼
Orchestration
      │
      ▼
Analytics
      │
      ▼
Core
      │
      ▼
Data
```

Lower layers shall never depend on higher layers.

---

# Import Rules

| Module | May Import |
|----------|------------|
| analytics | core |
| orchestration | analytics, core |
| automation | orchestration, analytics, core |
| api | orchestration, core |
| dashboard | api |
| monitoring | core |
| tests | All modules |

### Forbidden

- analytics → api
- analytics → dashboard
- analytics → orchestration
- analytics → automation
- dashboard → analytics
- dashboard → orchestration
- core → analytics
- core → api

Any exception requires an approved ADR.

---

# Dependency Matrix

```text
dashboard
      │
      ▼
api
      │
      ▼
automation
      │
      ▼
orchestration
      │
      ▼
analytics
      │
      ▼
core
      │
      ▼
data
```

Direct cross-layer imports are prohibited.

---

# Repository Governance

The repository is governed by the following principles.

- High Cohesion
- Low Coupling
- Clean Architecture
- Domain-Driven Design
- SOLID Principles
- Explicit Dependency Management
- Modular Ownership
- Independent Deployability

---

# Future Growth

New business capabilities belong inside **analytics**.

New workflow capabilities belong inside **orchestration**.

Shared reusable infrastructure belongs inside **core**.

New top-level modules require architectural review and an approved ADR before implementation.

---

# Repository Freeze

The repository structure defined in this document is considered stable.

Changes to:

- Top-level directories
- Dependency rules
- Architectural layers
- Import rules

shall be approved through an **Architecture Decision Record (ADR)** before implementation.

---

# Related Documents

- Architecture Overview
- System Design
- Data Flow
- Deployment Architecture
- CI/CD Architecture
- Security Architecture
- Operations Guide
- Architecture Decision Records (ADR)

---

End of Document