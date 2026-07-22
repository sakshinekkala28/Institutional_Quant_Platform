# Command Line Interface (CLI) Reference

The Institutional Quant Platform provides a collection of command-line utilities for running analytics, portfolio construction, risk analysis, reporting, monitoring, and infrastructure tasks.

---

# Prerequisites

Before running any commands, ensure that:

- Python 3.12 or later is installed.
- Project dependencies have been installed.
- The virtual environment is activated.
- Required environment variables are configured.

---

# Basic Usage

General syntax:

```bash
python <module> [OPTIONS]
```

Example:

```bash
python orchestration/run_pipeline.py
```

---

# Analytics Commands

## Run Complete Analytics Pipeline

```bash
python orchestration/run_pipeline.py
```

Runs the complete institutional analytics workflow including:

- Data ingestion
- Validation
- Factor calculation
- Alpha generation
- Portfolio construction
- Risk analysis
- Report generation

---

## Generate Alpha Signals

```bash
python analytics/live/live_signal_engine.py
```

Produces the latest investment signals for the configured investment universe.

---

## Run Market Regime Detection

```bash
python analytics/live/live_regime_engine.py
```

Determines the current market regime used by downstream portfolio and execution engines.

---

# Portfolio Commands

## Construct Portfolio

```bash
python analytics/live/live_portfolio_engine.py
```

Builds the target portfolio using the configured optimization model.

---

## Generate Rebalance Orders

```bash
python analytics/live/live_rebalance_engine.py
```

Creates portfolio rebalance instructions based on the latest target weights.

---

# Risk Commands

## Calculate Portfolio Risk

```bash
python analytics/live/live_risk_engine.py
```

Computes portfolio-level risk metrics including volatility, Value at Risk (VaR), Expected Shortfall (ES), and exposure analysis.

---

## Run Stress Tests

```bash
python analytics/live/live_stress_testing.py
```

Evaluates portfolio performance under predefined stress scenarios.

---

# Execution Commands

## Generate Trade List

```bash
python execution/trade_generator.py
```

Creates executable trade instructions from portfolio rebalance outputs.

---

## Transaction Cost Analysis

```bash
python execution/transaction_cost_analysis.py
```

Calculates estimated trading costs, slippage, and execution impact.

---

# Reporting Commands

## Generate Reports

```bash
python reporting/report_generator.py
```

Produces portfolio, risk, and performance reports.

---

## Export Dashboard Data

```bash
python reporting/dashboard_export.py
```

Exports data used by the Streamlit dashboard.

---

# API Commands

## Start FastAPI Server

Development mode:

```bash
uvicorn api.main:app --reload
```

Production mode:

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

---

# Dashboard Commands

## Launch Streamlit Dashboard

```bash
streamlit run streamlit_app/Home.py
```

Starts the interactive dashboard for portfolio analytics, risk monitoring, and reporting.

---

# Testing Commands

Run all tests:

```bash
pytest
```

Run unit tests:

```bash
pytest tests/unit
```

Run integration tests:

```bash
pytest tests/integration
```

Run performance tests:

```bash
pytest tests/performance
```

Generate coverage report:

```bash
pytest --cov
```

---

# Code Quality

Format code:

```bash
ruff format .
```

Lint project:

```bash
ruff check .
```

Type checking:

```bash
mypy .
```

---

# Docker Commands

Build container:

```bash
docker build -t institutional_quant_platform .
```

Run container:

```bash
docker run -p 8000:8000 institutional_quant_platform
```

---

# Documentation

Serve locally:

```bash
mkdocs serve
```

Build documentation:

```bash
mkdocs build
```

---

# Environment Information

Display Python version:

```bash
python --version
```

Installed packages:

```bash
pip list
```

Verify dependencies:

```bash
pip check
```

---

# Common Make Targets

If a Makefile is available:

```bash
make format
make lint
make typecheck
make test
make coverage
make security
make docs
make docker
make docker-run
```

---

# Exit Codes

| Exit Code | Description |
|-----------|-------------|
| 0 | Command completed successfully |
| 1 | General execution error |
| 2 | Invalid command-line arguments |
| 126 | Command found but not executable |
| 127 | Command not found |

---

# Best Practices

- Activate the project's virtual environment before executing commands.
- Keep dependencies up to date.
- Validate configuration before running production pipelines.
- Review logs for warnings or errors after execution.
- Run unit and integration tests before committing changes.
- Use version-controlled configuration files for reproducible environments.

---

# Related Documentation

- Getting Started
- Configuration Reference
- Environment Variables
- API Documentation
- Deployment Guide
- Tutorials