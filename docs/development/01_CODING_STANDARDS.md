# Coding Standards

> Institutional Quant Platform

---

# Document Information

| Field | Value |
|-------|-------|
| Document | Coding Standards |
| Version | 1.0.0 |
| Status | Approved |
| Owner | Platform Architecture |
| Classification | Internal |
| Last Updated | YYYY-MM-DD |
| Next Review | Quarterly |

---

# Purpose

This document defines the coding standards for the Institutional
Quant Platform.

These standards ensure

- Consistency
- Readability
- Maintainability
- Testability
- Scalability
- Production readiness

All production code shall comply with this document.

---

# Objectives

This guide standardizes

- Naming
- File organization
- Module organization
- Imports
- Classes
- Functions
- Exceptions
- Logging
- Type hints
- Documentation
- Formatting

---

# General Principles

Code shall be

- Simple
- Explicit
- Readable
- Modular
- Testable
- Reusable
- Deterministic

Avoid unnecessary complexity.

---

# Python Version

Supported version

```
Python 3.12+
```

New language features may be adopted after team review.

---

# Formatting

Formatting shall follow

PEP 8

Maximum line length

```
88
```

Formatting tool

```
Black
```

Import sorting

```
isort
```

Linting

```
Ruff
```

Static typing

```
mypy
```

---

# File Naming

Files use

```
snake_case.py
```

Examples

```
portfolio_engine.py

risk_engine.py

master_orchestrator.py
```

Avoid abbreviations.

---

# Module Naming

Modules describe their responsibility.

Examples

```
execution

portfolio

analytics

risk

reporting
```

Avoid

```
utils2

misc

helpers

common2
```

---

# Class Naming

Classes use

```
PascalCase
```

Examples

```
PortfolioEngine

RiskPipeline

MasterOrchestrator

SignalRepository
```

---

# Function Naming

Functions use

```
snake_case
```

Examples

```
load_data()

run_pipeline()

calculate_factor()

save_results()
```

Function names should start with verbs.

---

# Variable Naming

Variables use

```
snake_case
```

Examples

```
portfolio

security_master

daily_returns

covariance_matrix
```

Avoid

```
x

temp

data2

var
```

---

# Constants

Constants use

```
UPPER_SNAKE_CASE
```

Example

```
DEFAULT_TIMEOUT

MAX_RETRIES

OUTPUT_DIRECTORY
```

---

# Enumerations

Use Enum for fixed values.

Example

```
EngineStatus

PipelineStatus

ExecutionMode
```

Never use string literals throughout the codebase for enumerated values.

---

# Imports

Import order

```
Standard Library

↓

Third Party

↓

Project Modules
```

Example

```python
from pathlib import Path

import pandas as pd

from analytics.portfolio.portfolio_engine import (
    PortfolioEngine,
)
```

Avoid wildcard imports.

```
from x import *
```

---

# Type Hints

All public functions shall include type hints.

Example

```python
def load_data(
    path: Path,
) -> pd.DataFrame:
```

Avoid untyped public interfaces.

---

# Docstrings

Every public

- module
- class
- function

shall include a docstring.

Use Google-style or reStructuredText consistently.

Example

```python
def calculate_returns(
    prices: pd.Series,
) -> pd.Series:
    """
    Calculate simple daily returns.

    Parameters
    ----------
    prices
        Daily closing prices.

    Returns
    -------
    pd.Series
        Daily percentage returns.
    """
```

---

# Classes

Each class shall have one responsibility.

Avoid

- God classes
- Multiple unrelated responsibilities

Prefer

```
Small

Focused

Reusable
```

---

# Functions

Functions shall

- Perform one task
- Return predictable results
- Be independently testable

Target size

```
10–40 lines
```

Extract helper functions instead of creating excessively long methods.

---

# Exceptions

Raise specific exceptions.

Example

```
ValueError

FileNotFoundError

ConfigurationError

ValidationError
```

Avoid

```python
except Exception:
    pass
```

Never silently ignore exceptions.

---

# Logging

Use

```
logging
```

Never use

```
print()
```

outside

- tutorials
- debugging
- CLI entry points

Every production module shall obtain a module-level logger.

Example

```python
logger.info("Pipeline started.")
```

---

# Configuration

Never hardcode

- Paths
- Secrets
- URLs
- Credentials
- Tokens

Load configuration from

- Environment variables
- Configuration files
- Secret managers

---

# Dependency Injection

Prefer dependency injection.

Example

```python
PortfolioEngine(
    repository=repository,
)
```

Avoid creating dependencies inside constructors when they can be provided externally.

---

# Repository Pattern

Analytics shall never access storage directly.

Correct

```
Analytics

↓

Repository

↓

Storage
```

Incorrect

```
Analytics

↓

DuckDB
```

---

# Pipeline Rules

Pipelines

- Coordinate engines
- Do not perform calculations

Engines

- Perform calculations
- Return EngineResult

---

# Comments

Write comments explaining

```
WHY
```

Avoid comments explaining

```
WHAT
```

The code should make the "what" obvious.

---

# Magic Numbers

Avoid

```python
if x > 17:
```

Use

```python
MAX_POSITION_SIZE = 17
```

---

# Testing

Every production module shall include

- Unit tests
- Integration tests where applicable

Critical modules shall include performance tests.

---

# Performance

Prefer

- Vectorization
- Batch processing
- Lazy loading
- Efficient algorithms

Avoid unnecessary loops over large datasets.

---

# Security

Never

- Commit secrets
- Hardcode passwords
- Log sensitive information

Validate all external input.

---

# Anti-Patterns

Avoid

- Circular dependencies
- Duplicate code
- Global mutable state
- Hardcoded configuration
- Deep inheritance hierarchies
- Large monolithic classes
- Tight coupling

---

# Code Review Checklist

Reviewers shall verify

- Architecture compliance
- Naming
- Formatting
- Type hints
- Documentation
- Tests
- Logging
- Error handling
- Security

---

# Related Documents

- 00_DEVELOPMENT_GUIDE.md
- 02_ENGINE_GUIDE.md
- 03_PIPELINE_GUIDE.md
- 04_TESTING_GUIDE.md
- 05_LOGGING_GUIDE.md
- 06_ERROR_HANDLING.md
- ../architecture/05_ENGINES.md

---

# Revision History

| Version | Date | Description |
|----------|------|-------------|
| 1.0.0 | YYYY-MM-DD | Initial coding standards |

---

**End of Document**