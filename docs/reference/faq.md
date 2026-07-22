# Frequently Asked Questions (FAQ)

This document answers common questions about the **Institutional Quant Platform**, including installation, configuration, development, deployment, and troubleshooting.

---

# General

## What is the Institutional Quant Platform?

The Institutional Quant Platform is an enterprise-grade quantitative investment platform designed to support the complete investment lifecycle, including:

- Market Data Processing
- Alpha Research
- Portfolio Construction
- Risk Analytics
- Execution Management
- Performance Reporting
- Infrastructure Automation

---

## Who is this platform intended for?

The platform is designed for:

- Quantitative Researchers
- Portfolio Managers
- Data Scientists
- Financial Engineers
- Software Engineers
- DevOps Engineers
- Students interested in quantitative finance

---

## Which operating systems are supported?

The platform supports:

- Linux (Recommended)
- macOS
- Windows (WSL recommended)

---

## What Python version is required?

Python **3.12 or later** is recommended.

---

# Installation

## How do I install project dependencies?

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

---

## Should I use a virtual environment?

Yes.

Example:

```bash
python -m venv .venv
source .venv/bin/activate
```

Windows:

```powershell
.venv\Scripts\activate
```

---

## How do I verify my installation?

Run:

```bash
python --version
pytest
```

If all tests pass without errors, the installation is successful.

---

# Development

## How do I run the analytics pipeline?

```bash
python orchestration/run_pipeline.py
```

---

## How do I start the API?

```bash
uvicorn api.main:app --reload
```

---

## How do I launch the Streamlit dashboard?

```bash
streamlit run streamlit_app/Home.py
```

---

## How do I format the code?

```bash
ruff format .
```

---

## How do I lint the project?

```bash
ruff check .
```

---

## How do I run the test suite?

```bash
pytest
```

---

## How do I generate documentation?

```bash
mkdocs serve
```

or

```bash
mkdocs build
```

---

# Configuration

## Where is configuration stored?

Configuration is managed using:

- Environment variables
- Configuration files
- Infrastructure variables
- Runtime settings

Refer to the **Configuration Reference** and **Environment Variables** documentation for details.

---

## Should secrets be committed to Git?

**No.**

Secrets, credentials, API keys, and tokens should never be committed to version control.

Use environment variables or a secure secrets manager.

---

# Portfolio

## Which portfolio optimization methods are available?

The platform supports:

- Equal Weight
- Market Capitalization
- Factor Weighting
- Risk Parity
- Minimum Variance
- Hierarchical Risk Parity
- Black-Litterman

---

## Can I implement my own optimizer?

Yes.

Custom portfolio optimizers can be added by extending the portfolio module and registering the new implementation.

---

# Risk

## Which risk metrics are supported?

Examples include:

- Value at Risk (VaR)
- Expected Shortfall (ES)
- Volatility
- Beta
- Tracking Error
- Maximum Drawdown
- Factor Exposure
- Sector Exposure

---

## Can I build a custom risk model?

Yes.

The platform is modular and allows additional risk models to be implemented without modifying the existing framework.

---

# Data

## Which market data providers are supported?

The platform is designed to integrate with multiple providers depending on deployment requirements.

Examples include:

- Exchange APIs
- Institutional data vendors
- Internal datasets
- CSV and Parquet files
- SQL databases

---

## Does the platform support live market data?

Yes.

Live data support depends on the configured provider and available integrations.

---

# Deployment

## Is Docker supported?

Yes.

Example:

```bash
docker build -t institutional_quant_platform .
```

---

## Is Kubernetes supported?

Yes.

Deployment manifests and Helm charts are provided for container orchestration.

---

## Can the platform be deployed to the cloud?

Yes.

Typical deployment targets include:

- AWS
- Azure
- Google Cloud Platform
- Private Kubernetes clusters

---

# Security

## How are secrets managed?

Recommended approaches include:

- Environment variables
- Cloud secrets managers
- Kubernetes Secrets
- External secret management solutions

---

## How do I report a security vulnerability?

Please follow the responsible disclosure process described in **SECURITY.md**.

Do not create public GitHub issues for confidential vulnerabilities.

---

# Troubleshooting

## The application cannot find a module.

Possible causes:

- Virtual environment not activated
- Missing dependencies
- Incorrect `PYTHONPATH`

Run:

```bash
pip install -r requirements.txt
```

---

## The dashboard will not start.

Verify:

- Streamlit is installed.
- Dependencies are installed.
- Required configuration is available.
- The application entry point is correct.

---

## Tests are failing.

Check:

- Python version
- Dependency versions
- Environment variables
- Test data availability

---

## Where can I get help?

Consult:

- Project documentation
- API Reference
- CLI Reference
- Configuration Guide
- Security Documentation

If the issue persists, open a GitHub issue (for non-security-related problems) with:

- Error message
- Environment details
- Steps to reproduce
- Relevant logs

---

# Related Documentation

- Getting Started
- CLI Reference
- Configuration Reference
- Environment Variables
- API Documentation
- Security Guide
- Tutorials