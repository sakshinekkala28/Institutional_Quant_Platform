# Getting Started

Welcome to the **Institutional Quant Platform**.

This guide walks through setting up the platform for local development, running the analytics pipeline, launching the API, and exploring the dashboard.

---

# Prerequisites

Before you begin, ensure the following software is installed.

| Software | Recommended Version |
|----------|---------------------|
| Python | 3.12+ |
| Git | Latest |
| Docker | Latest |
| Make | Latest |
| VS Code (optional) | Latest |

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
python -m venv .venv

source .venv/bin/activate
```

Windows

```powershell
python -m venv .venv

.venv\Scripts\activate
```

---

# Install Dependencies

Runtime dependencies

```bash
pip install -r requirements.txt
```

Development dependencies

```bash
pip install -r requirements-dev.txt
```

Verify installation

```bash
pip check
```

---

# Configure the Environment

Create a local environment file if required.

Example:

```env
APP_ENV=development

LOG_LEVEL=INFO

DATABASE_URL=data/database.duckdb

API_HOST=0.0.0.0

API_PORT=8000
```

Refer to the **Environment Variables** documentation for a complete list of supported configuration options.

---

# Verify the Installation

Run:

```bash
python --version

pytest
```

All tests should complete successfully before continuing.

---

# Run the Analytics Pipeline

Execute the complete analytics workflow:

```bash
python orchestration/run_pipeline.py
```

Typical stages include:

- Data Loading
- Data Validation
- Alpha Generation
- Portfolio Construction
- Risk Analysis
- Report Generation

---

# Start the REST API

Development mode:

```bash
uvicorn api.main:app --reload
```

The API will typically be available at:

```
http://localhost:8000
```

Interactive API documentation:

```
http://localhost:8000/docs
```

---

# Launch the Dashboard

Start the Streamlit dashboard:

```bash
streamlit run streamlit_app/Home.py
```

The dashboard provides:

- Portfolio Analytics
- Performance Reporting
- Risk Monitoring
- Execution Analysis
- Market Insights

---

# Run Code Quality Checks

Format code:

```bash
ruff format .
```

Lint:

```bash
ruff check .
```

Type checking:

```bash
mypy .
```

---

# Run Tests

Run all tests:

```bash
pytest
```

Run specific test suites:

```bash
pytest tests/unit

pytest tests/integration

pytest tests/performance
```

Generate coverage:

```bash
pytest --cov
```

---

# Build Documentation

Serve documentation locally:

```bash
mkdocs serve
```

Build the documentation site:

```bash
mkdocs build
```

---

# Repository Overview

```text
analytics/
alpha/
api/
dashboard/
data/
deployment/
docs/
execution/
monitoring/
portfolio/
reporting/
research/
risk/
tests/
```

---

# Recommended Development Workflow

1. Pull the latest changes.
2. Create a feature branch.
3. Implement changes.
4. Run formatting and linting.
5. Execute the test suite.
6. Update documentation.
7. Submit a pull request.

---

# Troubleshooting

### Module Import Errors

Verify that:

- The virtual environment is active.
- Dependencies are installed.
- `PYTHONPATH` is configured correctly.

---

### API Does Not Start

Check:

- Port availability
- Configuration values
- Dependency installation
- Startup logs

---

### Dashboard Does Not Load

Verify:

- Streamlit is installed.
- The correct application entry point is used.
- Required data files are available.

---

### Tests Fail

Review:

- Python version
- Dependency versions
- Environment variables
- Test fixtures
- Generated artifacts

---

# Next Steps

After completing the setup, continue with the following tutorials:

1. Build Your First Strategy
2. Create an Alpha Model
3. Create a Risk Model
4. Deploy the Platform

---

# Related Documentation

- CLI Reference
- Configuration Reference
- Environment Variables
- Security Overview
- Deployment Guide
- API Documentation
- Tutorials