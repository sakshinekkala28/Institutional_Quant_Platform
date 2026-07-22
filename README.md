# Institutional Quant Platform

<div align="center">

# Enterprise-Grade Quantitative Investment Platform

**Portfolio Construction • Alpha Research • Risk Analytics • Execution • Market Data • Monitoring**

![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![CI](https://github.com/sakshinekkala28/Institutional_Quant_Platform/actions/workflows/ci.yml/badge.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)
![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-326CE5?logo=kubernetes&logoColor=white)
![Terraform](https://img.shields.io/badge/Terraform-IaC-7B42BC?logo=terraform&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?logo=fastapi&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)
![DuckDB](https://img.shields.io/badge/DuckDB-FFF000?logo=duckdb&logoColor=black)

*A cloud-native institutional investment platform for quantitative research, portfolio construction, risk management, execution analytics, and enterprise deployment.*

</div>

---

# Overview

Institutional Quant Platform is a modular, enterprise-grade quantitative investment platform built for institutional portfolio managers, quantitative researchers, and financial engineering teams.

The platform supports the complete investment lifecycle, from market data ingestion through alpha generation, portfolio optimization, risk analysis, execution simulation, reporting, monitoring, and cloud-native deployment.

Core capabilities include:

- Portfolio Construction
- Alpha Research
- Factor Investing
- Risk Analytics
- Execution Management
- Performance Attribution
- Market Regime Detection
- Data Engineering
- Infrastructure Automation
- Enterprise Monitoring

---

# System Architecture

```text
                          +----------------------+
                          | Market Data Sources  |
                          +----------+-----------+
                                     |
                                     v
                    +-------------------------------+
                    |      Data Engineering         |
                    | Cleaning • Validation • ETL  |
                    +---------------+---------------+
                                    |
                                    v
                    +-------------------------------+
                    |      Alpha Research           |
                    | Factors • Ranking • Signals   |
                    +---------------+---------------+
                                    |
                                    v
                    +-------------------------------+
                    |    Portfolio Construction     |
                    | Optimization • Constraints    |
                    +---------------+---------------+
                                    |
                                    v
                    +-------------------------------+
                    |        Risk Engine            |
                    | VaR • ES • Exposure • Stress  |
                    +---------------+---------------+
                                    |
                                    v
                    +-------------------------------+
                    |      Execution Engine         |
                    | Orders • Slippage • TCA       |
                    +---------------+---------------+
                                    |
                    +---------------+---------------+
                    |                               |
                    v                               v
            +---------------+             +----------------+
            | REST API      |             | Streamlit UI   |
            +---------------+             +----------------+
                    |                               |
                    +---------------+---------------+
                                    |
                                    v
                          Monitoring & Reporting
```

---

# Key Features

## Analytics

- Alpha Models
- Factor Models
- Universe Builder
- Market Regime Detection
- Ranking Engine
- Security Selection
- Capacity Analysis

## Portfolio

- Equal Weight
- Market Cap Weighting
- Factor Weighting
- Risk Parity
- Minimum Variance
- Black-Litterman
- Hierarchical Risk Parity
- Portfolio Constraints
- Transaction Cost Modelling
- Portfolio Rebalancing

## Risk

- Value at Risk (VaR)
- Expected Shortfall
- Tracking Error
- Stress Testing
- Scenario Analysis
- Factor Exposure
- Sector Exposure
- Beta Analytics
- Performance Attribution

## Execution

- Order Management
- Trade Generation
- Execution Analytics
- Transaction Cost Analysis
- Slippage Modelling
- Capacity Analysis

## Dashboard

- Streamlit Dashboard
- Portfolio Analytics
- Risk Dashboard
- Performance Dashboard
- Market Dashboard

## Infrastructure

- Docker
- Kubernetes
- Helm
- Terraform
- GitHub Actions
- Prometheus
- Grafana

---

# Platform Modules

| Module | Description |
|----------|------------|
| Analytics | Alpha generation, factors, rankings |
| Alpha | Signal generation and research |
| Portfolio | Portfolio optimization and construction |
| Risk | Risk analytics and stress testing |
| Execution | Trade generation and execution modelling |
| Reporting | Portfolio and risk reports |
| Dashboard | Interactive Streamlit dashboard |
| API | FastAPI REST services |
| Monitoring | Metrics, logging and alerting |
| Infrastructure | Docker, Kubernetes and Terraform |

---

# Repository Structure

```text
Institutional_Quant_Platform/

├── alpha/
├── analytics/
├── api/
├── dashboard/
├── data/
├── deployment/
├── docs/
├── execution/
├── infrastructure/
├── monitoring/
├── orchestration/
├── portfolio/
├── reporting/
├── research/
├── risk/
├── services/
├── streamlit_app/
├── telemetry/
├── tests/
└── utils/
```

---

# Technology Stack

| Category | Technology |
|-----------|------------|
| Language | Python 3.12 |
| API | FastAPI |
| Dashboard | Streamlit |
| Database | DuckDB |
| Analytics | NumPy, Pandas, Polars |
| Optimization | SciPy |
| Machine Learning | Scikit-Learn |
| Visualization | Plotly |
| Infrastructure | Docker, Kubernetes, Helm, Terraform |
| Monitoring | Prometheus, Grafana |
| CI/CD | GitHub Actions |
| Documentation | MkDocs Material |

---

# Quick Start

Clone the repository

```bash
git clone https://github.com/sakshinekkala28/Institutional_Quant_Platform.git

cd Institutional_Quant_Platform
```

Create a virtual environment

```bash
python -m venv .venv
```

Activate

Linux/macOS

```bash
source .venv/bin/activate
```

Windows

```powershell
.venv\Scripts\activate
```

Install dependencies

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

---

# Running the Platform

## Analytics Pipeline

```bash
python orchestration/run_pipeline.py
```

## REST API

```bash
uvicorn api.main:app --reload
```

## Dashboard

```bash
streamlit run streamlit_app/Home.py
```

---

# API Endpoints

| Endpoint | Description |
|-----------|-------------|
| `/health` | Health Check |
| `/metrics` | Prometheus Metrics |
| `/version` | Platform Version |
| `/portfolio` | Portfolio Services |
| `/risk` | Risk Analytics |
| `/execution` | Execution Analytics |

---

# Development

Formatting

```bash
make format
```

Linting

```bash
make lint
```

Type Checking

```bash
make typecheck
```

Testing

```bash
make test
```

Coverage

```bash
make coverage
```

Security

```bash
make security
```

Documentation

```bash
make docs
```

---

# Docker

Build

```bash
make docker
```

Run

```bash
make docker-run
```

---

# Documentation

Serve locally

```bash
mkdocs serve
```

Build documentation

```bash
mkdocs build
```

Documentation includes:

- Architecture
- API
- Deployment
- Monitoring
- Tutorials
- Reference
- Development Guides

---

# CI/CD

Automated workflows include

- Continuous Integration
- Unit Testing
- Integration Testing
- Docker Image Build
- Helm Packaging
- Kubernetes Validation
- Terraform Validation
- Security Scanning
- Dependency Updates
- Documentation Build
- Automated Releases

---

# Security

Security tooling includes

- CodeQL
- Bandit
- Semgrep
- Checkov
- Trivy
- Dependabot

Please refer to **SECURITY.md** for responsible disclosure.

---

# Testing

Supported testing suites

- Unit Tests
- Integration Tests
- Performance Tests
- Regression Tests
- Security Tests

Run all tests

```bash
make test
```

---

# Deployment

Supported deployment targets

- Docker
- Docker Compose
- Kubernetes
- Helm Charts
- GitHub Actions
- Terraform
- Azure
- AWS
- Google Cloud Platform

---

# Performance Targets

| Metric | Target |
|---------|---------|
| Supported Universe | 3,000+ Securities |
| Portfolio Size | 500 Holdings |
| Pipeline Runtime | < 5 Minutes |
| API Latency | < 200 ms |
| Test Coverage | > 90% |
| Platform Availability | 99.9% |

---

# Project Status

| Item | Status |
|------|--------|
| Version | 1.0.0 |
| Status | Active Development |
| Deployment | Production Ready |
| Python | 3.12 |
| License | MIT |

---

# Roadmap

Future enhancements include

- Machine Learning Alpha Models
- Reinforcement Learning Execution
- Portfolio Attribution Engine
- Real-Time Market Data
- Multi-Asset Portfolio Support
- Distributed Analytics
- Cloud-Native Scaling
- Multi-Broker Connectivity

---

# Contributing

Contributions are welcome.

Please review the following before submitting a pull request:

- CONTRIBUTING.md
- CODE_OF_CONDUCT.md
- GOVERNANCE.md
- SECURITY.md

---

# License

This project is licensed under the MIT License.

See the `LICENSE` file for details.

---

# Author

**Pavan Sai Nekkala**

GitHub: https://github.com/sakshinekkala28

---

# Acknowledgements

This project leverages the open-source Python ecosystem and cloud-native technologies to provide a scalable, modular, and production-ready platform for institutional quantitative investment research, portfolio management, and financial analytics.