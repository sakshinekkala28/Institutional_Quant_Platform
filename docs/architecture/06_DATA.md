# Data Architecture

Version: 1.0

Status: APPROVED

---

# Purpose

This document defines the official data architecture of the
Institutional Quant Platform.

The data layer is responsible for storing, organizing,
validating, and providing access to all datasets used by the
platform.

The data layer SHALL NOT contain business logic.

---

# Objectives

The data architecture shall provide

• reliable storage

• reproducible datasets

• versioned outputs

• schema validation

• high-performance access

• auditability

---

# Data Flow

External Data Sources

↓

Raw Data

↓

Validated Data

↓

Analytics

↓

Pipeline Outputs

↓

Reports

---

# Data Directory

data/

├── raw/

├── reference/

├── processed/

├── factors/

├── signals/

├── regime/

├── risk/

├── portfolios/

├── execution/

├── performance/

├── benchmark/

├── research/

├── live/

├── reports/

├── logs/

└── cache/

---

# Directory Responsibilities

## raw/

Contains original source files.

Examples

• NSE

• Yahoo Finance

• Vendor data

Files are immutable.

---

## reference/

Contains slowly changing data.

Examples

• Security Master

• Sector Mapping

• Exchange Calendar

• Industry Classification

---

## processed/

Validated datasets ready for analytics.

Examples

• Clean Prices

• Returns

• Metadata

---

## factors/

Stores factor datasets.

Examples

• Value

• Momentum

• Quality

• Size

• Low Volatility

---

## signals/

Stores generated signals.

Examples

• Buy

• Sell

• Watch

• Alpha Scores

---

## regime/

Stores market regime outputs.

Examples

• Bull

• Bear

• Sideways

---

## risk/

Stores risk model outputs.

Examples

• Covariance

• Beta

• Exposures

• Volatility

---

## portfolios/

Stores portfolios.

Examples

• Target Portfolio

• Current Portfolio

• Optimized Portfolio

---

## execution/

Stores execution outputs.

Examples

• Orders

• Trades

• Transaction Costs

---

## performance/

Stores attribution.

Examples

• Brinson

• Performance Attribution

• Security Attribution

---

## benchmark/

Stores benchmark datasets.

---

## research/

Stores experimental outputs.

Research outputs SHALL NOT be used by production pipelines
without approval.

---

## live/

Stores live trading outputs.

---

## reports/

Stores exported reports.

Examples

CSV

Excel

PDF

HTML

---

## logs/

Stores execution logs.

---

## cache/

Stores temporary datasets.

Cache may be deleted without affecting correctness.

---

# Storage Strategy

Preferred storage

DuckDB

Columnar storage

Parquet

Export

CSV

Reports

Excel

PDF

Storage technology may evolve without changing the logical
directory structure.

---

# Repository Layer

Analytics engines SHALL access data through repository classes.

Example

CSVRepository

DuckDBRepository

ParquetRepository

No engine shall directly manage storage implementations.

---

# Data Lifecycle

Acquire

↓

Validate

↓

Clean

↓

Transform

↓

Store

↓

Consume

↓

Archive

---

# Naming Convention

Examples

security_master.parquet

factor_master.parquet

signal_master.parquet

portfolio_history.parquet

risk_dashboard.parquet

Use lowercase.

Use underscores.

Avoid spaces.

---

# Validation

Every dataset shall validate

Schema

Data Types

Primary Keys

Missing Values

Duplicates

Date Ranges

Business Rules

---

# Versioning

Processed datasets should be reproducible.

Major structural changes require version updates.

Examples

factor_master_v2.parquet

risk_model_v3.parquet

---

# Retention

Raw Data

Retain indefinitely where practical.

Cache

Temporary.

Reports

Retention according to operational requirements.

Logs

Retention according to monitoring policy.

---

# Security

Sensitive configuration

Credentials

API Keys

Tokens

shall never be stored under data/.

---

# Dependency Rules

Allowed

Analytics

↓

Repository

↓

Data

Forbidden

API

↓

Raw Data

Dashboard

↓

Raw Data

All access shall occur through services or repositories.

---

# Testing

Validate

Schemas

Integrity

Performance

Reproducibility

---

# Future Extensions

Possible future domains

alternative_data/

macro/

news/

esg/

satellite/

options/

These follow the same data lifecycle.

---

# Architecture Freeze

The logical data architecture is stable.

Physical storage implementations may evolve without changing
the directory structure.

---

# Related Documents

00_ARCHITECTURE.md

02_ANALYTICS.md

05_ENGINES.md

07_EXECUTION.md

12_DEPLOYMENT.md

---

End of Document