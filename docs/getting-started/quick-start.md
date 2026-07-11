# Quick Start

## Institutional Quant Platform

---

# Purpose

This guide provides the fastest path to getting the Institutional Quant Platform up and running. In approximately 10 minutes, you will install the project, verify your environment, launch the dashboard and API, and execute your first analytics workflow.

---

# Prerequisites

Ensure the following software is installed:

| Software | Version |
|-----------|---------|
| Python | 3.12+ |
| Git | Latest |
| Docker | Latest (Optional) |
| VS Code | Latest |
| Make | Latest |

---

# Clone the Repository

```bash
git clone https://github.com/sakshinekkala28/Institutional_Quant_Platform.git

cd Institutional_Quant_Platform
```

---

# Create a Virtual Environment

Linux/macOS

```bash
python3 -m venv .venv

source .venv/bin/activate
```

Windows

```powershell
python -m venv .venv

.venv\Scripts\activate
```

---

# Install Dependencies

```bash
pip install --upgrade pip

pip install -r requirements.txt

pip install -r requirements-dev.txt
```

---

# Install the Project

```bash
pip install -e .
```

---

# Install Git Hooks

```bash
pre-commit install
```

---

# Verify the Development Environment

Run the following command:

```bash
make ci
```

Expected checks include:

- Ruff
- Black
- MyPy
- Pytest
- Coverage
- Security Scans
- Documentation Build

---

# Launch the Dashboard

```bash
streamlit run dashboard/app.py
```

Open:

```text
http://localhost:8501
```

---

# Launch the API

```bash
uvicorn api.main:app --reload
```

Open:

```text
http://localhost:8000/docs
```

---

# Run Your First Analytics Pipeline

Execute the analytics pipeline:

```bash
python -m orchestration.run_pipeline
```

The pipeline will:

1. Load market data
2. Validate datasets
3. Generate factor scores
4. Build the investment universe
5. Calculate alpha scores
6. Construct the portfolio
7. Evaluate portfolio risk
8. Generate rebalance orders
9. Produce reports

---

# Expected Output

After a successful execution, output files will be generated in the data directory.

Typical outputs include:

```text
target_portfolio.csv

rebalance_orders.csv

trade_list.csv

rebalance_summary.csv

rebalance_dashboard.csv

missing_data_report.csv
```

---

# View Results

Review the generated outputs.

Portfolio

```text
data/portfolios/
```

Reports

```text
reports/
```

Dashboard

```text
http://localhost:8501
```

---

# Useful Make Commands

Format code

```bash
make format
```

Lint

```bash
make lint
```

Run tests

```bash
make test
```

Generate coverage

```bash
make coverage
```

Run security checks

```bash
make security
```

Build documentation

```bash
make docs-build
```

Run the full validation pipeline

```bash
make ci
```

---

# Docker Quick Start

Build the image:

```bash
make docker
```

Run the container:

```bash
make docker-run
```

---

# GitHub Codespaces

If using GitHub Codespaces:

1. Open the repository on GitHub.
2. Create a new Codespace.
3. Wait for initialization.
4. The Dev Container will automatically configure the development environment.
5. Run:

```bash
make ci
```

---

# Common Issues

## Missing Dependencies

```bash
pip install -r requirements.txt

pip install -r requirements-dev.txt
```

---

## Formatting Errors

```bash
make format
```

---

## Test Failures

```bash
pytest -v
```

---

## Type Checking Issues

```bash
make typecheck
```

---

## Security Findings

```bash
make security
```

Review the generated reports and address any issues before committing changes.

---

# Next Steps

Continue with the following guides:

1. Development Guide
2. Configuration Guide
3. Architecture Overview
4. API Documentation
5. Analytics Documentation

---

# Related Documents

- Installation Guide
- Development Guide
- Configuration Guide
- Architecture Overview
- Deployment Guide
- Operations Guide

---

End of Document