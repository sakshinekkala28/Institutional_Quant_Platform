# Engine Architecture

Version: 1.0

Status: APPROVED

---

# Purpose

This document defines the official engine architecture of the
Institutional Quant Platform.

An engine is the smallest executable business component in the
platform.

Engines perform calculations.

Engines never coordinate execution.

---

# Definition

An Engine is an independent computational unit responsible for
one business capability.

Examples

• Factor Engine

• Risk Engine

• Portfolio Engine

• Execution Engine

• Benchmark Engine

Each engine performs one responsibility only.

---

# Design Principles

Every engine shall

• have one responsibility

• be deterministic

• be independently testable

• validate inputs

• validate outputs

• return EngineResult

Every engine shall NOT

• invoke pipelines

• invoke orchestrators

• invoke APIs

• communicate with dashboards

• schedule execution

• invoke other engines directly

---

# Engine Hierarchy

Analytics Engine

↓

BaseEngine

↓

Business Engine

↓

EngineResult

---

# Base Engine

Every engine shall inherit

BaseEngine

BaseEngine provides

• execution lifecycle

• logging

• validation

• metrics

• timing

• error handling

• persistence hooks

Business engines implement only domain logic.

---

# Engine Structure

Every engine follows the same structure.

Initialize

↓

Validate Inputs

↓

Load Inputs

↓

Business Computation

↓

Validate Outputs

↓

Persist Outputs

↓

Collect Metrics

↓

Return EngineResult

---

# Standard Layout

Every engine should contain

Configuration

Input Loader

Validation

Business Logic

Output Validation

Persistence

Metrics

Result Builder

---

# Engine Contract

Every engine exposes

main()

or

run()

Example

def main() -> EngineResult

or

class RiskEngine(BaseEngine)

    def run(self) -> EngineResult

No other public execution methods.

---

# Engine Result

Every engine returns

EngineResult

Contains

Status

Duration

Records Processed

Outputs

Warnings

Errors

Metadata

No engine returns

DataFrame

tuple

dict

bool

list

---

# Input Rules

Allowed inputs

Configuration

Repository

DuckDB

Parquet

CSV (import/export)

Execution Context

Forbidden

Hardcoded paths

Interactive user input

Global mutable state

---

# Output Rules

Preferred

DuckDB

Parquet

Optional

CSV export

All outputs are registered inside EngineResult.

---

# Logging

Every engine logs

Started

Configuration Loaded

Inputs Loaded

Validation Complete

Computation Complete

Outputs Persisted

Completed

Failed

Use

logger.debug()

logger.info()

logger.warning()

logger.error()

Never use

print()

---

# Validation

Before computation

Validate

Schema

Required columns

Data types

Configuration

Business rules

After computation

Validate

Schema

Missing values

Duplicates

Output consistency

---

# Error Handling

Recoverable failures

Return

EngineResult(status=FAILED)

Unexpected failures

Log exception

Raise exception

Silent failures are prohibited.

---

# Metrics

Every engine records

Execution Time

Rows Read

Rows Written

CPU Time

Memory Usage

Warnings

Errors

Retry Count

Cache Hits

Metrics become part of EngineResult.

---

# Dependencies

Allowed

Engine

↓

Core

↓

Repository

Forbidden

Engine

↓

Pipeline

Engine

↓

Master Orchestrator

Engine

↓

Another Engine

Engine communication occurs only through pipelines.

---

# Configuration

Configuration is injected.

Never hardcode

Paths

Credentials

Dates

Market parameters

---

# Persistence

Persistence is delegated to repository classes.

Engines never manipulate storage implementations directly.

Preferred

Repository

↓

DuckDB

↓

Parquet

↓

CSV Export

---

# Testing

Every engine requires

Unit Tests

Input Validation Tests

Output Validation Tests

Performance Tests

Failure Tests

---

# Naming Convention

Examples

FactorEngine

RiskEngine

PortfolioEngine

ExecutionEngine

BenchmarkEngine

CapacityEngine

SignalEngine

RegimeEngine

Method names

run()

main()

validate_inputs()

validate_outputs()

persist_outputs()

build_result()

---

# Future Engines

Future engines shall inherit BaseEngine.

No custom execution lifecycle is permitted.

---

# Architecture Freeze

The engine contract defined in this document is mandatory for
all analytics engines.

Changes require an Architecture Decision Record (ADR).

---

# Related Documents

00_ARCHITECTURE.md

02_ANALYTICS.md

03_ORCHESTRATION.md

04_PIPELINES.md

06_DATA.md

07_EXECUTION.md

---

End of Document